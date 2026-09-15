"""Population-evidence constant registry for the cohort sampler (rule 6).

Every scientific constant used by ``dataset/cohort.py`` is declared HERE,
exactly once, with the full SWARM_SPEC rule-6 metadata block:

    value, units, distribution, evidence_tier (E0..E5 harmonized scale),
    source (registry claim_id / dossier section), canonical|experimental
    status, uncertainty.

Nothing in this module is invented: each entry cites
docs/evidence_package/POPULATION_MODEL_EVIDENCE.md (POP), the frozen
validation/healthy_reference.yaml (G-P0-09), CONTRADICTION_AUDIT.md
targets, or the knowledge base.  Entries whose magnitude is
machine-fitted / provisional are marked ``canonical_status: experimental``
or ``provisional: true`` and surface as honesty flags on every record
that consumes them.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Rule-6 evidence blocks.  "source" cites registry claim_ids (EVD-*) where
# available and the dossier section otherwise.
# ---------------------------------------------------------------------------

POPULATION_EVIDENCE = {
    # --- Resting heart rate (POP A.1) --------------------------------------
    "rhr_mean_bpm": {
        "value": 65.5, "units": "bpm", "distribution": "normal(mean, sd)",
        "evidence_tier": "E2",
        "source": "EVD-POP-001; POP A.1 (Quer et al. 2020, n=92,457, PMC7001906)",
        "canonical_status": "canonical",
        "uncertainty": "sd 7.7 bpm; device/definition offsets +/-4-8 bpm (POP A.1 note)",
    },
    "rhr_sd_bpm": {
        "value": 7.7, "units": "bpm", "distribution": "sd of rhr_mean_bpm",
        "evidence_tier": "E2",
        "source": "EVD-POP-001; POP A.1 (Quer et al. 2020)",
        "canonical_status": "canonical",
        "uncertainty": "between-person SD of daily RHR",
    },
    "rhr_sex_effect_female_bpm": {
        "value": 3.0, "units": "bpm", "distribution": "additive shift",
        "evidence_tier": "E4",
        "source": "POP A.1/B (Quer 2020; NHANES I PMC1403631): women +~3 bpm at all ages",
        "canonical_status": "canonical",
        "uncertainty": "sex alone explains ~4% of between-person RHR variance",
    },
    "rhr_day_to_day_cv": {
        "value": 0.046, "units": "1", "distribution": "within-person CV of daily RHR",
        "evidence_tier": "E2/E3",
        "source": "EVD-POP-004; POP C (Quer 2020 SD 3.03 bpm -> CV ~4.6%; 5-day ICC 0.87)",
        "canonical_status": "canonical",
        "uncertainty": "CV rises when mean RHR <60 bpm",
    },
    # --- RHR <-> RMSSD coupling (POP B) ------------------------------------
    "rhr_lnrmssd_correlation": {
        "value": -0.6, "units": "1", "distribution": "gaussian-copula correlation, sampled U(-0.5, -0.7)",
        "evidence_tier": "E1",
        "source": "POP B (HR<->lnRMSSD |r| ~0.5-0.8; Monfredi 2014; Sacha 2013; van Roon 2016 PMID 27672028)",
        "canonical_status": "canonical",
        "uncertainty": "mechanistic: RMSSD ~ c*RR*(modulation); range 0.5-0.7 sampled per dataset spec master prompt",
    },
    # --- Healthy orthostatic axis (G-P0-09 frozen reference) ----------------
    "healthy_orthostatic_axis": {
        "value": "protocol-conditioned sampling from validation/healthy_reference.yaml tails",
        "units": "bpm", "distribution": "tail-preserving draw per protocol entry",
        "evidence_tier": "E3",
        "source": "validation/healthy_reference.yaml (G-P0-09 FROZEN; Plash 2013 PMC3478101; Lee 2020 PMC7429890)",
        "canonical_status": "canonical",
        "uncertainty": "between-subject SD is tail-implied (dispersion_note in reference); event-to-event CV 15-25% provisional (POP F gap)",
    },
    # --- Venous pooling capacity axis (mechanistic orthostatic lever) -------
    "pooling_capacity_range_ml": {
        "value": [500.0, 1000.0], "units": "mL",
        "distribution": "uniform within range, quantile-mapped from the orthostatic-axis draw",
        "evidence_tier": "E0-E1",
        "source": "models/baroreflex_model.py Cycle-2 docstring (VMvl/Cvu rescaled to physiological 500-1000 mL pooling, MP-01/Stewart 2004); tier C machine-proposed fit",
        "canonical_status": "canonical",
        "provisional": True,
        "uncertainty": "machine-fitted magnitude (tier C); direction anchored (0.5-1.0 L thoracic shift, EVD-AUTN-005)",
    },
    # --- POTS demographics (POP E.1 / H.2) ----------------------------------
    "pots_female_fraction": {
        "value": [0.85, 0.94], "units": "1", "distribution": "uniform range (sensitivity)",
        "evidence_tier": "E2",
        "source": "EVD-POP-006; POP E.1 (Shaw 2019 PMC6790699 94% self-report; 5:1 clinical estimate)",
        "canonical_status": "canonical",
        "uncertainty": "self-report ascertainment bias; 5:1 = 83% lower bound",
    },
    "pots_onset_age_mixture": {
        "value": {"mode_years": 14.0, "median_years": 17.0, "iqr_years": [13.0, 28.0],
                  "adult_onset_fraction": 0.47, "mean_years": 20.7, "sd_years": 12.0},
        "units": "years", "distribution": "mixture (point mass/lognormal mode 14 + broad adult component)",
        "evidence_tier": "E2",
        "source": "EVD-POP-006; POP E.1 (Shaw 2019, n=4,835)",
        "canonical_status": "canonical",
        "uncertainty": "survey-based; diagnostic delay median 24 mo",
    },
    "pots_diagnostic_delay_years": {
        "value": {"median": 2.0, "iqr": [0.5, 6.0]}, "units": "years",
        "distribution": "lognormal-ish (median 24 mo, IQR 6-72 mo)",
        "evidence_tier": "E2",
        "source": "POP E.1 (Shaw 2019)",
        "canonical_status": "canonical",
        "uncertainty": "median/IQR only",
    },
    # --- Hypovolemia severity axis (CONTRADICTION Target 3) -----------------
    "pots_blood_volume_deficit_ml": {
        "value": {"mean": 689.0, "sd": 270.0}, "units": "mL",
        "distribution": "normal(mean, sd), floored at 100 mL; sampled per subject (never the KB point value)",
        "evidence_tier": "E2",
        "source": "EVD-POTS-004 (Raj 2005 Circulation 111:1574-82, 131I-albumin deficit 689+/-270 mL); CONTRADICTION_AUDIT Target 3",
        "canonical_status": "canonical",
        "uncertainty": "n=15; OCPE KB point -1000 mL is a ~1.5x machine-calibrated extreme (tier C); the DISTRIBUTION is the evidence",
    },
    "pots_hypovolemic_branch_fraction": {
        "value": 0.45, "units": "1", "distribution": "mixture weight (hypovolemic vs volume-normal)",
        "evidence_tier": "E0",
        "source": "CONTRADICTION_AUDIT Target 3 (~45% hypovolemic branch); EVD-POTS-004",
        "canonical_status": "experimental",
        "provisional": True,
        "uncertainty": "no validated subtype prevalence (Pierson 2025, E0) - mixture weight is a scenario parameter",
    },
    # --- ME/CFS demographics (POP E.2 / H.3) --------------------------------
    "mecfs_female_fraction": {
        "value": 0.8, "units": "1", "distribution": "point (range 0.78-0.86)",
        "evidence_tier": "E2",
        "source": "POP E.2 (EMEA survey, >9,000; PMC13070794)",
        "canonical_status": "canonical",
        "uncertainty": "consistent across 10 countries",
    },
    "mecfs_onset_age_bimodal": {
        "value": {"early_mean": 16.0, "early_sd": 4.3, "late_mean": 36.6, "late_sd": 10.5,
                  "early_late_weight": [1.0, 1.5]},
        "units": "years", "distribution": "bimodal normal mixture",
        "evidence_tier": "E2",
        "source": "POP E.2 (PMC13070794)",
        "canonical_status": "canonical",
        "uncertainty": "early onset OR 2.15 for severe disease",
    },
    # --- Comorbidity co-occurrence (POP E.3 / dataset spec 5.3) -------------
    "comorbidity_rates": {
        "value": {
            "heds_given_pots": 0.31,        # prospective 2017 criteria (PMC7282488)
            "heds_given_mecfs": 0.155,      # midpoint 0.12-0.19 (NINDS Roadmap 2024)
            "mecfs_given_pots": 0.21,       # EVD-POTS-020
            "autoimmune_given_pots": 0.16,  # EVD-POTS-020
            "mecfs_given_longcovid": 0.58,  # screen+ (Frontiers Neurol 2024)
        },
        "units": "conditional probability",
        "distribution": "pairwise log-linear cells; pairwise-sufficient (3rd-order E0)",
        "evidence_tier": "E2",
        "source": "EVD-POP-007; POP E.3; EVD-POTS-020",
        "canonical_status": "canonical",
        "uncertainty": "ALL rates clinic/self-report inflated -> ascertainment down-weighting mandatory",
    },
    "comorbidity_ascertainment_downweight": {
        "value": [0.3, 0.5], "units": "1",
        "distribution": "uniform range multiplier on clinic rates (or declare cohort_frame: clinic)",
        "evidence_tier": "E2",
        "source": "EVD-POP-007 guidance; POP E.3 joint-sampling guidance; dataset spec 5.3",
        "canonical_status": "canonical",
        "uncertainty": "down-weight magnitude is guidance, not measurement",
    },
    # --- Anthropometrics (dataset-hardening W4-2; PROVISIONAL) --------------
    "bmi_distribution": {
        "value": {"mean": 26.0, "sd": 4.5, "min": 17.0, "max": 45.0},
        "units": "kg/m^2",
        "distribution": "truncated normal N(26.0, 4.5^2) on [17, 45]",
        "evidence_tier": "E4",
        "source": ("NHANES-informed adult BMI marginal (adult mean ~26-29, "
                   "sd ~4.5-5); the POP dossier documents only the U-shaped "
                   "BMI->RHR link (Quer 2020, E2), NOT a BMI marginal -> "
                   "PROVISIONAL distribution parameter"),
        "canonical_status": "canonical",
        "provisional": True,
        "uncertainty": ("provisional: NHANES-informed, not registry-anchored; "
                        "identical distribution MUST be used for every group "
                        "(matched nuisance)"),
    },
    "height_adult_cm": {
        "value": {"male": {"mean": 178.0, "sd": 7.0},
                  "female": {"mean": 164.0, "sd": 6.6},
                  "min_cm": 145.0, "max_cm": 205.0},
        "units": "cm",
        "distribution": "sex-specific truncated normal",
        "evidence_tier": "E4",
        "source": ("NHANES-informed adult height marginals (used only to "
                   "derive weight = BMI*h^2 for the Nadler blood-volume "
                   "hook); PROVISIONAL - not registry-anchored"),
        "canonical_status": "canonical",
        "provisional": True,
        "uncertainty": "provisional: NHANES-informed sex-specific marginals",
    },
    "nadler_blood_volume": {
        "value": {"male_coeff": {"h3": 0.3669, "w": 0.03219, "c": 0.6041},
                  "female_coeff": {"h3": 0.3561, "w": 0.03308, "c": 0.1833},
                  "between_person_cv": 0.06},
        "units": "L (h in m, weight in kg)",
        "distribution": ("Nadler equation (male: 0.3669*h^3+0.03219*w+0.6041; "
                         "female: 0.3561*h^3+0.03308*w+0.1833) x (1 + CV*z), "
                         "CV=0.06 between-person residual"),
        "evidence_tier": "E2 (equation) / E4 (residual CV, provisional)",
        "source": ("Nadler, Hidalgo & Bloch 1962 (Surgery 51:224-232) "
                   "prediction of blood volume from height/weight/sex; "
                   "between-person residual CV ~5-8% of predicted volume "
                   "(PROVISIONAL magnitude)"),
        "canonical_status": "canonical",
        "provisional": True,
        "uncertainty": ("replaces the engine's repo-legacy sex/BMI TotalVol "
                        "prior when height+BMI are sampled; residual CV is "
                        "provisional"),
    },
    # --- Fitness spectrum (dataset-hardening W4-2; PROVISIONAL) -------------
    "fitness_category_distribution": {
        "value": {"sedentary": 0.25, "average": 0.55, "athletic": 0.20},
        "units": "probability",
        "distribution": "categorical over engine fitness classes",
        "evidence_tier": "E4",
        "source": ("POP factor model (fitness latent factor; Copenhagen Male "
                   "Study RHR-fitness r=-0.34, E2); category PROPORTIONS are "
                   "PROVISIONAL (no registry-anchored marginal)"),
        "canonical_status": "canonical",
        "provisional": True,
        "uncertainty": ("provisional proportions; identical distribution MUST "
                        "be used for every group (matched nuisance)"),
    },
    "fitness_rhr_effect_bpm": {
        "value": {"sedentary": 4.0, "average": 0.0, "athletic": -5.0},
        "units": "bpm (additive on the RHR trait mean)",
        "distribution": "per-category additive shift",
        "evidence_tier": "E2 (direction) / E4 (magnitude, provisional)",
        "source": ("POP factor model: RHR-fitness r=-0.34 (Copenhagen Male "
                   "Study, Heart 99:882, E2); VO2max-RHR path; category shift "
                   "magnitudes PROVISIONAL (~0.5 SD of RHR per extreme "
                   "category)"),
        "canonical_status": "canonical",
        "provisional": True,
        "uncertainty": "provisional magnitudes; direction evidence-anchored",
    },
    # --- Tanaka HRmax residual (POP B/D) ------------------------------------
    "hrmax_tanaka_residual_sd_bpm": {
        "value": 10.7, "units": "bpm", "distribution": "normal(0, sd)",
        "evidence_tier": "E5",
        "source": "EVD-POP-003; POP B/D (Tanaka 2001 PMID 11153730; Shookster 2020 validation RMSE 10.7)",
        "canonical_status": "canonical",
        "uncertainty": "residual SD 10-12 bpm across studies",
    },
}

#: Evidence blocks that are provisional / machine-fitted: any record whose
#: subject consumed them must carry the matching honesty flag.
PROVISIONAL_HONESTY_FLAGS = {
    "pooling_capacity_range_ml": "pooling_capacity_tierC_machine_fitted",
    "pots_hypovolemic_branch_fraction": "subtype_mixture_weight_E0_scenario",
    "pots_blood_volume_deficit_ml": "severity_resampled_from_evidence_distribution",
    "bmi_distribution": "bmi_distribution_provisional_nhanes_informed",
    "height_adult_cm": "height_distribution_provisional_nhanes_informed",
    "nadler_blood_volume": "blood_volume_nadler_provisional_residual_cv",
    "fitness_category_distribution": "fitness_spectrum_provisional_proportions",
    "fitness_rhr_effect_bpm": "fitness_rhr_effect_provisional_magnitude",
}


def evidence_block(key: str) -> dict:
    """Return the rule-6 evidence block for a population constant."""
    return POPULATION_EVIDENCE[key]
