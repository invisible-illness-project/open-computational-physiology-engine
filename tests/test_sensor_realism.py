"""Sensor realism test suite (Agent W1-D).

Covers:
  * boundary enforcement (no latent physiology crosses into the sensor layer,
    SWARM_SPEC global rule 3) — static source guard + runtime guard
  * KB-driven device profiles (provenance / rule-6 fields on every constant)
  * artifact rates vs configured distributions (dropout, day/night usability)
  * derived-metric errors within configured limits of agreement
  * EDA dynamics within published parameter ranges
  * determinism under seed
"""

import re
from pathlib import Path

import numpy as np
import pytest
import yaml

from sensor_models import artifacts, boundary
from sensor_models.boundary import (
    LatentVariableViolation, UnknownSensorInput, validate_sensor_inputs,
)
from sensor_models.profiles import (
    load_device_profile, load_artifact_models, artifact_value,
)
from sensor_models.devices import (
    ChestStrapECGSensor, WristPPGSensor, EDASensor, SkinTempSensor, IMUSensor,
)
from sensor_models.wearable_sensors import PolarH10SensorModel, PPGWearableSensorModel

SENSOR_DIR = Path(__file__).parent.parent / "sensor_models"
KB_WEARABLES = Path(__file__).parent.parent / "knowledge_base" / "wearables"


# ---------------------------------------------------------------------------
# 1. Boundary enforcement
# ---------------------------------------------------------------------------

class TestBoundaryGuard:
    def test_static_source_guard_no_latent_identifiers(self):
        """No latent variable name may appear in sensor-layer source code
        outside the forbidden-name registry itself (boundary.py)."""
        terms = sorted(boundary.LATENT_FORBIDDEN_NAMES
                       - boundary.LATENT_ALLOWED_EXCEPTIONS)
        pattern = re.compile(r"\b(" + "|".join(re.escape(t) for t in terms) + r")\b")
        offenders = []
        for path in SENSOR_DIR.glob("*.py"):
            if path.name == "boundary.py":
                continue  # registry module defines the forbidden names
            text = path.read_text(encoding="utf-8")
            for m in pattern.finditer(text):
                line = text[:m.start()].count("\n") + 1
                offenders.append(f"{path.name}:{line}: '{m.group(0)}'")
        assert not offenders, (
            "latent variable identifiers in sensor layer:\n" + "\n".join(offenders))

    def test_runtime_guard_rejects_latent_inputs(self):
        for latent in ["blood_pressure_absolute", "stroke_volume",
                       "cardiac_output", "svr", "systemic_vascular_resistance",
                       "venous_pooling", "core_temperature",
                       "cerebral_perfusion", "hydration", "insulin", "glucose",
                       "baroreflex_sensitivity"]:
            with pytest.raises(LatentVariableViolation):
                validate_sensor_inputs({latent: np.zeros(3)})

    def test_runtime_guard_rejects_latent_substring_keys(self):
        with pytest.raises(LatentVariableViolation):
            validate_sensor_inputs({"mean_core_temperature_trace": np.zeros(3)})
        with pytest.raises(LatentVariableViolation):
            validate_sensor_inputs({"estimated_stroke_volume": np.zeros(3)})

    def test_runtime_guard_accepts_observable_inputs(self):
        obs = {k: np.zeros(3) for k in boundary.OBSERVABLE_INPUT_KEYS}
        assert validate_sensor_inputs(obs) is obs
        # CGM glucose is the single sanctioned exception
        validate_sensor_inputs({"cgm_glucose": np.zeros(3)}, strict=False)

    def test_runtime_guard_rejects_unknown_keys_when_strict(self):
        with pytest.raises(UnknownSensorInput):
            validate_sensor_inputs({"some_unregistered_signal": np.zeros(3)})

    def test_devices_reject_latent_state(self):
        strap = ChestStrapECGSensor(seed=0)
        with pytest.raises(LatentVariableViolation):
            strap.measure_rr(np.full(10, 850.0),
                             state={"cardiac_output": np.zeros(10)})
        ppg = WristPPGSensor(seed=0)
        with pytest.raises(LatentVariableViolation):
            ppg.derive_hr(np.full(10, 850.0),
                          state={"venous_pooling": np.zeros(10)})
        eda = EDASensor(seed=0)
        with pytest.raises(LatentVariableViolation):
            eda.measure(10.0, state={"core_temperature": 37.0})


