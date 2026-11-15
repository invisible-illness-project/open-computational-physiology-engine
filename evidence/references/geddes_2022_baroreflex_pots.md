# Postural orthostatic tachycardia syndrome explained using a baroreflex response model

---
publication:
  title: "Postural orthostatic tachycardia syndrome explained using a baroreflex response model"
  doi: "10.1098/rsif.2022.0220"
  pmid: "36069002"
  pmcid: "PMC9399868"
  journal: "Journal of The Royal Society Interface"
  year: 2022
  authors:
    - "Justen R. Geddes"
    - "Johnny T. Ottesen"
    - "Jesper Mehlsen"
    - "Mette S. Olufsen"
  evidence_level: "Level 4 (In silico computational modeling and validation)"
  study_type: "Computational physiological modeling and simulation with clinical validation"
  confidence_score: 9

population:
  cohorts:
    - cohort_id: "pots_clinical_cohort"
      sample_size: 25
      sex:
        male: null
        female: null
        other: null
      age:
        mean: null
        sd: null
        min: null
        max: null
      bmi:
        mean: null
        sd: null
      health_status: "POTS"
      severity: "unspecified"
      medications: []
      comorbidities: []
      inclusion_criteria:
        - "Sustained HR increase of >=30 bpm (or >=40 bpm for ages 12-19) within 10 minutes of standing/tilt in the absence of orthostatic hypotension"
      exclusion_criteria: []
    - cohort_id: "healthy_control_cohort"
      sample_size: 25
      sex:
        male: null
        female: null
        other: null
      age:
        mean: null
        sd: null
        min: null
        max: null
      bmi:
        mean: null
        sd: null
      health_status: "Healthy Control"
      severity: "healthy"
      medications: []
      comorbidities: []
      inclusion_criteria: []
      exclusion_criteria: []

variables:
  - name: "Upper Arterial Volume"
    symbol: "Vau"
    units: "ml"
    baseline_value:
      mean: 137.7
      sd: null
    measurement_method: "derived_from_compliance_and_pressure"
  - name: "Upper Venous Volume"
    symbol: "Vvu"
    units: "ml"
    baseline_value:
      mean: 195.075
      sd: null
    measurement_method: "derived_from_compliance_and_pressure"
  - name: "Lower Arterial Volume"
    symbol: "Val"
    units: "ml"
    baseline_value:
      mean: 34.425
      sd: null
    measurement_method: "derived_from_compliance_and_pressure"
  - name: "Lower Venous Volume"
    symbol: "Vvl"
    units: "ml"
    baseline_value:
      mean: 48.769
      sd: null
    measurement_method: "derived_from_compliance_and_pressure"
  - name: "Left Ventricular Volume"
    symbol: "Vlv"
    units: "ml"
    baseline_value:
      mean: 100.0
      sd: null
    measurement_method: "derived_from_elastance_and_pressure"
  - name: "Mean Carotid Pressure"
    symbol: "pcm"
    units: "mmHg"
    baseline_value:
      mean: 93.333
      sd: null
    measurement_method: "derived_from_upper_arterial_pressure_and_tilt"
  - name: "Upper Peripheral Resistance"
    symbol: "Raup"
    units: "mmHg*s/ml"
    baseline_value:
      mean: 1.5097
      sd: null
    measurement_method: "derived_from_flow_and_pressure_gradients"
  - name: "Lower Peripheral Resistance"
    symbol: "Ralp"
    units: "mmHg*s/ml"
    baseline_value:
      mean: 5.96
      sd: null
    measurement_method: "derived_from_flow_and_pressure_gradients"
  - name: "End Diastolic Elastance"
    symbol: "Ed"
    units: "mmHg/ml"
    baseline_value:
      mean: 0.025
      sd: null
    measurement_method: "derived_from_diastolic_pressure_and_volume"
  - name: "Heart Rate"
    symbol: "Hc"
    units: "bps"
    baseline_value:
      mean: 0.96
      sd: null
    measurement_method: "ECG/Derived"

