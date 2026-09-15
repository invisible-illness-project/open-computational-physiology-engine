"""Batch execution engine (G-P0-07 build items 3 & 6).

Deterministic, parallel-safe dataset builder:

  * Seed hierarchy: dataset_seed -> subject_seed (dataset.cohort.stable_seed)
    -> per-channel seeds (engine / rr / sensor) derived by SHA-256 mixing.
    Same seeds -> byte-identical records (numpy npz zip entries use fixed
    timestamps; YAML/JSON serialized with sorted keys and normalized
    values; generation_timestamp is a deterministic build clock).
  * Fail-closed governance: ``validation.provenance_gate.preflight_dataset_build``
    runs BEFORE any simulation; in canonical mode any refusal aborts the
    build.  Per-phenotype selection is additionally gated via
    ``gate_phenotype_selection`` (defense in depth).
  * Dataset-level phenotype exclusions (G-P0-03 interface): the KB does
    not yet carry the ``dataset_exclusion`` marker requested by W1-C
    (knowledge_base/diseases/pots.yaml header comment), so the
    engine-falsified neuropathic POTS phenotype is refused HERE in
    canonical mode (fail-closed), exactly as the G-P0-03 interface
    request specifies.  See DATASET_EXCLUDED_PHENOTYPES.
  * Subject construction: VirtualSubject priors -> machine-fitted RHR
    calibration of Hm (documented, tier C) -> canonical perturbations via
    PerturbationManager -> hypovolemia SEVERITY resampling (Raj 2005
    distribution, never the KB point extreme) -> pooling-axis (VMvl)
    placement.  Between-group separation comes from these MECHANISM
    levers only (rule 4/5).
  * Outputs per subject x protocol: ground_truth.npz (latent),
    sensors.npz (raw channels), derived.json, record.yaml; top-level
    manifest.yaml + manifest_summary.txt + cohort.csv.

``run_subject`` writes only under the subject's own directories and reads
only immutable config/KB state -> safe for multiprocessing sharding by
subject (the serial loop below is the reference executor).
"""

from __future__ import annotations

import csv
import io
import json
import os
from typing import Any, Dict, List, Optional

import numpy as np
import yaml

from dataset.cohort import CohortSampler, Subject, stable_seed
from dataset.kb_closure import externally_consumed_kb_files
from dataset.protocols import ProtocolSpec, parse_protocol
from dataset.rr_source import generate_rr_series, hrv_module_status, FALLBACK_HONESTY_FLAGS
from dataset import schema as recschema
from dataset.sensor_governance import audit_sensor_experimental_blocks
from dataset.provenance import (
    git_revision,
    kb_bundle_sha256,
    model_version,
    registry_version,
)
from dataset.population_evidence import evidence_block
from models.baroreflex_model import BaroreflexPOTSModel
from simulation.engine import SimulationEngine
from simulation.event_kernels import (
    make_exercise_kernel,
    make_meal_kernel,
    make_stress_kernel,
)
from simulation.population import VirtualSubject
from simulation.perturbations import PerturbationManager
from tools.kb_access import CANONICAL, load_kb
from validation.evaluator import (
    compare_distribution_to_reference,
    compute_orthostatic_metrics,
    load_healthy_reference,
    match_reference_protocol,
)
from validation.provenance_gate import (
    ExperimentalPerturbationError,
    gate_phenotype_selection,
    preflight_dataset_build,
)

#: G-P0-03 dataset-level exclusions (see module docstring). Fail-closed in
#: canonical mode regardless of KB canonical_status until the KB carries the
#: dataset_exclusion marker (W1-B schema interface, pending).
DATASET_EXCLUDED_PHENOTYPES = {
    "neuropathic_pots": (
        "G-P0-03: engine-falsified vs >=30 bpm sustained criterion "
        "(21.2 bpm; flat dose-response); canonical dataset generation must "
        "reject neuropathic POTS until bounded stress-relaxation creep / "
        "tilt-onset semantics land (knowledge_base/diseases/pots.yaml header)"
    ),
}

#: Empirical Hm -> supine-equilibrium-HR map for the RHR calibration
#: (machine-fitted on the merged engine, bench protocol, 2026-06; tier C
#: provisional).  equilibrium_bpm ~= RHR_EQ_INTERCEPT + RHR_EQ_SLOPE*(Hm-0.3)
#: measured at nominal params: Hm 0.142->62.5, 0.300->63.9, 0.674->71.6 bpm.
RHR_EQ_INTERCEPT = 63.9
RHR_EQ_SLOPE = 17.1
RHR_CALIBRATION_TOLERANCE_BPM = 3.0


def calibrate_hm_for_rhr(params: Dict[str, float], target_rhr_bpm: float) -> float:
    """Solve the HR-controller floor Hm so the supine equilibrium HR
    approximates the population-drawn RHR trait.

    Machine-fitted linear correction (constants above, tier C provisional,
    honesty-flagged): the Hill-at-pcm0 one-shot solve undershoots because
    the supine equilibrium drifts ~+5-7 bpm with sensitivity ~17 bpm per
    Hm unit.  Applied to the PRE-perturbation parameter set only, so
    disease resting tachycardia still emerges mechanistically.
    """
    hm = 0.3 + (float(target_rhr_bpm) - RHR_EQ_INTERCEPT) / RHR_EQ_SLOPE
    return float(min(1.5, max(0.05, hm)))


class BuildError(RuntimeError):
    pass


class BuildResult:
    def __init__(self):
        self.records: List[Dict[str, Any]] = []
        self.subjects: List[Subject] = []
        self.manifest: Dict[str, Any] = {}
        self.output_dir: Optional[str] = None
        self.preflight_warnings: List[str] = []
        self.validation: Dict[str, Any] = {}


