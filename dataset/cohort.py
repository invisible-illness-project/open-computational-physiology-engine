"""Cohort sampler (G-P0-07 build item 1).

Samples virtual-subject cohorts from the evidence-based population
distributions in docs/evidence_package/POPULATION_MODEL_EVIDENCE.md (POP)
and docs/evidence_package/OCPE_DATASET_SPECIFICATION.md section 5:

  * age/sex recipes per condition (healthy uniform 18-75; POTS female
    0.85-0.94 with onset-age mixture + diagnostic delay; ME/CFS female
    ~0.8 with bimodal onset);
  * resting HR ~ N(65.5, 7.7^2) with +3 bpm female shift (POP A.1);
  * RHR <-> ln(RMSSD) coupling via Gaussian copula, |r| ~ U(0.5, 0.7)
    (POP B, E1); ln(RMSSD) marginals from the Lifelines age/sex medians
    (POP A.2, E2);
  * day-to-day RHR CV 4.6% (POP C, EVD-POP-004);
  * healthy orthostatic-axis sampling from the FROZEN
    validation/healthy_reference.yaml tails (G-P0-09; quantile-mapped
    onto the mechanistic venous-pooling axis -- NEVER a label);
  * hypovolemia severity resampled from the Raj 2005 deficit
    distribution 689+/-270 mL (EVD-POTS-004; CONTRADICTION Target 3) --
    the KB point perturbation (-1000 mL) is a machine-calibrated extreme
    and is never applied as a point value to dataset subjects;
  * comorbidity joint sampling with mandatory 0.3-0.5x ascertainment
    down-weighting (POP E.3; pairwise-sufficient, 3rd-order E0).

A researcher specifies a cohort ENTIRELY via YAML config (see
``load_cohort_config`` and examples/generate_pilot_dataset.py); no
simulation code is touched.

Every sampled quantity traces to ``dataset/population_evidence.py``
(rule 6).  Consumption of provisional / machine-fitted blocks adds the
matching honesty flag to the subject (and hence to every record).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
import yaml
from scipy.stats import norm

from dataset.population_evidence import (
    POPULATION_EVIDENCE,
    PROVISIONAL_HONESTY_FLAGS,
    evidence_block,
)

# ---------------------------------------------------------------------------
# Lifelines RMSSD medians (POP A.2, Tegegne 2020, n=84,772, E2): age-band
# median RMSSD (ms) by sex.  Bands above/below the table clamp to the edge.
# ---------------------------------------------------------------------------
_RMSSD_BANDS = [  # (age_lo_incl, age_hi_excl, women_median_ms, men_median_ms)
    (13, 15, 66.5, 67.4), (15, 20, 60.7, 59.9), (20, 25, 52.1, 47.6),
    (25, 30, 47.5, 42.3), (30, 35, 42.3, 36.9), (35, 40, 37.9, 32.8),
    (40, 45, 33.9, 29.0), (45, 50, 29.2, 26.0), (50, 55, 26.6, 23.7),
    (55, 60, 22.5, 21.0), (60, 65, 20.5, 19.1), (65, 70, 17.8, 17.7),
    (70, 75, 18.3, 16.0), (75, 200, 16.1, 14.9),
]
#: Spread of ln(RMSSD): derived from the tabulated 2nd/98th percentiles
#: (POP A.2), e.g. women 25-29: ln(180.7/11.5)/(2*2.326) ~= 0.59; bands
#: span ~0.5-0.65 -> 0.55 representative (E2-derived).
_LN_RMSSD_SIGMA = 0.55


def rmssd_median_ms(age: float, sex: str) -> float:
    """Lifelines age/sex median RMSSD (ms) lookup (POP A.2)."""
    for lo, hi, w, m in _RMSSD_BANDS:
        if lo <= age < hi:
            return w if sex == "female" else m
    return _RMSSD_BANDS[-1][2] if sex == "female" else _RMSSD_BANDS[-1][3]


def stable_seed(*parts: Any) -> int:
    """Deterministic 63-bit seed from arbitrary parts (seed hierarchy)."""
    h = hashlib.sha256()
    for p in parts:
        h.update(str(p).encode("utf-8"))
        h.update(b"|")
    return int.from_bytes(h.digest()[:8], "big") & 0x7FFFFFFFFFFFFFFF


@dataclass
class Subject:
    """One sampled virtual subject (cohort draw; no engine state)."""
    subject_id: str
    cohort_id: str
    condition: str                      # healthy | pots | mecfs | long_covid
    phenotypes: List[str]               # engine perturbation ids (gated)
    age: float
    sex: str
    bmi: float
    fitness: str
    rhr_bpm: float                      # population trait draw (target)
    ln_rmssd_ms: float                  # copula-coupled HRV trait
    pooling_capacity_ml: float          # mechanistic orthostatic lever (VMvl)
    orthostatic_axis: Dict[str, Any]    # quantile + reference-protocol target
    blood_volume_deficit_ml: Optional[float]  # hypovolemic severity draw
    comorbidities: List[str]
    severity: Optional[float]
    cohort_frame: str                   # population | clinic
    subject_seed: int
    provenance: List[Dict[str, Any]] = field(default_factory=list)
    honesty_flags: List[str] = field(default_factory=list)

    def to_metadata(self) -> Dict[str, Any]:
        return {
            "subject_id": self.subject_id,
            "cohort_id": self.cohort_id,
            "condition": self.condition,
            "phenotypes": list(self.phenotypes),
            "demographics": {
                "age_years": round(float(self.age), 1),
                "sex": self.sex,
                "bmi": round(float(self.bmi), 1),
                "fitness": self.fitness,
            },
            "population_traits": {
                "rhr_bpm_target": round(float(self.rhr_bpm), 2),
                "ln_rmssd_ms": round(float(self.ln_rmssd_ms), 4),
                "rmssd_ms_median_implied": round(float(np.exp(self.ln_rmssd_ms)), 1),
                "pooling_capacity_ml": round(float(self.pooling_capacity_ml), 1),
                "orthostatic_axis": self.orthostatic_axis,
                "blood_volume_deficit_ml": (
                    round(float(self.blood_volume_deficit_ml), 1)
                    if self.blood_volume_deficit_ml is not None else None),
            },
            "comorbidities": list(self.comorbidities),
            "severity": self.severity,
            "cohort_frame": self.cohort_frame,
            "subject_seed": int(self.subject_seed),
        }


class CohortSampler:
    """Samples subjects for every cohort block of a dataset config.

    Config schema (YAML)::

        cohorts:
          - cohort_id: healthy
            condition: healthy            # healthy | pots | mecfs | long_covid
            n_subjects: 3
            phenotypes: []                # engine phenotype ids
            age: {dist: uniform, min: 18, max: 75}    # optional override
            sex: {female_fraction: 0.5}               # optional override
            bmi: 22.0                                   # optional (point)
            fitness: average                          # optional
            orthostatic_axis:
              enabled: true
              quantiles: [0.15, 0.5, 0.9]  # per-subject (cycled) or "random"
              reference_protocol: hut_60_70_10min
            severity: {dist: raj2005}    # hypovolemic deficit resampling
            comorbidities: {frame: population}       # population | clinic | off
    """

    def __init__(self, config: Dict[str, Any], dataset_seed: int):
        self.config = config or {}
        self.dataset_seed = int(dataset_seed)

    # ------------------------------------------------------------------
    def _rng(self, cohort_id: str, stream: str) -> np.random.Generator:
        return np.random.default_rng(
            stable_seed(self.dataset_seed, cohort_id, stream))

    # ------------------------------------------------------------------
    # Demographic recipes (POP H)
    # ------------------------------------------------------------------
    def _sample_sex(self, rng, condition: str, cfg: Dict[str, Any]) -> str:
        default = {"healthy": 0.5, "pots": None, "mecfs": 0.8,
                   "long_covid": 0.75}.get(condition, 0.5)
        ff = cfg.get("sex", {}).get("female_fraction", default)
        if ff is None:  # POTS: uniform over the evidence range 0.85-0.94
            lo, hi = evidence_block("pots_female_fraction")["value"]
            ff = rng.uniform(lo, hi)
        return "female" if rng.random() < ff else "male"

    def _sample_age(self, rng, condition: str, cfg: Dict[str, Any]) -> float:
        if "age" in cfg:
            a = cfg["age"]
            if a.get("dist", "uniform") == "uniform":
                return float(rng.uniform(a["min"], a["max"]))
            if a.get("dist") == "normal":
                return float(np.clip(rng.normal(a["mean"], a["sd"]), 12, 90))
            raise ValueError(f"unknown age distribution {a}")
        if condition == "pots":
            # Onset-age mixture (POP E.1/H.2): lognormal-ish early component
            # (mode 14, median 17, IQR 13-28) + broad adult component
            # (47% adult onset); present age = onset + diagnostic delay
            # (median 2 y, IQR 0.5-6).
            onset_cfg = evidence_block("pots_onset_age_mixture")["value"]
            if rng.random() < onset_cfg["adult_onset_fraction"]:
                onset = float(np.clip(rng.normal(28.0, 9.0), 19.0, 60.0))
            else:
                # adolescent component: lognormal around median 17 (IQR 13-28)
                onset = float(np.clip(rng.lognormal(np.log(17.0), 0.35), 10.0, 25.0))
            delay = float(np.clip(rng.lognormal(np.log(2.0), 0.8), 0.1, 15.0))
            return float(np.clip(onset + delay, 12.0, 75.0))
        if condition == "mecfs":
            b = evidence_block("mecfs_onset_age_bimodal")["value"]
            w = b["early_late_weight"]
            if rng.random() < w[0] / (w[0] + w[1]):
                onset = rng.normal(b["early_mean"], b["early_sd"])
            else:
                onset = rng.normal(b["late_mean"], b["late_sd"])
            duration = float(np.clip(rng.normal(12.0, 9.0), 0.5, 40.0))  # POP E.2
            return float(np.clip(onset + duration, 14.0, 80.0))
        # healthy / long_covid default: census-style uniform 18-75 (POP H.1)
        return float(rng.uniform(18.0, 75.0))

    # ------------------------------------------------------------------
    # Population traits (POP A/B/C)
    # ------------------------------------------------------------------
    def _sample_rhr_and_hrv(self, rng, age: float, sex: str):
        """RHR ~ N(65.5, 7.7) (+3 bpm female) coupled to ln(RMSSD) via a
        Gaussian copula with |r| ~ U(0.5, 0.7) (POP A.1/A.2/B)."""
        mean = evidence_block("rhr_mean_bpm")["value"]
        sd = evidence_block("rhr_sd_bpm")["value"]
        if sex == "female":
            mean += evidence_block("rhr_sex_effect_female_bpm")["value"]
        z1, z2 = rng.normal(0.0, 1.0, 2)
        r = -float(rng.uniform(0.5, 0.7))  # evidence range (rule-6 block)
        rhr = float(np.clip(mean + sd * z1, 39.7, 108.6))  # observed range
        z_rmssd = r * z1 + np.sqrt(1.0 - r * r) * z2
        ln_med = np.log(rmssd_median_ms(age, sex))
        ln_rmssd = float(ln_med + _LN_RMSSD_SIGMA * z_rmssd)
        return rhr, ln_rmssd, r

    # ------------------------------------------------------------------
    # Healthy orthostatic axis (G-P0-09 tail-preserving sampling)
    # ------------------------------------------------------------------
    def _sample_orthostatic_axis(self, rng, axis_cfg: Dict[str, Any],
                                 subject_index: int, reference: Dict[str, Any]):
        """Draw a healthy-axis quantile and map it onto the mechanistic
        pooling axis.  The between-subject SD is TAIL-IMPLIED by the frozen
        reference entry's fraction_exceeding_30bpm (the binding calibration
        target per the reference's own dispersion_note)."""
        proto = axis_cfg.get("reference_protocol", "hut_60_70_10min")
        entry = (reference or {}).get("protocols", {}).get(proto)
        q_cfg = axis_cfg.get("quantiles", "random")
        if q_cfg == "random":
            q = float(rng.random())
        else:
            q = float(q_cfg[subject_index % len(q_cfg)])
        q = min(0.999, max(0.001, q))
        axis = {"reference_protocol": proto, "quantile": round(q, 4),
                "sampling": "distribution"}
        if entry is not None:
            dist = entry["sustained_delta_HR_bpm"]
            tail = entry["fraction_exceeding_30bpm"]
            mean = float(dist["mean"])
            f = float(tail.get("point", 0.5))
            f = min(0.99, max(0.01, f))
            sd_tail = (30.0 - mean) / norm.ppf(1.0 - f)
            sd = max(float(dist.get("sd", 3.0)), abs(sd_tail))
            target = mean + sd * norm.ppf(q)
            axis.update({
                "target_sustained_delta_HR_bpm": round(float(target), 2),
                "target_window_semantics": "minutes 5-10 upright (reference protocol)",
                "reference_mean_bpm": mean,
                "reference_tail_implied_sd_bpm": round(float(sd), 2),
                "reference_fraction_ge_30bpm": tail,
                "note": ("axis target is a POPULATION draw on the reference "
                         "protocol semantics; the realized simulated response "
                         "emerges from mechanism (pooling/volume/baroreflex) "
                         "and is recorded separately"),
            })
        else:
            axis["note"] = "unresolved: no frozen reference entry for protocol"
        # Mechanistic mapping: quantile -> pooling capacity within the
        # documented 500-1000 mL axis (same axis for ALL conditions).
        lo, hi = evidence_block("pooling_capacity_range_ml")["value"]
        pooling = lo + (hi - lo) * q
        return pooling, axis

    # ------------------------------------------------------------------
    # Comorbidities (POP E.3, pairwise-sufficient, ascertainment-weighted)
    # ------------------------------------------------------------------
    _COMORBID_CELLS = {
        "pots": [("heds", "heds_given_pots"), ("mecfs", "mecfs_given_pots"),
                 ("autoimmune", "autoimmune_given_pots")],
        "mecfs": [("heds", "heds_given_mecfs")],
        "long_covid": [("mecfs", "mecfs_given_longcovid")],
        "healthy": [],
    }

    def _sample_comorbidities(self, rng, condition: str, frame: str) -> List[str]:
        rates = evidence_block("comorbidity_rates")["value"]
        out = []
        for name, key in self._COMORBID_CELLS.get(condition, []):
            rate = rates[key]
            if frame == "population":
                lo, hi = evidence_block("comorbidity_ascertainment_downweight")["value"]
                rate = rate * float(rng.uniform(lo, hi))
            if rng.random() < rate:
                out.append(name)
        return out

    # ------------------------------------------------------------------
    def sample(self) -> List[Subject]:
        from validation.evaluator import load_healthy_reference
        reference = load_healthy_reference()
        subjects: List[Subject] = []
        for ccfg in self.config.get("cohorts", []):
            cohort_id = ccfg["cohort_id"]
            condition = ccfg.get("condition", "healthy")
            n = int(ccfg.get("n_subjects", 1))
            rng = self._rng(cohort_id, "demographics")
            rng_traits = self._rng(cohort_id, "traits")
            axis_cfg = ccfg.get("orthostatic_axis", {}) or {}
            axis_enabled = bool(axis_cfg.get("enabled", condition == "healthy"))
            frame = (ccfg.get("comorbidities", {}) or {}).get("frame", "population")
            comorb_on = frame != "off"

            for i in range(n):
                sid = f"{cohort_id}-{i + 1:03d}"
                sex = self._sample_sex(rng, condition, ccfg)
                age = self._sample_age(rng, condition, ccfg)
                bmi = float(ccfg.get("bmi", 22.0))
                fitness = str(ccfg.get("fitness", "average"))
                rhr, ln_rmssd, r_coupling = self._sample_rhr_and_hrv(
                    rng_traits, age, sex)

                pooling, axis = 700.0, {"enabled": False}
                if axis_enabled:
                    pooling, axis = self._sample_orthostatic_axis(
                        rng_traits, axis_cfg, i, reference)
                    axis["enabled"] = True
                    axis["rhr_lnrmssd_copula_r"] = round(r_coupling, 3)

                deficit = None
                if "hypovolemic_pots" in (ccfg.get("phenotypes") or []):
                    d = evidence_block("pots_blood_volume_deficit_ml")["value"]
                    deficit = float(max(100.0, rng_traits.normal(d["mean"], d["sd"])))

                comorbid = (self._sample_comorbidities(rng_traits, condition, frame)
                            if comorb_on else [])

                prov_keys = ["rhr_mean_bpm", "rhr_sd_bpm", "rhr_day_to_day_cv",
                             "rhr_lnrmssd_correlation"]
                if axis_enabled:
                    prov_keys += ["healthy_orthostatic_axis",
                                  "pooling_capacity_range_ml"]
                if condition == "pots":
                    prov_keys += ["pots_female_fraction", "pots_onset_age_mixture",
                                  "pots_diagnostic_delay_years",
                                  "comorbidity_rates",
                                  "comorbidity_ascertainment_downweight"]
                if deficit is not None:
                    prov_keys += ["pots_blood_volume_deficit_ml"]
                if condition == "mecfs":
                    prov_keys += ["mecfs_female_fraction", "mecfs_onset_age_bimodal"]
                provenance = [dict({"constant": k}, **evidence_block(k))
                              for k in dict.fromkeys(prov_keys)]

                flags = sorted({
                    PROVISIONAL_HONESTY_FLAGS[k]
                    for k in prov_keys if k in PROVISIONAL_HONESTY_FLAGS})
                if condition != "healthy" and frame == "population":
                    flags.append("comorbidity_rates_ascertainment_downweighted")

                subjects.append(Subject(
                    subject_id=sid, cohort_id=cohort_id, condition=condition,
                    phenotypes=list(ccfg.get("phenotypes") or []),
                    age=age, sex=sex, bmi=bmi, fitness=fitness,
                    rhr_bpm=rhr, ln_rmssd_ms=ln_rmssd,
                    pooling_capacity_ml=pooling, orthostatic_axis=axis,
                    blood_volume_deficit_ml=deficit,
                    comorbidities=comorbid,
                    severity=(ccfg.get("severity", {}) or {}).get("value"),
                    cohort_frame=frame,
                    subject_seed=stable_seed(self.dataset_seed, sid),
                    provenance=provenance, honesty_flags=flags,
                ))
        return subjects


def load_cohort_config(path: str) -> Dict[str, Any]:
    """Load a cohort YAML config (researcher-facing; no code changes)."""
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if not isinstance(cfg, dict) or "cohorts" not in cfg:
        raise ValueError(f"cohort config {path} must define a 'cohorts' list")
    return cfg
