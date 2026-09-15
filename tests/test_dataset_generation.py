"""Tests for the OCPE dataset generation infrastructure (G-P0-07, W2-F).

Coverage (build item 9):
  * record schema validation (structural hook)
  * provenance validation (git rev / KB sha / registry / evidence blocks)
  * determinism: same seeds -> byte-identical records (npz/yaml/json/csv)
  * provenance gate fail-closed: experimental phenotype rejected in
    canonical mode; experimental mode requires opt-in; neuropathic POTS
    dataset-level exclusion (G-P0-03) enforced
  * latent-boundary guard end-to-end: no latent variable leaks into
    sensor channels or derived metrics (rule 3)
  * manifest completeness
  * orthostatic metric semantics identical to the frozen evaluator

Test runtime strategy: fast paths (cohort/protocol/schema/gate logic,
multiday slow-layer records) run in seconds; ONE small ODE bench build
(two subjects, 60 s protocol) exercises the full sensor + orthostatic
pipeline including byte-identical determinism (~2 min on 2 cores).

The governed-KB fixture is a minimal synthetic KB (tiny diseases /
mathematical-models / polar_h10-like wearable files) with AI-agent
reviews recorded via the public tools.review_tracker API; the gate's
human-L3 warning path is exercised but never a silent pass.
"""

import json
import os
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))

from dataset.cohort import CohortSampler, load_cohort_config, stable_seed
from dataset.protocols import parse_protocol
from dataset.runner import DatasetBuilder, DATASET_EXCLUDED_PHENOTYPES
from dataset import schema as recschema
from dataset.manifest import build_manifest, write_manifest
from dataset.rr_source import generate_rr_series, hrv_module_status
from validation.evaluator import compute_orthostatic_metrics
from validation.provenance_gate import (
    ExperimentalModeOptInRequired,
    ExperimentalPerturbationError,
    ProvenanceGateError,
    preflight_dataset_build,
)

# ---------------------------------------------------------------------------
# Minimal governed KB fixture
# ---------------------------------------------------------------------------

_REAL_KB = os.path.join(REPO_ROOT, "knowledge_base")


def _write(path: Path, doc: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, sort_keys=False)


def make_governed_kb(root: Path) -> Path:
    """Minimal gate-clean KB: reuses the repo's mathematical-models and
    polar_h10 wearable files (already governed), adds a tiny disease file
    with canonical + experimental phenotypes, and records AI-agent reviews.
    """
    from review_tracker import record_review

    kb = root / "kb"
    # equations: reuse the real model parameter file (canonical source).
    _write(kb / "equations" / "mathematical_models.yaml", yaml.safe_load(
        open(os.path.join(_REAL_KB, "equations", "mathematical_models.yaml"))))
    _write(kb / "diseases" / "test_conditions.yaml", {
        "version": "1.0",
        "disease": {
            "id": "test_conditions", "name": "Test conditions",
            "canonical_status": "canonical", "evidence_tier": "A",
            "provenance": {"source_claim_ids": ["EVD-TEST-000"]},
            "phenotypes": [
                {"id": "mild_hypovolemia", "name": "Mild hypovolemia (test)",
                 "canonical_status": "canonical", "evidence_tier": "A",
                 "provenance": {"source_claim_ids": ["EVD-TEST-001"]},
                 "parameters_perturbed": [
                     {"symbol": "TotalVol", "normal_value": 4500.0,
                      "perturbed_value": 4100.0, "units": "ml",
                      "evidence_tier": "B", "canonical_status": "canonical",
                      "provenance": {"source_claim_ids": ["EVD-TEST-002"]}}]},
                {"id": "experimental_tierD_condition", "name": "Tier-D (test)",
                 "canonical_status": "experimental", "evidence_tier": "D",
                 "provenance": {"source_claim_ids": ["EVD-TEST-003"]},
                 "parameters_perturbed": [
                     {"symbol": "kR", "normal_value": 25.0,
                      "perturbed_value": 30.0, "units": "1",
                      "evidence_tier": "D", "canonical_status": "experimental",
                      "provenance": {"source_claim_ids": ["EVD-TEST-004"]}}]},
                {"id": "neuropathic_pots", "name": "Neuropathic-like (test)",
                 "canonical_status": "canonical", "evidence_tier": "A",
                 "provenance": {"source_claim_ids": ["EVD-TEST-005"]},
                 "parameters_perturbed": [
                     {"symbol": "kR", "normal_value": 25.0,
                      "perturbed_value": 20.0, "units": "1",
                      "evidence_tier": "A", "canonical_status": "canonical",
                      "provenance": {"source_claim_ids": ["EVD-TEST-006"]}}]},
            ]}})
    # wearable: reuse the governed polar_h10 profile verbatim.
    _write(kb / "wearables" / "polar_h10.yaml", yaml.safe_load(
        open(os.path.join(_REAL_KB, "wearables", "polar_h10.yaml"))))
    for path in sorted(kb.rglob("*.yaml")):
        record_review(path, kind="ai_agent", name="W2-F test fixture",
                      scope=["test_fixture"],
                      comments="synthetic test fixture; human L3 not applicable")
    return kb


