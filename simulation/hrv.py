"""Structured beat-to-beat (RR) generation for OCPE — G-P0-05 (W2-E).

Replaces the legacy uniform +/-2% beat-noise path with a mechanistically
structured generator, per docs/evidence_package/TEMPORAL_MODEL_EVIDENCE.md
§beats and OCPE_DATASET_SPECIFICATION.md §L5:

  * IPFM core (Integral Pulse Frequency Modulation): beats fire when the
    integral of the instantaneous modulation function crosses threshold 1
    [E2: McSharry 2003 DOI 10.1109/TBME.2003.808805; Bailon 2021
    S1746809421003335; registry EVD-TEMP-011].
  * RSA: HF modulation at the (time-varying) respiration frequency,
    amplitude scaled by vagal drive; amplitude falls -20 dB/decade above
    0.1 Hz breathing frequency [E3: Hirsch & Bishop 1981, via AUTONOMIC
    dossier Claim 6.3, registry row 49]. Vagal limb bandwidth >=0.4-0.5 Hz
    [E4: AUTONOMIC Claim 3.1 / EVD-TEMP-005].
  * Mayer / LF: 0.1 Hz sympathetic-baroreflex component, bandwidth-limited
    <=0.1 Hz (sympathetic modulation cannot follow fluctuations faster than
    ~0.1-0.15 Hz [E4: Saul 1991 via PMC2269357; baroreflex low-pass,
    ineffective >0.1 Hz, pone.0248428]).
  * 1/f fractal noise: explicit spectral-shaping modulator; IPFM alone
    cannot produce fractal structure (TEMPORAL dossier §1). Calibrated so
    output RR DFA-alpha1 ~= 1.0 (healthy awake range 0.7-1.2,
    EVD-TEMP-001).
  * Ectopy: Bernoulli per-beat PVC/PAC events with phase reset and
    (fully) compensatory pause [E1: Holter PVC prevalence 40-75% of
    adults >=1/24 h, StatPearls NBK547713 / Dong 2022 BMJ Open e059337,
    SENSOR dossier; TEMPORAL dossier table row "Ectopy bursts"].

Autonomic drive inputs are passed through the latency/filter model of
AUTONOMIC dossier Claim 3.1 before they set modulation amplitudes:
vagal first-order tau_v ~ 0.5-1.5 s (+ pure delay 0.2-0.6 s); sympathetic
first-order tau_s ~ 5-15 s (+ pure delay ~1.5-2 s), bandwidth <=0.1 Hz.

Disease discipline (SPEC rule 4): this module contains NO disease-specific
HRV patterns. Disease affects the output only through the autonomic /
mean-HR inputs the engine already computes.

LF/HF NOTE (binding, AUTONOMIC dossier Claim 6.2): LF/HF is NOT a
sympathovagal index and is never emitted or labeled as such here. The
generator reproduces its known failure mode mechanistically: slow (0.1 Hz)
breathing shifts RSA power into the LF band and inflates LF/HF with ZERO
sympathetic change (validated in tests/test_hrv.py).

The inverse-Gaussian point process (EVD-TEMP-002) is the validation
reference distribution, NOT the generator (TEMPORAL dossier recommendation,
engineering judgment E5).
"""

from dataclasses import dataclass, field

import numpy as np
from scipy.signal import lfilter, lfilter_zi

HRV_CONFIG_VERSION = "1.0.0"

# Sleep-stage gain on overall HRV amplitude (state-dependent variance:
# sleep > rest; TEMPORAL dossier §7, E5 provisional engineering values).
STAGE_AMPLITUDE_GAIN = {0: 1.00, 1: 1.05, 2: 1.15, 3: 1.35, 4: 1.05}


