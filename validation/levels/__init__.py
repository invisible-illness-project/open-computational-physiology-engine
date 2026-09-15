"""OCPE release-gate validation levels (W3-V).

Runnable implementations of Levels 1-4 plus the anti-laundering negative
controls of ``docs/evidence_package/SYNTHETIC_TO_REAL_BENCHMARK.md``.

Modules
-------
l1                Level 1 - mathematical validity (determinism, conservation,
                  kernel baseline restoration, schema/provenance/contract
                  hooks, identifiability guards, honesty gating).
l2                Level 2 - physiological plausibility (event-protocol
                  trajectory battery + timescale signatures).
l3                Level 3 - clinical plausibility (frozen healthy reference,
                  published targets, disclosed limitations).
l4                Level 4 - real-data anchors (PRCP orthostatic comparison,
                  resting-HRV published norms).
negative_controls Anti-laundering battery (parity of acquisition/statistical
                  nuisance channels; trivial-separability classifier gate).
run_release_gates Single entry point -> docs/validation_report.md +
                  validation/release_gates.yaml.

Every check returns a :class:`CheckResult`.  Statuses:

  * ``pass`` / ``fail`` -- measured value inside / outside the
    pre-registered target.
  * ``unresolved`` -- the check could not be executed or the sample size /
    data access is insufficient to resolve the target (exact reason
    recorded; SWARM_SPEC global rule 1).
  * ``disclosed_limitation`` -- a documented model limitation that must
    surface in the report and must NOT be counted as a pass.

Governing statement (binding, benchmark §5.3 item 4; emitted in every
report): "OCPE synthetic data are candidate research artifacts whose
utility for any task is unestablished pending the Level-5 benchmark."
No Level-5 claims are made anywhere in this package: the L5 benchmark
matrix does not exist yet.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

#: Binding release language (SYNTHETIC_TO_REAL_BENCHMARK.md §5.3 item 4).
GOVERNING_STATEMENT = (
    "OCPE synthetic data are candidate research artifacts whose utility "
    "for any task is unestablished pending the Level-5 benchmark."
)

STATUS_PASS = "pass"
STATUS_FAIL = "fail"
STATUS_UNRESOLVED = "unresolved"
STATUS_LIMITATION = "disclosed_limitation"
STATUSES = (STATUS_PASS, STATUS_FAIL, STATUS_UNRESOLVED, STATUS_LIMITATION)


@dataclass
class CheckResult:
    """One release-gate check outcome (results-table row)."""
    gate: str                    # e.g. "L1", "L2", "L3", "L4", "NC"
    check: str                   # short check id, e.g. "1.5_determinism"
    target: str                  # pre-registered acceptance criterion (text)
    measured: Any                # measured value(s) (JSON-safe)
    status: str                  # one of STATUSES
    evidence: str = ""           # claim ids / sources / file references
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gate": self.gate,
            "check": self.check,
            "target": self.target,
            "measured": _json_safe(self.measured),
            "status": self.status,
            "evidence": self.evidence,
            "note": self.note,
        }


def _json_safe(x: Any) -> Any:
    if isinstance(x, dict):
        return {str(k): _json_safe(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_json_safe(v) for v in x]
    if isinstance(x, np.ndarray):
        return _json_safe(x.tolist())
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        x = float(x)
    if isinstance(x, float):
        return None if (math.isnan(x) or math.isinf(x)) else round(x, 6)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    return x


# ---------------------------------------------------------------------------
# Small self-contained statistics (numpy/scipy only; SWARM_SPEC rule 9)
# ---------------------------------------------------------------------------

def dfa_alpha1(rr_ms: Sequence[float], lo: int = 4, hi: int = 16) -> float:
    """Short-term DFA scaling exponent (windows lo..hi beats, linear
    detrend; EVD-TEMP-001 semantics)."""
    rr = np.asarray(rr_ms, dtype=float)
    rr = rr[np.isfinite(rr)]
    if rr.size < hi + 2:
        return float("nan")
    y = np.cumsum(rr - rr.mean())
    scales, fluct = [], []
    for s in range(lo, hi + 1):
        nseg = len(y) // s
        if nseg < 1:
            continue
        rms = []
        for j in range(nseg):
            seg = y[j * s:(j + 1) * s]
            x = np.arange(s)
            p = np.polyfit(x, seg, 1)
            rms.append(np.sqrt(np.mean((seg - np.polyval(p, x)) ** 2)))
        scales.append(s)
        fluct.append(np.mean(rms))
    if len(scales) < 3 or np.any(np.asarray(fluct) <= 0):
        return float("nan")
    a, _ = np.polyfit(np.log(scales), np.log(fluct), 1)
    return float(a)


def band_powers(rr_ms: Sequence[float], fs: float = 4.0):
    """Periodogram of the evenly resampled RR tachogram.

    Returns (freqs, power, lf, hf); LF = 0.04-0.15 Hz, HF = 0.15-0.40 Hz
    (Task Force 1996 bands)."""
    rr = np.asarray(rr_ms, dtype=float)
    rr = rr[np.isfinite(rr)]
    tt = np.cumsum(rr / 1000.0)
    tg = np.arange(0.0, tt[-1], 1.0 / fs)
    if tg.size < 16:
        return np.array([]), np.array([]), float("nan"), float("nan")
    sig = np.interp(tg, tt, rr)
    sig = sig - sig.mean()
    P = np.abs(np.fft.rfft(sig * np.hanning(len(sig)))) ** 2
    freqs = np.fft.rfftfreq(len(sig), 1.0 / fs)
    lf = float(P[(freqs >= 0.04) & (freqs < 0.15)].sum())
    hf = float(P[(freqs >= 0.15) & (freqs <= 0.40)].sum())
    return freqs, P, lf, hf


def peak_freq(freqs: np.ndarray, power: np.ndarray, lo: float, hi: float) -> float:
    mask = (freqs >= lo) & (freqs <= hi)
    if not np.any(mask):
        return float("nan")
    return float(freqs[mask][np.argmax(power[mask])])


def rmssd(rr_ms: Sequence[float]) -> float:
    rr = np.asarray(rr_ms, dtype=float)
    rr = rr[np.isfinite(rr)]
    if rr.size < 3:
        return float("nan")
    return float(np.sqrt(np.mean(np.diff(rr) ** 2)))


def sdnn(rr_ms: Sequence[float]) -> float:
    rr = np.asarray(rr_ms, dtype=float)
    rr = rr[np.isfinite(rr)]
    if rr.size < 3:
        return float("nan")
    return float(np.std(rr, ddof=1))


def auc_score(y_true: Sequence[int], y_score: Sequence[float]) -> float:
    """Rank-based AUC (Mann-Whitney), ties handled by average ranks."""
    y = np.asarray(y_true, dtype=int)
    s = np.asarray(y_score, dtype=float)
    pos = s[y == 1]
    neg = s[y == 0]
    if pos.size == 0 or neg.size == 0:
        return float("nan")
    wins, total = 0.0, pos.size * neg.size
    for p in pos:
        wins += float(np.sum(p > neg)) + 0.5 * float(np.sum(p == neg))
    return wins / total


def logistic_regression_fit(X: np.ndarray, y: np.ndarray, l2: float = 1.0,
                            n_iter: int = 200, lr: float = 0.1) -> np.ndarray:
    """Tiny L2-regularized logistic regression (gradient descent on the
    standardized design matrix; numpy only).  Returns weight vector with
    the intercept in position 0."""
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    n, d = X.shape
    Xd = np.column_stack([np.ones(n), X])
    w = np.zeros(d + 1)
    for _ in range(n_iter):
        z = Xd @ w
        p = 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))
        grad = Xd.T @ (p - y) / n
        grad[1:] += l2 * w[1:] / n
        w -= lr * grad
    return w


def loocv_auc(X: np.ndarray, y: np.ndarray, l2: float = 1.0) -> float:
    """Leave-one-out cross-validated AUC for the tiny-cohort separability
    gate.  Features are standardized on the training fold only."""
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=int)
    n = len(y)
    scores = np.empty(n)
    for i in range(n):
        tr = np.arange(n) != i
        mu = X[tr].mean(axis=0)
        sd = X[tr].std(axis=0)
        sd[sd == 0.0] = 1.0
        w = logistic_regression_fit((X[tr] - mu) / sd, y[tr], l2=l2)
        xi = (X[i] - mu) / sd
        z = w[0] + xi @ w[1:]
        scores[i] = 1.0 / (1.0 + math.exp(-float(np.clip(z, -30, 30))))
    return auc_score(y, scores)


def cosinor_amplitude(hours: np.ndarray, values: np.ndarray,
                      period_h: float = 24.0) -> Dict[str, float]:
    """Least-squares single-component cosinor fit.

    Returns mesor, amplitude (half-range) and acrophase (hours)."""
    hours = np.asarray(hours, dtype=float)
    values = np.asarray(values, dtype=float)
    w = 2.0 * np.pi / period_h
    A = np.column_stack([np.ones_like(hours), np.cos(w * hours),
                         np.sin(w * hours)])
    coef, *_ = np.linalg.lstsq(A, values, rcond=None)
    mesor = float(coef[0])
    amp = float(np.hypot(coef[1], coef[2]))
    acro = float((-np.arctan2(coef[2], coef[1])) % (2 * np.pi)) / w
    return {"mesor": mesor, "amplitude": amp, "acrophase_h": acro}
