"""KB-driven wearable device sensor models.

Devices consume ONLY observable physiology across the sensor boundary
(:mod:`sensor_models.boundary`): RR-interval series, normalized pulse
waveform, EDA drive, skin temperature, respiration, IMU/activity state.
Latent physiology (ground truth) never enters these APIs.

All measurement constants (biases, limits of agreement, sampling rates,
dropout fractions, usability targets) are loaded from
``knowledge_base/wearables/*.yaml``; each carries a registry claim_id /
DOI / PMID provenance block (SWARM_SPEC global rule 6).

Input contract for the dataset builder (W2-F)
---------------------------------------------
Every device method accepts the physiological series plus a ``state`` mapping
whose keys are a subset of ``boundary.OBSERVABLE_INPUT_KEYS``:

- ``rr_intervals_ms`` : (n_beats,) true RR intervals in milliseconds
- ``beat_times_s``    : (n_beats,) beat occurrence times (s)
- ``beat_types``      : (n_beats,) "normal"/"ectopic" labels (W2 HRV ectopy hook)
- ``pulse_waveform``  : (n,) unitless normalized blood-volume-pulse waveform
- ``activity_intensity`` : (n,) 0..1 motion intensity (from IMU)
- ``cadence_hz``      : (n,) step frequency during locomotion
- ``activity_state``  : (n,) labels ("rest","walk","run","sleep",...)
- ``is_night``        : (n,) bool day/night flag (drives usability profile)
- ``on_body``         : (n,) bool wear state
- ``fit_state``       : (n,) 0..1 strap/contact quality (1 = good fit)
- ``skin_temperature_c`` / ``ambient_temperature_c`` : (n,) deg C
- ``eda_drive``       : (n,) 0..1 sudomotor drive; or explicit SCR events via
  ``eda_event_times_s`` / ``eda_event_amplitudes_us``
- ``respiration_rate_hz`` / ``respiration_waveform``

Every model is deterministic given its ``seed``.
"""

from __future__ import annotations

import numpy as np

from . import artifacts
from .boundary import validate_sensor_inputs
from .profiles import load_device_profile, load_artifact_models, artifact_value


_NORMAL = "normal"


def _broadcast_state(state: dict, n: int, key: str, default):
    """Fetch state[key] broadcast to length n (scalar or array)."""
    v = state.get(key, default)
    arr = np.asarray(v, dtype=float) if not isinstance(v, (str, bytes)) else v
    if isinstance(arr, np.ndarray) and arr.ndim >= 1:
        if len(arr) != n:
            # nearest-neighbour resample to beat/sample grid
            idx = np.linspace(0, len(arr) - 1, n).round().astype(int)
            arr = arr[idx]
        return arr
    return np.full(n, float(arr)) if not isinstance(arr, str) else arr


class SensorDevice:
    """Base class: profile + artifact KB loading, seeded RNG, device clock."""

    def __init__(self, profile_id: str, seed: int | None = None,
                 regime: str = "on_device"):
        self.profile = load_device_profile(profile_id)
        self.artifact_cfg = load_artifact_models()
        self.rng = np.random.default_rng(seed)
        self.seed = seed
        if regime not in ("on_device", "streaming"):
            raise ValueError("regime must be 'on_device' or 'streaming'")
        self.regime = regime
        self.clock = artifacts.ClockModel(self.artifact_cfg)

    def _validate(self, inputs: dict):
        validate_sensor_inputs(inputs, strict=True)


# ---------------------------------------------------------------------------
# ECG chest strap (Polar-H10-like)
# ---------------------------------------------------------------------------

