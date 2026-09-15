"""Level 4 - SIGNAL-LEVEL COMPARISON vs REAL DATA (§L4).

Anchors implemented (VALIDATION_DATASETS.md priority ladder #1 and cheap
no-download norms):

  * PRCP (PhysioNet, OPEN): 10 healthy subjects, ECG+Finapres 250 Hz,
    slow/rapid tilt + stand-up.  Beat annotations (.wqrs) + major-event
    annotations (.anI) are downloaded (small files only) and parsed with a
    self-contained minimal WFDB annotation reader (numpy only - the wfdb
    package is NOT a dependency, SWARM_SPEC rule 9).
    Metric: per-episode orthostatic delta-HR (final 60 s of tilt hold vs
    final 120 s supine pre-tilt, matched windows), simulated vs real
    Wasserstein distance, pre-registered target W1 <= 3 bpm (benchmark §L4).
  * Resting HRV metrics of the healthy cohort vs published norms
    (EV-supine-rest: RMSSD ln-normal median ~35-42 ms young) - no download.
  * EUROBAVAR (open download, eurobavar.altervista.org): connection
    attempted; on failure the check is recorded ``unresolved`` with the
    exact reason (rule 1).

If the network is unavailable the PRCP comparison harness is still fully
exercised in unit tests against synthetic fixtures, and the release check
is recorded ``unresolved`` with the exact fetch error.
"""

from __future__ import annotations

import os
import urllib.error
import urllib.request

import numpy as np
from scipy.stats import wasserstein_distance

from validation.levels import (
    STATUS_FAIL, STATUS_PASS, STATUS_UNRESOLVED, CheckResult, rmssd, sdnn,
)

PRCP_BASE_URL = "https://physionet.org/files/prcp/1.0.0"
EUROBAVAR_URL = "https://eurobavar.altervista.org/"

#: Pre-registered tolerance (benchmark §L4 PRCP row).
WASSERSTEIN_TARGET_BPM = 3.0
#: Window matching for the delta-HR comparison: PRCP slow-tilt holds are
#: ~3 min, so the licensed 10-min simulated windows are re-sliced to the
#: same early-hold phase (minutes 2-3 post ramp) - disclosed in the report.
REAL_SUPINE_WINDOW_S = 120.0
REAL_TILT_TAIL_WINDOW_S = 60.0
#: Resting HRV norms (EV-supine-rest; EVD-HLTH-001/002): healthy young
#: supine RMSSD ln-normal median ~35-42 ms; gate band generous around it.
RMSSD_NORM_BAND_MS = (19.0, 60.0)


# ---------------------------------------------------------------------------
# Minimal WFDB annotation reader (self-contained, numpy only)
# ---------------------------------------------------------------------------

def read_wfdb_annotations(path):
    """Read a WFDB binary annotation file.

    Word layout (little-endian byte pairs b0,b1): sample-delta =
    b0 + 256*(b1 & 3) (10 bits); annotation code = b1 >> 2 (6 bits).
    SKIP (code 59): the next two words carry a 32-bit two's-complement
    delta as (w1.b0<<16)+(w1.b1<<24)+(w2.b0)+(w2.b1<<8).  Extra fields
    NUM(60)/SUB(61)/CHN(62)/AUX(63) follow their annotation; AUX length
    is in the delta field, padded to even.  Word 0x0000 = EOF.

    Returns list of dicts: sample, code, aux (str|None).
    """
    raw = np.fromfile(path, dtype=np.uint8)
    n_words = len(raw) // 2
    w0 = raw[0:2 * n_words:2].astype(np.int64)
    w1 = raw[1:2 * n_words:2].astype(np.int64)

    anns = []
    i, t = 0, 0
    while i < n_words:
        code = int(w1[i]) >> 2
        if code == 0 and int(w0[i]) == 0 and int(w1[i]) == 0:
            break  # EOF word
        if code == 59:  # SKIP
            if i + 2 >= n_words:
                break
            dt = ((int(w0[i + 1]) << 16) + (int(w1[i + 1]) << 24)
                  + (int(w0[i + 2])) + (int(w1[i + 2]) << 8))
            if dt > 2147483647:
                dt -= 4294967296
            t += dt
            i += 3
            continue
        t += int(w0[i]) + 256 * (int(w1[i]) & 3)
        i += 1
        aux = None
        # extra fields belonging to this annotation
        while i < n_words:
            ecode = int(w1[i]) >> 2
            if ecode not in (60, 61, 62, 63):
                break
            edelta = int(w0[i]) + 256 * (int(w1[i]) & 3)
            i += 1
            if ecode == 63:  # AUX
                nbytes = edelta
                start = 2 * i
                s = bytes(raw[start:start + nbytes]).decode("latin1").rstrip("\x00")
                i += (nbytes + 1) // 2
                aux = s
        anns.append({"sample": int(t), "code": code, "aux": aux})
    return anns


