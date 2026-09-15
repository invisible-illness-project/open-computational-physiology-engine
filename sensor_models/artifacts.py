"""State-dependent artifact models (SENSOR_MODEL_EVIDENCE.md §7/§8).

Every artifact here is *conditional on physiological/activity state*, never
i.i.d.: motion gating is driven by activity intensity / cadence (IMU channel),
contact loss is triggered at exercise onset and by wear state, day/night
usability follows the diurnal missingness profile, and optical front-end
amplitude depends on skin temperature (cold vasoconstriction).

All quantitative constants come from ``knowledge_base/wearables/artifact_models.yaml``
via :mod:`sensor_models.profiles`; nothing scientific is hardcoded here.
"""

from __future__ import annotations

import numpy as np

from .profiles import load_artifact_models, artifact_value


# ---------------------------------------------------------------------------
# Generic Markov burst processes
# ---------------------------------------------------------------------------

def markov_bad_mask(n: int, bad_fraction: float, mean_burst_len: float,
                    rng: np.random.Generator) -> np.ndarray:
    """Two-state (good/bad) Markov chain boolean mask (True = good).

    Stationary bad fraction is ``bad_fraction``; bad episodes have geometric
    durations with mean ``mean_burst_len`` samples. Used for BLE dropout
    bursts and quality-gated missingness (bursty, not i.i.d.).
    """
    bad_fraction = float(np.clip(bad_fraction, 0.0, 0.999))
    if bad_fraction == 0.0:
        return np.ones(n, dtype=bool)
    mean_burst_len = max(1.0, float(mean_burst_len))
    p_exit = 1.0 / mean_burst_len
    p_enter = bad_fraction * p_exit / (1.0 - bad_fraction)
    p_enter = min(p_enter, 1.0)
    good = np.ones(n, dtype=bool)
    bad = rng.random() < bad_fraction
    for i in range(n):
        if bad:
            good[i] = False
            bad = not (rng.random() < p_exit)
        else:
            bad = rng.random() < p_enter
    return good


def dropout_burst_mask(n: int, activity_intensity: np.ndarray, cfg: dict,
                       rng: np.random.Generator, regime: str = "on_device",
                       mean_burst_len: float = 5.0) -> np.ndarray:
    """BLE-type dropout bursts, motion-gated.

    Baseline loss fraction comes from the KB (streaming up to 49% vs <=9%
    on-device, EVD-SENS-003). Activity intensity multiplies the instantaneous
    loss probability (motion stress on the RF/link and electrode contact),
    clipped to the configured streaming ceiling.
    """
    if regime == "streaming":
        base = artifact_value(cfg, "dropout.streaming_loss_fraction_max")
    else:
        base = artifact_value(cfg, "dropout.on_device_loss_fraction_max")
    motion_gain = artifact_value(cfg, "dropout.motion_loss_gain", default=1.0)
    mean_intensity = float(np.mean(activity_intensity)) if len(activity_intensity) else 0.0
    effective = base * (1.0 + motion_gain * mean_intensity)
    ceiling = artifact_value(cfg, "dropout.streaming_loss_fraction_max")
    effective = min(effective, ceiling)
    return markov_bad_mask(n, effective, mean_burst_len, rng)


def day_night_quality_mask(is_night: np.ndarray, modality: str, cfg: dict,
                           rng: np.random.Generator,
                           mean_episode_len: float = 300.0) -> np.ndarray:
    """Per-sample good-quality mask reproducing day/night usability fractions.

    Targets (EVD-SENS-003): wrist PPG good-quality ~30-60% daytime vs
    65-75% night; EDA 65.6% day / 75.1% night; TEMP 96.1% overall.
    Implemented as a slowly switching Markov quality process whose stationary
    good fraction depends on the day/night state (minutes-scale dwell).
    """
    is_night = np.asarray(is_night, dtype=bool)
    n = len(is_night)
    good = np.ones(n, dtype=bool)
    if n == 0:
        return good
    key_day = f"day_night_usability.{modality}_day_good_fraction"
    key_night = f"day_night_usability.{modality}_night_good_fraction"
    p_day = artifact_value(cfg, key_day)
    p_night = artifact_value(cfg, key_night, default=p_day)
    # Split into contiguous day/night segments and run one Markov chain per
    # segment so the stationary fractions are exactly the configured targets.
    seg_start = 0
    state = is_night[0]
    for i in range(1, n + 1):
        if i == n or is_night[i] != state:
            target = p_night if state else p_day
            good[seg_start:i] = markov_bad_mask(
                i - seg_start, 1.0 - target, mean_episode_len, rng)
            if i < n:
                seg_start, state = i, is_night[i]
    return good