mathematical_models:
  - model_name: "Closed-Loop Lumped Cardiovascular Compartment Model with Baroreflex Feedback"
    equations:
      - label: "Upper Arterial Pressure"
        latex: 'p_{au}(t) = \frac{V_{au}(t)}{C_{au}}'
      - label: "Lower Arterial Pressure"
        latex: 'p_{al}(t) = \frac{V_{al}(t)}{C_{al}}'
      - label: "Upper Venous Pressure"
        latex: 'p_{vu}(t) = \frac{V_{vu}(t)}{C_{vu}}'
      - label: "Lower Venous Pressure"
        latex: 'p_{vl}(t) = \frac{1}{m_{vl}} \ln\left(\frac{V_{Mvl}}{V_{Mvl} - V_{vl}(t)}\right)'
      - label: "Left Ventricular Pressure"
        latex: 'p_{lv}(t) = E_{lv}(t) V_{lv}(t)'
      - label: "Varying Left Ventricular Elastance"
        latex: 'E_{lv}(t_{cycle}) = \begin{cases} E_d + \frac{E_s - E_d}{2} \left(1 - \cos\left(\frac{\pi t_{cycle}}{T_s}\right)\right) & t_{cycle} \le T_s \\ E_d + \frac{E_s - E_d}{2} \left(\cos\left(\frac{\pi (t_{cycle} - T_s)}{T_r}\right) + 1\right) & T_s < t_{cycle} \le T_s + T_r \\ E_d & t_{cycle} > T_s + T_r \end{cases}'
      - label: "Systolic Contraction Time Scale"
        latex: 'T_s = 0.001 \left(\frac{0.82}{1.82}\right) \left(522 - 1.87 \frac{60}{T}\right)'
      - label: "Systolic Relaxation Time Scale"
        latex: 'T_r = 0.001 \left(\frac{1}{1.82}\right) \left(522 - 1.87 \frac{60}{T}\right)'
      - label: "Carotid Sinus Pressure"
        latex: 'p_c(t) = p_{au}(t) - \rho g h_c \frac{\sin(\theta(t))}{conv}'
      - label: "Mean Carotid Pressure Tracking"
        latex: '\frac{d p_{cm}(t)}{d t} = \frac{p_c(t) - p_{cm}(t)}{\tau_P}'
      - label: "Upper Peripheral Resistance Control"
        latex: '\frac{d R_{aup}(t)}{d t} = \frac{-R_{aup}(t) + R_{aupf}(p_{cm}(t))}{\tau_r}'
      - label: "Upper Peripheral Resistance Target Hill Equation"
        latex: 'R_{aupf}(p_{cm}) = (R_{aupM} - R_{aupm}) \frac{p_{2Ru}^{k_R}}{p_{cm}^{k_R} + p_{2Ru}^{k_R}} + R_{aupm}'
      - label: "Lower Peripheral Resistance Control"
        latex: '\frac{d R_{alp}(t)}{d t} = \frac{-R_{alp}(t) + R_{alpf}(p_{cm}(t))}{\tau_r}'
      - label: "Lower Peripheral Resistance Target Hill Equation"
        latex: 'R_{alpf}(p_{cm}) = (R_{alpM} - R_{alpm}) \frac{p_{2Ra}^{k_R}}{p_{cm}^{k_R} + p_{2Ra}^{k_R}} + R_{alpm}'
      - label: "End Diastolic Elastance Control"
        latex: '\frac{d E_d(t)}{d t} = \frac{-E_d(t) + E_{df}(p_{cm}(t))}{\tau_E}'
      - label: "End Diastolic Elastance Target Hill Equation"
        latex: 'E_{df}(p_{cm}) = (E_{dM} - E_{dm}) \frac{p_{cm}^{k_E}}{p_{cm}^{k_E} + p_{2E}^{k_E}} + E_{dm}'
      - label: "Heart Rate Control"
        latex: '\frac{d H_c(t)}{d t} = \frac{-H_c(t) + H_f(p_{cm}(t))}{\tau_H}'
      - label: "Heart Rate Target Hill Equation"
        latex: 'H_f(p_{cm}) = (H_M - H_m) \frac{p_{2H}^{k_H}}{p_{cm}^{k_H} + p_{2H}^{k_H}} + H_m'
    parameters:
      - symbol: "Ral"
        name: "Arterial segment resistance upper-to-lower"
        value: 0.0622
        units: "mmHg*s/ml"
        description: "Vascular resistance between upper and lower arterial compartments"
      - symbol: "Rvl"
        name: "Venous segment resistance lower-to-upper"
        value: 0.0167
        units: "mmHg*s/ml"
        description: "Vascular resistance between lower and upper venous compartments"
      - symbol: "Cau"
        name: "Upper arterial compliance"
        value: 1.7213
        units: "ml/mmHg"
        description: "Elasticity of the upper arterial vessels"
      - symbol: "Cal"
        name: "Lower arterial compliance"
        value: 0.3726
        units: "ml/mmHg"
        description: "Elasticity of the lower arterial vessels"
      - symbol: "Cvu"
        name: "Upper venous compliance"
        value: 70.936
        units: "ml/mmHg"
        description: "Elasticity of the upper venous vessels"
      - symbol: "Es"
        name: "Systolic elastance of left heart"
        value: 3.0
        units: "mmHg/ml"
        description: "Maximum contractility of the left ventricle"
      - symbol: "Vd"
        name: "Unstressed left ventricular volume"
        value: 10.0
        units: "ml"
        description: "Residual volume of left ventricle at zero pressure"
      - symbol: "kR"
        name: "Hill coefficient for resistance control"
        value: 25.0
        units: "dimensionless"
        description: "Sensitivity parameter for sympathetic baroreflex resistance control"
      - symbol: "taur"
        name: "Time constant for resistance control"
        value: 12.5
        units: "s"
        description: "Delay time scale for peripheral resistance adjustments"
      - symbol: "RaupM"
        name: "Max upper peripheral resistance"
        value: 4.5292
        units: "mmHg*s/ml"
        description: "Upper bound of upper body peripheral resistance"
      - symbol: "Raupm"
        name: "Min upper peripheral resistance"
        value: 0.3019
        units: "mmHg*s/ml"
        description: "Lower bound of upper body peripheral resistance"
      - symbol: "p2Ru"
        name: "Half-saturation upper peripheral resistance"
        value: 89.97
        units: "mmHg"
        description: "Carotid pressure value at which resistance is halfway between min and max"
      - symbol: "RalpM"
        name: "Max lower peripheral resistance"
        value: 17.88
        units: "mmHg*s/ml"
        description: "Upper bound of lower body peripheral resistance (blunted in neuropathic POTS)"
      - symbol: "Ralpm"
        name: "Min lower peripheral resistance"
        value: 1.192
        units: "mmHg*s/ml"
        description: "Lower bound of lower body peripheral resistance"
      - symbol: "p2Ra"
        name: "Half-saturation lower peripheral resistance"
        value: 89.97
        units: "mmHg"
        description: "Carotid pressure value at which lower resistance is halfway between min and max"
      - symbol: "kE"
        name: "Hill coefficient for elastance control"
        value: 7.0
        units: "dimensionless"
        description: "Sensitivity parameter for parasympathetic baroreflex cardiac contractility control"
      - symbol: "tauE"
        name: "Time constant for elastance control"
        value: 12.5
        units: "s"
        description: "Delay time scale for contractility adjustments"
      - symbol: "EdM"
        name: "Max response for end diastolic elastance"
        value: 0.03125
        units: "mmHg/ml"
        description: "Upper bound of end-diastolic elastance"
      - symbol: "Edm"
        name: "Min response for end diastolic elastance"
        value: 0.00025
        units: "mmHg/ml"
        description: "Lower bound of end-diastolic elastance"
      - symbol: "p2E"
        name: "Half-saturation for elastance control"
        value: 76.62
        units: "mmHg"
        description: "Carotid pressure value at which cardiac elastance is halfway between min and max"
      - symbol: "kH"
        name: "Hill coefficient for heart rate control"
        value: 25.0
        units: "dimensionless"
        description: "Sensitivity parameter for baroreflex heart rate control (altered in hyperadrenergic POTS)"
      - symbol: "tauH"
        name: "Time constant for heart rate control"
        value: 6.25
        units: "s"
        description: "Delay time scale for heart rate adjustments"
      - symbol: "HM"
        name: "Max response for heart rate"
        value: 3.3333
        units: "bps"
        description: "Upper limit of heart rate (equivalent to 200 bpm)"
      - symbol: "Hm"
        name: "Min response for heart rate"
        value: 0.3
        units: "bps"
        description: "Lower limit of heart rate (equivalent to 18 bpm)"
      - symbol: "p2H"
        name: "Half-saturation for heart rate control"
        value: 88.66
        units: "mmHg"
        description: "Carotid pressure value at which heart rate is halfway between min and max"
      - symbol: "TotalVol"
        name: "Total blood volume (BV)"
        value: 4500.0
        units: "ml"
        phenotype_values:
          - phenotype_id: "hypovolemic_pots"
            value: 3500.0
        description: "Total systemic circulating blood volume"
      - symbol: "VMvl"
        name: "Max lower body venous volume"
        value: 195.075
        units: "ml"
        description: "Saturating volume for lower body venous compartment"
      - symbol: "mvl"
        name: "Venous compliance parameter"
        value: 0.0959
        units: "1/mmHg"
        description: "Parameter linking venous volume and pressure in lower body"
      - symbol: "tauP"
        name: "Time constant for carotid tracking"
        value: 2.5
        units: "s"
        description: "Delay in carotid sinus pressure sensing"
      - symbol: "Rav"
        name: "Aortic valve resistance"
        value: 0.0001
        units: "mmHg*s/ml"
        description: "Fluid resistance of the aortic valve during systole"
      - symbol: "Rmv"
        name: "Mitral valve resistance"
        value: 0.0001
        units: "mmHg*s/ml"
        description: "Fluid resistance of the mitral valve during diastole"
      - symbol: "h"
        name: "Height difference aorta to lower body"
        value: 25.0
        units: "cm"
        description: "Hydrostatic column height for lower body gravity calculations"
      - symbol: "hc"
        name: "Height difference aorta to carotid"
        value: 20.0
        units: "cm"
        description: "Hydrostatic column height for carotid pressure gravity calculations"
    assumptions:
      - "Zero-dimensional lumped parameter model representing systemic circulation as five blood compartments"
      - "Blood density is constant at 1.06 g/cm^3"
      - "Gravitational acceleration is constant at 982 cm/s^2"
      - "Flow obeys Ohm's Law (Q = dP / R) and valves prevent retrograde flow perfectly"
      - "All variables respond under continuous first-order delays"