class HRVParam:
    """A distributed scientific parameter (SPEC rule 6): value, units,
    distribution, evidence tier, source claim ids, uncertainty.

    The realized per-subject value is drawn from the distribution under the
    generator seed; ``mean`` is the calibrated population anchor.
    """

    def __init__(self, name, mean, units, distribution, spread, tier,
                 claim_ids, source, note=""):
        self.name = name
        self.mean = float(mean)
        self.units = units
        self.distribution = distribution  # "lognormal" | "normal" | "uniform" | "fixed"
        self.spread = spread              # lognormal/normal: CV; uniform: (lo, hi)
        self.tier = tier
        self.claim_ids = list(claim_ids)
        self.source = source
        self.note = note

    def realize(self, rng):
        if self.distribution == "fixed":
            return self.mean
        if self.distribution == "lognormal":
            cv = float(self.spread)
            sigma = np.sqrt(np.log(1.0 + cv ** 2))
            return float(self.mean * np.exp(rng.normal(-0.5 * sigma ** 2, sigma)))
        if self.distribution == "normal":
            return float(max(0.0, rng.normal(self.mean, abs(self.mean) * float(self.spread))))
        if self.distribution == "uniform":
            lo, hi = self.spread
            return float(rng.uniform(lo, hi))
        raise ValueError(f"unknown distribution {self.distribution!r}")

    def provenance(self, realized):
        return {
            "value_used": realized,
            "mean": self.mean,
            "units": self.units,
            "distribution": self.distribution,
            "spread": self.spread,
            "evidence_tier": self.tier,
            "claim_ids": self.claim_ids,
            "source": self.source,
            "note": self.note,
        }


# ---------------------------------------------------------------------------
# Parameter table (all values distribution-carrying, claim-cited).
# Amplitudes are fractions of the mean firing rate m0 (dimensionless),
# calibrated so a normative input (HR 65 bpm, vagal 0.5, symp 0.5,
# resp 15.5 brpm, awake) reproduces the Nunan 2010 5-min norms
# (RMSSD 42+/-15 ms, SDNN 50+/-16 ms, LF 519+/-291 ms^2, HF 657+/-777 ms^2;
# EVD-HLTH-002 / AUTONOMIC Claim 1.5).  Calibration anchors are E5
# engineering judgment ON TOP OF the cited normative distributions.
# ---------------------------------------------------------------------------
def default_params():
    return {
        # RSA amplitude at 0.1 Hz breathing and vagal_drive = 1 (fraction of m0).
        # Anchored to Nunan HF power 657 ms^2 at IBI ~926 ms with the
        # Hirsch & Bishop -20 dB/decade breathing-frequency fall-off.
        "rsa_amplitude_0p1Hz": HRVParam(
            "rsa_amplitude_0p1Hz", 0.170, "fraction of m0", "lognormal", 0.25,
            "E2/E3 (anchor E5-calibrated)",
            ["EVD-HLTH-002", "EVD-POP-002"],
            "Nunan 2010 PMID 20663071 (HF 657+/-777 ms^2); Hirsch & Bishop 1981 "
            "(-20 dB/decade >0.1 Hz, AUTONOMIC Claim 6.3)",
            "HF spread in norms is large -> lognormal CV 0.25"),
        # Mayer/LF amplitude at sympathetic_drive = 1 (fraction of m0).
        "mayer_amplitude": HRVParam(
            "mayer_amplitude", 0.070, "fraction of m0", "lognormal", 0.30,
            "E2/E5 (anchor E5-calibrated)",
            ["EVD-HLTH-002"],
            "Nunan 2010 LF 519+/-291 ms^2; 0.1 Hz Mayer frequency "
            "(EVD-TEMP-003 mechanism); sympathetic bandwidth <=0.1 Hz "
            "(AUTONOMIC Claim 3.1)"),
        # 1/f fractal modulator RMS amplitude (fraction of m0) and spectral
        # exponent of the MODULATOR.  beta_mod = 1.1 compensates the IPFM
        # integrate-and-hold transfer (boxcar over one beat) so the OUTPUT RR
        # series meets DFA-alpha1 ~= 1.0 (EVD-TEMP-001); E5 calibration,
        # documented in tests.
        "fractal_amplitude": HRVParam(
            "fractal_amplitude", 0.075, "fraction of m0 (RMS)", "lognormal", 0.15,
            "E1/E5 (anchor E5-calibrated)",
            ["EVD-TEMP-001"],
            "DFA-alpha1 ~1.0 rest (PMC7358842); SDNN 50+/-16 ms residual "
            "variance (Nunan 2010)"),
        "fractal_beta": HRVParam(
            "fractal_beta", 1.1, "PSD exponent of modulator", "normal", 0.02,
            "E5 (calibrated to EVD-TEMP-001)",
            ["EVD-TEMP-001"],
            "1/f (beta=1) idealization shifted to 1.1 to compensate IPFM "
            "integration filtering; achieves output DFA-alpha1 in [0.8, 1.2]"),
        # Vagal limb dynamics (AUTONOMIC Claim 3.1, E4).
        "vagal_tau_s": HRVParam(
            "vagal_tau_s", 1.0, "s", "uniform", (0.5, 1.5), "E4",
            ["EVD-TEMP-005"],
            "AUTONOMIC Claim 3.1: vagal first-order tau 0.5-1.5 s, "
            "bandwidth to 0.5 Hz"),
        "vagal_delay_s": HRVParam(
            "vagal_delay_s", 0.4, "s", "uniform", (0.2, 0.6), "E4",
            ["EVD-TEMP-005"],
            "AUTONOMIC Claim 3.1: vagal baroreflex latency 200-600 ms "
            "(PMC6931942)"),
        # Sympathetic limb dynamics (AUTONOMIC Claim 3.1, E4).
        "symp_tau_s": HRVParam(
            "symp_tau_s", 10.0, "s", "uniform", (5.0, 15.0), "E4",
            ["EVD-TEMP-005"],
            "AUTONOMIC Claim 3.1: sympathetic first-order tau 5-15 s, "
            "corner 0.01-0.02 Hz, bandwidth <=0.1 Hz"),
        "symp_delay_s": HRVParam(
            "symp_delay_s", 1.75, "s", "uniform", (1.5, 2.0), "E4",
            ["EVD-TEMP-005"],
            "AUTONOMIC Claim 3.1: sympathetic pure delay ~1.5-2 s "
            "(Berger 1989 PMID 2912176; PMC6931942)"),
        # Ectopy: Bernoulli per-beat probability. Default LOW (~2 events/day
        # at 100k beats/day), consistent with 40-75% of adults showing >=1
        # PVC/24 h while burden >=5% is rare (~7.7% of palpitation
        # outpatients). Configurable per cohort.
        "ectopy_prob_per_beat": HRVParam(
            "ectopy_prob_per_beat", 2.0e-5, "1/beat", "lognormal", 0.8, "E1",
            ["EVD-TEMP-011"],
            "Holter PVC prevalence 40-75% of adults >=1/24 h (StatPearls "
            "NBK547713; Dong 2022 BMJ Open e059337; SENSOR dossier); "
            "burden distribution right-skewed -> lognormal, default low"),
        # Ectopic coupling interval as fraction of the local sinus cycle.
        "ectopy_coupling_fraction": HRVParam(
            "ectopy_coupling_fraction", 0.725, "fraction of local RR",
            "uniform", (0.60, 0.85), "E5",
            ["EVD-TEMP-011"],
            "prematurity + fully compensatory pause (coupling + pause = "
            "2 x local RR); SA-node phase reset per TEMPORAL dossier "
            "(Bernoulli + phase reset with s-parameter)"),
    }


