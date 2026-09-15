"""Dataset manifest (G-P0-07 build item 5).

Machine-readable ``manifest.yaml`` + human-readable ``manifest_summary.txt``
at the dataset root, carrying: dataset version, ocpe_commit, kb_version,
registry_version, model_version, seeds, cohort composition, protocols,
evidence tiers, canonical/experimental status, validation status, provenance
gate outcome, and the anti-laundering disclosure (rule 5: between-group
separation must come from mechanism only and stay inside evidence-honest
bands).
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

import numpy as np
import yaml

from dataset import schema as recschema
from dataset.cohort import metadata_negative_control
from dataset.provenance import (
    git_revision,
    model_version,
    registry_version,
)
from dataset.rr_source import hrv_module_status


def _cohort_composition(subjects) -> List[Dict[str, Any]]:
    comp: Dict[str, Dict[str, Any]] = {}
    for s in subjects:
        c = comp.setdefault(s.cohort_id, {
            "cohort_id": s.cohort_id, "condition": s.condition,
            "phenotypes": sorted({p for p in s.phenotypes} ),
            "n_subjects": 0, "n_female": 0, "age_min": None, "age_max": None,
            "bmi_min": None, "bmi_max": None, "devices": set(),
            "demographics_matched_to": None,
            "cohort_frame": s.cohort_frame,
        })
        c["n_subjects"] += 1
        c["n_female"] += 1 if s.sex == "female" else 0
        c["age_min"] = s.age if c["age_min"] is None else min(c["age_min"], s.age)
        c["age_max"] = s.age if c["age_max"] is None else max(c["age_max"], s.age)
        c["bmi_min"] = s.bmi if c["bmi_min"] is None else min(c["bmi_min"], s.bmi)
        c["bmi_max"] = s.bmi if c["bmi_max"] is None else max(c["bmi_max"], s.bmi)
        if s.device_id:
            c["devices"].add(s.device_id)
        if s.demographics_matched_to:
            c["demographics_matched_to"] = s.demographics_matched_to
    out = []
    for c in comp.values():
        c["age_min"] = round(float(c["age_min"]), 1)
        c["age_max"] = round(float(c["age_max"]), 1)
        c["bmi_min"] = round(float(c["bmi_min"]), 1)
        c["bmi_max"] = round(float(c["bmi_max"]), 1)
        c["devices"] = sorted(c["devices"])
        c["female_fraction"] = round(c["n_female"] / max(1, c["n_subjects"]), 3)
        out.append(c)
    return sorted(out, key=lambda c: c["cohort_id"])


def _group_separation(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Realized between-condition overlap summary on the canonical sustained
    delta-HR (anti-laundering disclosure, rule 5).  Reports distributions,
    NOT a classifier: >0.95 AUC separation would be a release failure."""
    by_cond: Dict[str, List[float]] = {}
    for r in records:
        v = (r.get("derived_summary") or {}).get("sustained_delta_HR_bpm")
        if v is None:
            continue
        by_cond.setdefault(r["condition"], []).append(float(v))
    summary: Dict[str, Any] = {"metric": "sustained_delta_HR_bpm",
                               "groups": {}, "overlap_note": None}
    for cond, vals in sorted(by_cond.items()):
        arr = np.asarray(vals)
        summary["groups"][cond] = {
            "n": int(arr.size), "mean": round(float(arr.mean()), 2),
            "sd": round(float(arr.std(ddof=1)), 2) if arr.size > 1 else None,
            "min": round(float(arr.min()), 2), "max": round(float(arr.max()), 2),
        }
    conds = sorted(by_cond)
    if len(conds) >= 2:
        lo = max(min(v) for v in by_cond.values())
        hi = min(max(v) for v in by_cond.values())
        summary["overlap_note"] = (
            f"group ranges overlap on [{lo:.1f}, {hi:.1f}] bpm" if lo <= hi else
            "group ranges do not overlap on the realized sustained delta-HR; "
            "verify separation is mechanism-derived and within evidence bands "
            "(rule 5); small-n pilot note: overlap assessment is underpowered")
    return summary


