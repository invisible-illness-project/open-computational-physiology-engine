import os
import numpy as np
import yaml


# Width of the smooth hydrostatic venous-return gate transition (mmHg).
# Physiology-preserving: 0.1 mmHg is negligible against physiological
# driving pressures, and softplus(0.25, 0.1) ~= 0.25, so the supine
# operating-point conductance matches the ideal (hard) gate exactly.
_QVL_GATE_W = 0.1


def _softplus(x, w):
    """Numerically stable smooth approximation of max(x, 0) with transition
    width w: w * log(1 + exp(x / w))."""
    if x > 40.0 * w:
        return x
    return w * np.log1p(np.exp(x / w))


class BaroreflexPOTSModel:
    """
    Python implementation of the closed-loop cardiovascular-baroreflex model
    from Geddes et al. 2022. It separates canonical parameter definitions
    (stored in YAML) from the executable model code and applies disease phenotype
    overrides dynamically.

    Cycle 2 extension (venous/orthostatic physiology): the state vector is
    extended from 10 to 12 integrator states with
      Vvm - baroreflex venomotor reflex (reduction of lower venous capacity,
            Heldt 2002 structure, DOI 10.1152/japplphysiol.00241.2001),
      Vsr - venous stress-relaxation creep (slow capacity increase under
            sustained venous load, van Heusden 2006, DOI 10.1152/ajpheart.01268.2004),
    and the logarithmic lower-venous P-V law operates on the effective
    capacity VMvl - Vvm + Vsr. Lower/upper venous capacities (VMvl, Cvu) are
    rescaled to the physiological 500-1000 ml orthostatic pooling range
    (machine-proposed fit, tier C in the knowledge base).
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

        # Keep a pristine copy of the KB nominal parameter set. It is used by
        # initialize_steady_state() as the reference point for scaling the
        # initial compartment volumes when TotalVol is perturbed; it is never
        # written back into self.params.
        self.kb_nominal_params = dict(nominal_params)

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
        """
        Solve for the initial dynamic state (integrator initial conditions)
        consistent with the currently-applied parameter set.

        This method NEVER writes to self.params. All parameters (gains, time
        constants, compliances, volumes, resistances, Hill coefficients and
        half-saturation pressures) come from the knowledge base, disease
        perturbations and VirtualSubject priors, and are treated as sacred.
        Only the 12 integrator initial conditions are computed here:

            y0 = [Vau, Vvu, Val, Vvl, Vlv, pcm, Raup, Ralp, Ed, Hc, Vvm, Vsr]

        Initialization strategy (supine steady state):
        - Controller states (Raup, Ralp, Ed, Hc) are placed exactly on their
          Hill-equation targets at the supine mean carotid operating point, so
          every first-order control loop starts with dX/dt = 0.
        - Compartment volumes are derived from target filling pressures and the
          (sacred) compliance/capacity parameters, so the initial pressures
          implied by V/C are consistent with the parameter set.
        - Total blood volume perturbations (hypovolemia, fludrocortisone,
          demographic priors) are absorbed by scaling the compliant venous
          reservoir compartments, leaving the baroreflex-defended arterial
          pressures anchored at the reference operating point.
        """
        p = self.params

        # --- Supine operating point (state-initialization heuristics, NOT
        # parameters). Values reproduce the Geddes et al. 2022 healthy baseline.
        pcm0 = 93.333                     # mean carotid pressure setpoint (mmHg)
        pauD = 80.0                       # target diastolic upper arterial pressure
        pau_mean = (2.0 / 3.0) * pauD + (1.0 / 3.0) * 120.0  # ~93.33 mmHg
        pal0 = pau_mean * 0.99            # target lower arterial pressure
        pvu0 = 2.75                       # target upper venous pressure
        pvl0 = 3.00                       # target lower venous pressure

        # --- Controller states: exact steady state of each control loop at the
        # operating point (X0 = X_target(pcm0)  =>  dX/dt = 0).
        kR = p["kR"]
        kE = p["kE"]
        kH = p["kH"]

        Raup0 = (p["RaupM"] - p["Raupm"]) * (p["p2Ru"]**kR) / (pcm0**kR + p["p2Ru"]**kR) + p["Raupm"]
        Ralp0 = (p["RalpM"] - p["Ralpm"]) * (p["p2Ra"]**kR) / (pcm0**kR + p["p2Ra"]**kR) + p["Ralpm"]
        Ed0 = (p["EdM"] - p["Edm"]) * (pcm0**kE) / (pcm0**kE + p["p2E"]**kE) + p["Edm"]
        H0 = (p["HM"] - p["Hm"]) * (p["p2H"]**kH) / (pcm0**kH + p["p2H"]**kH) + p["Hm"]

        # --- Venomotor reflex state (Cycle 2, Heldt 2002 structure):
        # baroreflex-driven reduction of lower venous capacity. Start on the
        # Hill target at the supine operating point (dVvm/dt = 0).
        kV = p["kV"]
        Vvm0 = p["dV_veno_max"] * (p["p2V"]**kV) / (pcm0**kV + p["p2V"]**kV)

        # --- Venous stress-relaxation (creep) state (Cycle 2, van Heusden
        # 2006): supine pvl sits at the creep threshold, so creep target = 0.
        Vsr0 = p["G_sr"] * max(0.0, pvl0 - p["pvl_sr0"])

        # --- Compartment volumes from target filling pressures and the sacred
        # compliance / capacity parameters.
        Vau0 = pauD * p["Cau"]
        Val0 = pal0 * p["Cal"]
        Vvu0 = pvu0 * p["Cvu"]
        # Invert the logarithmic lower-venous pressure-volume relation against
        # the EFFECTIVE supine capacity (VMvl - Vvm0 + Vsr0):
        #   pvl = (1/mvl) * ln(VM_eff / (VM_eff - Vvl))  =>  Vvl = VM_eff * (1 - exp(-mvl*pvl))
        VMvl_eff0 = p["VMvl"] - Vvm0 + Vsr0
        Vvl0 = VMvl_eff0 * (1.0 - np.exp(-p["mvl"] * pvl0))

        # Blood-volume perturbations are absorbed by the compliant venous
        # reservoir (the venous system holds the bulk of circulating volume and
        # buffers filling-pressure changes); arterial volumes stay anchored to
        # the defended pressure setpoint.
        total_vol_ref = self.kb_nominal_params.get("TotalVol", 4500.0)
        vol_scale = p.get("TotalVol", total_vol_ref) / total_vol_ref
        Vvu0 *= vol_scale
        Vvl0 *= vol_scale

        # Left ventricular end-diastolic volume (start of the cardiac cycle).
        Vlv0 = 110.0 - p["Vd"]

        # Initial conditions:
        # y = [Vau, Vvu, Val, Vvl, Vlv, pcm, Raup, Ralp, Ed, Hc, Vvm, Vsr]
        self.initial_state = [Vau0, Vvu0, Val0, Vvl0, Vlv0, pcm0, Raup0, Ralp0, Ed0, H0, Vvm0, Vsr0]

    def compute_derivatives(self, t, y, current_T, current_ts, tilt_params):
        """
        Calculates the derivatives for the 12 state variables.
        y = [Vau, Vvu, Val, Vvl, Vlv, pcm, Raup, Ralp, Ed, Hc, Vvm, Vsr]

        Cycle 2 extension (venous/orthostatic physiology):
        - Vvm: baroreflex-driven venomotor reflex state (mL of lower venous
          capacity reduction), Heldt et al. 2002 structure (PMID 11842064).
        - Vsr: venous stress-relaxation (creep) state (mL of slow capacity
          increase under sustained venous load), van Heusden et al. 2006
          (PMID 16632542).
        The effective lower venous capacity is VMvl - Vvm + Vsr; the
        logarithmic P-V law operates on that effective capacity.
        """
        # Unpack state variables
        Vau, Vvu, Val, Vvl, Vlv, pcm, Raup, Ralp, Ed, Hc, Vvm, Vsr = y

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

        # Cycle 2 venomotor / stress-relaxation parameters
        dV_veno_max = self.params["dV_veno_max"]
        p2V = self.params["p2V"]
        kV = self.params["kV"]
        tau_veno = self.params["tau_veno"]
        G_sr = self.params["G_sr"]
        tau_sr = self.params["tau_sr"]
        pvl_sr0 = self.params["pvl_sr0"]
        
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
        
        # 1. Pressures (enforced physical non-negativity floors)
        pau = max(0.0, Vau) / Cau
        pal = max(0.0, Val) / Cal
        pvu = max(0.0, Vvu) / Cvu
        
        # Effective lower venous capacity: nominal capacity reduced by the
        # venomotor reflex (sympathetic venoconstriction) and increased by
        # slow stress-relaxation creep (Cycle 2 extension).
        VMvl_eff = VMvl - Vvm + Vsr
        # Avoid log of negative value or exceeding volume capacity for lower venous compartment
        v_diff = max(1.0, VMvl_eff - Vvl)
        pvl = (1.0 / mvl) * np.log(VMvl_eff / v_diff)
        pvl = max(0.0, pvl)
        
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
        
        # Valves are ideal diodes with a narrow smooth transition (0.05 mmHg)
        # instead of a hard on/off switch: physiology-preserving (the
        # transition width is negligible compared to physiological driving
        # pressures, and the regurgitant tail is <1 ml/s at >0.3 mmHg reverse
        # bias) but C^1-smooth, which removes relay chatter in the
        # beat-to-beat integration of the stiff valve dynamics.
        qav = _softplus(plv - pau, 0.05) / Rav
        qmv = _softplus(pvu - plv, 0.05) / Rmv
        
        qal = (pau - pal + rhogh) / Ral
        qaup = (pau - pvu) / Raup
        qalp = (pal - pvl) / Ralp
        
        # Hydrostatic venous-return gate, smoothed with a 0.1 mmHg transition
        # (negligible vs physiological driving pressures, and matched to the
        # hard-gate flow at the supine operating point so the baseline
        # equilibrium is unchanged).
        qvl = _softplus(pvl - pvu - rhogh, _QVL_GATE_W) / Rvl
        
        # 5. Controller derivatives
        dpcm = (pc - pcm) / tauP

        # Hill targets are evaluated at the non-negative part of pcm: negative
        # carotid pressure is physiologically impossible, and pcm**k with a
        # negative base is numerically undefined for large k.
        pcm_pow = max(0.0, pcm)
        
        # Upper peripheral resistance target and ODE
        Raupf = (RaupM - Raupm) * (p2Ru**kR) / (pcm_pow**kR + p2Ru**kR) + Raupm
        dRaup = (-Raup + Raupf) / taur
        
        # Lower peripheral resistance target and ODE
        Ralpf = (RalpM - Ralpm) * (p2Ra**kR) / (pcm_pow**kR + p2Ra**kR) + Ralpm
        dRalp = (-Ralp + Ralpf) / taur
        
        # End diastolic elastance target and ODE (parasympathetic loop)
        Edf = (EdM - Edm) * (pcm_pow**kE) / (pcm_pow**kE + p2E**kE) + Edm
        dEd = (-Ed + Edf) / tauE
        
        # Heart rate target and ODE
        Hf = (HM - Hm) * (p2H**kH) / (pcm_pow**kH + p2H**kH) + Hm
        dHc = (-Hc + Hf) / tauH

        # Venomotor reflex target and ODE (Cycle 2; Heldt 2002 structure):
        # falling carotid pressure recruits venoconstriction, reducing lower
        # venous capacity and mobilizing pooled blood back to the thorax.
        Vvmf = dV_veno_max * (p2V**kV) / (pcm_pow**kV + p2V**kV)
        dVvm = (-Vvm + Vvmf) / tau_veno

        # Venous stress-relaxation (creep) target and ODE (Cycle 2; van
        # Heusden 2006): sustained elevation of lower venous pressure slowly
        # increases venous capacity, spreading pooling over tens of seconds
        # to minutes instead of completing within ~30 s.
        Vsrf = G_sr * max(0.0, pvl - pvl_sr0)
        dVsr = (-Vsr + Vsrf) / tau_sr
        
        # 6. Mass conservation derivatives (with boundary non-negativity clamping)
        dVau = qav - qal - qaup
        if Vau <= 0.0 and dVau < 0.0: dVau = 0.0
        dVvu = qvl + qaup - qmv
        if Vvu <= 0.0 and dVvu < 0.0: dVvu = 0.0
        dVal = qal - qalp
        if Val <= 0.0 and dVal < 0.0: dVal = 0.0
        dVvl = qalp - qvl
        if Vvl <= 0.0 and dVvl < 0.0: dVvl = 0.0
        dVlv = qmv - qav
        if Vlv <= 0.0 and dVlv < 0.0: dVlv = 0.0
        
        return [dVau, dVvu, dVal, dVvl, dVlv, dpcm, dRaup, dRalp, dEd, dHc, dVvm, dVsr]