@dataclass
class HRVConfig:
    """Configuration for the structured HRV generator.

    integration_dt_s : fine integration grid (s). 0.05 s resolves RSA up to
        0.4 Hz with ~ms beat-time interpolation error.
    fractal_fs_hz : sampling rate of the fractal-noise modulator (Hz);
        4 Hz covers the DFA-alpha1 window scales (4-16 beats) plus HF
        content while keeping multi-day horizons cheap.
    chunk_s : processing chunk length (s) bounding memory on long horizons.
    age_years : optional subject age; enables the RSA/RMSSD age-decline
        factor (POPULATION dossier A.2: lnRMSSD decline ~-40% per 2 decades
        mid-life, plateau ~25% of young-adult value after ~60 y; E2/E4).
        None -> factor 1.0 (reference young adult).
    fitness_rsa_gain : multiplicative RSA hook for cardiorespiratory fitness
        (RMSSD<->VO2max r 0.2-0.6, E2 heterogeneous -> hook only, default 1).
    stage_amplitude_gain : per-sleep-stage HRV amplitude gain
        (state-dependent variance, TEMPORAL dossier §7, E5 provisional).
    subject_params : optional dict overriding realized parameter values
        (exact control; bypasses distribution sampling).
    sample_distributions : if True (default) draw per-subject realizations
        from the parameter distributions under the generator seed.
    ectopy_enabled : master switch for Bernoulli ectopy (default True).
    """

    integration_dt_s: float = 0.05
    fractal_fs_hz: float = 4.0
    chunk_s: float = 1800.0
    age_years: float | None = None
    fitness_rsa_gain: float = 1.0
    stage_amplitude_gain: dict = field(
        default_factory=lambda: dict(STAGE_AMPLITUDE_GAIN))
    subject_params: dict | None = None
    sample_distributions: bool = True
    ectopy_enabled: bool = True
    version: str = HRV_CONFIG_VERSION


