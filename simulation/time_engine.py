import numpy as np

class TimeEngine:
    """
    Manages continuous temporal physiological evolution.
    Models circadian rhythms, homeostatic sleep pressure, recovery dynamics,
    and delayed physiological responses such as Post-Exertional Malaise (PEM).
    """
    def __init__(self, start_hour=8.0):
        self.current_time_hours = start_hour
        self.exertion_history = []  # List of (time_hours, intensity)
        self.pem_active = False
        self.pem_onset_time = None
        self.pem_duration_hours = 24.0

    def step(self, dt_seconds, is_sleeping=False, current_exertion=0.0):
        """
        Advances the simulation clock and returns updated circadian/sleep states.
        dt_seconds: time step in seconds.
        """
        dt_hours = dt_seconds / 3600.0
        self.current_time_hours = (self.current_time_hours + dt_hours) % 24.0
        
        # Track exertion history
        if current_exertion > 0.0:
            self.exertion_history.append((self.current_time_hours, current_exertion))
            # Keep history to last 48 hours of simulation
            if len(self.exertion_history) > 10000:
                self.exertion_history.pop(0)
                
        return self.current_time_hours

    def get_circadian_drive(self):
        """
        Generates endogenous circadian wave: peak sympathetic at 14:00 (2 PM),
        peak parasympathetic (vagal) at 02:00 (2 AM).
        """
        # Cosine wave centered around 14:00
        return float(np.cos(2.0 * np.pi * (self.current_time_hours - 14.0) / 24.0))

    def update_sleep_pressure(self, sleep_pressure, is_sleeping, dt_seconds):
        """
        Accumulates sleep pressure during wakefulness, dissipates it during sleep.
        """
        dt_hours = dt_seconds / 3600.0
        if is_sleeping:
            # Exponential decay during sleep
            decay_const = 0.3  # half-life approx 2.3 hours
            return float(sleep_pressure * np.exp(-decay_const * dt_hours))
        else:
            # Linear accumulation during wakefulness
            accum_rate = 0.05  # Reaches 1.0 after 20 hours awake
            return float(min(1.0, sleep_pressure + accum_rate * dt_hours))

    def update_recovery_and_pem(self, latent_state, dt_seconds, is_sleeping, is_mecfs):
        """
        Updates latent variables for metabolic reserve, inflammation, and recovery.
        Checks for delayed PEM onset if the subject has ME/CFS.
        """
        dt_hours = dt_seconds / 3600.0
        
        # 1. Autonomic Recovery in Sleep
        rec_capacity = latent_state.get("autonomic_recovery_capacity")
        metab = latent_state.get("metabolic_reserve")
        infl = latent_state.get("inflammatory_burden")
        
        if is_sleeping:
            # Recovery is scaled by recovery capacity
            metab = min(1.0, metab + 0.08 * rec_capacity * dt_hours)
            infl = max(0.1, infl - 0.2 * rec_capacity * dt_hours)
        else:
            # Minor metabolic draw during wakefulness
            metab = max(0.0, metab - 0.01 * dt_hours)
            
        # 2. Delayed Post-Exertional Malaise (PEM) for ME/CFS
        # High exertion triggers PEM after a 12-hour delay
        if is_mecfs:
            current_time = self.current_time_hours
            # Check history for exertion 12 hours ago (approx ±1 hour window)
            for ex_time, intensity in list(self.exertion_history):
                # Calculate time difference in a circular 24-hr clock
                time_diff = (current_time - ex_time) % 24.0
                if 11.5 <= time_diff <= 12.5 and intensity > 0.6 and not self.pem_active:
                    print(f"[INFO] Delayed PEM triggered! Exertion of intensity {intensity:.1f} occurred 12 hours ago.")
                    self.pem_active = True
                    self.pem_onset_time = current_time
                    # Remove from history so it doesn't double-trigger
                    self.exertion_history.remove((ex_time, intensity))
                    break
                    
            if self.pem_active:
                # PEM effects: crush metabolic reserve, elevate inflammatory burden
                metab = max(0.1, metab - 0.5)
                infl = min(8.0, infl + 3.0)
                
                # Check if PEM duration has elapsed
                if self.pem_onset_time is not None:
                    pem_diff = (current_time - self.pem_onset_time) % 24.0
                    if pem_diff >= 2.0:  # Resolved after 2 hours for simulation speed demo
                        print("[INFO] Post-Exertional Malaise phase resolving.")
                        self.pem_active = False
                        self.pem_onset_time = None
                        
        latent_state.set("metabolic_reserve", metab)
        latent_state.set("inflammatory_burden", infl)