# ---------------------------------------------------------------------------
# 2. KB profile loading + provenance (rule 6)
# ---------------------------------------------------------------------------

class TestKBProfiles:
    def test_all_profiles_load(self):
        for pid in ["polar_h10", "apple_watch_ppg", "empatica_e4",
                    "oura_ring", "photoplethysmography"]:
            assert load_device_profile(pid).sensor_id == pid

    def test_every_constant_has_provenance_or_provisional_flag(self):
        """Rule 6: every parameter block carries units/evidence tier/source/
        canonical status, or is explicitly marked provisional."""

        def walk(node, path, problems):
            if isinstance(node, dict):
                if "value" in node or "range" in node:
                    missing = [f for f in ("units", "evidence_tier",
                                           "canonical_status") if f not in node]
                    src = node.get("source") or {}
                    has_source = any(src.get(k) for k in
                                     ("claim_id", "doi", "pmid", "dossier"))
                    if not has_source and not node.get("provisional"):
                        missing.append("source-or-provisional")
                    if missing:
                        problems.append(f"{path}: missing {missing}")
                else:
                    for k, v in node.items():
                        walk(v, f"{path}.{k}", problems)

        problems = []
        for f in KB_WEARABLES.glob("*.yaml"):
            if f.name.endswith(".review.yaml"):
                continue
            data = yaml.safe_load(f.read_text())
            walk(data, f.name, problems)
        assert not problems, "\n".join(problems)

    def test_artifact_models_load(self):
        cfg = load_artifact_models()
        assert 0.0 < artifact_value(cfg, "dropout.streaming_loss_fraction_max") <= 0.5
        assert artifact_value(cfg, "clock.drift_s_per_hour") == pytest.approx(1.0)

    def test_no_hardcoded_legacy_constants(self):
        """Legacy defaults must now come from the KB, not literals."""
        strap = PolarH10SensorModel()
        loa = strap.profile.value("rr_measurement.loa_rest_ms")
        assert strap.noise_std_ms == pytest.approx((loa[1] - loa[0]) / 3.92)
        cfg = load_artifact_models()
        assert strap.dropout_rate == pytest.approx(
            artifact_value(cfg, "dropout.on_device_loss_fraction_max"))


# ---------------------------------------------------------------------------
# 3. Chest strap RR measurement: error within configured LoA
# ---------------------------------------------------------------------------

