class BehaviorModel:
    """
    Simulates patient behaviors and lifestyle factors.
    Updates latent states and applies directional modulations to parameters,
    capturing bidirectional feedback between behavioral choice and physical capacity.
    """
    def __init__(self):
        self.current_activity = "rest"  # "rest", "exercise", "meal", "sleep", "stress"
        
    def trigger_behavior(self, activity):
        if activity in ["rest", "exercise", "meal", "sleep", "stress"]:
            self.current_activity = activity

    def modulate_latent_states(self, latent_state, time_sec):
        """
        Applies behavioral modulations to latent state variables.
        """
        # Read current latent states
        sym = latent_state.get("sympathetic_tone")
        para = latent_state.get("parasympathetic_tone")
        stress = latent_state.get("stress_load")
        hydr = latent_state.get("hydration")
        sleep_pres = latent_state.get("sleep_pressure")
        metab = latent_state.get("metabolic_reserve")
        
        # Apply changes based on behavior
        if self.current_activity == "exercise":
            # Exertion depletes metabolic reserve and increases stress/sympathetic
            sym = min(1.0, sym + 0.3)
            para = max(0.0, para - 0.4)
            metab = max(0.0, metab - 0.005)  # Depletion rate
            hydr = max(0.0, hydr - 0.002)     # Sweat loss
        elif self.current_activity == "sleep":
            # Sleep recovers metabolic reserve, decreases stress and sympathetic tone
            sym = max(0.05, sym - 0.1)
            para = min(0.95, para + 0.15)
            sleep_pres = max(0.0, sleep_pres - 0.01)
            stress = max(0.0, stress - 0.02)
            metab = min(1.0, metab + 0.01)
        elif self.current_activity == "stress":
            # Chronic/acute stress increases sympathetic tone
            stress = min(1.0, stress + 0.05)
            sym = min(1.0, sym + 0.15)
            para = max(0.0, para - 0.1)
        elif self.current_activity == "meal":
            # Digestion increases parasympathetic tone slightly
            para = min(0.9, para + 0.05)
            
        latent_state.set("sympathetic_tone", sym)
        latent_state.set("parasympathetic_tone", para)
        latent_state.set("stress_load", stress)
        latent_state.set("hydration", hydr)
        latent_state.set("sleep_pressure", sleep_pres)
        latent_state.set("metabolic_reserve", metab)
        
    def modulate_parameters(self, base_params, latent_state):
        """
        Applies direct behavioral parameter shifts to the mechanistic model.
        E.g., postprandial splanchnic vasodilation.
        """
        params = base_params.copy()
        
        # 1. Postprandial splanchnic pooling
        if self.current_activity == "meal":
            # Meal causes splanchnic pooling (vasodilation in lower body)
            params["RalpM"] *= 0.75
            params["Ralpm"] *= 0.75
            params["Cal"] *= 1.15
            
        # 2. Hydration state affects blood volume
        hydr = latent_state.get("hydration")
        # Hydration scales total volume: 0.0 is dehydrated (-500ml), 1.0 is hydrated (+200ml)
        volume_delta = -500.0 + 700.0 * hydr
        params["TotalVol"] += volume_delta
        
        # 3. Exercise transiently elevates cardiac contractility
        if self.current_activity == "exercise":
            params["Es"] *= 1.30
            
        return params
        
    def check_behavioral_feedback(self, symptoms):
        """
        Bidirectional feedback: high symptoms can force changes in behavior.
        E.g., extreme fatigue forces rest, dizziness during exercise stops it.
        """
        fatigue = symptoms.get("fatigue", 0.0)
        dizziness = symptoms.get("dizziness", 0.0)
        
        if fatigue > 0.8 and self.current_activity == "exercise":
            print("[INFO] Physiological feedback loop: Exercise aborted due to severe fatigue.")
            self.current_activity = "rest"
            
        if dizziness > 0.7 and self.current_activity == "exercise":
            print("[INFO] Physiological feedback loop: Exercise stopped due to orthostatic dizziness.")
            self.current_activity = "rest"