@pytest.fixture(scope="module")
def governed_kb(tmp_path_factory):
    return make_governed_kb(tmp_path_factory.mktemp("govkb"))


# ---------------------------------------------------------------------------
# Fast configs
# ---------------------------------------------------------------------------

def _multiday_config(seed=777):
    """Fast config: no ODE run (slow-layer multiday record)."""
    return {
        "dataset_name": "test_multiday", "dataset_seed": seed,
        "generation_mode": "canonical",
        "cohorts": [{"cohort_id": "healthy", "condition": "healthy",
                     "n_subjects": 1,
                     "orthostatic_axis": {"enabled": False}}],
        "protocols": [{"protocol_id": "day1", "family": "multiday",
                       "days": 1, "step_s": 120.0}],
        "sensors": [{"sensor_id": "polar_h10", "channels": ["rr"]}],
    }


def _bench_config(seed=4242):
    """One-subject ODE bench build (minimal but end-to-end)."""
    return {
        "dataset_name": "test_bench", "dataset_seed": seed,
        "generation_mode": "canonical",
        "cohorts": [{"cohort_id": "healthy", "condition": "healthy",
                     "n_subjects": 1,
                     "age": {"dist": "uniform", "min": 25, "max": 30},
                     "orthostatic_axis": {"enabled": True,
                                          "quantiles": [0.5],
                                          "reference_protocol": "hut_60_70_10min"}}],
        "protocols": [{"protocol_id": "hut60_mini", "family": "tilt_first",
                       "phases": [{"name": "supine_baseline", "duration_s": 40},
                                  {"name": "head_up_tilt", "angle_degrees": 60,
                                   "duration_s": 30},
                                  {"name": "supine_recovery", "duration_s": 20}],
                       "covariates": {"fasting": True,
                                      "time_of_day": "morning"}}],
        "sensors": [{"sensor_id": "polar_h10", "channels": ["rr"]}],
        "engine": {"dt": 0.02},
    }


# ---------------------------------------------------------------------------
# Cohort sampler
# ---------------------------------------------------------------------------