# ---------------------------------------------------------------------------
# Motion-gated waveform artifacts
# ---------------------------------------------------------------------------

def cadence_locked_artifact(t: np.ndarray, activity_intensity: np.ndarray,
                            cadence_hz: np.ndarray, pulse_ac_amplitude: float,
                            cfg: dict, rng: np.random.Generator) -> np.ndarray:
    """PPG motion artifact concentrated at step frequency + first harmonic.

    During rhythmic locomotion the artifact spectrum concentrates at cadence
    and its harmonics; amplitude can exceed the pulse AC component (ratio from
    KB, EVD-SENS-004). Gated by activity intensity — zero at rest.
    """
    t = np.asarray(t, float)
    intensity = np.asarray(activity_intensity, float)
    cadence = np.asarray(cadence_hz, float)
    ratio = artifact_value(cfg, "motion_ppg.amplitude_vs_pulse_ac")
    phase1 = rng.uniform(0, 2 * np.pi)
    phase2 = rng.uniform(0, 2 * np.pi)
    # integrate instantaneous cadence to get phase of the step process
    dt = np.diff(t, prepend=t[0])
    step_phase = 2 * np.pi * np.cumsum(cadence * dt)
    fund = np.sin(step_phase + phase1)
    harm = 0.5 * np.sin(2.0 * step_phase + phase2)
    broadband = rng.normal(0.0, 0.3, size=len(t))
    artifact = ratio * pulse_ac_amplitude * intensity * (fund + harm + broadband)
    return artifact


def ecg_motion_bursts(t: np.ndarray, activity_intensity: np.ndarray,
                      qrs_amplitude: float, cfg: dict,
                      rng: np.random.Generator) -> np.ndarray:
    """Electrode-motion transient bursts on ECG during trunk/strap motion.

    Bursts last 300-500 ms with amplitude 1-3x QRS (KB / NSTDB
    characterization, E4), occurring as a Poisson process whose rate scales
    with activity intensity.
    """
    t = np.asarray(t, float)
    intensity = np.asarray(activity_intensity, float)
    n = len(t)
    if n == 0:
        return np.zeros(0)
    fs = 1.0 / np.median(np.diff(t)) if n > 1 else 130.0
    dur_range = cfg["motion_ecg"]["burst_duration_s"].get("range", [0.3, 0.5])
    amp_range = cfg["motion_ecg"]["burst_amplitude_vs_qrs"].get("range", [1.0, 3.0])
    rate_per_s = artifact_value(cfg, "motion_ecg.burst_rate_per_s_at_full_intensity",
                                default=0.5)
    artifact = np.zeros(n)
    # Poisson burst onsets, rate proportional to local activity intensity
    lam = rate_per_s * intensity / fs
    onsets = rng.random(n) < lam
    idx = np.flatnonzero(onsets)
    for i in idx:
        dur = rng.uniform(dur_range[0], dur_range[1])
        length = max(1, int(round(dur * fs)))
        amp = rng.uniform(amp_range[0], amp_range[1]) * qrs_amplitude
        sign = rng.choice([-1.0, 1.0])
        j = min(n, i + length)
        # half-sine transient envelope
        env = np.sin(np.pi * np.arange(j - i) / max(1, (j - i)))
        artifact[i:j] += sign * amp * env
    return artifact


def emg_noise(t: np.ndarray, activity_intensity: np.ndarray,
              qrs_amplitude: float, cfg: dict,
              rng: np.random.Generator) -> np.ndarray:
    """Broadband muscle artifact, sigma ~10% of QRS under muscle activity."""
    sigma_frac = artifact_value(cfg, "motion_ecg.emg_sigma_vs_qrs", default=0.1)
    intensity = np.asarray(activity_intensity, float)
    return rng.normal(0.0, 1.0, size=len(t)) * (sigma_frac * qrs_amplitude) * intensity


def baseline_wander(t: np.ndarray, amplitude: float, cfg: dict,
                    rng: np.random.Generator, n_components: int = 8) -> np.ndarray:
    """Baseline wander: colored content in the 0.05-1 Hz band (NSTDB, E4).

    Sum of sinusoids with frequencies log-spaced across the band, ~1/f
    amplitude weighting and random phases; scaled to the requested amplitude.
    """
    t = np.asarray(t, float)
    f_lo, f_hi = cfg["baseline_wander"]["band_hz"].get("range", [0.05, 1.0])
    freqs = np.exp(np.linspace(np.log(f_lo), np.log(f_hi), n_components))
    phases = rng.uniform(0, 2 * np.pi, size=n_components)
    weights = 1.0 / freqs
    weights /= weights.sum()
    signal = np.zeros(len(t))
    for f, p, w in zip(freqs, phases, weights):
        signal += w * np.sin(2 * np.pi * f * t + p)
    # normalize to requested peak amplitude
    peak = np.max(np.abs(signal))
    if peak > 0:
        signal *= amplitude / peak
    return signal


