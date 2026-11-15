# Latent Physiology Design Document

This document describes the design, integration, and mathematical mapping of latent physiological state variables. These variables represent unobserved internal states that dictate the dynamics of observable wearable telemetry.

---

## 1. Why Latent Physiology?

Traditional synthetic wearable simulators model observables (such as heart rate, heart rate variability, or blood pressure) directly using signal processing heuristics. This approach fails to capture the underlying feedback loops of healthy and diseased states, especially under challenges like orthostasis or physical stress.

Evolving the engine into a **Physiology Engine** requires that observable signals emerge from **hidden (latent) physiological states**.

```text
Internal Latent States (e.g., Sympathetic Tone, Compliance, Contractility)
  │
  ▼
Cardiovascular lumped compartment ODEs (mass & flow dynamics)
  │
  ▼
Raw physical waveforms (pulsatile arterial pressures, cardiac flows)
  │
  ▼
Wearable sensor models (sampling resolution, motion artifacts, optical capture)
  │
  ▼
Synthetic telemetry output (HR, RR intervals, PPG waveforms)
```

---

## 2. Supported Latent States & Mappings

The engine extracts and logs the following latent states from the mathematical model:

| Latent Variable | Symbol | Definition & Physiological Meaning | Mathematical Mapping in the Engine |
| :--- | :--- | :--- | :--- |
| **Sympathetic Tone** | $T_{sym}$ | Fight-or-flight autonomic activation. Causes distal vasoconstriction and elevates heart rate. | Calculated from the upper peripheral resistance Hill activation term:<br>$T_{sym} = \frac{p_{2Ru}^{k_R}}{p_{cm}^{k_R} + p_{2Ru}^{k_R}}$ |
| **Parasympathetic Tone** | $T_{para}$ | Rest-and-digest autonomic activation. Promotes cardiac compliance and decelerates heart rate. | Calculated from the left ventricular diastolic elastance Hill term:<br>$T_{para} = \frac{p_{cm}^{k_E}}{p_{cm}^{k_E} + p_{2E}^{k_E}}$ |
| **Cardiac Contractility** | $E_{syst}$ | The force of myocardial contraction during systole. | Represented by the maximum ventricular elastance parameter:<br>$E_s = 3.0$ mmHg/ml |
| **Total Blood Volume** | $V_{total}$ | The total systemic circulating blood volume. | Parametrized by $TotalVol$ (4500 ml nominal, decreased to 3500 ml in hypovolemia). |
| **Vascular Compliance** | $C_{vasc}$ | Distensibility of arterial and venous vessels. | Extracted from compliance constants ($Cau, Cal, Cvu$) and the logarithmic lower venous pressure volume limit ($mvl, VMvl$). |
| **Peripheral Resistance** | $R_{periph}$ | Friction to blood flow in the microvasculature. | Dictated by time-varying state variables $R_{aup}(t)$ and $R_{alp}(t)$, controlled by the sympathetic feedback loop. |

---

## 3. Dynamic Signal Generation Workflow

1. **Autonomic Challenge**: Tilt table transitions alter hydrostatic pressure ($\rho g h_c \sin(\theta)$) at the aorta and carotid sinus.
2. **Baroreceptor Sensation**: Mean carotid pressure ($pcm$) drops.
3. **Autonomic Adjustments**:
   * As $pcm$ drops, Sympathetic Tone ($T_{sym}$) rises towards 1.0. This drives $R_{aup}$ and $R_{alp}$ upwards, increasing peripheral resistance to restore pressure.
   * Simultaneously, Parasympathetic Tone ($T_{para}$) falls towards 0.0, causing the heart rate controller ($Hc$) to accelerate towards maximum beats per second ($HM$).
4. **Observable Outputs**:
   * Pulsatile upper arterial pressure ($pau = Vau / Cau$) is solved at $50$ Hz or higher.
   * Heart rate beat lengths ($T$) are computed dynamically using $1.0 / Hc$, with beat-to-beat variability (HRV) added via a random distribution.
   * Sensor models process the $pau$ and $T$ streams to synthesize the Polar H10 RR interval list and optical PPG waveform.