class TestCohortSampler:
    def test_population_distributions(self):
        cfg = {"cohorts": [
            {"cohort_id": "h", "condition": "healthy", "n_subjects": 40,
             "orthostatic_axis": {"enabled": False}}]}
        subs = CohortSampler(cfg, 1).sample()
        rhrs = np.array([s.rhr_bpm for s in subs])
        assert abs(rhrs.mean() - 65.5 - 1.5) < 4.0  # +3 female shift at 50/50
        assert 3.0 < rhrs.std() < 14.0
        assert all(18 <= s.age <= 75 for s in subs)

    def test_pots_demographic_recipe(self):
        cfg = {"cohorts": [
            {"cohort_id": "p", "condition": "pots", "n_subjects": 60,
             "phenotypes": ["hypovolemic_pots"],
             "orthostatic_axis": {"enabled": False}}]}
        subs = CohortSampler(cfg, 2).sample()
        ff = np.mean([s.sex == "female" for s in subs])
        assert 0.70 <= ff <= 1.0  # evidence range 0.85-0.94 (n=60 sampling)
        deficits = [s.blood_volume_deficit_ml for s in subs]
        assert all(d is not None and d >= 100.0 for d in deficits)
        assert 350 < np.mean(deficits) < 1050  # Raj 689+/-270 (n=60)

    def test_rhr_rmssd_coupling(self):
        cfg = {"cohorts": [
            {"cohort_id": "h", "condition": "healthy", "n_subjects": 200,
             "age": {"dist": "uniform", "min": 25, "max": 35},
             "orthostatic_axis": {"enabled": False}}]}
        subs = CohortSampler(cfg, 3).sample()
        r = np.corrcoef([s.rhr_bpm for s in subs],
                        [s.ln_rmssd_ms for s in subs])[0, 1]
        assert -0.85 < r < -0.35  # evidence band |r| ~ 0.5-0.7 (E1)

    def test_deterministic_sampling(self):
        cfg = {"cohorts": [{"cohort_id": "h", "condition": "healthy",
                            "n_subjects": 5}]}
        a = CohortSampler(cfg, 9).sample()
        b = CohortSampler(cfg, 9).sample()
        assert [s.to_metadata() for s in a] == [s.to_metadata() for s in b]

    def test_seed_hierarchy_unique(self):
        cfg = {"cohorts": [{"cohort_id": "h", "condition": "healthy",
                            "n_subjects": 4}]}
        subs = CohortSampler(cfg, 5).sample()
        seeds = [s.subject_seed for s in subs]
        assert len(set(seeds)) == len(seeds)
        assert stable_seed(5, "h-001") != stable_seed(6, "h-001")

    def test_yaml_config_driven(self, tmp_path):
        cfg = {"cohorts": [{"cohort_id": "h", "condition": "healthy",
                            "n_subjects": 2}]}
        p = tmp_path / "cohort.yaml"
        p.write_text(yaml.safe_dump(cfg))
        loaded = load_cohort_config(str(p))
        assert loaded["cohorts"][0]["n_subjects"] == 2


# ---------------------------------------------------------------------------
# Protocol scheduler
# ---------------------------------------------------------------------------

class TestProtocols:
    def test_tilt_first_compilation(self):
        spec = parse_protocol({
            "protocol_id": "p1", "family": "tilt_first",
            "phases": [{"name": "supine_baseline", "duration_s": 150},
                       {"name": "head_up_tilt", "angle_degrees": 65,
                        "duration_s": 600},
                       {"name": "supine_recovery", "duration_s": 120}]})
        tp = spec.to_engine_tilt_params()
        assert tp["tup"] == 150.0 and tp["tend"] == 750.0
        assert tp["tsim_end"] == 870.0  # recovery included (additive key)
        assert tp["angle"] == 65.0
        assert spec.method == "head_up_tilt"
        cov = spec.mandatory_covariates()
        assert cov["upright_duration_s"] == 600.0
        assert cov["supine_rest_duration_s"] == 150.0

    def test_angle_band_enforced(self):
        with pytest.raises(ValueError, match="canonical"):
            parse_protocol({
                "protocol_id": "bad", "family": "tilt_first",
                "phases": [{"name": "supine_baseline", "duration_s": 10},
                           {"name": "head_up_tilt", "angle_degrees": 45,
                            "duration_s": 60}]})

    def test_event_scheduling_and_flags(self):
        spec = parse_protocol({
            "protocol_id": "p2", "family": "tilt_first",
            "phases": [{"name": "supine_baseline", "duration_s": 100},
                       {"name": "head_up_tilt", "angle_degrees": 60,
                        "duration_s": 100}],
            "events": [{"type": "meal", "at_s": 20},
                       {"type": "exercise", "at_s": 30, "duration_s": 60,
                        "intensity": 0.5}]})
        assert "exercise_pem_channel_inactive_in_ode_runs" in spec.honesty_flags()
        assert "short_protocol_sustained_window_proxy" in spec.honesty_flags()
        with pytest.raises(ValueError, match="outside protocol horizon"):
            parse_protocol({
                "protocol_id": "p3", "family": "tilt_first",
                "phases": [{"name": "supine_baseline", "duration_s": 100}],
                "events": [{"type": "meal", "at_s": 5000}]})


