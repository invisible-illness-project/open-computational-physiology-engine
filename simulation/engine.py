import numpy as np
from scipy.integrate import solve_ivp

class SimulationEngine:
    """
    Simulates the closed-loop cardiovascular system beat by beat,
    reproducing the original MATLAB solver structure but with Pythonic
    extensions, latent state extraction, and detailed telemetry logging.
    """
    def __init__(self, model, dt=0.01, hrv_noise=0.02):
        self.model = model
        self.dt = dt
        self.hrv_noise = hrv_noise

    def run(self, tilt_params):
        """
        Runs the simulation.
        tilt_params: dict containing:
          - tup: start of tilt (s)
          - tend: end of simulation (s)
          - height: hydrostatic height (cm)
          - angle: tilt angle (degrees)
        """
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
        
        # Latent state lists
        latent_series = {
            "sympathetic_tone": [],
            "parasympathetic_tone": [],
            "baroreflex_gain": [],
            "blood_volume": [],
            "left_ventricular_pressure": [],
            "aortic_flow": [],
            "mitral_flow": [],
            "carotid_pressure": []
        }
        
        current_ts = 0.0
        
        # Set up solver parameters
        # Radau/BDF is suitable for stiff equations (comparable to ode15s)
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
            
            # Extract latent states for each evaluated point in this beat
            for i in range(cycle_len):
                t_val = sol.t[i]
                y_val = sol.y[:, i]
                
                # Sensed mean carotid pressure (pcm is index 5)
                pcm = y_val[5]
                pau = y_val[0] / self.model.params["Cau"]
                
                # Compute tilt angle at this t_val
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
                
                # Carotid pressure
                rho = 1.06
                g = 982.0
                conv = 1333.22
                rhogh_tilde = rho * g * 20.0 * (np.sin(arg * np.pi / 180.0) / conv)
                pc = pau - rhogh_tilde
                
                # Sympathetic Tone: derived from Hill activation function for peripheral resistance
                kR = self.model.params["kR"]
                p2Ru = self.model.params["p2Ru"]
                sym_tone = (p2Ru**kR) / (pcm**kR + p2Ru**kR)
                
                # Parasympathetic Tone: derived from Hill activation function for ventricular elastance
                kE = self.model.params["kE"]
                p2E = self.model.params["p2E"]
                para_tone = (pcm**kE) / (pcm**kE + p2E**kE)
                
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
                
                latent_series["sympathetic_tone"].append(sym_tone)
                latent_series["parasympathetic_tone"].append(para_tone)
                latent_series["baroreflex_gain"].append(kR)
                latent_series["blood_volume"].append(self.model.params["TotalVol"])
                latent_series["left_ventricular_pressure"].append(plv)
                latent_series["aortic_flow"].append(qav)
                latent_series["mitral_flow"].append(qmv)
                latent_series["carotid_pressure"].append(pc)
                
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
        
        # Add last latent state point (using final values)
        latent_series["sympathetic_tone"].append(latent_series["sympathetic_tone"][-1])
        latent_series["parasympathetic_tone"].append(latent_series["parasympathetic_tone"][-1])
        latent_series["baroreflex_gain"].append(latent_series["baroreflex_gain"][-1])
        latent_series["blood_volume"].append(latent_series["blood_volume"][-1])
        latent_series["left_ventricular_pressure"].append(latent_series["left_ventricular_pressure"][-1])
        latent_series["aortic_flow"].append(latent_series["aortic_flow"][-1])
        latent_series["mitral_flow"].append(latent_series["mitral_flow"][-1])
        latent_series["carotid_pressure"].append(latent_series["carotid_pressure"][-1])
        
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
        
        for k, v in latent_series.items():
            results[k] = np.array(v)
            
        return results
