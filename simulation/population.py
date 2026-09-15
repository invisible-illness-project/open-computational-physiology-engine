import numpy as np


class VirtualSubject:
    """
    Represents a virtual patient cohort subject. Defines demographics,
    fitness, and health attributes that establish prior distributions
    for latent state variables and mechanistic model parameters.

    Prior provenance (G-P0-04):
      * HRmax: Tanaka et al. 2001 (208 - 0.7*age, residual SD ~10-12 bpm;
        PMID 11153730, E5 per EVD-HLTH-005 / EVD-METB-010).  REPLACES the
        Fox 220-age equation, which the evidence package explicitly
        supersedes.
      * Female resting HR: +4.4 bpm (Health eHeart, n=25,408; EVD-HLTH-001,
        E2) -- implemented as a mild Hm/HM scaling (see below).
      * Sex/fitness/BMI volume and compliance scalings: repo-legacy
        magnitudes, directionally consistent with the POPULATION dossier but
        NOT directly cited -> flagged PROVISIONAL (tier C) pending curation.
    """

    def __init__(self, age=25, sex="female", bmi=22.0, fitness="average",
                 disease_severity=1.0, seed=None):
        self.age = age
        self.sex = sex.lower()
        self.bmi = bmi
        self.fitness = fitness.lower()  # "athletic", "average", "sedentary"
        self.disease_severity = disease_severity
        # Optional RNG for the Tanaka HRmax residual; None = deterministic
        # (residual 0), preserving reproducibility of existing call sites.
        self.seed = seed

    def tanaka_hrmax_bpm(self):
        """Tanaka 2001 HRmax = 208 - 0.7*age (E5; residual ~N(0, 10.7) bpm,
        sampled only when a seed was supplied)."""
        hrmax = 208.0 - 0.7 * self.age
        if self.seed is not None:
            rng = np.random.default_rng(self.seed)
            hrmax += rng.normal(0.0, 10.7)  # Tanaka validation RMSE 10.7 bpm
        return hrmax

    def adjust_parameters(self, base_params):
        """
        Applies demographic and fitness priors to mechanistic parameters.
        """
        params = base_params.copy()

        # 1. Age adjustments
        # Max heart rate: Tanaka 208 - 0.7*age (EVD-HLTH-005 / EVD-METB-010,
        # E5).  Was Fox 220 - age (superseded; G-P0-04).
        max_hr_bpm = self.tanaka_hrmax_bpm()
        params["HM"] = max_hr_bpm / 60.0

        # Stiffer blood vessels with age (reduced compliance).
        # PROVISIONAL (tier C): direction standard geriatric physiology;
        # 0.5%/yr slope is a repo-legacy magnitude, not directly cited.
        if self.age > 30:
            age_factor = 1.0 - 0.005 * (self.age - 30)
            age_factor = max(0.6, age_factor)
            params["Cau"] *= age_factor
            params["Cal"] *= age_factor

        # 2. Sex adjustments
        # Females: lower average circulating volume (direction standard;
        # -10% magnitude PROVISIONAL tier C) and higher resting HR
        # (+4.4 bpm, Health eHeart n=25,408, EVD-HLTH-001, E2) expressed via
        # the HR bounds (Hm x1.10 raises the controller floor; the effective
        # resting shift at the supine operating point is ~+1-2 bpm, within
        # the anchored range given the model's low resting-HR baseline).
        if self.sex == "female":
            params["TotalVol"] *= 0.90
            params["Hm"] *= 1.10

        # 3. BMI adjustments
        # Larger body mass scales total blood volume (mildly).
        # PROVISIONAL (tier C): repo-legacy slope.
        bmi_ref = 22.0
        vol_scale = 1.0 + 0.015 * (self.bmi - bmi_ref)
        vol_scale = max(0.8, min(1.3, vol_scale))
        params["TotalVol"] *= vol_scale

        # 4. Fitness adjustments
        # PROVISIONAL (tier C): directions anchored (athletes: lower resting
        # HR ~8-12 bpm, EVD-HLTH-001; higher vagal/HRV, POPULATION dossier);
        # specific multipliers are repo-legacy magnitudes pending curation.
        if self.fitness == "athletic":
            params["Hm"] *= 0.80          # Lower resting HR (bradycardia)
            params["Es"] *= 1.25          # Enhanced left ventricular contractility
            params["kR"] *= 1.15          # Higher baroreflex sensitivity
            params["kH"] *= 1.15
        elif self.fitness == "sedentary":
            params["Hm"] *= 1.15          # Elevated resting HR
            params["Es"] *= 0.85          # Lower baseline contractility
            params["kR"] *= 0.80          # Decreased baroreflex sensitivity
            params["kH"] *= 0.80

        # Ensure Hm never exceeds healthy limits
        params["Hm"] = max(0.3, min(params["Hm"], 1.5))

        return params