# ---------------------------------------------------------------------------
# Gate fail-closed behavior
# ---------------------------------------------------------------------------

class TestGateFailClosed:
    def test_experimental_phenotype_rejected_canonical(self, governed_kb):
        cfg = _multiday_config()
        cfg["cohorts"][0]["phenotypes"] = ["experimental_tierD_condition"]
        b = DatasetBuilder(cfg, kb_dir=str(governed_kb),
                           output_dir="/tmp/unused")
        b.sample_cohort()
        with pytest.raises(ProvenanceGateError):
            b.preflight()

    def test_experimental_mode_requires_optin(self, governed_kb):
        with pytest.raises(ExperimentalModeOptInRequired):
            preflight_dataset_build(str(governed_kb), mode="experimental")

    def test_experimental_mode_with_optin(self, governed_kb):
        cfg = _multiday_config()
        cfg["generation_mode"] = "experimental"
        cfg["allow_experimental"] = True
        cfg["cohorts"][0]["phenotypes"] = ["experimental_tierD_condition"]
        b = DatasetBuilder(cfg, kb_dir=str(governed_kb),
                           output_dir="/tmp/unused")
        b.sample_cohort()
        report = b.preflight()
        assert report.ok

    def test_neuropathic_dataset_exclusion(self, governed_kb):
        """G-P0-03: neuropathic POTS refused at dataset level in canonical
        mode even though the (fixture) KB block is canonical-eligible."""
        assert "neuropathic_pots" in DATASET_EXCLUDED_PHENOTYPES
        cfg = _multiday_config()
        cfg["cohorts"][0]["phenotypes"] = ["neuropathic_pots"]
        b = DatasetBuilder(cfg, kb_dir=str(governed_kb),
                           output_dir="/tmp/unused")
        b.sample_cohort()
        with pytest.raises(ExperimentalPerturbationError,
                           match="G-P0-03"):
            b.preflight()

    def test_hash_tamper_refused(self, tmp_path):
        """Modifying a KB file after review must fail the gate (STALE)."""
        kb = make_governed_kb(tmp_path)
        target = kb / "diseases" / "test_conditions.yaml"
        with open(target, "a", encoding="utf-8") as f:
            f.write("\n# tampered after review\n")
        with pytest.raises(ProvenanceGateError):
            preflight_dataset_build(str(kb), mode="canonical"
                                    ).raise_if_failed()


# ---------------------------------------------------------------------------
# Schema / provenance / scientific-contract hooks (fast, synthetic records)
# ---------------------------------------------------------------------------

def _minimal_record(**overrides):
    rec = {
        "record_id": "00000000-0000-5000-8000-000000000000",
        "subject_id": "h-001", "protocol_id": "p1",
        "physiological_state": {"condition": "healthy"},
        "events": [],
        "latent_parameters": {"variables": ["pau_mmHg"],
                              "reference": "ground_truth.npz"},
        "observable_parameters": {"channels": [
            {"name": "polar_h10__rr__rr_intervals_ms"}]},
        "sensor_configuration": {"devices": []},
        "derived_metrics": {"metrics": {}},
        "evidence": {"population_constants": [], "perturbations": []},
        "uncertainty": {},
        "canonical_status": "canonical",
        "honesty": {cat: [] for cat in recschema.HONESTY_CATEGORIES},
        "honesty_flags": [],
        "seed": 1,
        "ocpe_commit": "a" * 40,
        "kb_version": "b" * 64,
        "registry_version": {"version": "1.0", "sha256": "c" * 64},
        "model_version": "mathematical_models-1.0",
        "schema_version": recschema.SCHEMA_VERSION,
        "generation_timestamp": "2026-01-01T00:00:00+00:00",
    }
    rec.update(overrides)
    return rec