class ChestStrapECGSensor(SensorDevice):
    """Dry-electrode ECG chest strap: RR telemetry + optional raw ECG.

    Error model (EVD-SENS-002 / Schaffarczyk 2022, doi:10.3390/s22176536):
    RR bias 0.7->0.4 ms with LoA +4.3/-2.8 ms at rest and +1.3/-0.5 ms at
    high intensity; noise sigma is DERIVED from the KB LoA (LoA width / 3.92),
    never hardcoded. Missingness: BLE dropout bursts (EVD-SENS-003) plus
    dry-strap contact loss gated at exercise onset.
    """

    def __init__(self, profile_id: str = "polar_h10", seed: int | None = None,
                 regime: str = "on_device"):
        super().__init__(profile_id, seed=seed, regime=regime)

    def _rr_error_params(self, intensity: float):
        """Bias/sigma (ms) interpolated between rest and exercise by intensity."""
        p = self.profile
        bias_rest = p.value("rr_measurement.bias_ms_rest")
        bias_ex = p.value("rr_measurement.bias_ms_exercise")
        loa_rest_lo, loa_rest_hi = p.value("rr_measurement.loa_rest_ms")
        loa_ex_lo, loa_ex_hi = p.value("rr_measurement.loa_exercise_ms")
        w = float(np.clip(intensity, 0.0, 1.0))
        bias = (1 - w) * bias_rest + w * bias_ex
        # sigma derived from LoA: LoA = bias +/- 1.96*sigma
        sigma_rest = (loa_rest_hi - loa_rest_lo) / 3.92
        sigma_ex = (loa_ex_hi - loa_ex_lo) / 3.92
        sigma = (1 - w) * sigma_rest + w * sigma_ex
        return bias, sigma

    def measure_rr(self, rr_intervals_ms, state: dict | None = None) -> dict:
        """Measure an RR-interval series. Returns measured RR with NaN gaps.

        ``state`` may carry ``beat_times_s``, ``activity_intensity``,
        ``is_night``, ``beat_types`` (ectopy hook), ``on_body``.
        """
        state = dict(state or {})
        rr = np.asarray(rr_intervals_ms, dtype=float)
        n = len(rr)
        self._validate({"rr_intervals_ms": rr, **state})

        intensity = _broadcast_state(state, n, "activity_intensity", 0.0)
        on_body = _broadcast_state(state, n, "on_body", 1.0).astype(bool)
        beat_times = np.asarray(state.get(
            "beat_times_s", np.cumsum(rr) / 1000.0), dtype=float)
        beat_types = state.get("beat_types", np.full(n, _NORMAL))

        # per-beat bias + LoA-derived noise, interpolated by activity state
        err = np.empty(n)
        for i in range(n):
            bias, sigma = self._rr_error_params(intensity[i])
            err[i] = bias + self.rng.normal(0.0, sigma)
            # ectopy hook (W2 HRV module): arrhythmic beats degrade accuracy
            # (Vermunicht 2025 negative finding, EVD-SENS-002 limitations)
            if beat_types[i] != _NORMAL:
                widen = artifact_value(self.artifact_cfg,
                                       "ectopy.rr_error_widen_factor", default=2.0)
                err[i] += self.rng.normal(0.0, widen * sigma)

        measured = rr + err

        # state-conditional missingness: contact loss at motion onset + BLE
        # dropout bursts; off-body beats are never recorded
        contact = artifacts.contact_loss_mask(beat_times, intensity,
                                              self.artifact_cfg, self.rng)
        stream = artifacts.dropout_burst_mask(n, intensity, self.artifact_cfg,
                                              self.rng, regime=self.regime)
        good = contact & stream & on_body
        measured = np.where(good, measured, np.nan)

        observed_times = self.clock.observed_times(beat_times, self.rng)
        valid = ~np.isnan(measured)
        hr = np.full(n, np.nan)
        hr[valid] = 60000.0 / measured[valid]
        return {
            "times_s": observed_times,
            "rr_intervals_ms": measured,
            "heart_rate_bpm": hr,
            "quality_good": good,
            "beat_types": np.asarray(beat_types),
            "provenance": self.profile.provenance("rr_measurement.bias_ms_rest"),
        }

    def synthesize_ecg(self, time_s, beat_times_s, state: dict | None = None) -> dict:
        """Raw single-lead ECG at the profile sampling rate (mV).

        Includes band-limiting note (0.7-40 Hz strap front-end), baseline
        wander, motion-gated electrode-motion bursts + EMG noise, contact-loss
        zero-lines and ADC clipping.
        """
        state = dict(state or {})
        time_s = np.asarray(time_s, dtype=float)
        beat_times_s = np.asarray(beat_times_s, dtype=float)
        self._validate({"time_s": time_s, "beat_times_s": beat_times_s, **state})

        fs = self.profile.value("ecg.sampling_frequency_hz")
        t = np.arange(time_s[0], time_s[-1], 1.0 / fs)
        qrs_amp = self.profile.value("ecg.qrs_amplitude_mv", default=1.0)
        intensity = _broadcast_state(
            state, len(t), "activity_intensity",
            float(np.mean(state.get("activity_intensity", 0.0))))

        # synthetic QRS train: narrow Gaussian R-peaks (morphology-fragile
        # strap front-end; adequate for RR timing only)
        ecg = np.zeros(len(t))
        width = 0.012  # ~QRS width placeholder for timing-adequate waveform
        for bt in beat_times_s:
            ecg += qrs_amp * np.exp(-0.5 * ((t - bt) / width) ** 2)

        wander_amp = (artifact_value(self.artifact_cfg,
                                     "baseline_wander.amplitude_vs_qrs")
                      * qrs_amp)
        ecg += artifacts.baseline_wander(t, wander_amp, self.artifact_cfg, self.rng)
        ecg += artifacts.ecg_motion_bursts(t, intensity, qrs_amp,
                                           self.artifact_cfg, self.rng)
        ecg += artifacts.emg_noise(t, intensity, qrs_amp,
                                   self.artifact_cfg, self.rng)

        contact = artifacts.contact_loss_mask(t, intensity, self.artifact_cfg,
                                              self.rng)
        ecg = np.where(contact, ecg, 0.0)  # zero-line on contact loss

        fsr = self.profile.value("ecg.adc_full_scale_mv", default=5.0)
        ecg = artifacts.clip_signal(ecg, -fsr, fsr)
        return {
            "time_s": self.clock.observed_times(t, self.rng),
            "ecg_mv": ecg,
            "sampling_frequency_hz": fs,
            "passband_hz": self.profile.value("ecg.passband_hz", default=[0.7, 40.0]),
            "contact_ok": contact,
        }


