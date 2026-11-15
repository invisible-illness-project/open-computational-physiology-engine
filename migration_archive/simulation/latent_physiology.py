import numpy as np

class LatentPhysiologyState:
    """
    Manages and tracks the hidden (latent) physiology state variables.
    Provides a standardized container to read/write latent states and map
    them to parameters of the mechanistic cardiovascular model.
    """
    def __init__(self):
        # Initial default values for a standard healthy reference patient
        self.states = {
            "sympathetic_tone": 0.3,          # T_sym [0, 1]
            "parasympathetic_tone": 0.7,      # T_para [0, 1]
            "baroreflex_gain": 25.0,          # G_baro (kR/kH) [0, 100]
            "blood_volume": 4500.0,           # V_total [2000, 7000] ml
            "cardiac_contractility": 3.0,     # E_syst (Es) [0.5, 10] mmHg/ml
            "peripheral_resistance": 1.0,     # R_periph (baseline modifier)
            "vascular_compliance": 1.0,       # C_vasc (baseline modifier)
            "circadian_drive": 0.0,           # D_circ [-1, 1]
            "sleep_pressure": 0.1,            # P_sleep [0, 1]
            "hydration": 0.9,                 # H_hydr [0, 1]
            "stress_load": 0.1,               # L_stress [0, 1]
            "inflammatory_burden": 0.1,       # B_infl [0, 10]
            "metabolic_reserve": 1.0,         # R_metab [0, 1]
            "hormonal_state": 0.0,            # S_horm [-1, 1]
            "autonomic_recovery_capacity": 1.0 # C_rec [0, 1]
        }
        
    def get(self, name, default=0.0):
        return self.states.get(name, default)
        
    def set(self, name, value):
        if name in self.states:
            self.states[name] = value
            
    def update_derived_states(self, pc_mean, model_params):
        """
        Dynamically calculates active states that emerge from pressure feedback
        and model parameters (e.g., Sympathetic and Parasympathetic Tone).
        """
        kR = model_params.get("kR", 25.0)
        p2Ru = model_params.get("p2Ru", 89.97)
        kE = model_params.get("kE", 7.0)
        p2E = model_params.get("p2E", 76.62)
        
        # Sympathetic Tone (Hill activation, inversely proportional to carotid pressure)
        self.states["sympathetic_tone"] = (p2Ru**kR) / (pc_mean**kR + p2Ru**kR)
        
        # Parasympathetic Tone (Hill activation, directly proportional to carotid pressure)
        self.states["parasympathetic_tone"] = (pc_mean**kE) / (pc_mean**kE + p2E**kE)
        
    def copy(self):
        new_state = LatentPhysiologyState()
        new_state.states = self.states.copy()
        return new_state
