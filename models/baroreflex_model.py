import os
import numpy as np
import yaml

class BaroreflexPOTSModel:
    """
    Python implementation of the closed-loop cardiovascular-baroreflex model
    from Geddes et al. 2022. It separates canonical parameter definitions
    (stored in YAML) from the executable model code and applies disease phenotype
    overrides dynamically.
    """
    def __init__(self, phenotype=None, subject=None, kb_path=None):
        self.phenotype = phenotype
        self.subject = subject
        if kb_path is None:
            self.kb_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_base")
        else:
            self.kb_path = kb_path
            
        self.params = {}
        self.initial_state = []
        self.load_parameters()
        self.initialize_steady_state()

    def load_parameters(self):
        # 1. Load nominal parameters from mathematical_models.yaml
        models_file = os.path.join(self.kb_path, "equations", "mathematical_models.yaml")
        with open(models_file, "r") as f:
            model_data = yaml.safe_load(f)
        
        # Extract the parameters list
        nominal_params = {}
        for model in model_data.get("models", []):
            if model.get("model_id") == "pots_baroreflex_response_model":
                for param in model.get("parameters", []):
                    nominal_params[param["symbol"]] = param["nominal_value"]
        
        # 2. Apply Virtual Subject demographic/fitness priors
        if self.subject:
            nominal_params = self.subject.adjust_parameters(nominal_params)
            print(f"[INFO] Applied Virtual Subject priors (Age={self.subject.age}, Sex={self.subject.sex}, Fitness={self.subject.fitness})")

        # 3. Load phenotype overrides via Composable Perturbation Manager
        if self.phenotype:
            from simulation.perturbations import PerturbationManager
            pm = PerturbationManager(kb_path=self.kb_path)
            nominal_params, applied_phenos = pm.apply_perturbations(nominal_params, self.phenotype)
            print(f"[INFO] Applied composed phenotypes: {applied_phenos}")
        
        self.params = nominal_params

    def initialize_steady_state(self):
        # Read parameters loaded from KB
        kR = self.params.get("kR", 25.0)
        kH = self.params.get("kH", 25.0)
        TotalVol = self.params.get("TotalVol", 4500.0)
        
        # Cardiac output and initial heart rate
        TotFlow = TotalVol / 60.0  # ml/s
        HI = 0.96  # initial heart rate (beats/sec)
        
        # Flows
        qaup = TotFlow * 0.80
        qal = TotFlow * 0.20
        qvl = qal
        qalp = qal
        
        # Pressures
        pauD = 80.0
        pauS = 120.0
        pau = (2.0/3.0)*pauD + (1.0/3.0)*pauS
        pm = pau
        pal = pau * 0.99
        pvu = 2.75
        pvl = 3.00
        plvD = 2.5
        Vd = 10.0
        
        Vlvm = 50.0 - Vd
        VlvM = 110.0 - Vd
        
        # Initial Resistances (Ohm's law)
        RaupI = (pau - pvu) / qaup
        self.params["Ral"] = (pau - pal) / qal
        self.params["Rvl"] = (pvl - pvu) / qvl
        RalpI = (pal - pvl) / qalp
        
        # Volumes
        TotalVolSV = TotalVol * 0.85
        Vart = TotalVolSV * 0.15
        Vven = TotalVolSV * 0.85
        
        Vau = Vart * 0.80 * 0.30
        Val = Vart * 0.20 * 0.30
        Vvu = Vven * 0.80 * 0.075
        Vvl = Vven * 0.20 * 0.075
        
        # Compliances
        self.params["Cau"] = Vau / pauD
        self.params["Cvu"] = Vvu / pvu
        self.params["Cal"] = Val / pal
        
        # Venous capacity parameter
        self.params["VMvl"] = 4.0 * Vvl
        self.params["mvl"] = np.log(self.params["VMvl"] / (self.params["VMvl"] - Vvl)) / pvl
        
        # Left ventricular parameters
        EdI = plvD / VlvM
        self.params["Es"] = pauS / Vlvm
        self.params["Vd"] = Vd
        
        # Autonomic time constants
        self.params["taur"] = 12.5
        self.params["tauE"] = 12.5
        self.params["tauH"] = 6.25
        self.params["tauP"] = 2.5
        
        # Controller parameters
        self.params["RaupM"] = 3.0 * RaupI
        self.params["Raupm"] = 0.2 * RaupI
        alpha_u = (RaupI - self.params["Raupm"]) / (self.params["RaupM"] - self.params["Raupm"])
        self.params["p2Ru"] = (pm**kR * alpha_u / (1.0 - alpha_u))**(1.0 / kR)
        
        # Apply RalpM override if phenotype neuropathic was applied
        # In neuropathic POTS, max peripheral resistance in lower body is blunted.
        # RalpM is loaded from parameters (override value), so let's preserve it.
        # But if it's healthy, we compute it as 3 * RalpI.
        if "RalpM" not in self.params or self.params["RalpM"] == 17.88:
            # Let's compute default
            self.params["RalpM"] = 3.0 * RalpI
        
        # If the phenotype is neuropathic, self.params['RalpM'] was already set to 6.5.
        # We compute Ralpm as 0.2 * RalpI
        self.params["Ralpm"] = 0.2 * RalpI
        alpha_l = (RalpI - self.params["Ralpm"]) / (self.params["RalpM"] - self.params["Ralpm"])
        # Handle cases where alpha_l is out of bounds or negative due to phenotype override
        alpha_l = max(0.001, min(0.999, alpha_l))
        self.params["p2Ra"] = (pm**kR * alpha_l / (1.0 - alpha_l))**(1.0 / kR)
        
        # Contractility
        self.params["EdM"] = 1.25 * EdI
        self.params["Edm"] = 0.01 * EdI
        self.params["kE"] = 7.0
        alpha_E = (EdI - self.params["Edm"]) / (self.params["EdM"] - self.params["Edm"])
        alpha_E = max(0.001, min(0.999, alpha_E))
        self.params["p2E"] = (pm**self.params["kE"] * (1.0 - alpha_E) / alpha_E)**(1.0 / self.params["kE"])
        
        # Heart rate
        self.params["HM"] = 200.0 / 60.0  # equivalent to 200 bpm
        self.params["Hm"] = 0.3
        alpha_H = (HI - self.params["Hm"]) / (self.params["HM"] - self.params["Hm"])
        alpha_H = max(0.001, min(0.999, alpha_H))
        self.params["p2H"] = (pm**kH * alpha_H / (1.0 - alpha_H))**(1.0 / kH)
        
        # Initial conditions: y = [Vau, Vvu, Val, Vvl, Vlv, pcm, Raup, Ralp, Ed, Hc]
        self.initial_state = [Vau, Vvu, Val, Vvl, VlvM, pm, RaupI, RalpI, EdI, HI]

    def compute_derivatives(self, t, y, current_T, current_ts, tilt_params):
        """
        Calculates the derivatives for the 10 state variables.
        y = [Vau, Vvu, Val, Vvl, Vlv, pcm, Raup, Ralp, Ed, Hc]
        """
        # Unpack state variables
        Vau, Vvu, Val, Vvl, Vlv, pcm, Raup, Ralp, Ed, Hc = y
        
        # Unpack parameters
        Ral = self.params["Ral"]
        Rvl = self.params["Rvl"]
        Cau = self.params["Cau"]
        Cal = self.params["Cal"]
        Cvu = self.params["Cvu"]
        VMvl = self.params["VMvl"]
        mvl = self.params["mvl"]
        Es = self.params["Es"]
        Vd = self.params["Vd"]
        
        taur = self.params["taur"]
        tauE = self.params["tauE"]
        tauH = self.params["tauH"]
        tauP = self.params["tauP"]
        
        kR = self.params["kR"]
        kE = self.params["kE"]
        kH = self.params["kH"]
        
        RaupM = self.params["RaupM"]
        Raupm = self.params["Raupm"]
        p2Ru = self.params["p2Ru"]
        
        RalpM = self.params["RalpM"]
        Ralpm = self.params["Ralpm"]
        p2Ra = self.params["p2Ra"]
        
        EdM = self.params["EdM"]
        Edm = self.params["Edm"]
        p2E = self.params["p2E"]
        
        HM = self.params["HM"]
        Hm = self.params["Hm"]
        p2H = self.params["p2H"]
        
        # 1. Pressures
        pau = Vau / Cau
        pal = Val / Cal
        
        # Avoid log of negative value for lower venous pressure
        v_diff = max(1e-3, VMvl - Vvl)
        pvl = (1.0 / mvl) * np.log(VMvl / v_diff)
        pvu = Vvu / Cvu
        
        # 2. Tilt and Hydrostatic Column
        # tilt_params: {"tup": 200, "tend": 300, "height": 25, "angle": 60}
        tup = tilt_params.get("tup", 200.0)
        tend = tilt_params.get("tend", 300.0)
        height = tilt_params.get("height", 25.0)
        max_angle = tilt_params.get("angle", 60.0)
        
        rho = 1.06
        g = 982.0
        conv = 1333.22
        
        # Calculate tilt angle over time
        if t < tup:
            arg = 0.0
        elif t < tup + 14.0:
            a = max_angle / 14.0
            arg = a * (t - tup)
        elif t < tend:
            arg = max_angle
        elif t < tend + 14.0:
            a = max_angle / 14.0
            arg = max_angle - a * (t - tend)
        else:
            arg = 0.0
            
        rhogh = rho * g * height * (np.sin(arg * np.pi / 180.0) / conv)
        
        # Pressure difference aortic-carotid (distance = 20cm)
        rhogh_tilde = rho * g * 20.0 * (np.sin(arg * np.pi / 180.0) / conv)
        pc = pau - rhogh_tilde
        
        # 3. Ventricular Elastance and Pressure
        # Ts and Tr calculations based on current cycle length T
        Ts = 0.001 * (0.82 / 1.82) * (522.0 - 1.87 * 60.0 / current_T)
        Tr = 0.001 * (1.0 / 1.82) * (522.0 - 1.87 * 60.0 / current_T)
        
        t_cycle = t - current_ts
        if t_cycle <= Ts:
            Elv = Ed + ((Es - Ed) / 2.0) * (1.0 - np.cos(np.pi * t_cycle / Ts))
        elif t_cycle <= Ts + Tr:
            Elv = Ed + ((Es - Ed) / 2.0) * (np.cos(np.pi * (t_cycle - Ts) / Tr) + 1.0)
        else:
            Elv = Ed
            
        plv = Elv * Vlv
        
        # 4. Flows (Valves & Ohmic transport)
        Rav = 0.0001
        Rmv = 0.0001
        
        qav = (plv - pau) / Rav if plv > pau else 0.0
        qmv = (pvu - plv) / Rmv if pvu > plv else 0.0
        
        qal = (pau - pal + rhogh) / Ral
        qaup = (pau - pvu) / Raup
        qalp = (pal - pvl) / Ralp
        
        qvl = (pvl - pvu - rhogh) / Rvl if pvl > (pvu + rhogh) else 0.0
        
        # 5. Controller derivatives
        dpcm = (pc - pcm) / tauP
        
        # Upper peripheral resistance target and ODE
        Raupf = (RaupM - Raupm) * (p2Ru**kR) / (pcm**kR + p2Ru**kR) + Raupm
        dRaup = (-Raup + Raupf) / taur
        
        # Lower peripheral resistance target and ODE
        Ralpf = (RalpM - Ralpm) * (p2Ra**kR) / (pcm**kR + p2Ra**kR) + Ralpm
        dRalp = (-Ralp + Ralpf) / taur
        
        # End diastolic elastance target and ODE (parasympathetic loop)
        Edf = (EdM - Edm) * (pcm**kE) / (pcm**kE + p2E**kE) + Edm
        dEd = (-Ed + Edf) / tauE
        
        # Heart rate target and ODE
        Hf = (HM - Hm) * (p2H**kH) / (pcm**kH + p2H**kH) + Hm
        dHc = (-Hc + Hf) / tauH
        
        # 6. Mass conservation derivatives
        dVau = qav - qal - qaup
        dVvu = qvl + qaup - qmv
        dVal = qal - qalp
        dVvl = qalp - qvl
        dVlv = qmv - qav
        
        return [dVau, dVvu, dVal, dVvl, dVlv, dpcm, dRaup, dRalp, dEd, dHc]
