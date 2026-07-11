import numpy as np

class VirtualSubject:
    """
    Represents a virtual patient cohort subject. Defines demographics,
    fitness, and health attributes that establish prior distributions
    for latent state variables and mechanistic model parameters.
    """
    def __init__(self, age=25, sex="female", bmi=22.0, fitness="average", disease_severity=1.0):
        self.age = age
        self.sex = sex.lower()
        self.bmi = bmi
        self.fitness = fitness.lower()  # "athletic", "average", "sedentary"
        self.disease_severity = disease_severity

    def adjust_parameters(self, base_params):
        """
        Applies demographic and fitness priors to mechanistic parameters.
        """
        params = base_params.copy()
        
        # 1. Age adjustments
        # Chronotropic incompetence / max heart rate drops with age
        max_hr_bpm = 220.0 - self.age
        params["HM"] = max_hr_bpm / 60.0
        
        # Stiffer blood vessels with age (reduced compliance)
        if self.age > 30:
            age_factor = 1.0 - 0.005 * (self.age - 30)
            age_factor = max(0.6, age_factor)
            params["Cau"] *= age_factor
            params["Cal"] *= age_factor
            
        # 2. Sex adjustments
        # Females have lower average circulating volume and slightly higher resting heart rates
        if self.sex == "female":
            params["TotalVol"] *= 0.90
            params["Hm"] *= 1.10
            
        # 3. BMI adjustments
        # Larger body mass scales total blood volume (mildly)
        bmi_ref = 22.0
        vol_scale = 1.0 + 0.015 * (self.bmi - bmi_ref)
        vol_scale = max(0.8, min(1.3, vol_scale))
        params["TotalVol"] *= vol_scale
        
        # 4. Fitness adjustments
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