def rmssd_age_factor(age_years):
    """RSA/RMSSD age-decline factor relative to a 25-y reference.

    POPULATION dossier A.2 + age-decline summary (E2/E4): parasympathetic
    indices fall ~40% per 2 decades mid-life (steepest 20s->30s... 50s),
    then plateau ~25% of young-adult values after ~60-70 y.
    """
    age = float(age_years)
    factor = 0.6 ** ((age - 25.0) / 20.0)
    return float(min(1.25, max(0.25, factor)))


def _fractal_noise(n, beta, rng):
    """Unit-RMS Gaussian noise with PSD ~ 1/f^beta (FFT spectral shaping)."""
    if n < 8:
        return np.zeros(n)
    white = rng.standard_normal(n)
    W = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(n, d=1.0)
    freqs[0] = freqs[1]
    amp = freqs ** (-beta / 2.0)
    amp[0] = 0.0  # zero DC: mean HR is owned by m0
    x = np.fft.irfft(W * amp, n=n)
    sd = x.std()
    return x / sd if sd > 0 else x


def _validate_inputs(hrv_inputs):
    required = ("time_s", "mean_hr_bpm", "vagal_drive", "sympathetic_drive",
                "respiration_rate_brpm")
    for k in required:
        if k not in hrv_inputs:
            raise KeyError(f"hrv_inputs missing required key {k!r}")
    t = np.asarray(hrv_inputs["time_s"], dtype=np.float64)
    hr = np.asarray(hrv_inputs["mean_hr_bpm"], dtype=np.float64)
    vag = np.asarray(hrv_inputs["vagal_drive"], dtype=np.float64)
    sym = np.asarray(hrv_inputs["sympathetic_drive"], dtype=np.float64)
    resp = np.asarray(hrv_inputs["respiration_rate_brpm"], dtype=np.float64)
    n = t.shape[0]
    for name, arr in (("mean_hr_bpm", hr), ("vagal_drive", vag),
                      ("sympathetic_drive", sym), ("respiration_rate_brpm", resp)):
        if arr.shape[0] != n:
            raise ValueError(f"{name} length {arr.shape[0]} != time_s length {n}")
    if n < 3:
        raise ValueError("hrv_inputs too short (need >= 3 samples)")
    if np.any(np.diff(t) <= 0):
        raise ValueError("time_s must be strictly increasing")
    if np.any(hr <= 0):
        raise ValueError("mean_hr_bpm must be positive (noise-free mean trajectory)")
    if "sleep_stage_code" in hrv_inputs:
        stage = np.asarray(hrv_inputs["sleep_stage_code"], dtype=int)
    else:
        stage = np.zeros(n, dtype=int)
    return t, hr, vag, sym, resp, stage


