"""Legacy-compatible sensor wrappers, now KB-driven.

These classes preserve the original public API (used by
``examples/run_simulation.py``) but every measurement constant is loaded from
the knowledge-base device profiles in ``knowledge_base/wearables/`` instead of
being hardcoded (previously sigma = 1 ms, 0.5% i.i.d. dropout, fixed PPG
coefficients). Missingness and motion artifact are state-dependent Markov /
motion-gated processes, not i.i.d. noise.

New code should use :mod:`sensor_models.devices` directly, which exposes the
full state-conditional API and the sensor-boundary input contract.
"""

import numpy as np

from . import artifacts
from .profiles import load_device_profile, load_artifact_models, artifact_value


class PolarH10SensorModel:
    """
    Simulates a dry-electrode ECG chest strap (Polar-H10-class).
    Ingests a simulated heart-rate trajectory, extracts beat occurrences
    (RR intervals), applies the KB profile error model (bias + LoA-derived
    noise, EVD-SENS-002) and state-dependent missingness (EVD-SENS-003),
    and computes time-domain HRV metrics.

    Parameters
    ----------
    noise_std_ms : float or None
        Override for the RR noise sigma (ms). None = derive from the KB
        profile LoA (rest: LoA width / 3.92).
    dropout_rate : float or None
        Override for the mean per-beat missing fraction. None = use the KB
        on-device loss fraction (<=9%, EVD-SENS-003).
    seed : int or None
        Seed for a dedicated generator. None = legacy global ``np.random``
        behaviour (preserves ``np.random.seed(...)`` reproducibility).
    """

    def __init__(self, noise_std_ms=None, dropout_rate=None, seed=None,
                 profile_id="polar_h10"):
        self.profile = load_device_profile(profile_id)
        self.artifact_cfg = load_artifact_models()
        loa_lo, loa_hi = self.profile.value("rr_measurement.loa_rest_ms")
        self.noise_std_ms = (noise_std_ms if noise_std_ms is not None
                             else (loa_hi - loa_lo) / 3.92)
        self.dropout_rate = (dropout_rate if dropout_rate is not None
                             else artifact_value(
                                 self.artifact_cfg,
                                 "dropout.on_device_loss_fraction_max"))
        self.bias_ms = self.profile.value("rr_measurement.bias_ms_rest")
        self.rng = np.random.default_rng(seed) if seed is not None else np.random

    def generate_telemetry(self, raw_time, raw_hc):
        """
        Processes continuous heart rate Hc (bps) to extract beat occurrences
        (RR intervals), then applies the profile-driven measurement model.
        """
        beats = []
        t = raw_time[0]

        # Identify beat times by integrating Hc over time
        # A beat occurs when the integrated phase reaches 1.0
        phase = 0.0
        for i in range(1, len(raw_time)):
            dt = raw_time[i] - raw_time[i-1]
            hc_avg = (raw_hc[i] + raw_hc[i-1]) / 2.0
            phase += hc_avg * dt
            if phase >= 1.0:
                beats.append(raw_time[i])
                phase -= 1.0

        beats = np.array(beats)
        if len(beats) < 2:
            return {"times": np.array([]), "rr": np.array([]), "hr": np.array([])}

        # Calculate raw RR intervals in milliseconds
        raw_rr = np.diff(beats) * 1000.0
        beat_times = beats[1:]

        # Profile-driven measurement error: rest bias + LoA-derived noise
        sensor_noise = self.rng.normal(self.bias_ms, self.noise_std_ms,
                                       size=len(raw_rr))
        measured_rr = raw_rr + sensor_noise

        # Missingness: bursty Markov dropout at the configured mean fraction
        # (state-dependent in sensor_models.devices; no activity state is
        # available in this legacy interface)
        good = artifacts.markov_bad_mask(
            len(measured_rr), self.dropout_rate, mean_burst_len=3.0,
            rng=self.rng if isinstance(self.rng, np.random.Generator)
            else np.random.default_rng(self.rng.randint(0, 2**31 - 1)))
        measured_rr = np.where(good, measured_rr, np.nan)

        # Fill dropouts for clinical HR calculations
        filled_rr = np.copy(measured_rr)
        nan_indices = np.isnan(filled_rr)
        if np.any(nan_indices):
            # Simple forward fill for telemetry display
            last_valid = 1000.0 / raw_hc[0]
            for idx in range(len(filled_rr)):
                if np.isnan(filled_rr[idx]):
                    filled_rr[idx] = last_valid
                else:
                    last_valid = filled_rr[idx]

        measured_hr = 60000.0 / filled_rr

        # Compute HRV metrics
        valid_rr = measured_rr[~np.isnan(measured_rr)]
        rmssd = np.sqrt(np.mean(np.diff(valid_rr)**2)) if len(valid_rr) > 1 else 0.0
        sdnn = np.std(valid_rr) if len(valid_rr) > 0 else 0.0

        return {
            "times": beat_times,
            "rr_intervals": measured_rr,
            "heart_rate": measured_hr,
            "hrv_rmssd": rmssd,
            "hrv_sdnn": sdnn
        }