relationships:
  - relationship_id: "p_cm_to_Hc"
    cause: "pcm"
    effect: "Hc"
    type: "sigmoid_hill"
    strength: null
    equation_ref: "Heart Rate Target Hill Equation"
    evidence_level: "Level 4"
    citations:
      - "10.1098/rsif.2022.0220"
  - relationship_id: "p_cm_to_Raup"
    cause: "pcm"
    effect: "Raup"
    type: "sigmoid_hill"
    strength: null
    equation_ref: "Upper Peripheral Resistance Target Hill Equation"
    evidence_level: "Level 4"
    citations:
      - "10.1098/rsif.2022.0220"
  - relationship_id: "p_cm_to_Ralp"
    cause: "pcm"
    effect: "Ralp"
    type: "sigmoid_hill"
    strength: null
    equation_ref: "Lower Peripheral Resistance Target Hill Equation"
    evidence_level: "Level 4"
    citations:
      - "10.1098/rsif.2022.0220"
  - relationship_id: "p_cm_to_Ed"
    cause: "pcm"
    effect: "Ed"
    type: "sigmoid_hill"
    strength: null
    equation_ref: "End Diastolic Elastance Target Hill Equation"
    evidence_level: "Level 4"
    citations:
      - "10.1098/rsif.2022.0220"