def generate_rr_series(hrv_inputs, seed, config=None):
    """Generate a structured RR series from engine HRV inputs (G-P0-05).

    Parameters
    ----------
    hrv_inputs : dict
        Contract from ``SimulationEngine.get_hrv_inputs()``: keys
        ``time_s``, ``mean_hr_bpm`` (noise-free), ``vagal_drive`` [0,1],
        ``sympathetic_drive`` [0,1], ``respiration_rate_brpm``,
        ``sleep_stage_code`` (optional; default awake).
    seed : int | None
        Deterministic under a fixed seed (numpy Generator); None draws from
        OS entropy.
    config : HRVConfig | None

    Returns
    -------
    dict with keys
      ``beat_times_s``    float64 [N], absolute beat times (s), same time
                          base as ``hrv_inputs['time_s']``
      ``rr_intervals_ms`` float64 [N-1], successive RR intervals (ms)
      ``beat_types``      str array [N] ("<U8"), "normal" | "ectopic";
                          element i classifies the beat at beat_times_s[i]
                          (an ectopic beat is the PREMATURE one; the beat
                          after its compensatory pause is "normal")
      ``provenance``      dict: parameter sources, claim_ids, seed, config
                          version, honesty notes
    """
    cfg = config if config is not None else HRVConfig()
    rng = np.random.default_rng(seed)
    t, hr, vag, sym, resp, stage = _validate_inputs(hrv_inputs)

    # --- Realize subject-level parameters from their distributions --------
    paramspec = default_params()
    realized = {}
    overrides = cfg.subject_params or {}
    for name, p in paramspec.items():
        if name in overrides:
            realized[name] = float(overrides[name])
        elif cfg.sample_distributions:
            realized[name] = p.realize(rng)
        else:
            realized[name] = p.mean
    if not cfg.ectopy_enabled:
        realized["ectopy_prob_per_beat"] = 0.0

    age_gain = (rmssd_age_factor(cfg.age_years) if cfg.age_years is not None
                else 1.0)

    # --- Fractal modulator on its own coarse grid (full horizon) ----------
    dt = float(cfg.integration_dt_s)
    fs_f = float(cfg.fractal_fs_hz)
    t0, t1 = float(t[0]), float(t[-1])
    n_f = max(8, int((t1 - t0) * fs_f) + 1)
    tf = t0 + np.arange(n_f) / fs_f
    frac_coarse = _fractal_noise(n_f, realized["fractal_beta"], rng)

    # --- Chunked IPFM integration -----------------------------------------
    dt_v = realized["vagal_delay_s"]
    dt_s = realized["symp_delay_s"]
    # First-order low-pass coefficients (b, a) for y_i=(1-c)y_{i-1}+c x_i
    cv_ = 1.0 - np.exp(-dt / realized["vagal_tau_s"])
    cs_ = 1.0 - np.exp(-dt / realized["symp_tau_s"])
    b_v, a_v = [cv_], [1.0, -(1.0 - cv_)]
    b_s, a_s = [cs_], [1.0, -(1.0 - cs_)]

    beat_times = []
    integ_offset = 0.0     # integral value at chunk start
    level = 1              # next integer threshold to cross
    phase_offset = 0.0     # RSA respiratory phase at chunk start (rad)
    zi_v = zi_s = None
    chunk_len = max(16, int(cfg.chunk_s / dt))
    n_grid = int(np.ceil((t1 - t0) / dt)) + 1

    for start in range(0, n_grid, chunk_len):
        stop = min(start + chunk_len, n_grid)
        tg = t0 + np.arange(start, stop) * dt
        m0 = np.interp(tg, t, hr) / 60.0
        f_resp = np.interp(tg, t, resp) / 60.0
        vag_c = np.interp(tg - dt_v, t, vag, left=vag[0])
        sym_c = np.interp(tg - dt_s, t, sym, left=sym[0])
        gain_c = np.interp(tg, t, stage.astype(float))
        gain_c = np.vectorize(cfg.stage_amplitude_gain.get, otypes=[float])(
            gain_c.astype(int))
        # Latency/filter model (AUTONOMIC Claim 3.1); steady-state filter
        # state initialisation avoids a startup transient at chunk 0.
        if zi_v is None:
            zi_v = lfilter_zi(b_v, a_v) * vag_c[0]
            zi_s = lfilter_zi(b_s, a_s) * sym_c[0]
        vag_f, zi_v = lfilter(b_v, a_v, vag_c, zi=zi_v)
        sym_f, zi_s = lfilter(b_s, a_s, sym_c, zi=zi_s)

        # RSA: amplitude -20 dB/decade above 0.1 Hz breathing frequency
        ffac = np.where(f_resp > 0.1, 0.1 / np.maximum(f_resp, 1e-3), 1.0)
        phase = phase_offset + 2.0 * np.pi * np.cumsum(f_resp) * dt
        phase_offset = float(phase[-1])
        rsa = (realized["rsa_amplitude_0p1Hz"] * age_gain
               * cfg.fitness_rsa_gain * vag_f * ffac * np.sin(phase))

        mayer = realized["mayer_amplitude"] * sym_f * np.sin(
            2.0 * np.pi * 0.1 * (tg - t0))

        frac = realized["fractal_amplitude"] * np.interp(tg, tf, frac_coarse)

        mod = gain_c * (rsa + mayer + frac)
        rate = m0 * (1.0 + mod)
        # Safety clip: firing rate must stay positive (documented guard;
        # inactive for normative parameter ranges).
        rate = np.maximum(rate, 0.05 * m0)
        integ_before = integ_offset  # integral one grid step before tg[0]
        integ = integ_offset + np.cumsum(rate) * dt
        integ_offset = float(integ[-1])

        hi = int(np.floor(integ[-1]))
        if hi >= level:
            levels = np.arange(level, hi + 1, dtype=np.float64)
            # Extend the interpolation domain one step back so a threshold
            # crossing in the gap between chunks is placed exactly (chunking
            # is a memory bound only; it must not perturb the series).
            integ_ext = np.concatenate(([integ_before], integ))
            tg_ext = np.concatenate(([tg[0] - dt], tg))
            beat_times.append(np.interp(levels, integ_ext, tg_ext))
            level = hi + 1

    if not beat_times:
        raise ValueError("no beats generated; mean_hr_bpm or horizon too small")
    beats = np.concatenate(beat_times)
    types = np.full(beats.shape[0], "normal", dtype="<U8")

    # --- Bernoulli ectopy with phase reset + compensatory pause -----------
    p_ect = realized["ectopy_prob_per_beat"]
    if p_ect > 0.0 and beats.shape[0] > 4:
        fires = rng.random(beats.shape[0]) < p_ect
        k = 1
        while k < beats.shape[0] - 2:
            if fires[k]:
                t_loc = np.interp(beats[k], t, hr)
                T_loc = 60.0 / t_loc
                coup = realized["ectopy_coupling_fraction"] * T_loc
                # Phase reset: premature firing of the integrator
                beats[k] = beats[k - 1] + coup
                types[k] = "ectopic"
                # Fully compensatory pause: coupling + pause = 2 x local RR
                beats[k + 1] = beats[k] + (2.0 * T_loc - coup)
                k += 2  # no stacked ectopy (physiological refractoriness)
            else:
                k += 1

    rr_ms = np.diff(beats) * 1000.0

    provenance = {
        "module": "simulation/hrv.py",
        "generator": "IPFM + RSA(vagal, resp-gated) + Mayer 0.1 Hz "
                     "(sympathetic, <=0.1 Hz) + 1/f fractal + Bernoulli "
                     "ectopy (phase reset, compensatory pause)",
        "config_version": cfg.version,
        "seed": seed,
        "parameters": {name: paramspec[name].provenance(realized[name])
                       for name in paramspec},
        "age_gain": age_gain,
        "fitness_rsa_gain": cfg.fitness_rsa_gain,
        "stage_amplitude_gain": {int(k): v for k, v in
                                 cfg.stage_amplitude_gain.items()},
        "claim_ids": sorted({cid for p in paramspec.values()
                             for cid in p.claim_ids}),
        "integration_dt_s": dt,
        "fractal_fs_hz": fs_f,
        "honesty_notes": [
            "LF/HF is NOT a sympathovagal index (AUTONOMIC Claim 6.2); it "
            "is never emitted as such. Slow (0.1 Hz) breathing inflates "
            "LF/HF with zero sympathetic change by design.",
            "Inverse-Gaussian point process (EVD-TEMP-002) is the "
            "validation reference distribution, not the generator (E5).",
            "Fractal modulator beta=1.1 is an E5 calibration compensating "
            "IPFM integration filtering to achieve output DFA-alpha1 ~= 1.0 "
            "(EVD-TEMP-001).",
            "No disease-specific HRV patterns (SPEC rule 4): disease acts "
            "only via engine-computed autonomic/mean-HR inputs.",
        ],
        "input_honesty_flags": list(hrv_inputs.get("honesty_flags", [])),
    }

    return {
        "beat_times_s": beats.astype(np.float64),
        "rr_intervals_ms": rr_ms.astype(np.float64),
        "beat_types": types,
        "provenance": provenance,
    }
