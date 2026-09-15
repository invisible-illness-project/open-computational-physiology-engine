#!/usr/bin/env python3
"""Generate the OCPE pilot dataset (G-P0-07 build item 8).

Pilot design (mechanism-only separation, rule 4/5):

  * 3 healthy subjects spanning the healthy orthostatic axis via
    tail-preserving sampling from the FROZEN healthy_reference.yaml
    (hut_60_70_10min entry): low-normal (q~0.15) / typical (q~0.50) /
    high-normal (q~0.90).  The quantile is mapped onto the mechanistic
    venous-pooling axis (VMvl, 500-1000 mL); the realized response emerges
    from the ODE -- this is NOT a label hack.
  * 3 hypovolemic-POTS-like subjects (CANONICAL phenotype): same pooling
    axis (random quantiles) + a blood-volume deficit resampled from the
    Raj 2005 distribution (689+/-270 mL, EVD-POTS-004; CONTRADICTION
    Target 3) -- never the KB point extreme.  Mild deficits + low pooling
    overlap the healthy high-normal tail by construction.
  * Matched protocols (identical tilt-first bench protocol for every
    subject).
  * DEMOGRAPHIC MATCHING (adversarial review F1, release-blocking): the
    POTS cohort copies the healthy cohort's demographic rows pairwise
    (``match_demographics``) and the healthy cohort uses exact-count
    stratified sex sampling -- a metadata-only classifier (sex/age/BMI/
    fitness/device) sits at AUC 0.5 BY CONSTRUCTION.  The POTS cohort
    intentionally does NOT use the epidemiological POTS sex/age recipe
    for this matched case-control pilot (documented trade-off).
  * REALISTIC NUISANCE VARIATION (review F2): BMI ~ truncated
    N(26, 4.5) on [17, 45] (NHANES-informed, PROVISIONAL E4), fitness
    spectrum (sedentary/average/athletic, provisional proportions) with a
    provisional RHR shift, sex-specific height sampling feeding a Nadler
    expected-blood-volume hook (between-person CV 0.06, provisional) so
    healthy TotalVol varies with body size.  Nuisance distributions are
    identical across groups.
  * Canonical mode: only the canonical chest-strap profile (polar_h10) is
    governance-clean today, so every subject is assigned polar_h10
    (group-matched by construction).  Per-subject device randomization
    across the 5 sensor profiles is implemented (cohort ``device`` spec)
    but the wrist/ring/band profiles lack upstream governance metadata /
    are experimental and are REFUSED in canonical mode (gate + dataset
    sensor audit); randomization activates once W1-D/W1-B governance
    lands.  Wrist/ring/band profiles require
    --mode experimental --allow-experimental.

The build is FAIL-CLOSED: the provenance gate preflight must pass before
any simulation runs.  The integration-branch KB currently has STALE /
ungoverned wearable files (wave-1 merge state); --kb-dir accepts any
gate-clean KB, and --kb-closure DIR builds a minimal verbatim-copy
closure with fresh AI-agent reviews (human-L3 pending; disclosed in the
manifest) so the pilot runs TODAY without editing the governed KB.

Runtime: ~1 min per subject on 2 cores (ODE bench protocol, dt=0.02).

Usage:
    python3 examples/generate_pilot_dataset.py \
        --kb-closure /tmp/ocpe_pilot_kb --output results/pilot_v1
    python3 examples/generate_pilot_dataset.py --kb-dir <governed-kb> ...
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataset.runner import DatasetBuilder
from dataset.kb_closure import CLOSURE_DISCLOSURE, prepare_kb_closure
from dataset.manifest import human_summary
from validation.provenance_gate import ProvenanceGateError

PILOT_CONFIG = {
    "dataset_name": "ocpe_pilot_v1",
    "dataset_version": "0.1.0",
    "dataset_seed": 20260601,
    "generation_mode": "canonical",
    "cohorts": [
        {"cohort_id": "healthy", "condition": "healthy", "n_subjects": 3,
         "age": {"dist": "uniform", "min": 20, "max": 45},
         # Exact-count stratified sex sampling (review F1): no binomial
         # 3/0 confound at n=3.
         "sex": {"female_fraction": 0.5, "enforce_exact": True},
         # Realistic nuisance sampling (review F2); PROVISIONAL E4
         # distributions, identical across groups.
         "bmi": {"dist": "nhanes_provisional"},
         "fitness": {"dist": "spectrum"},
         "height": {"dist": "sex_specific_population"},
         # Only canonical-governed device today; identical across groups.
         "device": "polar_h10",
         "orthostatic_axis": {"enabled": True,
                              "quantiles": [0.15, 0.50, 0.90],
                              "reference_protocol": "hut_60_70_10min"},
         "comorbidities": {"frame": "off"}},
        {"cohort_id": "pots_hypovolemic", "condition": "pots", "n_subjects": 3,
         "phenotypes": ["hypovolemic_pots"],
         # Case-control pairwise demographic matching (review F1): copies
         # sex/age/BMI/fitness/height/device rows from the healthy cohort;
         # the metadata negative control holds by construction.  The
         # epidemiological POTS sex/age recipe is deliberately NOT used in
         # this matched pilot (documented).
         "match_demographics": "healthy",
         "orthostatic_axis": {"enabled": True, "quantiles": "random",
                              "reference_protocol": "hut_60_70_10min"},
         "comorbidities": {"frame": "population"}},
    ],
    "protocols": [
        {"protocol_id": "hut60_bench_v1", "family": "tilt_first",
         "phases": [
             {"name": "supine_baseline", "duration_s": 150},
             {"name": "head_up_tilt", "angle_degrees": 60, "duration_s": 100},
             {"name": "supine_recovery", "duration_s": 60}],
         "covariates": {"fasting": True, "time_of_day": "morning",
                        "height_cm": 25.0}},
    ],
    "sensors": [{"sensor_id": "polar_h10", "regime": "on_device",
                 "channels": ["rr"]}],
    "engine": {"dt": 0.02, "hrv_noise": 0.02},
}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--kb-dir", default=None,
                    help="governed KB directory (default: repo knowledge_base)")
    ap.add_argument("--kb-closure", default=None, metavar="DIR",
                    help="build a minimal verbatim-copy KB closure at DIR "
                         "(fresh AI-agent reviews; human-L3 pending) and "
                         "build against it")
    ap.add_argument("--output", default="results/ocpe_pilot_v1")
    ap.add_argument("--mode", default="canonical",
                    choices=["canonical", "experimental"])
    ap.add_argument("--allow-experimental", action="store_true")
    args = ap.parse_args()

    cfg = dict(PILOT_CONFIG)
    cfg["generation_mode"] = args.mode
    cfg["allow_experimental"] = args.allow_experimental

    kb_dir = args.kb_dir
    if args.kb_closure:
        kb_dir = prepare_kb_closure(args.kb_closure)
        cfg["kb_closure_note"] = CLOSURE_DISCLOSURE
        print(f"[kb] closure prepared at {kb_dir} "
              f"(excludes + disclosure in manifest)")

    builder = DatasetBuilder(cfg, kb_dir=kb_dir, output_dir=args.output)
    builder.sample_cohort()
    print(f"[cohort] {len(builder.subjects)} subjects sampled "
          f"(seed {cfg['dataset_seed']})")

    try:
        result = builder.build()
    except ProvenanceGateError as exc:
        print("\n[FAIL-CLOSED] provenance gate refused the build:\n")
        print(exc)
        print("\nResolve KB governance (reviews/tiers) or pass --kb-dir / "
              "--kb-closure pointing at a gate-clean KB.")
        sys.exit(2)

    print("\n" + human_summary(result.manifest))
    print(f"[done] pilot dataset at {result.output_dir}")


if __name__ == "__main__":
    main()