# ---------------------------------------------------------------------------
# Contact loss -> zero-lines
# ---------------------------------------------------------------------------

def contact_loss_mask(t: np.ndarray, activity_intensity: np.ndarray,
                      cfg: dict, rng: np.random.Generator,
                      mean_episode_s: float = 20.0) -> np.ndarray:
    """Zero-line contact-loss episodes (dry strap, electrode lift).

    Episode onset probability is gated by *increases* in activity intensity
    (dry-strap contact loss at exercise onset; strap slip during vigorous
    motion, E2/E3). True = contact OK, False = zero-line.
    """
    t = np.asarray(t, float)
    n = len(t)
    if n == 0:
        return np.ones(0, dtype=bool)
    intensity = np.asarray(activity_intensity, float)
    # motion-onset gate: positive derivative of intensity
    d_intensity = np.diff(intensity, prepend=intensity[0])
    onset_gate = np.clip(d_intensity, 0.0, None)
    base_prob = artifact_value(cfg, "contact_loss.onset_prob_at_exercise_start",
                               default=0.3)
    fs = 1.0 / np.median(np.diff(t)) if n > 1 else 1.0
    mean_len = max(1, int(round(mean_episode_s * fs)))
    good = np.ones(n, dtype=bool)
    i = 0
    while i < n:
        # per-sample onset probability, boosted at motion onsets
        p = 1e-5 + base_prob * min(1.0, onset_gate[i] * 10.0) / fs
        if rng.random() < p:
            length = rng.integers(1, mean_len * 2)
            good[i:min(n, i + length)] = False
            i += int(length)
        else:
            i += 1
    return good


# ---------------------------------------------------------------------------
# Clipping / saturation
# ---------------------------------------------------------------------------

def clip_signal(signal: np.ndarray, low: float, high: float) -> np.ndarray:
    """Saturate a channel at its front-end full-scale range."""
    return np.clip(signal, low, high)


# ---------------------------------------------------------------------------
# Clock drift + timing jitter
# ---------------------------------------------------------------------------

class ClockModel:
    """Device clock: linear drift (~1 s/hour, EVD-SENS-003 dossier table) plus
    BLE-type timing jitter (ms scale; CI 7.5 ms - 4 s, dossier §7)."""

    def __init__(self, cfg: dict):
        self.drift_s_per_hour = artifact_value(cfg, "clock.drift_s_per_hour")
        self.jitter_std_ms = artifact_value(cfg, "clock.jitter_std_ms", default=5.0)

    def observed_times(self, t: np.ndarray, rng: np.random.Generator,
                       drift_sign: float | None = None) -> np.ndarray:
        t = np.asarray(t, float)
        if drift_sign is None:
            drift_sign = rng.choice([-1.0, 1.0])
        drift = drift_sign * self.drift_s_per_hour * (t - t[0]) / 3600.0
        jitter = rng.normal(0.0, self.jitter_std_ms / 1000.0, size=len(t))
        return t + drift + jitter


# ---------------------------------------------------------------------------
# Temperature effects on the optical front-end
# ---------------------------------------------------------------------------

def optical_amplitude_temperature_factor(skin_temperature_c: np.ndarray,
                                         cfg: dict) -> np.ndarray:
    """Cold-vasoconstriction amplitude factor for optical channels.

    Peripheral cooling collapses perfusion index (<0.3% in cold immersion,
    dossier §2.7); modelled as a smooth factor falling from 1 at thermoneutral
    skin temperature toward a small floor at/below the cold threshold.
    """
    temp = np.asarray(skin_temperature_c, float)
    t_neutral = artifact_value(cfg, "temperature_optical.neutral_skin_temp_c",
                               default=33.0)
    t_cold = artifact_value(cfg, "temperature_optical.cold_skin_temp_c",
                            default=25.0)
    floor = artifact_value(cfg, "temperature_optical.cold_amplitude_floor",
                           default=0.05)
    # logistic transition between neutral (factor 1) and cold (factor floor)
    midpoint = 0.5 * (t_neutral + t_cold)
    steepness = 6.0 / max(1e-6, (t_neutral - t_cold))
    logistic = 1.0 / (1.0 + np.exp(-steepness * (temp - midpoint)))
    return floor + (1.0 - floor) * logistic
