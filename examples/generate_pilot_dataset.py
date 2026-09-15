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
  * Canonical mode: only the canonical chest-strap profile (polar_h10).
    Wrist/ring/band profiles are canonical_status=experimental upstream
    and require --mode experimental --allow-experimental.

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
         "orthostatic_axis": {"enabled": True,
                              "quantiles": [0.15, 0.50, 0.90],
                              "reference_protocol": "hut_60_70_10min"},
         "comorbidities": {"frame": "off"}},
        {"cohort_id": "pots_hypovolemic", "condition": "pots", "n_subjects": 3,
         "phenotypes": ["hypovolemic_pots"],
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
