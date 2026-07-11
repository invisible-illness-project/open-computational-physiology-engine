import numpy as np
from scipy.integrate import solve_ivp
from simulation.latent_physiology import LatentPhysiologyState
from simulation.behavior import BehaviorModel
from simulation.symptoms import SymptomFramework
from simulation.time_engine import TimeEngine

class SimulationEngine:
    """
    Simulates the closed-loop cardiovascular system beat by beat,
    reproducing the original MATLAB solver structure but with Pythonic
    extensions, latent state extraction, behavioral/symptom loops, and temporal tracking.
    """
    def __init__(self, model, dt=0.01, hrv_noise=0.02):
        self.model = model
        self.dt = dt
        self.hrv_noise = hrv_noise
        
        # Instantiate architectural subsystems
        self.latent_state = LatentPhysiologyState()
        self.behavior = BehaviorModel()
        self.symptoms = SymptomFramework()
        self.time_engine = TimeEngine()

    def run(self, tilt_params):
        """
        Runs the simulation.
        tilt_params: dict containing:
          - tup: start of tilt (s)
          - tend: end of simulation (s)
          - height: hydrostatic height (cm)
          - angle: tilt angle (degrees)
          - active_behavior: optional string trigger (e.g. 'exercise', 'meal')
        """
        # Set up behavior if specified in tilt_params
        active_behavior = tilt_params.get("active_behavior", "rest")
        self.behavior.trigger_behavior(active_behavior)
        
        # Read initial values
        y_init = list(self.model.initial_state)
        
        # Start time and initial cycle length
        t_start = 0.0
        t_end = tilt_params.get("tend", 300.0)
        
        # Initial heart rate from state variables
        H = y_init[9]  # Hc is index 9
        T = round((1.0 / H) / self.dt) * self.dt
        
        # Output lists
        time_series = []
        state_series = []
        
        # Latent state and symptom series lists
        latent_keys = [
            "sympathetic_tone", "parasympathetic_tone", "baroreflex_gain",
            "blood_volume", "left_ventricular_pressure", "aortic_flow",
            "mitral_flow", "carotid_pressure", "circadian_drive",
            "sleep_pressure", "hydration", "stress_load",
            "inflammatory_burden", "metabolic_reserve", "hormonal_state",
            "autonomic_recovery_capacity"
        ]
        symptom_keys = [
            "fatigue", "brain_fog", "pain", "orthostatic_intolerance",
            "palpitations", "sleepiness", "dizziness"
        ]
        
        output_series = {k: [] for k in (latent_keys + symptom_keys)}
        
        current_ts = 0.0
        method = "Radau"
        
        # Loop beat-by-beat
        while current_ts < t_end:
            # Grid of time points for current cardiac cycle
            n_steps = int(round(T / self.dt))
            if n_steps < 2:
                n_steps = 2
            
            t_span_cycle = [current_ts, current_ts + T]
            t_eval_cycle = np.linspace(current_ts, current_ts + T, n_steps, endpoint=True)
            
            # Define derivative function for this cardiac cycle
            def derivatives_wrapper(t, y):
                return self.model.compute_derivatives(t, y, T, current_ts, tilt_params)
            
            # Integrate the ODE system over the cycle
            sol = solve_ivp(
                fun=derivatives_wrapper,
                t_span=t_span_cycle,
                y0=y_init,
                t_eval=t_eval_cycle,
                method=method,
                rtol=1e-6,
                atol=1e-8
            )
            
            # If solve failed, break
            if not sol.success:
                print(f"[ERROR] ODE integration failed at t = {current_ts}")
                break
                
            # Append cycle solutions (excluding last element to avoid duplicating boundaries)
            cycle_len = len(sol.t) - 1
            if cycle_len < 1:
                cycle_len = 1
                
            time_series.extend(sol.t[:cycle_len])
            state_series.extend(sol.y[:, :cycle_len].T)
            
            # Update temporal components for this cardiac cycle
            # Advance simulation clock (convert cycle length T to seconds)
            self.time_engine.step(T)
            
            # Update homeostatic sleep pressure
            sleep_pres = self.time_engine.update_sleep_pressure(
                self.latent_state.get("sleep_pressure"), 
                is_sleeping=False, 
                dt_seconds=T
            )
            self.latent_state.set("sleep_pressure", sleep_pres)
            self.latent_state.set("circadian_drive", self.time_engine.get_circadian_drive())
            
            # Update recovery and PEM
            is_mecfs = self.model.phenotype is not None and "mecfs" in self.model.phenotype
            self.time_engine.update_recovery_and_pem(self.latent_state, T, is_sleeping=False, is_mecfs=is_mecfs)
            
            # Modulate latent states with current behavior
            self.behavior.modulate_latent_states(self.latent_state, current_ts)
            
            # Feed current hemodynamic state back into parameters
            self.model.params = self.behavior.modulate_parameters(self.model.params, self.latent_state)
            
            # Extract latent states and symptoms for each evaluated point in this beat
            for i in range(cycle_len):
                t_val = sol.t[i]
                y_val = sol.y[:, i]
                
                # Sensed mean carotid pressure (pcm is index 5)
                pcm = y_val[5]
                pau = y_val[0] / self.model.params["Cau"]
                
                # Compute tilt angle at this t_val for carotid pressure height effect
                tup = tilt_params.get("tup", 200.0)
                tend = tilt_params.get("tend", 300.0)
                max_angle = tilt_params.get("angle", 60.0)
                if t_val < tup:
                    arg = 0.0
                elif t_val < tup + 14.0:
                    arg = (max_angle / 14.0) * (t_val - tup)
                elif t_val < tend:
                    arg = max_angle
                elif t_val < tend + 14.0:
                    arg = max_angle - (max_angle / 14.0) * (t_val - tend)
                else:
                    arg = 0.0
                
                # Carotid pressure height adjustment
                rho = 1.06
                g = 982.0
                conv = 1333.22
                rhogh_tilde = rho * g * 20.0 * (np.sin(arg * np.pi / 180.0) / conv)
                pc = pau - rhogh_tilde
                
                # Update derived autonomic states
                self.latent_state.update_derived_states(pcm, self.model.params)
                
                # Compute symptoms probabilistically from updated state
                current_hr = y_val[9] * 60.0  # bpm
                symptom_scores = self.symptoms.compute_symptoms(self.latent_state, current_hr, pcm)
                
                # Apply feedback loops to behavior
                self.behavior.check_behavioral_feedback(symptom_scores)
                
                # Ventricular Elastance and Pressure
                Ts = 0.001 * (0.82 / 1.82) * (522.0 - 1.87 * 60.0 / T)
                Tr = 0.001 * (1.0 / 1.82) * (522.0 - 1.87 * 60.0 / T)
                t_cycle = t_val - current_ts
                
                if t_cycle <= Ts:
                    Elv = y_val[8] + ((self.model.params["Es"] - y_val[8]) / 2.0) * (1.0 - np.cos(np.pi * t_cycle / Ts))
                elif t_cycle <= Ts + Tr:
                    Elv = y_val[8] + ((self.model.params["Es"] - y_val[8]) / 2.0) * (np.cos(np.pi * (t_cycle - Ts) / Tr) + 1.0)
                else:
                    Elv = y_val[8]
                    
                plv = Elv * y_val[4] # Elv * Vlv
                
                # Aortic and mitral flows
                qav = (plv - pau) / 0.0001 if plv > pau else 0.0
                pvu = y_val[1] / self.model.params["Cvu"]
                qmv = (pvu - plv) / 0.0001 if pvu > plv else 0.0
                
                # Log all latent variable states
                output_series["sympathetic_tone"].append(self.latent_state.get("sympathetic_tone"))
                output_series["parasympathetic_tone"].append(self.latent_state.get("parasympathetic_tone"))
                output_series["baroreflex_gain"].append(self.model.params["kR"])
                output_series["blood_volume"].append(self.model.params["TotalVol"])
                output_series["left_ventricular_pressure"].append(plv)
                output_series["aortic_flow"].append(qav)
                output_series["mitral_flow"].append(qmv)
                output_series["carotid_pressure"].append(pc)
                output_series["circadian_drive"].append(self.latent_state.get("circadian_drive"))
                output_series["sleep_pressure"].append(self.latent_state.get("sleep_pressure"))
                output_series["hydration"].append(self.latent_state.get("hydration"))
                output_series["stress_load"].append(self.latent_state.get("stress_load"))
                output_series["inflammatory_burden"].append(self.latent_state.get("inflammatory_burden"))
                output_series["metabolic_reserve"].append(self.latent_state.get("metabolic_reserve"))
                output_series["hormonal_state"].append(self.latent_state.get("hormonal_state"))
                output_series["autonomic_recovery_capacity"].append(self.latent_state.get("autonomic_recovery_capacity"))
                
                # Log all symptom states
                for sk in symptom_keys:
                    output_series[sk].append(symptom_scores[sk])
                
            # Set initial conditions for next cycle
            y_init = sol.y[:, -1]
            current_ts = sol.t[-1]
            
            # Determine next cycle length T from the heart rate Hc at the end of the beat
            # Add random HRV noise
            H_end = y_init[9] # Hc
            base_T = 1.0 / H_end
            noise = np.random.uniform(-1.0, 1.0) * self.hrv_noise
            T = round((base_T * (1.0 + noise)) / self.dt) * self.dt
            
        # Add last point
        time_series.append(current_ts)
        state_series.append(y_init)
        
        # Carry over final states to ensure array length matches
        for k in output_series.keys():
            output_series[k].append(output_series[k][-1])
            
        # Format outputs as numpy arrays
        time_arr = np.array(time_series)
        state_arr = np.array(state_series)
        
        results = {
            "time": time_arr,
            "Vau": state_arr[:, 0],
            "Vvu": state_arr[:, 1],
            "Val": state_arr[:, 2],
            "Vvl": state_arr[:, 3],
            "Vlv": state_arr[:, 4],
            "pcm": state_arr[:, 5],
            "Raup": state_arr[:, 6],
            "Ralp": state_arr[:, 7],
            "Ed": state_arr[:, 8],
            "Hc": state_arr[:, 9],
            "pau": state_arr[:, 0] / self.model.params["Cau"],
            "pal": state_arr[:, 2] / self.model.params["Cal"],
            "pvu": state_arr[:, 1] / self.model.params["Cvu"],
        }
        
        for k, v in output_series.items():
            results[k] = np.array(v)
            
        return results