class TestSchemaHooks:
    def test_valid_record_passes(self):
        rec = _minimal_record()
        assert recschema.validate_record_schema(rec) == []
        assert recschema.validate_record_provenance(rec) == []
        assert recschema.validate_scientific_contract(rec) == []

    def test_missing_fields(self):
        rec = _minimal_record()
        del rec["record_id"], rec["honesty"]
        errors = recschema.validate_record_schema(rec)
        assert any("record_id" in e for e in errors)
        assert any("honesty" in e for e in errors)

    def test_missing_honesty_category(self):
        rec = _minimal_record()
        del rec["honesty"]["latent_only_variables"]
        assert any("latent_only_variables" in e
                   for e in recschema.validate_record_schema(rec))

    def test_provenance_errors(self):
        rec = _minimal_record(ocpe_commit="unknown", kb_version="short",
                              registry_version={})
        errors = recschema.validate_record_provenance(rec)
        assert len(errors) >= 3

    def test_latent_leak_rejected(self):
        for bad in ("blood_pressure", "stroke_volume", "systolic_bp_trace",
                    "mean_stroke_volume_trace", "hydration",
                    "cerebral_perfusion"):
            rec = _minimal_record()
            rec["observable_parameters"]["channels"] = [{"name": bad}]
            errors = recschema.validate_scientific_contract(rec)
            assert errors, f"latent channel '{bad}' not rejected"

    def test_cgm_exception_allowed(self):
        rec = _minimal_record()
        rec["observable_parameters"]["channels"] = [{"name": "cgm_glucose"}]
        assert recschema.validate_scientific_contract(rec) == []

    def test_honesty_flag_union_enforced(self):
        rec = _minimal_record()
        rec["honesty"]["extrapolated_features"] = ["extrapolated_E0"]
        rec["honesty_flags"] = []
        assert recschema.validate_scientific_contract(rec)
        rec["honesty_flags"] = ["extrapolated_E0"]
        assert recschema.validate_scientific_contract(rec) == []

    def test_canonical_record_no_experimental(self):
        rec = _minimal_record()
        rec["honesty"]["experimental_features"] = ["x:kR"]
        rec["honesty_flags"] = ["x:kR"]
        assert any("experimental" in e
                   for e in recschema.validate_scientific_contract(rec))

    def test_orthostatic_semantics_declared(self):
        rec = _minimal_record()
        rec["derived_metrics"]["metrics"] = {"orthostatic": {
            "semantics": {"source": None, "sustained_delta_HR": None}}}
        assert recschema.validate_scientific_contract(rec)


# ---------------------------------------------------------------------------
# RR source adapter
# ---------------------------------------------------------------------------

class TestRRSource:
    def _hrv_inputs(self, n=600, hr=65.0):
        t = np.arange(n, dtype=float)
        return {"time_s": t, "mean_hr_bpm": np.full(n, hr),
                "vagal_drive": np.full(n, 0.5),
                "sympathetic_drive": np.full(n, 0.3),
                "respiration_rate_brpm": np.full(n, 15.0),
                "sleep_stage_code": np.zeros(n, dtype=int),
                "sleep_stage_names": ["awake"] * n, "source": "test",
                "honesty_flags": []}

    def test_aligned_arrays(self):
        rr = generate_rr_series(self._hrv_inputs(), seed=1)
        n = len(rr["beat_times_s"])
        assert len(rr["rr_intervals_ms"]) == n
        assert len(rr["beat_types"]) == n
        assert np.all(np.diff(rr["beat_times_s"]) > 0)

    def test_fallback_flagged(self):
        if hrv_module_status()["w2e_hrv_module_available"]:
            pytest.skip("W2-E module present; fallback not active")
        rr = generate_rr_series(self._hrv_inputs(), seed=1)
        assert rr["provenance"]["source"] == "fallback_mean_hr_phase_integration"
        assert "rr_fallback_no_structured_hrv" in rr["provenance"]["honesty_flags"]

    def test_deterministic(self):
        a = generate_rr_series(self._hrv_inputs(), seed=7)
        b = generate_rr_series(self._hrv_inputs(), seed=7)
        assert np.array_equal(a["beat_times_s"], b["beat_times_s"])
        assert np.array_equal(a["rr_intervals_ms"], b["rr_intervals_ms"])

    def test_mean_rr_matches_hr(self):
        rr = generate_rr_series(self._hrv_inputs(hr=60.0), seed=1)
        assert abs(np.mean(rr["rr_intervals_ms"]) - 1000.0) < 5.0