class DatasetBuilder:
    """Builds an OCPE synthetic dataset from one YAML-able config."""

    def __init__(self, config: Dict[str, Any], kb_dir: Optional[str] = None,
                 output_dir: Optional[str] = None):
        self.config = dict(config)
        self.name = self.config.get("dataset_name", "ocpe_dataset")
        self.version = str(self.config.get("dataset_version", "0.1.0"))
        self.dataset_seed = int(self.config.get("dataset_seed", 0))
        self.mode = str(self.config.get("generation_mode", CANONICAL))
        self.allow_experimental = bool(self.config.get("allow_experimental", False))
        self.kb_dir = kb_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "knowledge_base")
        self.output_dir = output_dir or os.path.join("results", self.name)
        self.generation_timestamp = self.config.get("generation_timestamp") or \
            recschema.deterministic_build_timestamp(self.dataset_seed)
        self.protocols: List[ProtocolSpec] = [
            parse_protocol(p) for p in self.config.get("protocols", [])]
        self.sensor_configs = list(self.config.get("sensors", []) or [])
        self.engine_cfg = dict(self.config.get("engine", {}) or {})
        self.subjects: List[Subject] = []
        self._preflight_report = None
        self._sensor_audit: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------
    def kb_version(self) -> str:
        """Consumed-KB bundle hash: closure/kb_dir data files (review
        sidecars excluded -- volatile UUID/wall-clock fields, review F5)
        PLUS the externally consumed wearable/artifact files
        (artifact_models.yaml et al.) that sensor_models loads read-only
        from the repo KB (review F13 completeness)."""
        return kb_bundle_sha256(
            self.kb_dir,
            extra_files=externally_consumed_kb_files(self.kb_dir))

    # ------------------------------------------------------------------
    # Governance
    # ------------------------------------------------------------------
    def preflight(self):
        """Fail-closed provenance-gate preflight over the whole build."""
        phenotype_ids = sorted({pid for s in self.subjects for pid in s.phenotypes})
        sensor_ids = sorted({s["sensor_id"] for s in self.sensor_configs})
        report = preflight_dataset_build(
            self.kb_dir, mode=self.mode,
            allow_experimental=self.allow_experimental,
            phenotype_ids=phenotype_ids, sensor_ids=sensor_ids)
        report.raise_if_failed()  # fail-closed (ProvenanceGateError)

        # Dataset-level exclusions (G-P0-03; see DATASET_EXCLUDED_PHENOTYPES)
        if self.mode == CANONICAL:
            for pid in phenotype_ids:
                if pid in DATASET_EXCLUDED_PHENOTYPES:
                    raise ExperimentalPerturbationError(
                        f"phenotype '{pid}' excluded from canonical dataset "
                        f"generation: {DATASET_EXCLUDED_PHENOTYPES[pid]}")

        # Per-phenotype selection gate (defense in depth)
        kb = load_kb(self.kb_dir)
        for pid in phenotype_ids:
            pheno = kb.phenotypes.get(pid)
            if pheno is None:
                raise BuildError(f"unknown phenotype id {pid!r}")
            gate_phenotype_selection(
                pheno, mode=self.mode, allow_experimental=self.allow_experimental)

        # Dataset-side per-block experimental audit (review F8): the gate
        # checks sensor-LEVEL canonical_status; experimental parameter
        # blocks INSIDE canonical-status device/artifact files are refused
        # or strip-and-flagged here (fail-closed in canonical mode).
        self._sensor_audit = audit_sensor_experimental_blocks(
            self.kb_dir, self.sensor_configs, mode=self.mode)
        self._preflight_report = report
        return report

    # ------------------------------------------------------------------
    # Subject -> parameterized model
    # ------------------------------------------------------------------
    def build_model(self, subject: Subject):
        """Construct the mechanistic model for one subject.

        Order (mechanism-first): KB nominals -> VirtualSubject priors
        (Tanaka HRmax, sex/BMI/fitness) -> RHR calibration (Hm,
        pre-perturbation) -> canonical phenotype perturbations -> hypovolemia
        severity resample (TotalVol deficit from the Raj 2005 distribution)
        -> pooling-axis VMvl placement -> steady-state init.
        """
        vs = VirtualSubject(age=int(round(subject.age)), sex=subject.sex,
                            bmi=subject.bmi, fitness=subject.fitness,
                            seed=subject.subject_seed % (2 ** 31))
        model = BaroreflexPOTSModel(phenotype=None, subject=vs,
                                    kb_path=self.kb_dir)
        evidence: Dict[str, Any] = {"population_constants": subject.provenance,
                                    "perturbations": []}

        # RHR calibration on the pre-perturbation parameters.
        target_hm = calibrate_hm_for_rhr(model.params, subject.rhr_bpm)
        model.params["Hm"] = target_hm
        # Expected blood volume for THIS subject (post-prior, pre-perturbation);
        # the hypovolemia deficit draw is relative to this (Raj 2005 semantics).
        expected_vol_ml = float(model.params.get("TotalVol", 4500.0))
        # Nadler body-size hook (dataset-hardening W4-2, review F2): when the
        # cohort sampled height+BMI, replace the engine's repo-legacy sex/BMI
        # TotalVol prior with the Nadler expectation + between-person residual
        # (provisional E4 residual; honesty-flagged).  Healthy subjects then
        # vary in TotalVol with body size instead of sharing one point value.
        if subject.blood_volume_expected_ml is not None:
            evidence["blood_volume_nadler"] = {
                "parameter": "TotalVol",
                "engine_prior_value_ml": round(expected_vol_ml, 1),
                "applied_value_ml": round(subject.blood_volume_expected_ml, 1),
                "method": ("Nadler 1962 height/weight/sex equation + "
                           "between-person residual (CV 0.06, provisional E4); "
                           "weight = sampled BMI x sampled height^2"),
                "evidence": evidence_block("nadler_blood_volume"),
                "honesty_flag": "blood_volume_nadler_provisional_residual_cv",
            }
            expected_vol_ml = float(subject.blood_volume_expected_ml)
            model.params["TotalVol"] = expected_vol_ml
        evidence["rhr_calibration"] = {
            "target_rhr_bpm": round(subject.rhr_bpm, 2),
            "hm_applied": round(target_hm, 4),
            "method": "machine-fitted linear supine-equilibrium map (tier C provisional)",
            "tolerance_bpm": RHR_CALIBRATION_TOLERANCE_BPM,
        }

        # Canonical perturbations via the governed PerturbationManager.
        if subject.phenotypes:
            pm = PerturbationManager(
                kb_path=self.kb_dir,
                include_experimental=(self.mode != CANONICAL))
            params, applied = pm.apply_perturbations(dict(model.params),
                                                     list(subject.phenotypes))
            model.params = params
            for pid in applied:
                prov = (pm.last_application or {}).get("phenotypes", {}).get(pid, {})
                evidence["perturbations"].append({
                    "phenotype_id": pid,
                    "mode": (pm.last_application or {}).get("mode", "canonical"),
                    "canonical_parameters": prov.get("canonical", {}),
                    "experimental_parameters": prov.get("experimental", {}),
                })

        # Hypovolemia SEVERITY: resample the deficit from the Raj 2005
        # distribution (CONTRADICTION Target 3); the KB point -1000 mL is a
        # ~1.5x machine-calibrated extreme and is replaced by the draw.
        if subject.blood_volume_deficit_ml is not None:
            kb_vol = float(model.params.get("TotalVol", expected_vol_ml))
            model.params["TotalVol"] = expected_vol_ml - subject.blood_volume_deficit_ml
            evidence["severity_resample"] = {
                "parameter": "TotalVol",
                "kb_point_value_ml": kb_vol,
                "applied_value_ml": round(model.params["TotalVol"], 1),
                "deficit_draw_ml": round(subject.blood_volume_deficit_ml, 1),
                "evidence": evidence_block("pots_blood_volume_deficit_ml"),
                "honesty_flag": "severity_resampled_from_evidence_distribution",
            }

        # Pooling axis (VMvl): mechanistic orthostatic lever, same axis for
        # every condition (healthy axis sampling AND POTS subjects).
        if subject.orthostatic_axis.get("enabled"):
            model.params["VMvl"] = float(subject.pooling_capacity_ml)
            evidence["pooling_axis"] = {
                "parameter": "VMvl",
                "applied_value_ml": round(subject.pooling_capacity_ml, 1),
                "evidence": evidence_block("pooling_capacity_range_ml"),
                "honesty_flag": "pooling_capacity_tierC_machine_fitted",
            }

        model.initialize_steady_state()
        return model, evidence

    # ------------------------------------------------------------------
    # Engine execution
    # ------------------------------------------------------------------
    def _engine_seed(self, subject: Subject, protocol_id: str) -> int:
        return stable_seed(subject.subject_seed, "engine", protocol_id) % (2 ** 31)

    def _channel_seed(self, subject: Subject, *parts) -> int:
        return stable_seed(subject.subject_seed, *parts) % (2 ** 31)

    def _run_protocol(self, subject: Subject, model, protocol: ProtocolSpec):
        """Execute one protocol; returns (engine_results, hrv_inputs, honesty)."""
        seed = self._engine_seed(subject, protocol.protocol_id)
        engine = SimulationEngine(
            model, dt=float(self.engine_cfg.get("dt", 0.02)),
            hrv_noise=float(self.engine_cfg.get("hrv_noise", 0.02)),
            seed=seed,
            start_hour=float(self.engine_cfg.get("start_hour", 8.6667)))
        if protocol.family == "multiday":
            hrv_inputs = engine.run_multiday(
                protocol.days, step_s=protocol.step_s,
                exertion_schedule=protocol.exertion_schedule)
            results = dict(hrv_inputs)
            results["time"] = hrv_inputs["time_s"]
            honesty = list(hrv_inputs.get("honesty_flags", []))
            return results, hrv_inputs, honesty, engine

        # tilt_first: schedule declarative events as behavior kernels
        rng = np.random.default_rng(self._channel_seed(subject, "events",
                                                       protocol.protocol_id))
        for ev in protocol.events:
            if ev.type == "meal":
                engine.behavior.kernels.add_kernel(
                    make_meal_kernel(ev.at_s, time_scale=ev.params.get(
                        "kernel_time_scale", 1.0)), rng)
            elif ev.type == "exercise":
                engine.behavior.kernels.add_kernel(
                    make_exercise_kernel(
                        ev.at_s, duration_s=ev.params.get("duration_s", 300.0),
                        intensity=ev.params.get("intensity", 0.7)), rng)
            elif ev.type == "stress":
                engine.behavior.kernels.add_kernel(
                    make_stress_kernel(ev.at_s, duration_s=ev.params.get(
                        "duration_s", 600.0)), rng)
        results = engine.run(protocol.to_engine_tilt_params())
        hrv_inputs = engine.get_hrv_inputs()
        honesty = list(results.get("honesty_flags", []))
        return results, hrv_inputs, honesty, engine

    # ------------------------------------------------------------------
    # Observable coupling (engine-side observable proxies; rule 3)
    # ------------------------------------------------------------------
    def _observable_coupling(self, results, hrv_inputs, rr, protocol,
                             subject: Subject) -> Dict[str, Any]:
        """Build the whitelisted observable inputs for the sensor layer.

        Coupling-not-readout (OCPE_DATASET_SPECIFICATION section 0.1):
        latent state modulates observable DRIVES through documented
        mechanisms; latent values themselves never cross the boundary.
        """
        t = np.asarray(hrv_inputs["time_s"], dtype=float)
        n = len(t)
        beat_times = np.asarray(rr["beat_times_s"], dtype=float)
        symp = np.asarray(results.get("sympathetic_tone",
                                      hrv_inputs.get("sympathetic_drive",
                                                     np.zeros(n))), dtype=float)
        if symp.size != n:
            symp = np.resize(symp, n)

        # Activity/posture state from the protocol (passive tilt = rest).
        intensity = np.zeros(n)
        cadence = np.zeros(n)
        for ev in protocol.events:
            if ev.type == "exercise":
                dur = float(ev.params.get("duration_s", 300.0))
                m = (t >= ev.at_s) & (t < ev.at_s + dur)
                intensity[m] = float(ev.params.get("intensity", 0.7))
                cadence[m] = 1.8  # walk-jog cadence placeholder (observable)
        activity_state = np.where(intensity > 0.0, "exercise", "rest")

        # Normalized pulse waveform (unitless blood-volume pulse; dataset
        # spec section 2.2 item 3, engineering judgment): per-beat canonical
        # shape, amplitude modulated by a perfusion drive, NEVER by latent
        # pressure/volume readouts.
        pulse_t = t
        pulse = np.zeros(n)
        rr_ms = np.asarray(rr["rr_intervals_ms"], dtype=float)
        for i, bt in enumerate(beat_times):
            dur = rr_ms[i] / 1000.0 if i < len(rr_ms) else 0.9
            sys_frac = min(0.35, 0.25 * (0.9 / max(0.3, dur)))
            rel = (pulse_t - bt) / max(0.2, dur)
            m = (rel >= 0.0) & (rel < 1.0)
            x = rel[m]
            shape = np.where(x < sys_frac,
                             np.sin(0.5 * np.pi * x / sys_frac) ** 2,
                             np.exp(-(x - sys_frac) / 0.25))
            pulse[m] += shape
        pulse = np.clip(pulse, 0.0, 1.2) / 1.2

        # EDA sudomotor drive: skin-sympathetic cholinergic drive tracks
        # sympathetic arousal (EVD-SENS-006 mechanism class, E4) + event bumps.
        eda_drive = np.clip(0.15 + 0.6 * symp + 0.5 * intensity, 0.0, 1.0)

        # Skin temperature: wrist mesor ~33 deg C (POP A.7, EVD-SENS-007,
        # E3) with a vasomotor coupling to sympathetic drive (direction E3;
        # magnitude engineering judgment -> honesty-flagged).
        skin_temp = 33.0 - 0.8 * symp - 0.5 * intensity

        resp_hz = np.asarray(hrv_inputs.get("respiration_rate_brpm",
                                            np.full(n, 15.0)), dtype=float) / 60.0
        start_hour = float(self.engine_cfg.get("start_hour", 8.6667))
        hour = (start_hour + t / 3600.0) % 24.0
        is_night = (hour >= 22.0) | (hour < 6.0)

        return {
            "time_s": t,
            "beat_times_s": beat_times,
            "rr_intervals_ms": rr_ms,
            "beat_types": np.asarray(rr["beat_types"]),
            "pulse_waveform": pulse,
            "pulse_waveform_times_s": pulse_t,
            "eda_drive": eda_drive,
            "skin_temperature_c": skin_temp,
            "ambient_temperature_c": np.full(n, 22.0),
            "respiration_rate_hz": resp_hz,
            "respiration_waveform": np.sin(2 * np.pi * np.cumsum(resp_hz) *
                                           (t[1] - t[0] if n > 1 else 1.0)),
            "acceleration_g": 1.0 + 0.3 * intensity,
            "activity_intensity": intensity,
            "activity_state": activity_state,
            "cadence_hz": cadence,
            "is_night": is_night.astype(float),
            "on_body": np.ones(n),
            "fit_state": np.ones(n),
            "perfusion_drive": np.clip(0.5 + 0.5 * (1.0 - symp), 0.0, 1.0),
        }

    # ------------------------------------------------------------------
    # Sensor execution
    # ------------------------------------------------------------------
    def _sensor_configs_for(self, subject: Subject) -> List[Dict[str, Any]]:
        """Sensor configs active for THIS subject.  When the cohort sampler
        assigned a per-subject device (matched nuisance distribution across
        groups, review F2), only that device runs; otherwise the dataset-
        level sensor list applies (legacy behavior)."""
        if subject.device_id is None:
            return self.sensor_configs
        matched = [sc for sc in self.sensor_configs
                   if sc["sensor_id"] == subject.device_id]
        if not matched:
            raise BuildError(
                f"subject {subject.subject_id} assigned device "
                f"{subject.device_id!r} which is not in the dataset sensor "
                f"configuration {[sc['sensor_id'] for sc in self.sensor_configs]}")
        return matched

    def _run_sensors(self, subject: Subject, obs: Dict[str, Any]):
        """Run the configured KB-driven device models over the observable
        coupling.  Returns (channels, device_configs).  All inputs pass the
        sensor boundary guard (strict whitelist) inside the device APIs."""
        from sensor_models.devices import (
            ChestStrapECGSensor,
            EDASensor,
            IMUSensor,
            SkinTempSensor,
            WristPPGSensor,
        )
        channels: Dict[str, np.ndarray] = {}
        devices: List[Dict[str, Any]] = []
        t = obs["time_s"]

        def _collect(prefix: str, out: Dict[str, Any]):
            """Numeric/string array channels only; dict provenance goes to
            record.yaml, never into sensors.npz (no object arrays)."""
            for k, v in out.items():
                if k == "provenance" or isinstance(v, (dict, list)):
                    continue
                arr = np.asarray(v)
                if arr.dtype == object:
                    continue
                channels[f"{prefix}__{k}"] = arr
        for scfg in self._sensor_configs_for(subject):
            sid = scfg["sensor_id"]
            regime = scfg.get("regime", "on_device")
            seed = self._channel_seed(subject, "sensor", sid)
            chans = scfg.get("channels") or ["rr"]
            dev_cfg = {"sensor_id": sid, "regime": regime, "seed": int(seed),
                       "channels": list(chans)}

            if sid == "polar_h10":
                dev = ChestStrapECGSensor(sid, seed=seed, regime=regime)
                if "rr" in chans:
                    out = dev.measure_rr(obs["rr_intervals_ms"], state={
                        "beat_times_s": obs["beat_times_s"],
                        "activity_intensity": obs["activity_intensity"],
                        "is_night": obs["is_night"],
                        "beat_types": obs["beat_types"],
                        "on_body": obs["on_body"]})
                    _collect(f"{sid}__rr", out)
                    dev_cfg["provenance"] = out.get("provenance", {})
                if "ecg" in chans:
                    out = dev.synthesize_ecg(t, obs["beat_times_s"], state={
                        "activity_intensity": obs["activity_intensity"]})
                    _collect(f"{sid}__ecg", out)
            elif sid == "apple_watch_ppg":
                dev = WristPPGSensor(sid, seed=seed, regime=regime)
                if "hr" in chans:
                    out = dev.derive_hr(obs["rr_intervals_ms"], state={
                        "beat_times_s": obs["beat_times_s"],
                        "activity_intensity": obs["activity_intensity"],
                        "cadence_hz": obs["cadence_hz"],
                        "is_night": obs["is_night"],
                        "on_body": obs["on_body"]})
                    _collect(f"{sid}__hr", out)
                    dev_cfg["provenance"] = out.get("provenance", {})
                if "ppg" in chans:
                    out = dev.synthesize_ppg(t, obs["pulse_waveform"], state={
                        "activity_intensity": obs["activity_intensity"],
                        "cadence_hz": obs["cadence_hz"],
                        "skin_temperature_c": obs["skin_temperature_c"],
                        "is_night": obs["is_night"],
                        "on_body": obs["on_body"],
                        "fit_state": obs["fit_state"]})
                    _collect(f"{sid}__ppg", out)
            elif sid == "empatica_e4":
                if "eda" in chans:
                    dev = EDASensor(sid, seed=seed, regime=regime)
                    out = dev.measure(float(t[-1] - t[0]), state={
                        "eda_drive": obs["eda_drive"],
                        "ambient_temperature_c": obs["ambient_temperature_c"],
                        "activity_intensity": obs["activity_intensity"],
                        "is_night": obs["is_night"],
                        "on_body": obs["on_body"]})
                    _collect(f"{sid}__eda", out)
                    dev_cfg["provenance"] = out.get("provenance", {})
                if "imu" in chans:
                    dev = IMUSensor(sid, seed=seed, regime=regime)
                    out = dev.measure(t, obs["acceleration_g"], state={})
                    _collect(f"{sid}__imu", out)
            elif sid == "oura_ring":
                dev = SkinTempSensor(sid, seed=seed, regime=regime)
                out = dev.measure(t, obs["skin_temperature_c"], state={
                    "on_body": obs["on_body"],
                    "ambient_temperature_c": obs["ambient_temperature_c"],
                    "is_night": obs["is_night"]})
                _collect(f"{sid}__temp", out)
                dev_cfg["provenance"] = out.get("provenance", {})
            else:
                raise BuildError(f"no device mapping for sensor_id {sid!r}")
            devices.append(dev_cfg)
        return channels, devices

    # ------------------------------------------------------------------
    # Derived metrics (frozen evaluator semantics)
    # ------------------------------------------------------------------
    def _derived_metrics(self, subject, results, hrv_inputs, rr, channels,
                         protocol: ProtocolSpec):
        dm: Dict[str, Any] = {}
        t = np.asarray(hrv_inputs["time_s"], dtype=float)
        hr_true = np.asarray(hrv_inputs["mean_hr_bpm"], dtype=float)

        if protocol.family == "tilt_first" and protocol.tilt_duration_s > 0:
            sem = protocol.metric_semantics()
            om_true = compute_orthostatic_metrics(
                time=t, hr_bpm=hr_true, onset_s=sem["onset_s"],
                tilt_duration_s=sem["tilt_duration_s"],
                baseline_window_s=sem["baseline_window_s"])
            # Measured-channel metric (chest strap) with the SAME semantics.
            om_meas = None
            key = "polar_h10__rr__heart_rate_bpm"
            if key in channels:
                hr_m = np.asarray(channels[key], dtype=float)
                tm = np.asarray(channels["polar_h10__rr__times_s"], dtype=float)
                good = ~np.isnan(hr_m)
                if good.sum() > 10:
                    om_meas = compute_orthostatic_metrics(
                        time=tm[good], hr_bpm=hr_m[good],
                        onset_s=sem["onset_s"],
                        tilt_duration_s=sem["tilt_duration_s"],
                        baseline_window_s=sem["baseline_window_s"])
            # Protocol-conditioned healthy reference comparison (single run).
            ref_cmp = {"status": "not_applicable"}
            try:
                reference = load_healthy_reference()
                pid = match_reference_protocol(
                    reference, protocol.method, protocol.angle_degrees,
                    protocol.tilt_duration_s,
                    supine_rest_s=protocol.onset_s)
                if pid is not None and not np.isnan(
                        om_true["sustained_delta_HR_bpm"]):
                    ref_cmp = dict(compare_distribution_to_reference(
                        [om_true["sustained_delta_HR_bpm"]], pid,
                        reference=reference), status="compared",
                        note="single-run comparison")
            except (OSError, KeyError, ValueError) as exc:
                ref_cmp = {"status": "unavailable", "reason": str(exc)}
            dm["orthostatic"] = {
                "semantics": {
                    "source": "validation/evaluator.py::compute_orthostatic_metrics",
                    "sustained_delta_HR": "mean(HR, minutes 5-10 of tilt) - mean(HR, final 5 min supine)",
                    "initial_transient": "max(HR, first 30 s post-onset) - mean(HR, final 5 min supine)",
                    "frozen_by": "G-P0-09 (validation/healthy_reference.yaml)",
                },
                "true": om_true,
                "measured_chest_strap": om_meas,
                "baseline_hr_bpm": om_true["baseline_hr_bpm"],
                "sustained_delta_HR_bpm": om_true["sustained_delta_HR_bpm"],
                "sustained_window_kind": om_true["sustained_window_kind"],
                "initial_transient_bpm": om_true["initial_transient_bpm"],
                "reference_comparison": ref_cmp,
                "covariates": protocol.mandatory_covariates(),
            }

        # HRV summary from the TRUE beat series: only meaningful when the
        # structured W2-E generator is active; the fallback resampling has
        # no short-term structure (honesty: unresolved instead of a fake
        # number, rule 1).
        prov = rr.get("provenance", {})
        fallback = prov.get("source") == "fallback_mean_hr_phase_integration"
        rr_ms = np.asarray(rr["rr_intervals_ms"], dtype=float)
        hrv_block: Dict[str, Any] = {
            "rr_source": prov.get("source"),
            "mean_rr_ms": float(np.mean(rr_ms)) if rr_ms.size else None,
            "n_beats": int(len(rr.get("beat_times_s", []))),
        }
        if fallback:
            hrv_block["rmssd_ms"] = None
            hrv_block["rmssd_status"] = (
                "unresolved: fallback RR source has no structured HRV "
                "(no RSA/Mayer/1-f); short-term variability would be "
                "underestimated (rule 1)")
        elif rr_ms.size > 2:
            hrv_block["rmssd_ms"] = float(
                np.sqrt(np.mean(np.diff(rr_ms) ** 2)))
            hrv_block["ln_rmssd"] = float(np.log(max(1e-6, hrv_block["rmssd_ms"])))
            hrv_block["subject_ln_rmssd_trait"] = round(subject.ln_rmssd_ms, 4)
        dm["hrv"] = hrv_block
        return dm

    # ------------------------------------------------------------------
    # Ground truth (latent) extraction
    # ------------------------------------------------------------------
    _GT_MAP = {  # engine result key -> ground-truth array name (latent only)
        "time": "time_s", "pau": "pau_mmHg", "pal": "pal_mmHg",
        "pvu": "pvu_mmHg", "pcm": "pcm_mmHg", "Vau": "Vau_ml",
        "Vvu": "Vvu_ml", "Val": "Val_ml", "Vvl": "Vvl_ml", "Vlv": "Vlv_ml",
        "Vvm": "Vvm_ml", "Vsr": "Vsr_ml", "Hc": "Hc_bps",
        "left_ventricular_pressure": "left_ventricular_pressure_mmHg",
        "aortic_flow": "aortic_flow", "mitral_flow": "mitral_flow",
        "sympathetic_tone": "sympathetic_tone",
        "parasympathetic_tone": "parasympathetic_tone",
        "baroreflex_gain": "baroreflex_gain", "blood_volume": "blood_volume_ml",
        "hydration": "hydration", "stress_load": "stress_load",
        "inflammatory_burden": "inflammatory_burden",
        "metabolic_reserve": "metabolic_reserve",
        "hormonal_state": "hormonal_state",
        "autonomic_recovery_capacity": "autonomic_recovery_capacity",
        "sleep_pressure": "sleep_pressure", "circadian_drive": "circadian_drive",
        "fatigue": "fatigue", "brain_fog": "brain_fog", "pain": "pain",
        "orthostatic_intolerance": "orthostatic_intolerance",
        "palpitations": "palpitations", "sleepiness": "sleepiness",
        "dizziness": "dizziness",
        "vagal_drive": "vagal_drive", "sympathetic_drive": "sympathetic_drive",
        "respiration_rate_brpm": "respiration_rate_brpm",
        "sleep_stage": "sleep_stage_code",
        "mean_hr_bpm": "mean_hr_bpm",
        "pem_symptom_envelope": "pem_symptom_envelope",
        "slowed_recovery_envelope": "slowed_recovery_envelope",
        "bp_setpoint_factor": "bp_setpoint_factor",
    }

    def _ground_truth(self, results) -> Dict[str, np.ndarray]:
        gt: Dict[str, np.ndarray] = {}
        for src, dst in self._GT_MAP.items():
            if src in results:
                gt[dst] = np.asarray(results[src])
        if "time_s" not in gt and "time" in results:
            gt["time_s"] = np.asarray(results["time"])
        return gt

    # ------------------------------------------------------------------
    # Record assembly
    # ------------------------------------------------------------------
    def _assemble_record(self, subject: Subject, protocol: ProtocolSpec,
                         model, model_evidence, rr, channels, devices,
                         derived, engine_honesty, gt) -> Dict[str, Any]:
        flags = set(subject.honesty_flags)
        flags.update(engine_honesty)
        flags.update(protocol.honesty_flags())
        rr_prov = rr.get("provenance", {})
        flags.update(rr_prov.get("honesty_flags", []))
        flags.add("skin_temp_vasomotor_coupling_engineering_judgment")
        flags.add("pulse_waveform_shape_engineering_judgment")
        flags.add("rhr_calibration_machine_fitted_tierC")
        if model_evidence.get("severity_resample"):
            flags.add("severity_resampled_from_evidence_distribution")
        if subject.comorbidities:
            flags.add("comorbidities_metadata_only_not_engine_perturbed")

        experimental_items: List[str] = []
        for pert in model_evidence.get("perturbations", []):
            for sym in (pert.get("experimental_parameters") or {}):
                experimental_items.append(f"{pert['phenotype_id']}:{sym}")
        weak = sorted(f for f in flags if any(tok in f for tok in (
            "tierC", "machine_fitted", "engineering_judgment", "E0",
            "resampled", "provisional", "machine_calibrated")))
        extrapolated = sorted(f for f in flags if any(tok in f for tok in (
            "extrapolated", "E0", "fallback", "unresolved")))
        limitations = sorted(set(protocol.honesty_flags()) | {
            f for f in flags if "proxy" in f or "approximated" in f
            or "inactive" in f or "unvalidated" in f})
        # Sensor experimental-block audit dispositions (review F8):
        # consumed neutral no-ops are weakly evidenced; blocks excluded by
        # channel selection are recorded as governance limitations.
        audit = self._sensor_audit or {}
        weak = sorted(set(weak) | {
            f for f in audit.get("flags", [])
            if f.startswith("experimental_block_consumed_as_neutral_noop")})
        limitations = sorted(set(limitations) | {
            f for f in audit.get("flags", [])
            if f.startswith("experimental_block_excluded_by_channel")})
        if "hyperadrenergic_pots" in subject.phenotypes:
            limitations.append(
                "hyperadrenergic_pots upright delta-SBP pressor criterion "
                "NOT met by the 0-D model (disclosed; evaluator limitations)")
        if "neuropathic_pots" in subject.phenotypes:
            limitations.append("neuropathic_pots_unvalidated_engine_falsified_xfail")

        honesty = {
            "extrapolated_features": extrapolated,
            "latent_only_variables": list(recschema.LATENT_GROUND_TRUTH_VARIABLES),
            "experimental_features": experimental_items,
            "weakly_evidenced_features": weak,
            "validation_limitations": limitations,
        }
        # RHR calibration is a machine-fitted map (tier C); flag subjects
        # whose realized supine baseline misses the population-drawn target
        # beyond the documented tolerance (model floor / phenotype shift).
        ortho = (derived or {}).get("orthostatic") or {}
        baseline = ortho.get("baseline_hr_bpm")
        if baseline is not None and abs(
                baseline - subject.rhr_bpm) > RHR_CALIBRATION_TOLERANCE_BPM:
            honesty["weakly_evidenced_features"].append(
                "rhr_calibration_mismatch_beyond_tolerance")

        # Flat flag list = union of the five honesty categories (the schema
        # validator compares exactly this).
        flat_flags = sorted({f for cat in recschema.HONESTY_CATEGORIES
                             for f in honesty[cat]})

        sensor_channels = [
            {"name": name, "device": name.split("__")[0],
             "channel": "__".join(name.split("__")[1:]),
             "kind": "sensor_measurement"}
            for name in sorted(channels.keys())
        ]
        record = {
            "record_id": recschema.make_record_id(
                self.dataset_seed, subject.subject_id, protocol.protocol_id),
            "subject_id": subject.subject_id,
            "protocol_id": protocol.protocol_id,
            "physiological_state": {
                "condition": subject.condition,
                "phenotypes": list(subject.phenotypes),
                "severity": subject.severity,
                "comorbidities": list(subject.comorbidities),
                "demographics": subject.to_metadata()["demographics"],
                "protocol_family": protocol.family,
            },
            "events": [ev.to_record() for ev in protocol.events] + (
                [{"type": "head_up_tilt", "t_start_s": protocol.onset_s,
                  "params": {"angle_degrees": protocol.angle_degrees,
                             "duration_s": protocol.tilt_duration_s}}]
                if protocol.family == "tilt_first"
                and protocol.tilt_duration_s > 0 else []),
            "latent_parameters": {
                "role": "GROUND TRUTH ONLY - never a sensor channel (rule 3)",
                "reference": "ground_truth.npz",
                "variables": [k for k in sorted(gt.keys())],
                "population_traits": subject.to_metadata()["population_traits"],
            },
            "observable_parameters": {
                "reference": "sensors.npz",
                "channels": sensor_channels,
                "boundary": ("sensor_models/boundary.py OBSERVABLE_INPUT_KEYS "
                             "(strict whitelist; latent names rejected at runtime)"),
            },
            "sensor_configuration": {
                "devices": devices,
                "kb_wearables_dir": "knowledge_base/wearables",
            },
            "derived_metrics": {
                "reference": "derived.json",
                "metrics": derived,
                "semantics_source": "validation/evaluator.py (G-P0-09 frozen)",
            },
            "evidence": model_evidence,
            "uncertainty": {
                "population_constants": [
                    {"constant": p["constant"],
                     "uncertainty": p.get("uncertainty")}
                    for p in subject.provenance],
                "rhr_calibration_tolerance_bpm": RHR_CALIBRATION_TOLERANCE_BPM,
                "comorbidity_rates": ("ascertainment-downweighted 0.3-0.5x; "
                                      "pairwise-sufficient (3rd-order E0)"),
            },
            "canonical_status": (CANONICAL if self.mode == CANONICAL
                                 else "experimental"),
            "honesty": honesty,
            "honesty_flags": flat_flags,
            "seed": int(subject.subject_seed),
            "seed_hierarchy": {
                "dataset_seed": int(self.dataset_seed),
                "subject_seed": int(subject.subject_seed),
                "engine_seed": int(self._engine_seed(subject, protocol.protocol_id)),
                "sensor_seeds": {d["sensor_id"]: d["seed"] for d in devices},
            },
            "ocpe_commit": git_revision(),
            "kb_version": self.kb_version(),
            "registry_version": registry_version(),
            "model_version": model_version(),
            "schema_version": recschema.SCHEMA_VERSION,
            "generation_timestamp": self.generation_timestamp,
            "generation_mode": self.mode,
            "hrv_source": hrv_module_status(),
            "cohort_frame": subject.cohort_frame,
        }
        return recschema.normalize(record)

    # ------------------------------------------------------------------
    # Output writing (deterministic)
    # ------------------------------------------------------------------
    def _write_outputs(self, subject: Subject, protocol: ProtocolSpec,
                       record, gt, channels, derived) -> str:
        subj_dir = os.path.join(self.output_dir, "subjects", subject.subject_id,
                                protocol.protocol_id)
        os.makedirs(subj_dir, exist_ok=True)
        np.savez(os.path.join(subj_dir, "ground_truth.npz"),
                 **{k: np.asarray(v) for k, v in sorted(gt.items())})
        np.savez(os.path.join(subj_dir, "sensors.npz"),
                 **{k: np.asarray(v) for k, v in sorted(channels.items())})
        with open(os.path.join(subj_dir, "derived.json"), "w", encoding="utf-8") as f:
            json.dump(recschema.normalize(derived), f, indent=2, sort_keys=True)
            f.write("\n")
        with open(os.path.join(subj_dir, "record.yaml"), "w", encoding="utf-8") as f:
            yaml.safe_dump(recschema.normalize(record), f, sort_keys=True,
                           default_flow_style=False, width=100)
        return subj_dir

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------
    def sample_cohort(self) -> List[Subject]:
        sampler = CohortSampler(self.config, self.dataset_seed)
        self.subjects = sampler.sample()
        return self.subjects

    def run_subject(self, subject: Subject) -> List[Dict[str, Any]]:
        """Execute all protocols for one subject; returns record info list.
        Parallel-safe: touches only this subject's output directories."""
        model, model_evidence = self.build_model(subject)
        infos = []
        for protocol in self.protocols:
            results, hrv_inputs, engine_honesty, _engine = self._run_protocol(
                subject, model, protocol)
            rr = generate_rr_series(
                hrv_inputs, seed=self._channel_seed(subject, "rr", protocol.protocol_id),
                config={"subject_traits": {
                    "ln_rmssd_ms": subject.ln_rmssd_ms,
                    "rhr_bpm": subject.rhr_bpm}})
            obs = self._observable_coupling(results, hrv_inputs, rr, protocol, subject)
            channels, devices = self._run_sensors(subject, obs)
            derived = self._derived_metrics(subject, results, hrv_inputs, rr,
                                            channels, protocol)
            gt = self._ground_truth(results)
            # True beat-level observable ground truth (RR is measurable,
            # not latent): stored for sensor-error verification.
            gt["beat_times_s"] = np.asarray(rr["beat_times_s"], dtype=float)
            gt["rr_intervals_ms"] = np.asarray(rr["rr_intervals_ms"], dtype=float)
            record = self._assemble_record(subject, protocol, model,
                                           model_evidence, rr, channels,
                                           devices, derived, engine_honesty, gt)
            errors = (recschema.validate_record_schema(record)
                      + recschema.validate_record_provenance(record)
                      + recschema.validate_scientific_contract(record))
            if errors:
                raise BuildError(
                    f"record {subject.subject_id}/{protocol.protocol_id} failed "
                    f"dataset CI validation: {errors}")
            out_dir = self._write_outputs(subject, protocol, record, gt,
                                          channels, derived)
            infos.append({
                "record_id": record["record_id"],
                "subject_id": subject.subject_id,
                "cohort_id": subject.cohort_id,
                "condition": subject.condition,
                "protocol_id": protocol.protocol_id,
                "canonical_status": record["canonical_status"],
                "honesty_flags": record["honesty_flags"],
                "output_dir": os.path.relpath(out_dir, self.output_dir),
                "derived_summary": {
                    "baseline_hr_bpm": (derived.get("orthostatic") or {}).get(
                        "baseline_hr_bpm"),
                    "sustained_delta_HR_bpm": (derived.get("orthostatic") or {}).get(
                        "sustained_delta_HR_bpm"),
                    "sustained_window_kind": (derived.get("orthostatic") or {}).get(
                        "sustained_window_kind"),
                },
                "validation": {"schema": "pass", "provenance": "pass",
                               "scientific_contract": "pass"},
            })
        return infos

    def build(self) -> BuildResult:
        """Full build: cohort sampling -> preflight -> execute -> manifest."""
        from dataset.manifest import build_manifest, write_manifest
        result = BuildResult()
        if not self.subjects:
            self.sample_cohort()
        report = self.preflight()  # fail-closed before any simulation
        result.preflight_warnings = list(report.warnings)
        os.makedirs(self.output_dir, exist_ok=True)

        infos: List[Dict[str, Any]] = []
        for subject in self.subjects:
            infos.extend(self.run_subject(subject))
        result.records = infos
        result.subjects = self.subjects

        self._write_cohort_csv()
        manifest = build_manifest(self, infos, report)
        write_manifest(manifest, self.output_dir)
        result.manifest = manifest
        result.output_dir = self.output_dir
        result.validation = manifest.get("validation_status", {})
        return result

    def _write_cohort_csv(self) -> str:
        path = os.path.join(self.output_dir, "cohort.csv")
        cols = ["subject_id", "cohort_id", "condition", "phenotypes",
                "age_years", "sex", "bmi", "fitness", "height_cm",
                "device_id", "rhr_bpm_target", "ln_rmssd_ms",
                "pooling_capacity_ml", "blood_volume_expected_ml",
                "blood_volume_deficit_ml", "comorbidities", "severity",
                "cohort_frame", "demographics_matched_to", "subject_seed"]
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(cols)
            for s in self.subjects:
                meta = s.to_metadata()
                w.writerow([
                    s.subject_id, s.cohort_id, s.condition,
                    "*".join(s.phenotypes), meta["demographics"]["age_years"],
                    s.sex, meta["demographics"]["bmi"], s.fitness,
                    meta["demographics"]["height_cm"], s.device_id,
                    meta["population_traits"]["rhr_bpm_target"],
                    meta["population_traits"]["ln_rmssd_ms"],
                    meta["population_traits"]["pooling_capacity_ml"],
                    meta["population_traits"]["blood_volume_expected_ml"],
                    meta["population_traits"]["blood_volume_deficit_ml"],
                    "*".join(s.comorbidities), s.severity, s.cohort_frame,
                    s.demographics_matched_to, s.subject_seed])
        return path