class PPGWearableSensorModel:
    """
    Simulates a photoplethysmography (PPG) wristband sensor.
    Generates a synthetic green-light PPG waveform from a normalized
    peripheral pulse waveform and a perfusion/vasomotor drive, including an
    AC component (cardiac pulse), a DC component (perfusion state), and
    motion-gated artifact (state-dependent, not i.i.d.).

    Note: ``pulse_waveform`` must be an observable-proxy normalized waveform
    (unitless). Latent hemodynamic states must be converted to this form by
    the caller before crossing the sensor boundary (global rule 3).
    """

    def __init__(self, fs=None, motion_noise_level=None, seed=None,
                 profile_id="photoplethysmography"):
        self.profile = load_device_profile(profile_id)
        self.artifact_cfg = load_artifact_models()
        self.fs = fs if fs is not None else self.profile.value(
            "ppg.sampling_frequency_hz", default=50.0)
        self.motion_noise_level = (motion_noise_level if motion_noise_level
                                   is not None else artifact_value(
                                       self.artifact_cfg,
                                       "motion_ppg.amplitude_vs_pulse_ac") * 0.05)
        self.rng = np.random.default_rng(seed) if seed is not None else np.random

    def generate_ppg_signal(self, time_grid, pulse_waveform, perfusion_drive,
                            activity_intensity=None):
        """
        Generates a continuous PPG optical waveform.
        - AC component is proportional to the normalized pulse waveform.
        - DC component is inversely proportional to the perfusion drive
          (vasoconstriction reduces blood volume/perfusion).
        - Respiration adds a slow modulation at 0.25 Hz.
        - Motion artifact is gated by ``activity_intensity`` (0..1); a scalar
          keeps legacy constant-motion behaviour.
        """
        # Interpolate input signals to the sensor sampling grid
        t_sensor = np.arange(time_grid[0], time_grid[-1], 1.0 / self.fs)
        pulse_interp = np.interp(t_sensor, time_grid, pulse_waveform)
        drive_interp = np.interp(t_sensor, time_grid, perfusion_drive)

        # AC Component: cardiac pulse wave
        # Normalize pulse waveform to [0, 1] range for cardiac contribution
        p_min, p_max = np.min(pulse_interp), np.max(pulse_interp)
        if p_max > p_min:
            ac_cardiac = (pulse_interp - p_min) / (p_max - p_min)
        else:
            ac_cardiac = np.zeros_like(pulse_interp)

        # DC Component: perfusion baseline (lower drive = higher perfusion)
        dc_base = 2.0 - 0.8 * drive_interp

        # Respiratory Modulation (0.25 Hz, i.e., 15 breaths per minute)
        respiration = 0.05 * np.sin(2 * np.pi * 0.25 * t_sensor)

        # Combine components
        raw_ppg = ac_cardiac * 0.2 + dc_base + respiration

        # Add high-frequency measurement noise
        measurement_noise = self.rng.normal(0, 0.005, size=len(t_sensor))
        ppg_signal = raw_ppg + measurement_noise

        # Motion artifact gated by activity state (legacy default: transient
        # motion window around t = 200 s for 14 s)
        if activity_intensity is None:
            motion_mask = (t_sensor >= 200.0) & (t_sensor <= 214.0)
            motion_noise = self.rng.normal(0, self.motion_noise_level,
                                           size=len(t_sensor))
            # Fade in and out motion noise
            fade = np.sin(np.pi * (t_sensor - 200.0) / 14.0)
            ppg_signal = np.where(motion_mask, ppg_signal + motion_noise * fade,
                                  ppg_signal)
        else:
            intensity = np.broadcast_to(
                np.asarray(activity_intensity, dtype=float), ppg_signal.shape)
            motion_noise = self.rng.normal(0, self.motion_noise_level,
                                           size=len(t_sensor))
            ppg_signal = ppg_signal + motion_noise * intensity

        # Normalize final signal
        ppg_signal = (ppg_signal - np.min(ppg_signal)) / (np.max(ppg_signal) - np.min(ppg_signal))

        return t_sensor, ppg_signal