conflicts:
  - topic: "POTS Pathophysiological Heterogeneity"
    description: "The paper models POTS subtypes as isolated parameter changes, but clinical POTS is highly heterogeneous and represents overlapping phenotypes."
    possible_explanations:
      - "Simulations isolate single parameter variations to demonstrate bifurcation behavior and Mayer wave generation mechanisms."
---

## Supporting Text and Audit Trail

### Study Design and Clinical Validation
The study implements a closed-loop baroreflex model to explain the transition from supine to upright postures (Head-Up Tilt) and the generation of tachycardia and low-frequency oscillations. 
> "The model consists of a cardiovascular submodel and a baroreflex control submodel... Simulations with nominal parameter values are shown to predict physiological responses of healthy subjects, whereas simulations with parameter values representing POTS demonstrate the characteristic tachycardia and low-frequency oscillations in blood pressure and heart rate."

### Subtype Simulations and Bifurcations
1.  **Neuropathic POTS:** Simulated by decreasing the efficacy of lower peripheral resistance control (blunting of $R_{alp}$).
2.  **Hyperadrenergic POTS:** Simulated by increasing the Hill coefficients ($k_R$ and $k_H$) which increases the feedback gain, inducing a Hopf bifurcation that generates ~0.1 Hz Mayer waves.
3.  **Hypovolemic POTS:** Simulated by lowering total blood volume $BV$ from 4500 ml to 3500 ml or lower.

### Mathematical Parameterization Justification
All parameters are coded in the accompanying software library. The compliance $C_{au}$ and $C_{vu}$ represent upper arterial and venous compliance respectively, and the volumes $V_{au}$ and $V_{vu}$ represent the unstressed and stressed volume partitions.
- $C_{au} = 1.7213$ ml/mmHg
- $C_{al} = 0.3726$ ml/mmHg
- $C_{vu} = 70.936$ ml/mmHg
- $V_d = 10.0$ ml (unstressed ventricular volume)
- $E_s = 3.0$ mmHg/ml (systolic elastance)
- $\tau_r = 12.5$ s (resistance time scale)
- $\tau_E = 12.5$ s (elastance time scale)
- $\tau_H = 6.25$ s (heart rate time scale)