def build_manifest(builder, records: List[Dict[str, Any]],
                   preflight_report) -> Dict[str, Any]:
    """Assemble the manifest dict (deterministic; normalized for YAML)."""
    evidence_tiers = sorted({
        p.get("evidence_tier") for s in builder.subjects for p in s.provenance
        if p.get("evidence_tier")})
    single_source = sorted({
        f for r in records for f in r.get("honesty_flags", [])
        if "single_source" in f})
    manifest = {
        "dataset_name": builder.name,
        "dataset_version": builder.version,
        "schema_version": recschema.SCHEMA_VERSION,
        "spec_reference": ("docs/evidence_package/OCPE_DATASET_SPECIFICATION.md "
                           "v0.1; master prompt sections 7/18/21"),
        "generation_mode": builder.mode,
        "canonical_status": ("canonical" if builder.mode == "canonical"
                             else "experimental"),
        "ocpe_commit": git_revision(),
        "kb_dir": builder.kb_dir,
        "kb_version": builder.kb_version(),
        "kb_version_semantics": (
            "sha256 over consumed KB data-file contents (review sidecars "
            "excluded: volatile UUID/wall-clock fields; governance freshness "
            "is gate-enforced at build time) + externally consumed wearable/"
            "artifact files hashed under external: labels (review F5/F13)"),
        "registry_version": registry_version(),
        "model_version": model_version(),
        "generation_timestamp": builder.generation_timestamp,
        "seeds": {
            "dataset_seed": int(builder.dataset_seed),
            "hierarchy": "dataset_seed -> subject_seed -> channel seeds (SHA-256 mixing)",
            "subject_seeds": {s.subject_id: int(s.subject_seed)
                              for s in builder.subjects},
        },
        "hrv_source": hrv_module_status(),
        "cohort_composition": _cohort_composition(builder.subjects),
        "protocols": [p.to_record() for p in builder.protocols],
        "sensors": builder.sensor_configs,
        "evidence_tiers_present": evidence_tiers,
        "provenance_gate": {
            "mode": builder.mode,
            "ok": bool(preflight_report.ok),
            "n_warnings": len(preflight_report.warnings),
            "human_l3_review": ("ABSENT (AI-agent/validator reviews only; "
                                "surfaced as warnings, never silent pass)"),
            "warnings": list(preflight_report.warnings),
        },
        "records": records,
        "n_records": len(records),
        "validation_status": {
            "record_checks": ("schema + provenance + scientific-contract hooks "
                              "passed for every record (fail-closed build CI)"),
            "all_records_passed": True,
            "healthy_reference_comparisons": (
                "per-record reference_comparison blocks in derived.json "
                "(single-run; cohort-level comparison requires the full "
                "healthy distribution)"),
        },
        "anti_laundering": {
            "rule": ("between-condition separation comes from mechanism only "
                     "(volume deficit, pooling axis, baroreflex); no label "
                     "conditioning of signals; >0.95 AUC = release failure"),
            "group_separation": _group_separation(records),
            "metadata_negative_control": metadata_negative_control(
                builder.subjects),
            "metadata_negative_control_note": (
                "sex/age/BMI/fitness/device metadata-only classifier must "
                "sit at AUC <= 0.5+epsilon (review F1); enforced upstream "
                "by matched/stratified cohort sampling, never by label "
                "manipulation. Small-n note: per-feature AUC at n<=3/group "
                "is exactly 0.5 only under pairwise-matched sampling."),
            "single_source_flags": single_source,
        },
        "sensor_governance_audit": (builder._sensor_audit or {}),
        "kb_closure_note": builder.config.get("kb_closure_note"),
    }
    return recschema.normalize(manifest)


def human_summary(manifest: Dict[str, Any]) -> str:
    """Human-readable one-page summary of the manifest."""
    lines = []
    a = lines.append
    a(f"OCPE dataset '{manifest['dataset_name']}' v{manifest['dataset_version']} "
      f"({manifest['canonical_status']}, mode={manifest['generation_mode']})")
    a(f"  records: {manifest['n_records']}  "
      f"schema: {manifest['schema_version']}  "
      f"built: {manifest['generation_timestamp']}")
    a(f"  ocpe_commit: {manifest['ocpe_commit']}")
    a(f"  kb_version (bundle sha256): {manifest['kb_version'][:16]}...")
    rv = manifest.get("registry_version", {})
    a(f"  registry_version: {rv.get('version')} ({str(rv.get('sha256'))[:16]}...)")
    a(f"  model_version: {manifest['model_version']}")
    a(f"  hrv_source: {manifest['hrv_source']['active_source']}")
    a(f"  provenance gate: ok={manifest['provenance_gate']['ok']} "
      f"warnings={manifest['provenance_gate']['n_warnings']} "
      f"(human L3 review absent - pending)")
    a("  cohorts:")
    for c in manifest["cohort_composition"]:
        a(f"    - {c['cohort_id']}: {c['condition']} n={c['n_subjects']} "
          f"female={c['female_fraction']:.2f} age {c['age_min']}-{c['age_max']} "
          f"phenotypes={c['phenotypes']}")
    a("  protocols:")
    for p in manifest["protocols"]:
        a(f"    - {p['protocol_id']} ({p['family']}, {p['total_duration_s']:.0f} s)")
    gs = manifest["anti_laundering"]["group_separation"]
    a(f"  group separation ({gs['metric']}):")
    for cond, g in gs.get("groups", {}).items():
        a(f"    - {cond}: n={g['n']} mean={g['mean']} sd={g['sd']} "
          f"range=[{g['min']}, {g['max']}]")
    if gs.get("overlap_note"):
        a(f"    {gs['overlap_note']}")
    if manifest.get("kb_closure_note"):
        a(f"  kb closure: {manifest['kb_closure_note']}")
    return "\n".join(lines) + "\n"


def write_manifest(manifest: Dict[str, Any], output_dir: str) -> str:
    """Write manifest.yaml + manifest_summary.txt at the dataset root."""
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "manifest.yaml"), "w", encoding="utf-8") as f:
        yaml.safe_dump(recschema.normalize(manifest), f, sort_keys=True,
                       default_flow_style=False, width=100)
    with open(os.path.join(output_dir, "manifest_summary.txt"), "w",
              encoding="utf-8") as f:
        f.write(human_summary(manifest))
    return os.path.join(output_dir, "manifest.yaml")