# ---------------------------------------------------------------------------
# PRCP download + delta-HR extraction
# ---------------------------------------------------------------------------

def _fetch(url, dest, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": "ocpe-validation/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r, open(dest, "wb") as f:
        f.write(r.read())


def download_prcp_annotations(dest_dir, records=None, timeout=30):
    """Download .hea/.anI/.wqrs for PRCP records.  Returns (record_ids,
    error_string).  Small annotation files only (no waveform .dat)."""
    os.makedirs(dest_dir, exist_ok=True)
    if records is None:
        rec_list_path = os.path.join(dest_dir, "RECORDS")
        _fetch(f"{PRCP_BASE_URL}/RECORDS", rec_list_path, timeout)
        with open(rec_list_path, "r", encoding="utf-8") as f:
            records = [ln.strip() for ln in f if ln.strip()]
    fetched, errors = [], []
    for rec in records:
        try:
            for ext in ("hea", "anI", "wqrs"):
                _fetch(f"{PRCP_BASE_URL}/{rec}.{ext}",
                       os.path.join(dest_dir, f"{rec}.{ext}"), timeout)
            fetched.append(rec)
        except (urllib.error.URLError, OSError, TimeoutError) as exc:
            errors.append(f"{rec}: {exc}")
    return fetched, ("; ".join(errors) if errors else None)


def prcp_delta_hr_episodes(dest_dir, record, fs=250.0):
    """Per slow-tilt episode delta-HR (bpm): mean HR over the final
    REAL_TILT_TAIL_WINDOW_S of the tilt hold minus mean HR over the final
    REAL_SUPINE_WINDOW_S supine before tilt initiation."""
    anns = read_wfdb_annotations(os.path.join(dest_dir, f"{record}.anI"))
    beats = np.array([a["sample"] for a in read_wfdb_annotations(
        os.path.join(dest_dir, f"{record}.wqrs"))], dtype=float) / fs

    events = []
    pending = None
    for a in anns:
        aux = (a.get("aux") or "").lower()
        t = a["sample"] / fs
        if "initiate slow tilt up" in aux:
            pending = t
        elif "initiate slow tilt down" in aux and pending is not None:
            events.append((pending, t))  # (tilt_start, hold_end)
            pending = None
    out = []
    for t_start, t_end in events:
        if t_end - t_start < REAL_TILT_TAIL_WINDOW_S + 20.0:
            continue
        sup = beats[(beats >= t_start - REAL_SUPINE_WINDOW_S) & (beats < t_start)]
        up = beats[(beats >= t_end - REAL_TILT_TAIL_WINDOW_S) & (beats < t_end)]
        if sup.size < 20 or up.size < 10:
            continue
        hr_sup = 60.0 / np.mean(np.diff(sup))
        hr_up = 60.0 / np.mean(np.diff(up))
        if np.isfinite(hr_sup) and np.isfinite(hr_up):
            out.append({"record": record, "tilt_start_s": t_start,
                        "hold_s": t_end - t_start,
                        "hr_supine_bpm": float(hr_sup),
                        "hr_tilt_bpm": float(hr_up),
                        "delta_hr_bpm": float(hr_up - hr_sup)})
    return out


def compare_orthostatic_distributions(real_dhr, sim_dhr):
    """Wasserstein distance between real and simulated orthostatic
    delta-HR distributions (pre-registered target <= 3 bpm)."""
    real = np.asarray(real_dhr, dtype=float)
    sim = np.asarray(sim_dhr, dtype=float)
    real = real[np.isfinite(real)]
    sim = sim[np.isfinite(sim)]
    if real.size == 0 or sim.size == 0:
        return float("nan")
    return float(wasserstein_distance(real, sim))


def run(ctx: dict) -> list:
    results = []

    # --- PRCP orthostatic anchor -------------------------------------------
    prcp = ctx.get("prcp")
    if prcp is None:
        results.append(CheckResult(
            "L4", "4_prcp_orthostatic_wasserstein",
            f"Wasserstein(sim, PRCP) on orthostatic dHR <= "
            f"{WASSERSTEIN_TARGET_BPM} bpm",
            None, STATUS_UNRESOLVED,
            evidence="PRCP PhysioNet OPEN; VALIDATION_DATASETS §1.1",
            note="context artifact 'prcp' not provided"))
    elif prcp.get("error"):
        results.append(CheckResult(
            "L4", "4_prcp_orthostatic_wasserstein",
            f"Wasserstein(sim, PRCP) on orthostatic dHR <= "
            f"{WASSERSTEIN_TARGET_BPM} bpm",
            {"fetch_error": prcp["error"]}, STATUS_UNRESOLVED,
            evidence="PRCP PhysioNet OPEN; VALIDATION_DATASETS §1.1",
            note="comparison harness implemented; download failed "
                 "(exact reason recorded)"))
    else:
        w1 = compare_orthostatic_distributions(prcp["real_delta_hr_bpm"],
                                               prcp["sim_delta_hr_bpm"])
        ok = np.isfinite(w1) and w1 <= WASSERSTEIN_TARGET_BPM
        results.append(CheckResult(
            "L4", "4_prcp_orthostatic_wasserstein",
            f"Wasserstein(sim healthy tilt dHR, PRCP real dHR) <= "
            f"{WASSERSTEIN_TARGET_BPM} bpm",
            {"wasserstein_bpm": w1,
             "n_real_episodes": len(prcp["real_delta_hr_bpm"]),
             "n_sim_subjects": len(prcp["sim_delta_hr_bpm"]),
             "real_delta_hr_bpm": prcp["real_delta_hr_bpm"],
             "sim_delta_hr_bpm": prcp["sim_delta_hr_bpm"],
             "window_semantics": prcp.get("window_semantics")},
            STATUS_PASS if ok else STATUS_FAIL,
            evidence="PRCP (PhysioNet, OPEN, Heldt et al.); benchmark §L4",
            note=prcp.get("note", "")))

    # --- EUROBAVAR (optional second anchor) ---------------------------------
    eur = ctx.get("eurobavar")
    if eur is None:
        results.append(CheckResult(
            "L4", "4_eurobavar_reflex_gain",
            "EUROBAVAR supine->standing reflex-gain comparison (reflex-gain "
            "validation ONLY, not a POTS cohort)",
            None, STATUS_UNRESOLVED,
            evidence="VALIDATION_DATASETS §1.2; reviewer Criterion 8",
            note="context artifact 'eurobavar' not provided"))
    elif eur.get("error"):
        results.append(CheckResult(
            "L4", "4_eurobavar_reflex_gain",
            "EUROBAVAR supine->standing reflex-gain comparison",
            {"fetch_error": eur["error"]}, STATUS_UNRESOLVED,
            evidence="VALIDATION_DATASETS §1.2",
            note="download/parse failed (exact reason recorded)"))
    else:
        results.append(CheckResult(
            "L4", "4_eurobavar_reflex_gain",
            "EUROBAVAR supine->standing reflex-gain comparison",
            eur.get("measured"), STATUS_PASS if eur.get("pass") else STATUS_FAIL,
            evidence="VALIDATION_DATASETS §1.2"))

    # --- Resting HRV vs published norms (no download) ------------------------
    hrv = ctx.get("resting_hrv")
    if hrv is None:
        results.append(CheckResult(
            "L4", "4_resting_hrv_norms",
            f"healthy resting RMSSD median within {RMSSD_NORM_BAND_MS} ms "
            "(EV-supine-rest norms, no download)",
            None, STATUS_UNRESOLVED, evidence="EVD-HLTH-001/002",
            note="context artifact 'resting_hrv' not provided"))
    else:
        med = hrv["rmssd_median_ms"]
        ok = np.isfinite(med) and RMSSD_NORM_BAND_MS[0] <= med <= RMSSD_NORM_BAND_MS[1]
        results.append(CheckResult(
            "L4", "4_resting_hrv_norms",
            f"healthy resting RMSSD median within {RMSSD_NORM_BAND_MS} ms "
            "(ln-normal median ~35-42 ms young; EV-supine-rest)",
            hrv, STATUS_PASS if ok else STATUS_FAIL,
            evidence="EV-supine-rest (EVD-HLTH-001/002); published norms "
                     "(literature-constraint tier, no download)"))

    return results