# ---------------------------------------------------------------------------
# End-to-end builds (multiday = fast; bench ODE = slow, module-scoped)
# ---------------------------------------------------------------------------

class TestMultidayBuild:
    @pytest.fixture(scope="class")
    def built(self, governed_kb, tmp_path_factory):
        out = tmp_path_factory.mktemp("ds_md")
        b = DatasetBuilder(_multiday_config(), kb_dir=str(governed_kb),
                           output_dir=str(out))
        return b.build(), out

    def test_record_files_exist(self, built):
        res, out = built
        rec_dir = Path(out) / "subjects" / "healthy-001" / "day1"
        for fname in ("ground_truth.npz", "sensors.npz", "derived.json",
                      "record.yaml"):
            assert (rec_dir / fname).is_file(), fname
        assert (Path(out) / "manifest.yaml").is_file()
        assert (Path(out) / "manifest_summary.txt").is_file()
        assert (Path(out) / "cohort.csv").is_file()

    def test_record_passes_hooks(self, built):
        res, out = built
        rec = yaml.safe_load(open(
            Path(out) / "subjects" / "healthy-001" / "day1" / "record.yaml"))
        assert recschema.validate_record_schema(rec) == []
        assert recschema.validate_record_provenance(rec) == []
        assert recschema.validate_scientific_contract(rec) == []

    def test_no_latent_in_sensor_npz(self, built):
        """Boundary guard end-to-end: sensor channel names in sensors.npz
        carry no latent variable names (rule 3)."""
        res, out = built
        npz = np.load(Path(out) / "subjects" / "healthy-001" / "day1"
                      / "sensors.npz")
        from sensor_models.boundary import LATENT_FORBIDDEN_NAMES
        for name in npz.files:
            low = name.lower()
            for latent in LATENT_FORBIDDEN_NAMES:
                assert low != latent
                assert not low.startswith(latent + "_")
                assert not low.endswith("_" + latent)
                assert ("_" + latent + "_") not in low

    def test_ground_truth_has_latents(self, built):
        res, out = built
        npz = np.load(Path(out) / "subjects" / "healthy-001" / "day1"
                      / "ground_truth.npz")
        assert "time_s" in npz.files
        assert "mean_hr_bpm" in npz.files

    def test_manifest_completeness(self, built):
        res, out = built
        m = yaml.safe_load(open(Path(out) / "manifest.yaml"))
        for key in ("dataset_version", "ocpe_commit", "kb_version",
                    "registry_version", "model_version", "seeds",
                    "cohort_composition", "protocols", "evidence_tiers_present",
                    "canonical_status", "validation_status", "provenance_gate",
                    "generation_timestamp", "hrv_source"):
            assert key in m, key
        assert m["canonical_status"] == "canonical"
        assert m["n_records"] == 1
        assert m["provenance_gate"]["ok"] is True
        assert m["validation_status"]["all_records_passed"] is True

    def test_determinism_byte_identical(self, governed_kb, tmp_path_factory):
        """Same seeds -> byte-identical outputs across two full builds."""
        outs = []
        for i in range(2):
            out = tmp_path_factory.mktemp(f"ds_det{i}")
            b = DatasetBuilder(_multiday_config(), kb_dir=str(governed_kb),
                               output_dir=str(out))
            b.build()
            outs.append(Path(out))
        rel_files = sorted(
            str(p.relative_to(outs[0])) for p in outs[0].rglob("*")
            if p.is_file())
        assert rel_files, "no outputs written"
        # manifest.yaml embeds kb_dir-independent content only; compare all
        for rel in rel_files:
            a = (outs[0] / rel).read_bytes()
            b_ = (outs[1] / rel).read_bytes()
            assert a == b_, f"non-deterministic output: {rel}"