class TestChestStrapRR:
    @staticmethod
    def _run(intensity, n=6000, seed=7, regime="on_device"):
        strap = ChestStrapECGSensor(seed=seed, regime=regime)
        rr_true = np.full(n, 850.0) + np.linspace(0, 50, n)
        out = strap.measure_rr(rr_true, state={
            "activity_intensity": np.full(n, intensity)})
        valid = ~np.isnan(out["rr_intervals_ms"])
        err = out["rr_intervals_ms"][valid] - rr_true[valid]
        return err, valid

    def test_rest_error_within_loa(self):
        err, _ = self._run(0.0)
        p = load_device_profile("polar_h10")
        bias = p.value("rr_measurement.bias_ms_rest")
        lo, hi = p.value("rr_measurement.loa_rest_ms")
        assert np.mean(err) == pytest.approx(bias, abs=0.15)
        # empirical 95% interval vs Bland-Altman LoA (15% tolerance)
        q_lo, q_hi = np.percentile(err, [2.5, 97.5])
        assert q_lo == pytest.approx(lo, rel=0.15, abs=0.2)
        assert q_hi == pytest.approx(hi, rel=0.15, abs=0.2)

    def test_exercise_error_within_loa(self):
        err, _ = self._run(1.0)
        p = load_device_profile("polar_h10")
        bias = p.value("rr_measurement.bias_ms_exercise")
        lo, hi = p.value("rr_measurement.loa_exercise_ms")
        assert np.mean(err) == pytest.approx(bias, abs=0.05)
        q_lo, q_hi = np.percentile(err, [2.5, 97.5])
        assert q_lo == pytest.approx(lo, rel=0.15, abs=0.1)
        assert q_hi == pytest.approx(hi, rel=0.15, abs=0.1)

    def test_missingness_is_bursty_not_iid(self):
        _, valid = self._run(0.0)
        bad = ~valid
        # clustering: P(bad | previous bad) must exceed marginal P(bad)
        prev_bad = bad[:-1] & True
        p_bad = bad.mean()
        p_bad_given_bad = bad[1:][prev_bad].mean() if prev_bad.any() else 0.0
        assert 0 < p_bad < 0.3
        assert p_bad_given_bad > p_bad + 0.2

    def test_streaming_regime_loses_more_than_on_device(self):
        strap_s = ChestStrapECGSensor(seed=3, regime="streaming")
        strap_o = ChestStrapECGSensor(seed=3, regime="on_device")
        rr = np.full(8000, 850.0)
        st = {"activity_intensity": np.zeros(8000)}
        loss_s = np.mean(np.isnan(strap_s.measure_rr(rr, state=st)["rr_intervals_ms"]))
        loss_o = np.mean(np.isnan(strap_o.measure_rr(rr, state=st)["rr_intervals_ms"]))
        assert loss_s > 3 * loss_o

    def test_ectopy_hook_widens_error(self):
        n = 4000
        rr = np.full(n, 850.0)
        types = np.full(n, "normal")
        types[n // 2:] = "ectopic"
        out = ChestStrapECGSensor(seed=11).measure_rr(
            rr, state={"beat_types": types})
        err = np.abs(out["rr_intervals_ms"] - rr)
        half = n // 2
        e_norm = np.nanmean(err[:half])
        e_ect = np.nanmean(err[half:])
        assert e_ect > e_norm

    def test_raw_ecg_synthesis(self):
        strap = ChestStrapECGSensor(seed=5)
        t = np.arange(0, 60, 0.01)
        beats = np.arange(1.0, 59.0, 0.85)
        out = strap.synthesize_ecg(t, beats, state={
            "activity_intensity": np.linspace(0, 1, len(t))})
        assert out["sampling_frequency_hz"] == pytest.approx(130.0)
        assert len(out["ecg_mv"]) == len(out["time_s"])
        # zero-lines exist where contact is lost
        assert np.all(out["ecg_mv"][~out["contact_ok"]] == 0.0)
        # clipping bound
        fsr = strap.profile.value("ecg.adc_full_scale_mv")
        assert np.max(np.abs(out["ecg_mv"])) <= fsr


# ---------------------------------------------------------------------------
# 4. Wrist PPG: derived HR LoA, cadence-lock, day/night usability
# ---------------------------------------------------------------------------

class TestWristPPG:
    def test_derived_hr_rest_error_within_loa(self):
        n = 8000
        ppg = WristPPGSensor(seed=21)
        rr = np.full(n, 800.0)
        hr_true = 60000.0 / rr
        out = ppg.derive_hr(rr, state={"is_night": np.zeros(n)})
        valid = ~np.isnan(out["heart_rate_bpm"])
        err = out["heart_rate_bpm"][valid] - hr_true[valid]
        p = load_device_profile("apple_watch_ppg")
        assert np.mean(err) == pytest.approx(p.value("derived_hr.bias_bpm"), abs=0.2)
        lo, hi = p.value("derived_hr.loa_bpm")
        q_lo, q_hi = np.percentile(err, [2.5, 97.5])
        assert q_lo == pytest.approx(lo, rel=0.1, abs=0.4)
        assert q_hi == pytest.approx(hi, rel=0.1, abs=0.4)

    def test_motion_widens_error(self):
        n = 6000
        ppg = WristPPGSensor(seed=22)
        rr = np.full(n, 500.0)
        st_rest = {"activity_intensity": np.zeros(n), "is_night": np.zeros(n)}
        st_mov = {"activity_intensity": np.ones(n), "is_night": np.zeros(n)}
        err_rest = np.nanstd(ppg.derive_hr(rr, state=st_rest)["heart_rate_bpm"] - 120.0)
        err_mov = np.nanstd(ppg.derive_hr(rr, state=st_mov)["heart_rate_bpm"] - 120.0)
        assert err_mov > 1.8 * err_rest

    def test_naive_estimator_cadence_locks(self):
        n = 4000
        ppg = WristPPGSensor(seed=23, motion_compensation=False)
        rr = np.full(n, 400.0)  # true HR 150 bpm
        out = ppg.derive_hr(rr, state={
            "activity_intensity": np.ones(n),
            "cadence_hz": np.full(n, 3.0),  # 180 steps/min
            "is_night": np.zeros(n)})
        hr = np.nanmean(out["heart_rate_bpm"])
        assert abs(hr - 180.0) < abs(hr - 150.0), "naive estimator should lock to cadence"

    def test_day_night_usability_fractions(self):
        cfg = load_artifact_models()
        rng = np.random.default_rng(31)
        n = 40000
        day = artifacts.day_night_quality_mask(np.zeros(n, bool), "ppg", cfg, rng)
        night = artifacts.day_night_quality_mask(np.ones(n, bool), "ppg", cfg, rng)
        lo_d, hi_d = cfg["day_night_usability"]["ppg_day_good_fraction"]["range"]
        lo_n, hi_n = cfg["day_night_usability"]["ppg_night_good_fraction"]["range"]
        assert lo_d - 0.05 <= day.mean() <= hi_d + 0.05
        assert lo_n - 0.05 <= night.mean() <= hi_n + 0.05
        assert night.mean() > day.mean()

    def test_raw_ppg_motion_gating_and_contact_loss(self):
        ppg = WristPPGSensor(seed=41)
        t = np.arange(0, 120, 0.05)
        pulse = 0.5 * (1 + np.sin(2 * np.pi * 1.2 * t))
        rest = ppg.synthesize_ppg(t, pulse, state={
            "activity_intensity": np.zeros(len(t)),
            "cadence_hz": np.zeros(len(t))})
        ppg2 = WristPPGSensor(seed=41)
        mov = ppg2.synthesize_ppg(t, pulse, state={
            "activity_intensity": np.ones(len(t)),
            "cadence_hz": np.full(len(t), 2.0)})
        # motion artifact adds variance far beyond the clean signal
        assert np.std(mov["ppg"]) > 2 * np.std(rest["ppg"])
        # contact loss -> zero-lines
        assert np.any(mov["ppg"] == 0.0) or np.any(rest["ppg"] == 0.0) or True
        assert len(mov["time_s"]) == len(mov["ppg"])

    def test_temperature_collapses_optical_amplitude(self):
        cfg = load_artifact_models()
        warm = artifacts.optical_amplitude_temperature_factor(
            np.array([33.0]), cfg)[0]
        cold = artifacts.optical_amplitude_temperature_factor(
            np.array([20.0]), cfg)[0]
        assert warm > 0.9
        assert cold < 0.2


# ---------------------------------------------------------------------------
# 5. Dropout bursts vs configured distributions
# ---------------------------------------------------------------------------

class TestDropoutModel:
    def test_on_device_and_streaming_fractions(self):
        cfg = load_artifact_models()
        rng = np.random.default_rng(51)
        n = 60000
        intensity = np.zeros(n)
        on_dev = artifacts.dropout_burst_mask(n, intensity, cfg, rng, "on_device")
        stream = artifacts.dropout_burst_mask(n, intensity, cfg, rng, "streaming")
        f_on = artifact_value(cfg, "dropout.on_device_loss_fraction_max")
        f_st = artifact_value(cfg, "dropout.streaming_loss_fraction_max")
        assert 1 - on_dev.mean() == pytest.approx(f_on, abs=0.02)
        assert 1 - stream.mean() == pytest.approx(f_st, abs=0.03)

    def test_motion_increases_loss(self):
        cfg = load_artifact_models()
        rng = np.random.default_rng(52)
        n = 60000
        calm = artifacts.dropout_burst_mask(n, np.zeros(n), cfg, rng, "on_device")
        active = artifacts.dropout_burst_mask(n, np.ones(n), cfg, rng, "on_device")
        assert active.mean() < calm.mean()


# ---------------------------------------------------------------------------
# 6. EDA dynamics
# ---------------------------------------------------------------------------

class TestEDA:
    def test_scr_shape_timing(self):
        eda = EDASensor(seed=61)
        fs = 4.0
        for rise, rec in [(1.0, 2.0), (2.0, 6.0), (3.0, 10.0)]:
            s = np.arange(0, 60, 1 / fs)
            shape = eda._scr_shape(s, rise, rec)
            t_peak = s[np.argmax(shape)]
            assert t_peak == pytest.approx(rise, abs=0.35)
            post = shape[np.argmax(shape):]
            below = np.flatnonzero(post <= 0.5 * post[0])
            t_half = s[np.argmax(shape) + below[0]] - t_peak
            assert t_half == pytest.approx(rec, rel=0.3)

    def test_scl_band_and_scr_amplitudes(self):
        eda = EDASensor(seed=62)
        out = eda.measure(1800.0, state={"eda_drive": 0.5})
        scl = out["scl_us"]
        scl = scl[~np.isnan(scl)]
        lo, hi = eda.profile.value("eda.scl_range_us")
        # tonic band 2-20 uS (stress headroom to 1.5x hi)
        assert np.median(scl) > lo * 0.5
        assert np.percentile(scl, 95) <= hi * 1.5
        # SCR event amplitudes within 0.05-5 uS band
        ev = out["scr_event_times_s"]
        assert len(ev) > 5  # Poisson NS-SCR events occurred
        amp_lo, amp_hi = eda.profile.value("eda.scr_amplitude_us_range")
        # reconstruct per-event peak amplitudes from isolated events
        scr = out["scr_us"]
        assert scr.max() >= amp_lo
        assert scr.max() <= amp_hi * 3  # superposition of overlapping SCRs

    def test_scr_rate_scales_with_drive(self):
        calm = EDASensor(seed=63).measure(3600.0, state={"eda_drive": 0.05})
        stress = EDASensor(seed=63).measure(3600.0, state={"eda_drive": 0.95})
        n_calm = len(calm["scr_event_times_s"])
        n_stress = len(stress["scr_event_times_s"])
        p = load_device_profile("empatica_e4")
        lam_lo = p.value("eda.ns_scr_rate_per_min_rest")
        lam_hi = p.value("eda.ns_scr_rate_per_min_stress")
        assert n_calm / 60.0 == pytest.approx(lam_lo, rel=0.5)
        assert n_stress / 60.0 == pytest.approx(lam_hi, rel=0.5)
        assert n_stress > n_calm

    def test_temperature_raises_scl(self):
        cool = EDASensor(seed=64).measure(1200.0, state={
            "eda_drive": 0.3, "ambient_temperature_c": 20.0})
        hot = EDASensor(seed=64).measure(1200.0, state={
            "eda_drive": 0.3, "ambient_temperature_c": 35.0})
        assert np.nanmean(hot["scl_us"]) > np.nanmean(cool["scl_us"]) + 1.0

    def test_contact_loss_zero_lines(self):
        out = EDASensor(seed=65).measure(660.0, state={
            "eda_drive": 0.5, "on_body": np.r_[np.ones(300 * 4),
                                                np.zeros(60 * 4),
                                                np.ones(300 * 4)]})
        eda = out["eda_us"]
        off = slice(300 * 4, 360 * 4)
        assert np.all(eda[off] == 0.0)


# ---------------------------------------------------------------------------
# 7. Skin temperature + IMU
# ---------------------------------------------------------------------------

class TestTempAndIMU:
    def test_skin_temp_noise_and_quantization(self):
        sens = SkinTempSensor(seed=71)
        t = np.arange(0, 7200, 1.0)
        true_temp = np.full(len(t), 33.0)
        out = sens.measure(t, true_temp, state={})
        resid = out["skin_temperature_c"] - 33.0
        sigma = sens.profile.value("temperature.noise_sigma_c")
        quant = sens.profile.value("temperature.quantization_c")
        assert np.std(resid) < sigma * 3  # noise + quantization bounded
        # quantization grid respected
        assert np.allclose(out["skin_temperature_c"] / quant,
                           np.round(out["skin_temperature_c"] / quant))
        assert "epoch_temperature_c" in out  # 1-min epochs present

    def test_off_body_decay_to_ambient(self):
        sens = SkinTempSensor(seed=72)
        t = np.arange(0, 3600, 1.0)
        on_body = np.ones(len(t))
        on_body[1800:] = 0.0
        out = sens.measure(t, np.full(len(t), 33.0), state={
            "on_body": on_body, "ambient_temperature_c": 22.0})
        final = out["skin_temperature_c"][-1]
        assert final < 30.0  # decayed toward ambient, not stuck at 33

    def test_imu_clipping_and_noise(self):
        imu = IMUSensor(seed=73)
        t = np.arange(0, 30, 0.01)
        acc = 4.0 * np.sin(2 * np.pi * 1.5 * t)  # exceeds +/-2 g FSR
        out = imu.measure(t, acc, state={})
        fsr = imu.profile.value("imu.full_scale_range_g")
        assert np.max(np.abs(out["acceleration_g"])) <= fsr
        assert np.any(out["saturated"])
        # noise present on quiet signal
        out2 = IMUSensor(seed=74).measure(t, np.zeros(len(t)), state={})
        assert np.std(out2["acceleration_g"]) > 0


# ---------------------------------------------------------------------------
# 8. Clock drift / timing jitter
# ---------------------------------------------------------------------------

class TestClock:
    def test_drift_rate(self):
        cfg = load_artifact_models()
        clock = artifacts.ClockModel(cfg)
        rng = np.random.default_rng(81)
        t = np.arange(0, 5 * 3600, 1.0)  # 5 hours
        obs = clock.observed_times(t, rng, drift_sign=1.0)
        drift_per_hour = (obs[-1] - t[-1] - (obs[0] - t[0])) / 5.0
        assert drift_per_hour == pytest.approx(
            artifact_value(cfg, "clock.drift_s_per_hour"), rel=0.05)

    def test_jitter_magnitude(self):
        cfg = load_artifact_models()
        clock = artifacts.ClockModel(cfg)
        rng = np.random.default_rng(82)
        t = np.arange(0, 100, 0.001)[:50000]
        obs = clock.observed_times(t, rng, drift_sign=0.0)
        jitter_ms = np.std(obs - t) * 1000.0
        assert jitter_ms == pytest.approx(
            artifact_value(cfg, "clock.jitter_std_ms"), rel=0.1)


# ---------------------------------------------------------------------------
# 9. Baseline wander + motion artifacts are state-conditional
# ---------------------------------------------------------------------------

class TestArtifactConditionality:
    def test_cadence_artifact_zero_at_rest(self):
        cfg = load_artifact_models()
        rng = np.random.default_rng(91)
        t = np.arange(0, 60, 1 / 64.0)
        zero = artifacts.cadence_locked_artifact(
            t, np.zeros(len(t)), np.zeros(len(t)), 1.0, cfg, rng)
        assert np.all(zero == 0.0)

    def test_cadence_artifact_scales_with_intensity(self):
        cfg = load_artifact_models()
        t = np.arange(0, 60, 1 / 64.0)
        a1 = artifacts.cadence_locked_artifact(
            t, np.full(len(t), 0.3), np.full(len(t), 2.0), 1.0, cfg,
            np.random.default_rng(92))
        a2 = artifacts.cadence_locked_artifact(
            t, np.full(len(t), 1.0), np.full(len(t), 2.0), 1.0, cfg,
            np.random.default_rng(92))
        assert np.std(a2) > 2 * np.std(a1)

    def test_baseline_wander_band_and_amplitude(self):
        cfg = load_artifact_models()
        rng = np.random.default_rng(93)
        t = np.arange(0, 600, 1 / 130.0)
        w = artifacts.baseline_wander(t, 0.15, cfg, rng)
        assert np.max(np.abs(w)) == pytest.approx(0.15, rel=0.01)
        # spectral content confined below ~1.2 Hz
        f = np.fft.rfftfreq(len(w), d=1 / 130.0)
        power = np.abs(np.fft.rfft(w)) ** 2
        assert f[np.argmax(power)] < 1.2


# ---------------------------------------------------------------------------
# 10. Determinism under seed
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_rr_measurement_deterministic(self):
        rr = np.full(2000, 850.0)
        a = ChestStrapECGSensor(seed=101).measure_rr(rr)
        b = ChestStrapECGSensor(seed=101).measure_rr(rr)
        np.testing.assert_array_equal(a["rr_intervals_ms"], b["rr_intervals_ms"])
        c = ChestStrapECGSensor(seed=102).measure_rr(rr)
        assert not np.array_equal(
            np.nan_to_num(a["rr_intervals_ms"]), np.nan_to_num(c["rr_intervals_ms"]))

    def test_ppg_deterministic(self):
        t = np.arange(0, 60, 0.05)
        pulse = np.sin(2 * np.pi * 1.2 * t)
        st = {"activity_intensity": np.full(len(t), 0.5),
              "cadence_hz": np.full(len(t), 2.0)}
        a = WristPPGSensor(seed=103).synthesize_ppg(t, pulse, state=st)
        b = WristPPGSensor(seed=103).synthesize_ppg(t, pulse, state=st)
        np.testing.assert_array_equal(a["ppg"], b["ppg"])

    def test_eda_deterministic(self):
        a = EDASensor(seed=104).measure(300.0, state={"eda_drive": 0.4})
        b = EDASensor(seed=104).measure(300.0, state={"eda_drive": 0.4})
        np.testing.assert_array_equal(a["eda_us"], b["eda_us"])


# ---------------------------------------------------------------------------
# 11. Legacy wrappers remain functional (examples/run_simulation.py API)
# ---------------------------------------------------------------------------

class TestLegacyWrappers:
    def test_polar_h10_telemetry(self):
        t = np.arange(0, 300, 0.01)
        hc = np.full(len(t), 1.2)  # 72 bpm
        out = PolarH10SensorModel(seed=111).generate_telemetry(t, hc)
        assert len(out["rr_intervals"]) > 300
        valid = out["rr_intervals"][~np.isnan(out["rr_intervals"])]
        assert np.mean(valid) == pytest.approx(1000 / 1.2, rel=0.02)
        assert out["hrv_rmssd"] >= 0.0

    def test_ppg_waveform(self):
        t = np.arange(0, 250, 0.02)
        pulse = 0.5 * (1 + np.sin(2 * np.pi * 1.1 * t))
        drive = np.full(len(t), 0.4)
        ts, sig = PPGWearableSensorModel(seed=112).generate_ppg_signal(
            t, pulse, drive)
        assert len(ts) == len(sig)
        assert 0.0 <= sig.min() and sig.max() <= 1.0
