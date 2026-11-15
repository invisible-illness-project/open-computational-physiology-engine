import numpy as np

class SymptomFramework:
    """
    Simulates the emergence of clinical symptoms probabilistically
    based on the underlying latent physiology state.
    """
    def __init__(self):
        self.symptoms = {
            "fatigue": 0.0,
            "brain_fog": 0.0,
            "pain": 0.0,
            "orthostatic_intolerance": 0.0,
            "palpitations": 0.0,
            "sleepiness": 0.0,
            "dizziness": 0.0
        }

    def compute_symptoms(self, latent_state, hr_bpm, pc_mean):
        """
        Updates symptom levels based on latent variables and hemodynamics.
        Outputs symptom levels in the range [0.0, 1.0].
        """
        # Read latent states
        sym_tone = latent_state.get("sympathetic_tone")
        sleep_pres = latent_state.get("sleep_pressure")
        stress = latent_state.get("stress_load")
        infl = latent_state.get("inflammatory_burden")
        metab = latent_state.get("metabolic_reserve")
        
        # 1. Palpitations
        # Driven by high heart rate and elevated sympathetic tone
        if hr_bpm > 80.0:
            palp_prob = (hr_bpm - 80.0) / 100.0 + 0.2 * sym_tone
            self.symptoms["palpitations"] = float(max(0.0, min(1.0, palp_prob)))
        else:
            self.symptoms["palpitations"] = 0.0
            
        # 2. Dizziness
        # Driven by cerebral hypoperfusion (low carotid pressure)
        if pc_mean < 85.0:
            diz = (85.0 - pc_mean) / 35.0
            self.symptoms["dizziness"] = float(max(0.0, min(1.0, diz)))
        else:
            self.symptoms["dizziness"] = 0.0
            
        # 3. Orthostatic Intolerance
        # Combination of dizziness, rapid heart rate, and low carotid pressure
        oi = 0.5 * self.symptoms["dizziness"] + 0.3 * (self.symptoms["palpitations"]) + 0.2 * sym_tone
        self.symptoms["orthostatic_intolerance"] = float(max(0.0, min(1.0, oi)))
        
        # 4. Fatigue
        # Strongly driven by depleted metabolic reserve, high inflammatory burden, and sleep pressure
        fat = (1.0 - metab) * 0.6 + (infl / 10.0) * 0.3 + 0.1 * sleep_pres
        self.symptoms["fatigue"] = float(max(0.0, min(1.0, fat)))
        
        # 5. Brain Fog
        # Driven by low carotid pressure (hypoperfusion), inflammatory burden, and sleep pressure
        bf_perf = (90.0 - pc_mean) / 30.0 if pc_mean < 90.0 else 0.0
        bf = 0.4 * bf_perf + 0.3 * (infl / 10.0) + 0.3 * sleep_pres
        self.symptoms["brain_fog"] = float(max(0.0, min(1.0, bf)))
        
        # 6. Sleepiness
        # Proportional to homeostatic sleep pressure
        self.symptoms["sleepiness"] = float(max(0.0, min(1.0, sleep_pres)))
        
        # 7. Pain
        # Influenced by inflammatory burden and stress load (allostatic burden)
        pn = 0.7 * (infl / 10.0) + 0.3 * stress
        self.symptoms["pain"] = float(max(0.0, min(1.0, pn)))
        
        return self.symptoms.copy()