# ---------------------------------------------------------------------------
# Wrist PPG (consumer, Apple-Watch-like; also Empatica-E4-class via profile)
# ---------------------------------------------------------------------------

class WristPPGSensor(SensorDevice):
    """Reflectance wrist PPG: raw corrupted waveform + derived HR.

    Derived-HR error model (EVD-SENS-001 / Lambe 2026 meta-analysis,
    PMID 41513748): bias -0.27 bpm, LoA -7.19/+6.64 bpm at rest; motion
    widens the tails (pediatric/ambulatory +/-19 bpm). Optional naive
    cadence-lock mode reproduces the ~26 bpm running MAE of non
    motion-compensated estimators (EVD-SENS-004). Usability follows the
    day/night missingness profile (EVD-SENS-003).
    """

    def __init__(self, profile_id: str = "apple_watch_ppg",
                 seed: int | None = None, regime: str = "on_device",
                 motion_compensation: bool = True):
        super().__init__(profile_id, seed=seed, regime=regime)
        # motion_compensation=False selects the naive (cadence-locking)
        # derived-HR estimator; the RAW waveform is always corrupted.
        self.motion_compensation = motion_compensation

    def synthesize_ppg(self, time_s, pulse_waveform, state: dict | None = None) -> dict:
        """Raw PPG waveform at the profile sampling rate.

        ``pulse_waveform`` is a unitless normalized blood-volume-pulse series
        on the ``time_s`` grid. State: ``activity_intensity``, ``cadence_hz``,
        ``skin_temperature_c``, ``is_night``, ``on_body``, ``fit_state``.
        """
        state = dict(state or {})
        time_s = np.asarray(time_s, dtype=float)
        pulse = np.asarray(pulse_waveform, dtype=float)
        self._validate({"time_s": time_s, "pulse_waveform": pulse, **state})

        fs = self.profile.value("ppg.sampling_frequency_hz")
        t = np.arange(time_s[0], time_s[-1], 1.0 / fs)
        n = len(t)
        pulse_resamp = np.interp(t, time_s, pulse)

        intensity = _broadcast_state(state, n, "activity_intensity", 0.0)
        cadence = _broadcast_state(state, n, "cadence_hz", 0.0)
        skin_temp = _broadcast_state(state, n, "skin_temperature_c", 33.0)
        is_night = _broadcast_state(state, n, "is_night", 0.0).astype(bool)
        on_body = _broadcast_state(state, n, "on_body", 1.0).astype(bool)
        fit = _broadcast_state(state, n, "fit_state", 1.0)

        # optical amplitude: perfusion/temperature dependence + fit
        ac_amp = self.profile.value("ppg.pulse_ac_amplitude", default=1.0)
        temp_factor = artifacts.optical_amplitude_temperature_factor(
            skin_temp, self.artifact_cfg)
        dc_level = self.profile.value("ppg.dc_level", default=2.0)
        signal = dc_level + ac_amp * temp_factor * fit * pulse_resamp

        # motion-gated cadence-lock artifact (zero at rest)
        signal += artifacts.cadence_locked_artifact(
            t, intensity, cadence, ac_amp, self.artifact_cfg, self.rng)

        # ambient light leakage spikes when fit is poor and it is daytime
        leak_gain = artifact_value(self.artifact_cfg,
                                   "ambient_light.leak_amplitude", default=3.0)
        leak_prob = artifact_value(self.artifact_cfg,
                                   "ambient_light.spike_prob_per_s", default=0.01)
        loose_day = (fit < 0.7) & (~is_night)
        spikes = (self.rng.random(n) < leak_prob / fs) & loose_day
        signal += spikes * self.rng.uniform(0.5, 1.0, n) * leak_gain * ac_amp

        # contact loss -> zero-lines; off-body -> floor
        contact = artifacts.contact_loss_mask(t, intensity, self.artifact_cfg,
                                              self.rng)
        signal = np.where(contact & on_body, signal, 0.0)

        # front-end saturation + quantization
        fsr = self.profile.value("ppg.adc_full_scale", default=4.0)
        signal = artifacts.clip_signal(signal, 0.0, fsr)
        bits = self.profile.value("ppg.adc_bits", default=None)
        if bits:
            levels = 2 ** int(bits)
            signal = np.round(signal / fsr * (levels - 1)) / (levels - 1) * fsr

        # day/night usability gating (quality flag, not signal deletion)
        quality = artifacts.day_night_quality_mask(is_night, "ppg",
                                                   self.artifact_cfg, self.rng)
        quality &= contact & on_body
        return {
            "time_s": self.clock.observed_times(t, self.rng),
            "ppg": signal,
            "sampling_frequency_hz": fs,
            "quality_good": quality,
        }

    def derive_hr(self, rr_intervals_ms, state: dict | None = None) -> dict:
        """Derived per-beat HR (bpm) with state-dependent error + missingness.

        State: ``activity_intensity``, ``cadence_hz``, ``is_night``,
        ``on_body``, ``beat_times_s``.
        """
        state = dict(state or {})
        rr = np.asarray(rr_intervals_ms, dtype=float)
        n = len(rr)
        self._validate({"rr_intervals_ms": rr, **state})
        hr_true = 60000.0 / rr

        intensity = _broadcast_state(state, n, "activity_intensity", 0.0)
        cadence_hz = _broadcast_state(state, n, "cadence_hz", 0.0)
        is_night = _broadcast_state(state, n, "is_night", 0.0).astype(bool)
        on_body = _broadcast_state(state, n, "on_body", 1.0).astype(bool)
        beat_times = np.asarray(state.get(
            "beat_times_s", np.cumsum(rr) / 1000.0), dtype=float)

        p = self.profile
        bias = p.value("derived_hr.bias_bpm")
        loa_lo, loa_hi = p.value("derived_hr.loa_bpm")
        sigma_rest = (loa_hi - loa_lo) / 3.92
        widen = p.value("derived_hr.motion_loa_widen_factor", default=2.7)

        err = np.empty(n)
        for i in range(n):
            sigma = sigma_rest * (1.0 + (widen - 1.0) * intensity[i])
            e = bias + self.rng.normal(0.0, sigma)
            if not self.motion_compensation and intensity[i] > 0.5 and cadence_hz[i] > 0:
                # naive estimator locks onto step cadence (EVD-SENS-004)
                cadence_bpm = cadence_hz[i] * 60.0
                lock = artifact_value(self.artifact_cfg,
                                      "motion_ppg.cadence_lock_strength", default=0.8)
                e = lock * (cadence_bpm - hr_true[i]) + self.rng.normal(0.0, sigma)
            err[i] = e
        hr_meas = hr_true + err

        good = artifacts.day_night_quality_mask(is_night, "ppg",
                                                self.artifact_cfg, self.rng,
                                                mean_episode_len=60.0)
        stream = artifacts.dropout_burst_mask(n, intensity, self.artifact_cfg,
                                              self.rng, regime=self.regime)
        good &= stream & on_body
        hr_meas = np.where(good, hr_meas, np.nan)
        return {
            "times_s": self.clock.observed_times(beat_times, self.rng),
            "heart_rate_bpm": hr_meas,
            "quality_good": good,
            "provenance": p.provenance("derived_hr.bias_bpm"),
        }