class TestBenchBuild:
    """Full ODE bench build: sensors + orthostatic semantics end-to-end."""

    @pytest.fixture(scope="class")
    def built(self, governed_kb, tmp_path_factory):
        out = tmp_path_factory.mktemp("ds_bench")
        b = DatasetBuilder(_bench_config(), kb_dir=str(governed_kb),
                           output_dir=str(out))
        return b.build(), out

    def test_bench_record_valid(self, built):
        res, out = built
        rec_dir = Path(out) / "subjects" / "healthy-001" / "hut60_mini"
        rec = yaml.safe_load(open(rec_dir / "record.yaml"))
        assert recschema.validate_record_schema(rec) == []
        assert recschema.validate_record_provenance(rec) == []
        assert recschema.validate_scientific_contract(rec) == []
        assert rec["canonical_status"] == "canonical"

    def test_orthostatic_semantics_match_evaluator(self, built):
        """derived.json orthostatic metrics must equal a direct call to the
        frozen evaluator on the same ground-truth trajectory."""
        res, out = built
        rec_dir = Path(out) / "subjects" / "healthy-001" / "hut60_mini"
        derived = json.load(open(rec_dir / "derived.json"))
        gt = np.load(rec_dir / "ground_truth.npz")
        om = compute_orthostatic_metrics(
            time=gt["time_s"], hr_bpm=gt["mean_hr_bpm"], onset_s=40.0,
            tilt_duration_s=30.0, baseline_window_s=30.0)
        got = derived["orthostatic"]
        assert got["sustained_window_kind"] == om["sustained_window_kind"]
        assert got["baseline_hr_bpm"] == pytest.approx(om["baseline_hr_bpm"])
        if not np.isnan(om["sustained_delta_HR_bpm"]):
            assert got["sustained_delta_HR_bpm"] == pytest.approx(
                om["sustained_delta_HR_bpm"])
        assert got["semantics"]["source"].startswith(
            "validation/evaluator.py")

    def test_short_protocol_flagged(self, built):
        res, out = built
        rec = yaml.safe_load(open(
            Path(out) / "subjects" / "healthy-001" / "hut60_mini"
            / "record.yaml"))
        assert "short_protocol_sustained_window_proxy" in rec["honesty_flags"]

    def test_sensor_rr_channel_close_to_truth(self, built):
        """Chest-strap RR telemetry tracks the TRUE beat RR series within
        the KB profile's bias+LoA bounds (Schaffarczyk 2022, EVD-SENS-002),
        on the aligned beat grid stored as ground truth."""
        res, out = built
        rec_dir = Path(out) / "subjects" / "healthy-001" / "hut60_mini"
        sensors = np.load(rec_dir / "sensors.npz")
        gt = np.load(rec_dir / "ground_truth.npz")
        meas = sensors["polar_h10__rr__rr_intervals_ms"]
        true = gt["rr_intervals_ms"]
        assert len(meas) == len(true)
        good = ~np.isnan(meas)
        assert good.mean() > 0.5  # on-device strap: mostly usable
        err = np.abs(meas[good] - true[good])
        assert np.median(err) < 15.0      # small bias + quantization
        assert np.percentile(err, 95) < 60.0  # LoA-scale noise, not drift

    def test_bench_determinism(self, governed_kb, tmp_path_factory):
        outs = []
        for i in range(2):
            out = tmp_path_factory.mktemp(f"ds_bdet{i}")
            b = DatasetBuilder(_bench_config(), kb_dir=str(governed_kb),
                               output_dir=str(out))
            b.build()
            outs.append(Path(out))
        for rel in ("subjects/healthy-001/hut60_mini/ground_truth.npz",
                    "subjects/healthy-001/hut60_mini/sensors.npz",
                    "subjects/healthy-001/hut60_mini/derived.json",
                    "subjects/healthy-001/hut60_mini/record.yaml",
                    "cohort.csv"):
            assert (outs[0] / rel).read_bytes() == (outs[1] / rel).read_bytes(), rel