# ---------------------------------------------------------------------------
# EDA (Empatica-E4-like)
# ---------------------------------------------------------------------------

class EDASensor(SensorDevice):
    """Electrodermal activity: tonic SCL + phasic SCRs at the profile rate.

    Dynamics (EVD-SENS-006; Dawson 2016/Boucsein 2012): SCL 2-20 uS random
    walk, SCR amplitude 0.05-5 uS (log-normal), latency 1-3 s, rise 1-3 s,
    half-recovery 2-10 s; ambient heat/humidity raise SCL independent of
    arousal. Artifacts: contact-loss zero-lines and >20%/2 s motion steps
    flagged as bad quality.
    """

    def __init__(self, profile_id: str = "empatica_e4", seed: int | None = None,
                 regime: str = "on_device"):
        super().__init__(profile_id, seed=seed, regime=regime)

    def _scr_shape(self, s: np.ndarray, rise_s: float, half_rec_s: float) -> np.ndarray:
        """Bateman (biexponential) SCR shape, peak-normalized.

        s = time since end of latency. tau_rec from half-recovery; tau_rise
        solved so the peak occurs at ``rise_s``.
        """
        tau_rec = half_rec_s / np.log(2.0)

        def peak_time(tau_r):
            if tau_r >= tau_rec:
                return np.inf
            return tau_r * tau_rec / (tau_rec - tau_r) * np.log(tau_rec / tau_r)

        lo, hi = 1e-3, tau_rec * 0.999
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if peak_time(mid) < rise_s:
                lo = mid
            else:
                hi = mid
        tau_rise = 0.5 * (lo + hi)
        shape = np.exp(-s / tau_rec) - np.exp(-s / tau_rise)
        peak = np.max(shape)
        return shape / peak if peak > 0 else shape

    def measure(self, duration_s: float, state: dict | None = None) -> dict:
        """Synthesize measured EDA for ``duration_s`` seconds.

        State: ``eda_drive`` (0..1, scalar or series), ``ambient_temperature_c``,
        ``activity_intensity``, ``on_body``; or explicit SCR events via
        ``eda_event_times_s`` / ``eda_event_amplitudes_us``.
        """
        state = dict(state or {})
        self._validate(state)
        fs = self.profile.value("eda.sampling_frequency_hz")
        n = max(1, int(round(duration_s * fs)))
        t = np.arange(n) / fs

        drive = _broadcast_state(state, n, "eda_drive", 0.2)
        ambient = _broadcast_state(state, n, "ambient_temperature_c", 23.0)
        intensity = _broadcast_state(state, n, "activity_intensity", 0.0)
        on_body = _broadcast_state(state, n, "on_body", 1.0).astype(bool)

        cfg = self.profile
        scl_lo, scl_hi = cfg.value("eda.scl_range_us")
        # tonic SCL: mean-reverting random walk; level set by drive, plus
        # thermal SCL elevation independent of arousal (EVD-SENS-006)
        temp_ref = cfg.value("eda.temperature_reference_c", default=25.0)
        temp_gain = cfg.value("eda.temperature_gain_us_per_c", default=0.3)
        target = scl_lo + np.clip(drive, 0, 1) * (scl_hi - scl_lo) * 0.7 \
            + temp_gain * np.clip(ambient - temp_ref, 0.0, None)
        scl = np.empty(n)
        scl[0] = np.clip(target[0], scl_lo, scl_hi)
        theta = 1.0 / (60.0 * fs)  # ~1 min mean reversion
        rw_sigma = cfg.value("eda.scl_random_walk_sigma_us", default=0.005)
        for i in range(1, n):
            scl[i] = scl[i - 1] + theta * (target[i] - scl[i - 1]) \
                + self.rng.normal(0.0, rw_sigma)
        scl = np.clip(scl, 0.5 * scl_lo, 1.5 * scl_hi)

        # phasic SCR events: explicit, or Poisson with state-dependent rate
        lat_lo, lat_hi = cfg.value("eda.scr_latency_s_range")
        rise_lo, rise_hi = cfg.value("eda.scr_rise_s_range")
        rec_lo, rec_hi = cfg.value("eda.scr_half_recovery_s_range")
        amp_lo, amp_hi = cfg.value("eda.scr_amplitude_us_range")
        if "eda_event_times_s" in state:
            ev_t = np.asarray(state["eda_event_times_s"], dtype=float)
            ev_a = np.asarray(state.get(
                "eda_event_amplitudes_us",
                np.full(len(ev_t), 0.5)), dtype=float)
        else:
            lam_lo = cfg.value("eda.ns_scr_rate_per_min_rest")
            lam_hi = cfg.value("eda.ns_scr_rate_per_min_stress")
            rate_hz = (lam_lo + np.clip(drive, 0, 1) * (lam_hi - lam_lo)) / 60.0
            events = self.rng.random(n) < rate_hz / fs
            ev_t = t[events]
            # log-normal amplitudes within the 0.05-5 uS band
            med = np.sqrt(amp_lo * amp_hi)
            ev_a = np.exp(self.rng.normal(np.log(med), 0.7, size=len(ev_t)))
            ev_a = np.clip(ev_a, amp_lo, amp_hi)
        scr = np.zeros(n)
        for t0, a in zip(ev_t, ev_a):
            lat = self.rng.uniform(lat_lo, lat_hi)
            rise = self.rng.uniform(rise_lo, rise_hi)
            rec = self.rng.uniform(rec_lo, rec_hi)
            start = int(round((t0 + lat) * fs))
            if start >= n:
                continue
            s = t[start:] - t[start]
            scr[start:] += a * self._scr_shape(s, rise, rec)

        eda = scl + scr

        # motion step artifacts (>20%/2 s flagged bad, E4 quality pipeline)
        step_prob = artifact_value(self.artifact_cfg,
                                   "eda_steps.step_prob_per_s_at_full_intensity",
                                   default=0.02)
        steps = (self.rng.random(n) < step_prob * intensity / fs)
        step_flags = np.zeros(n, dtype=bool)
        idx = np.flatnonzero(steps)
        for i in idx:
            delta = self.rng.choice([-1.0, 1.0]) * self.rng.uniform(0.2, 0.6) * eda[i]
            eda[i:] += delta
            step_flags[i:min(n, i + int(2 * fs))] = True

        # front-end range/resolution (valid signal only; zero-lines applied after)
        range_lo, range_hi = cfg.value("eda.measurement_range_us")
        eda = artifacts.clip_signal(eda, range_lo, range_hi)

        # contact loss -> zero-line; off-body -> zero-line
        contact = artifacts.contact_loss_mask(t, intensity, self.artifact_cfg,
                                              self.rng)
        good = contact & on_body & (~step_flags)
        eda = np.where(contact & on_body, eda, 0.0)

        resolution = cfg.value("eda.resolution_us", default=0.0009)
        eda = np.round(eda / resolution) * resolution

        # day/night usability
        is_night = _broadcast_state(state, n, "is_night", 0.0).astype(bool)
        quality = artifacts.day_night_quality_mask(is_night, "eda",
                                                   self.artifact_cfg, self.rng)
        quality &= good
        return {
            "time_s": self.clock.observed_times(t, self.rng),
            "eda_us": eda,
            "scl_us": np.where(contact & on_body, scl, np.nan),
            "scr_us": scr,
            "sampling_frequency_hz": fs,
            "quality_good": quality,
            "scr_event_times_s": ev_t,
            "provenance": cfg.provenance("eda.scl_range_us"),
        }


# ---------------------------------------------------------------------------
# Skin temperature (Oura-ring-like)
# ---------------------------------------------------------------------------

class SkinTempSensor(SensorDevice):
    """Ring/wrist thermistor skin-temperature channel.

    Noise sigma 0.03-0.1 deg C, quantization 0.02-0.07 deg C, off-body decay
    toward ambient with a minutes-scale time constant (EVD-SENS-007 dossier
    §4). TEMP is the highest-quality modality (~96% good quality,
    EVD-SENS-003).
    """

    def __init__(self, profile_id: str = "oura_ring", seed: int | None = None,
                 regime: str = "on_device"):
        super().__init__(profile_id, seed=seed, regime=regime)

    def measure(self, time_s, skin_temperature_c, state: dict | None = None) -> dict:
        state = dict(state or {})
        time_s = np.asarray(time_s, dtype=float)
        temp_true = np.asarray(skin_temperature_c, dtype=float)
        self._validate({"time_s": time_s, "skin_temperature_c": temp_true, **state})

        p = self.profile
        fs = p.value("temperature.sampling_frequency_hz")
        t = np.arange(time_s[0], time_s[-1], 1.0 / fs)
        n = len(t)
        true_resamp = np.interp(t, time_s, temp_true)
        on_body = _broadcast_state(state, n, "on_body", 1.0).astype(bool)
        ambient = _broadcast_state(state, n, "ambient_temperature_c", 22.0)

        # off-body: first-order decay toward ambient (tau 2-10 min, KB)
        tau_lo, tau_hi = p.value("temperature.ambient_leak_tau_s_range",
                                 default=[120.0, 600.0])
        tau = self.rng.uniform(tau_lo, tau_hi)
        alpha = 1.0 - np.exp(-1.0 / (tau * fs))
        sig = np.empty(n)
        sig[0] = true_resamp[0]
        for i in range(1, n):
            if on_body[i]:
                sig[i] = true_resamp[i]
            else:
                sig[i] = sig[i - 1] + alpha * (ambient[i] - sig[i - 1])

        sigma = p.value("temperature.noise_sigma_c")
        sig += self.rng.normal(0.0, sigma, n)
        quant = p.value("temperature.quantization_c", default=0.07)
        sig = np.round(sig / quant) * quant

        # epoch aggregation (e.g. 1-min epochs for ring-class devices)
        epoch_s = p.value("temperature.epoch_s", default=None)
        quality = artifacts.day_night_quality_mask(
            _broadcast_state(state, n, "is_night", 0.0).astype(bool),
            "temp", self.artifact_cfg, self.rng)
        quality &= on_body
        out = {
            "time_s": self.clock.observed_times(t, self.rng),
            "skin_temperature_c": sig,
            "sampling_frequency_hz": fs,
            "quality_good": quality,
            "provenance": p.provenance("temperature.noise_sigma_c"),
        }
        if epoch_s:
            ep = int(round(epoch_s * fs))
            m = (n // ep) * ep
            out["epoch_time_s"] = out["time_s"][:m].reshape(-1, ep)[:, -1]
            out["epoch_temperature_c"] = sig[:m].reshape(-1, ep).mean(axis=1)
        return out


# ---------------------------------------------------------------------------
# IMU (accelerometry)
# ---------------------------------------------------------------------------

class IMUSensor(SensorDevice):
    """MEMS accelerometer channel: noise density, 1/f noise, FSR clipping.

    Also serves as the motion/activity ground-truth channel that DRIVES the
    state-dependent artifacts of the optical/ECG/EDA channels.
    """

    def __init__(self, profile_id: str = "empatica_e4", seed: int | None = None,
                 regime: str = "on_device"):
        super().__init__(profile_id, seed=seed, regime=regime)

    def measure(self, time_s, acceleration_g, state: dict | None = None) -> dict:
        state = dict(state or {})
        time_s = np.asarray(time_s, dtype=float)
        acc = np.asarray(acceleration_g, dtype=float)
        self._validate({"time_s": time_s, "acceleration_g": acc, **state})

        p = self.profile
        fs = p.value("imu.sampling_frequency_hz")
        t = np.arange(time_s[0], time_s[-1], 1.0 / fs)
        n = len(t)
        resamp = np.interp(t, time_s, acc)

        # white noise from KB noise density (ug/sqrt(Hz)) at fs/2 bandwidth
        density_ug = p.value("imu.noise_density_ug_per_sqrt_hz")
        sigma_g = density_ug * 1e-6 * np.sqrt(fs / 2.0)
        sig = resamp + self.rng.normal(0.0, sigma_g, n)
        # 1/f component (random walk, small)
        sig += np.cumsum(self.rng.normal(0.0, sigma_g * 0.02, n))

        fsr = p.value("imu.full_scale_range_g")
        clipped = artifacts.clip_signal(sig, -fsr, fsr)
        saturation = np.abs(sig) >= fsr
        return {
            "time_s": self.clock.observed_times(t, self.rng),
            "acceleration_g": clipped,
            "sampling_frequency_hz": fs,
            "saturated": saturation,
        }
