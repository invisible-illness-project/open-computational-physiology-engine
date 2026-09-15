# OCPE — Temporal Modeling Evidence Report (Pass 1: Discovery)

**Scope.** Model classes and parameterizations for generating physiological dynamics from the cardiac cycle (~ms) to longitudinal (~months), with evidence-based justification per timescale. Each model class is justified by the dynamics it must reproduce, not by available machinery.

## Evidence classification

| Code | Meaning |
|------|---------|
| **E0** | Established consensus: replicated across many independent studies / textbook-level (e.g., HRV standards) |
| **E1** | Strong: multiple independent peer-reviewed studies, meta-analyses, or systematic reviews |
| **E2** | Moderate: single peer-reviewed study or small-sample experimental validation |
| **E3** | Preliminary: preprint, pilot, conference abstract, or indirect evidence |
| **E4** | Expert opinion / review assertion without direct quantitative test |
| **E5** | Engineering judgment: no direct physiological evidence; chosen for parsimony, tractability, or computational necessity (always flagged) |

---

## 1. Cardiac-cycle scale (0.3–3 s): beat-to-beat interval generation

### Dynamics inventory
- SA node firing gated by autonomic modulation → beat occurrence is a *point process*, not a sampled continuous signal.
- Respiratory sinus arrhythmia (RSA): vagally mediated modulation at respiratory frequency (0.15–0.4 Hz; ~0.25 Hz at rest) [E0].
- Mayer waves: ~0.1 Hz BP/HR oscillations from baroreflex feedback-loop delay (loop delay ~10 s) [E0/E1; Geddes 2022, J R Soc Interface, rsif.2022.0220].
- Fractal / 1/f correlation structure: healthy RR series show DFA short-term scaling exponent α1 ≈ 1.0 (range ~0.7–1.2); α1 = 0.5 is white noise; α1 declines with exercise intensity and disease [E1: systematic review, PMC7358842; sleep/aging study (Schumann et al., Sleep 2010) — α1 age-dependent, differs by sleep stage].
- Beat intervals are non-Gaussian; the history-dependent **inverse Gaussian** density is the best-fitting simple probabilistic structure among Gaussian/lognormal/gamma/inverse-Gaussian [E2: Barbieri et al. 2005, PMID 15374824; Chen et al. 2008/2012, PMID 22375120].

### Recommended model class (two defensible options)

**Option A — IPFM (Integral Pulse Frequency Modulation) core.** The standard, parsimonious beat generator:
```
1 = ∫_{t_k}^{t_{k+1}} [ m0 + m(t) ] dt        (threshold 1; beat at t_{k+1})
m(t) = C_S·sin(ω_S t + φ_S) + C_V·sin(ω_V t + φ_V) + n(t) + slow_modulators(t)
ω_S = 2π·0.1 Hz (Mayer/baroreflex band),  ω_V = 2π·0.25 Hz (RSA/vagal band)
n(t) = fractal (1/f-type) noise process (see §7)
```
Evidence: an IPFM variant driven by separately estimated sympathetic/vagal indices (Laguerre expansions of RR AR kernels) produced synthetic RR series that **did not differ statistically from real recordings** across rest and postural change, and outperformed the standard IPFM (Bailón et al., Biomed Signal Process Control 2021; S1746809421003335) [E2]. Classic IPFM with sinusoidal modulation reproduces RSA + Mayer waves and LF/HF ratio (McSharry et al., IEEE TBME 50(3):289–294, 2003, DOI 10.1109/TBME.2003.808805) [E2].
*Justification:* physiologically interpretable (integrate-to-threshold = SA node membrane approximation), trivially couples to slower modulators, and its spectra match HRV bands. It does NOT by itself produce 1/f structure — a fractal modulating noise must be added.

**Option B — Point-process generator (Barbieri/Brown).** Draw RR_k from a history-dependent inverse Gaussian:
```
p(RR_k | history) ~ IG( μ_RR(t_k), θ ),  μ_RR(t) = μ_0 + Σ_{j=1..p} a_j(t) RR_{k-j}  (+ covariates: respiration, BP)
```
Validated on tilt-table data in 10 healthy subjects; goodness-of-fit assessed by Kolmogorov–Smirnov tests under the time-rescaling theorem; "a highly accurate description … at rest and in extreme physiological conditions" [E2: Barbieri et al. 2005, PMID 15374824]. Nonlinear (Wiener–Volterra 2nd-order) extensions exist but add little for generation purposes (Chen et al. 2010, IEEE TBME 57(6):1335–1347) [E2].
*Justification:* statistically rigorous, handles non-stationarity, gives exact distributional control. *Cost:* harder to couple mechanistically to orthostatic/circadian states than IPFM.

**Recommendation for OCPE:** IPFM core (Option A) with an additive fractal-noise modulator and state-dependent modulation amplitudes C_S, C_V driven by the slow layers. Use the inverse-Gaussian point process as the *reference distribution* for validation, not as the generator [E5 — engineering judgment: IPFM integrates more cleanly with the multi-timescale architecture; no evidence it is physiologically superior].

### ECG/PPG waveforms
Do **not** simulate hemodynamics to get waveforms. After beat times t_k are generated, derive the ECG via the McSharry–Clifford 3-ODE dynamical model (Gaussian-kernel PQRST morphology around a unit circle in phase space), which reproduces RSA, Mayer waves, LF/HF, QT dispersion and R-peak amplitude modulation [E2: DOI 10.1109/TBME.2003.808805]. PPG waveform = filtered/phase-shifted derivative of the same pulse train [E5].

### Validation tests (cardiac scale)
| Signature | Target | Evidence |
|---|---|---|
| DFA-α1 (4–16 beats) | ≈ 1.0 rest (0.7–1.2); ↓ with exercise | E1 PMC7358842 |
| Spectral peaks | 0.1 Hz (LF/Mayer) and respiratory 0.15–0.4 Hz (HF/RSA); LF/HF ≈ 1–2 seated rest | E0 |
| Poincaré SD1/SD2, SD1/SD2 ratio | Comet-shaped cluster; SD1 << SD2 | E0 |
| RR distribution | inverse-Gaussian, not Gaussian | E2 PMID 15374824 |
| Multiscale entropy | must be distinguishable-as-real vs. shuffled (PhysioNet CinC 2002 challenge: MSE separates synthetic from real) | E2 (Costa et al., CinC 2002) |

### Alternatives rejected
- **Coupled nonlinear oscillators (Zeeman/van der Pol, 3-oscillator models):** reproduce some HRV phenomenology but introduce unvalidated chaotic dynamics and extra unidentifiable parameters; no demonstrated superiority for generation (rejected: complexity without evidential gain).
- **Pure AR/ARMA resampling of RR series:** reproduces short-lag correlation but not event structure or refractoriness; fails under state transitions [E5].
- **Full baroreflex delay-differential-equation core at cardiac scale:** justified only at the seconds–minutes scale (§2), not for beat timing per se.

---

## 2. Seconds–minutes: orthostatic transitions, exercise on/off kinetics

### Dynamics inventory
- Postural change (supine→stand/HUT): venous pooling (~300–800 mL shift to lower body, gravity-driven), transient BP dip, baroreflex-mediated HR rise of 10–25 bpm within ~30 s [E0/E1: PMC9517804 cites normal orthostatic HR response 10–25 bpm].
- In POTS: sustained HR rise ≥30 bpm and amplified ~0.1 Hz HR/BP oscillations after HUT [E1: Geddes et al. 2022, J R Soc Interface rsif.2022.0220].
- Exercise on-kinetics: HR rises mono-exponentially toward steady state; time constant τ ~10–45 s depending on intensity/fitness [E2: HR-kinetics modeling literature, PMC4395265; τ range is textbook exercise physiology, E0 for order-of-magnitude].
- Off-kinetics (HRR): better fit by **double exponential** than mono-exponential after maximal exercise (fast vagal-reactivation + slow sympathetic-withdrawal components) [E2: IJPP 2023 exponential HRR modelling; consistent with kinetics literature, E1 for two-component structure].
- Autonomic latencies: vagal chronotropic effect < ~1 beat (sub-second), sympathetic effect delayed ~5–20 s plus norepinephrine washout [E4 — standard autonomic physiology; no single clean primary citation found in this pass].

### Recommended model class: small closed-loop ODE compartment model + first-order kinetics
**Structure (justified minimal, Geddes 2022 pattern):** 5-compartment cardiovascular model (left ventricle, upper/lower arteries, upper/lower veins) + baroreflex controller:
```
dV_i/dt = Q_in - Q_out ;  P_i = (V_i - V0_i)/C_i ;  Q_ij = (P_i - P_j)/R_ij     (circuit analog)
dX_c/dt = (X_target(P_carotid) - X_c)/τ_c ,  X ∈ {HR, contractility E_max, R_upper, R_lower}
X_target = Hill functions of carotid pressure (saturating, set-point)
HUT input: hydrostatic gradient θ(t) redistributes V between upper/lower compartments
```
Geddes et al. showed this ~5-ODE core + first-order baroreflex kinetics reproduces (i) normal HUT HR/BP response and (ii) POTS phenotypes (neuropathic: lower-body vasculature control loss + reduced central blood volume; hyperadrenergic: increased BR gain) including the amplified 0.1 Hz oscillations [E2, single-model demonstration: rsif.2022.0220]. Mayer waves emerge from feedback delay — gain increase destabilizes the loop; no explicit oscillator needed [E2].

**Exercise kinetics:** first-order (mono-exponential) on/off HR response with intensity-dependent asymptote:
```
dHR/dt = (HR_ss(intensity) - HR)/τ_on ,  τ_on ∈ 10–45 s   [E0 for structure; τ range E2]
off: HR(t) = HR_rest + A_fast e^{-t/τ_fast} + A_slow e^{-t/τ_slow}, τ_fast ≈ 15–30 s, τ_slow ≈ 2–4 min  [E2]
```
Parameter counts in published orthostatic models: Heldt et al. 2002 (J Appl Physiol 92:1239–54, DOI 10.1152/japplphysiol.00241.2001) — full pulsatile circulation + regulation, ~100 parameters; Olufsen et al. 2006 (AJP Regul 291:R1355–68, DOI 10.1152/ajpregu.00205.2006) — HR-regulation-only model fitted per-subject by least squares, required the **vestibulo-sympathetic reflex** term to match data [E2]; Ursino pulsatile + baroreflex models and Gallo et al. 2022 (Front Physiol, DOI 10.3389/fphys.2022.826989) multiscale HUT model validated in vivo [E2]. **OCPE should implement the Geddes-scale (≈5 compartments, ≈20–30 parameters) version**, not the Heldt/Ursino full models (see identifiability, §8) [E5].

### Validation tests (seconds–minutes)
| Signature | Target | Evidence |
|---|---|---|
| Stand HR rise | +10–25 bpm healthy; ≥30 bpm POTS | E0/E1 |
| Post-tilt 0.1 Hz oscillation power | small healthy, amplified in POTS | E2 rsif.2022.0220 |
| Exercise on/off HR | mono-exp on (τ 10–45 s); bi-exp off | E2 |
| Baroreflex latency/hysteresis | hysteresis loop in firing-vs-BP curve | E2 PMID 16793939 |

### Alternatives rejected
- Full pulsatile distributed (1D) hemodynamics at this scale for a *wearable-data generator*: waveform detail not observable in wrist/finger wearables; parameter burden unjustified [E5].
- Pure empirical AR fits of tilt transients: no extrapolation to unseen posture/condition sequences [E5].

---

## 3. Minutes–hours: meals, stress episodes, thermoregulatory transients, symptom episodes

### Dynamics inventory
- **Postprandial:** HF-HRV (vagal) decreases (e.g., −4.8 normalized units; PMC3403707), LF/HF rises (1.78 → 2.50–2.68 after 500 kcal meal; PMID 10219849), cardiac vagal tone reduced for ~1–2 h [E2 each]; typical HR rise ~10–20 bpm peaking 30–60 min post-meal [E4 — clinical-review level; treat magnitude as approximate].
- **Stress episodes:** sympathetic surge + vagal withdrawal; minutes-scale rise and decay; quantified in point-process frameworks during anesthesia [E2: PMID 22375120].
- **Thermoregulatory transients:** skin temperature responds on ~minutes scale to environment/vasomotor state; core temperature on tens-of-minutes scale [E4; quantitative transient parameters not pinned down in this pass — gap].

### Recommended model class: event-kernel convolution on slow autonomic state + AR/SSM for residual
```
autonomic state s(t) = baseline(t) + Σ_events A_e · k_e(t - t_e)
k_e(τ) = (τ/τ_pk) · exp(1 - τ/τ_pk)   (gamma-style asymmetric kernel; rise ~10–30 min, decay 1–3 h)  [E5 shape; timing anchored E2/E4 above]
```
Then s(t) modulates IPFM parameters (m0, C_S, C_V) and skin/core temperature layers. For the residual HR/HRV dynamics at 1-min sampling, an **AR(p) / state-space model** is well supported: point-process AR (p≈16, local-likelihood 120 s window) tracked tilt dynamics instantaneously [E2: Barbieri framework; Wiley Psychophysiology 2022 usage p=16, l=120 s, Δ=5 ms].
*Justification:* the dynamics here are input-driven transients (meals, stressors), not self-sustaining oscillations — a kernel-convolved event model matches the causal structure; a full ODE meal model would be speculative [E5].

### Validation tests
- Postprandial dip in HF/rMSSD of correct sign and 1–2 h duration [E2 anchors].
- Kernel-convolved series must reproduce cross-correlation lag structure between event times and HR/HRV deflections [E5 — proposed test].

### Alternatives rejected
- Pharmacokinetic multi-compartment absorption models for every meal/stressor: parameters unidentifiable from wearable HR/temp alone [E5 + §8].
- Hidden Markov models with many latent states: tempting but states are not physiologically identified from HR alone; use few (2–4) interpretable states (rest/active/stress/sleep) gated by IMU [E5].

---

## 4. Circadian (24 h)

### Dynamics inventory
- Endogenous circadian period τ ≈ 24 h 11 min ± 16 min (free-running; Czeisler 1999) [E0].
- Core body temperature (CBT): endogenous amplitude ~0.5 °C (order of magnitude; masking inflates raw amplitude), nadir ~2 h before habitual wake (~03:00–05:00), peak ~1–2 h before sleep [E0/E1: circadian assessment review PMC6857846; WJP review 2026].
- DLMO ~2 h before habitual sleep onset; DLMO→wake ≈ 9.2 h (young), MELmid→wake ≈ 4.2 h (Duffy et al. 2001, DOI 10.1152/ajpendo.00268.2001) [E1].
- Melatonin phase markers are more reliable/stable than CBT or cortisol markers (Klerman et al. 2002; Benloucif et al. 2005) [E1].
- HR, HRV, respiratory rate all show 24-h modulation: nocturnal HR dip ~10–20%, nocturnal HRV increase, vagal predominance in sleep [E0 — standard; wearable-population confirmation, e.g., Oura large-N datasets, E3].
- Circadian misalignment (shift work, jet lag): amplitude reduction, phase desynchrony between CBT/melatonin/cortisol [E1].

### Recommended model class
**Cosinor/harmonic regression for observable wearable variables + two-process (S+C) for sleep-wake gating.** Do not simulate SCN biochemistry.
```
Circadian carrier:   c(t) = M + A1·cos(ωt + φ1) + A2·cos(2ωt + φ2),  ω = 2π/(24 h)
   (second harmonic needed: HR/temperature rhythms are non-sinusoidal — sharper night trough) [E5; cosinor terms mesor/acrophase/amplitude are standard, E0]
Two-process sleep:   dS/dt = (1 - S)/χ  (wake, saturating rise);  dS/dt = -S/χ_d (sleep, exp decay)
                     Process C = sine;  sleep onset when S > H + C(t); wake when S < L + C(t)
   [E0: Borbély 1982; Daan et al. 1984; Achermann & Borbély 1990; review PMC9540767]
Coupling: circadian phase φ modulates IPFM m0 (nocturnal bradycardia), C_V (nocturnal vagal gain),
   skin-temperature vasomotor set-point, and S dynamics. Masking terms: posture/activity act on
   observed temperature/HR additively (CBT masking is documented, E1).
```
*Justification:* cosinor is the validated, identifiable standard for rhythm quantification from sparse noisy wearable data; two-process model has 40 years of quantitative validation of sleep timing/duration and deprivation response [E0/E1]. van-der-Pol-type SCN oscillator models (Forger/Jewett/Kronauer) are only needed if phase-response to light must be simulated — include optionally, justified by PRC evidence, not by default [E5 conditional].

### Validation tests
| Signature | Target | Evidence |
|---|---|---|
| Cosinor fit of 24-h HR | significant 24-h component; acrophase afternoon, nadir ~03–05 | E0 |
| CBT/distal-temp nadir timing | ~2 h before wake (after removing masking) | E1 |
| Sleep timing distribution | consistent with S+C thresholds; sleep-deprivation rebound dynamics | E0 |
| Misalignment simulation | amplitude dampening, phase split under shifted light schedule | E1 (qualitative) |

### Alternatives rejected
- Molecular clock models (Goodwin/SCN gene-network ODEs): far below observable granularity, unidentifiable — rejected [E5].
- Pure 24-h Fourier series without two-process gating: cannot produce sleep-dependent masking or irregular sleep schedules — insufficient alone [E5].

---

## 5. Daily / multi-day: sleep-wake cycling, baseline drift, menstrual cycle, illness

### Dynamics inventory
- Day-to-day HRV is substantially variable: weekly lnRMSSD coefficient of variation ~3–10% in athletes; CV ≈ 2.8% at stable baseline vs ≈ 8.1% during functional overreaching (case study; PMC9505647, PMC12787763) [E2].
- Baseline resting HR drifts day to day; weekly-mean HRV reflects adaptation, weekly CV reflects perturbation [E1: sports-monitoring review PMC12787763].
- **Menstrual cycle (verified numbers):** distal skin temperature and nocturnal HR elevated in mid/late luteal vs menses/ovulation (p < 0.001 / p < 0.03), rMSSD trend lower; temperature dip around ovulation (Alzueta et al. 2022, Int J Womens Health, PMID 35422659; PMC9005074) [E2, n=26]. Larger Oura dataset (48,720 cycles, 7,877 users): large effects — temperature, respiratory rate, HR higher luteal; HRV lower luteal [E3, conference abstract WSS 2022]. Magnitudes: RHR +~2–7 bpm follicular→luteal (one study +3.8 bpm mid-luteal, n=91); nocturnal skin temp +~0.2–0.3 °C (up to 0.5 °C individually); BBT +0.3–0.7 °C post-ovulation is century-old textbook physiology; HRV (RMSSD) decrease ~4–5 ms meta-analytic wearables estimate; SDNN −12% in one lab study [E1–E2 compiled; individual numbers E2].
- **Illness episodes:** resting HR elevation ~ several bpm, HRV suppression, temperature elevation over days (wearable illness-detection literature — not deeply searched this pass; gap, E3).

### Recommended model class: latent OU process + slow harmonic + episode events
```
Daily baseline:    dB(t) = -(B - μ(t))/τ_B dt + σ_B dW,   τ_B ≈ 3–7 days (OU mean-reversion)   [E5 — see §8 for OU validation evidence]
Menstrual modulator (where applicable): cycle phase θ(t) = 2π (t - t_menses)/T_cycle,
   T_cycle ~ 28.6 ± 3.8 d (PMID 35422659);
   temperature_offset(t) = +0.2–0.3 °C during luteal window (θ ∈ [ovulation, menses)),
   RHR_offset(t) = +2–5 bpm luteal, RMSSD_multiplier ≈ 0.9 luteal; brief −temp dip at ovulation.  [E2 magnitudes]
Illness episode: event kernel on B, HR, temperature with 2–7 day duration  [E5 structure]
```
*Justification:* OU gives bounded, mean-reverting drift matching observed within-person stability of weekly baselines; a pure random walk is non-stationary and produces unrealistic long-run variance [E5 choice; boundedness argument E0].

### Validation tests
- Weekly lnRMSSD CV in 3–10% range; RHR day-to-day SD realistic (~1–3 bpm) [E2 anchors].
- Simulated menstrual cycles reproduce biphasic temperature (detectable by standard cycle-detection algorithms; wearable biphasic pattern detected in 82% of real cycles — good falsification target) [E2].
- Cross-correlation: HR↑ co-occurs with HRV↓ in luteal phase (anti-correlated biphasic pattern) [E2 PMID 35422659].

---

## 6. Weekly / longitudinal: adaptation, flares, PEM

### Dynamics inventory
- **Training adaptation:** meta-analysis of 16 RCTs (623 participants): exercise training improves SDNN (SMD 0.58, 95% CI 0.16–1.00), RMSSD (SMD 0.84, 0.36–1.31), HF power (SMD 0.89, 0.27–1.51) over ~8–12 week programs [E1: PMC11250637]. Resistance training 24 wk reduced resting HR [E2: PMC9517804]. Detraining reverses over similar weeks-scale [E4].
- **PEM (ME/CFS / Long COVID):** symptom exacerbation delayed 12–48 h (often 24–48 h) after exertion; peak frequently day 1–2; recovery days to weeks — 7-day follow-up: all controls recovered by day 2 vs 60% of ME/CFS patients needing >5 days (VanNess et al. 2010); mean relapse 8.8 days with 22% still relapsed at day 12 (Lapp); 87% report PEM ≥ 24 h; up to 37% onset ≥ 1 day post-trigger (Chu et al. Stanford survey) [E1 for delay/duration phenomenology, mostly E2 study-level].

### Recommended model class
```
Adaptation: slow saturating state   dF/dt = (F_target(load_history) - F)/τ_adapt,  τ_adapt ≈ 2–6 weeks
   F modulates: resting HR (↓ with F), RMSSD/HF (↑ with F), exercise HR at fixed workload (↓)   [structure E5; magnitudes anchored E1 SMDs]
PEM/flare: delayed kernel convolution of exertion history E(t):
   symptom(t) = Σ_e A_e · K(t - t_e),   K(τ) = gamma kernel, delay-to-peak ≈ 24–48 h, decay τ ≈ 2–8 days
   trigger threshold = f(current capacity state);  severity out-of-proportion-to-load parameter [E1 timing; kernel form E5]
```
*Justification:* the defining feature of PEM is the **delay** — any instantaneous dose-response model is falsified by the 24–48 h lag; convolution with a delayed kernel is the minimal structure with the right causal signature. Adaptation is well described by first-order approach-to-asymptote (no evidence for oscillatory or higher-order adaptation dynamics) [E5].

### Validation tests
- Simulated training block: RMSSD weekly-mean rise of SMD ~0.6–0.9 equivalent over 8–12 wk; RHR drop ~2–6 bpm [E1/E2].
- Simulated PEM: lag from exertion event to symptom/HRV-deflection peak ∈ [12, 72] h, distribution right-skewed; recovery ≥ 5 days in severe cases [E1 phenomenology].

---

## 7. Stochastic components (noise models per variable)

| Variable / layer | Recommended noise model | Justification | Evidence |
|---|---|---|---|
| Beat-level HRV modulator | 1/f (pink) noise + AR(1) components; inverse-Gaussian beat distribution | healthy RR is fractal (α1≈1); white noise (α1=0.5) is falsified | E1 (DFA lit.); E2 PMID 15374824 |
| Daily baseline drift | OU process (τ 3–7 d) | bounded, matches weekly-baseline stability | E5 + E2 CV anchors |
| Within-day residual (1-min HR) | AR(1)/AR(p) | standard, validated in point-process/AR frameworks | E2 |
| Measurement noise (PPG HR) | white + state-dependent heteroscedastic (motion-gated) | PPG error grows with motion; IMU-state gating is standard wearable engineering | E4/E5 |
| Ectopy bursts | Bernoulli per-beat ectopy + compensatory pause (IPFM phase reset with s-parameter) | PVCs on 24-h Holter: 40–75% of adults show ≥1; 69% healthy adults; burden ≥5% in ~7.7% of palpitation outpatients; ≥10% pathological | E1 (StatPearls NBK547713; Dong 2022 BMJ Open e059337) |
| Motion artifact | IMU-driven gating process (multiplicative corruption during activity states) | engineering necessity, not physiology | E5 |

State-dependent variance: HRV amplitude scales with state (sleep > rest > exercise); implement multiplicatively on IPFM modulator [E5, consistent with α1 shifts E1].

---

## 8. Model-selection & identifiability evidence (critical for OCPE falsifiability)

- **Structural identifiability of cardiovascular compartment models is limited when only pressure OR volume is observed.** Pironet et al.: linear 6-compartment model identifiable only if outputs contain *both* pressures in all compartments *and* ventricular stroke volumes; pressure-only or volume-only = structurally unidentifiable. Kirk et al.: 3 of 4 Windkessel parameters identifiable (Marquis et al. 2018, Math Biosci 304:9–24, DOI 10.1016/j.mbs.2018.07.001; arXiv 1710.07989) [E1].
- A-priori identifiability analysis of an orthostatic (body/head) model: baroreflex time constant τ_h had **infinitely many solutions**; compliances C_lb, C_lh and τ_b were linearly related to τ_h — only resistance parameters uniquely identifiable (PMC4696755) [E2].
- Practical identifiability workflow used by Olufsen group: local sensitivity ranking → subset selection (correlated parameters removed) → estimate only the sensitive/uncorrelated subset; typical lumped models reduce from ~20+ to ~5–6 estimable parameters from finger-BP + cerebral-flow data (Pope et al.; MBE 2009, DOI 10.3934/mbe.2009.6.93) [E1]. Bayesian UQ recommended over point estimates (PMC10353701) [E2].
- **Implication for OCPE:** HR + wrist PPG + skin temp + IMU observe far less than a tilt-table lab. Treat ODE-layer parameters as *population priors with documented uncertainty*, not as per-subject identifiable quantities. Any internal parameter that cannot be recovered from the simulator's own output under realistic noise must be labeled non-identifiable and fixed to literature distributions [E5 design rule derived from E1 evidence].
- **Simpler models validated against physiological time series:** cosinor (circadian standard, E0); two-process S+C (40 y of quantitative sleep data, E0/E1); OU/first-order kinetics for HR exercise transients (E2); inverse-Gaussian point process for beats (E2, KS-validated). No evidence found that higher-complexity generators (chaotic oscillator ensembles, deep generative models) beat these on physiological fidelity metrics; PhysioNet CinC 2002 showed simple models are detectable-as-synthetic mainly via multiscale entropy — i.e., the bar for "realistic" is fractal/complexity statistics, not waveform realism [E2].

---

## 9. Multi-timescale coupling architecture (recommended)

```
┌─────────────────────────────────────────────────────────────────────┐
│ SLOW LATENT MODULATORS (sampled at 1/day – 1/min)                    │
│  • OU baseline drift B(t) (τ≈3–7 d)                                  │
│  • Adaptation state F(t) (τ≈2–6 wk) ← training-load history          │
│  • Menstrual phase θ(t) (T≈28.6±3.8 d) [if applicable]               │
│  • Illness/flare episodes (event kernels, days)                      │
│  • PEM kernel: K(τ), delay-to-peak 24–48 h ← exertion history        │
├─────────────────────────────────────────────────────────────────────┤
│ CIRCADIAN LAYER (1/min sampling sufficient)                          │
│  • Cosinor carrier c(t) (24 h + 12 h harmonic), phase φ from light   │
│  • Two-process S+C → sleep/wake gating (masks HR, temp, HRV)         │
├─────────────────────────────────────────────────────────────────────┤
│ EVENT LAYER (minutes–hours)                                          │
│  • Meals, stress, exercise bouts → gamma kernels on autonomic state  │
├─────────────────────────────────────────────────────────────────────┤
│ FAST ODE CORE (integrate at 10–100 Hz)                               │
│  • ~5-compartment cardiovascular ODE + baroreflex Hill control       │
│    (Geddes-scale); posture/exercise inputs; produces HR, BP targets  │
│    and 0.1 Hz feedback oscillations                                  │
├─────────────────────────────────────────────────────────────────────┤
│ BEAT GENERATOR (event-driven)                                        │
│  • IPFM: m0, C_S, C_V set by all layers above; + 1/f fractal noise;  │
│    ectopy via Bernoulli + phase-reset                                │
├─────────────────────────────────────────────────────────────────────┤
│ MEASUREMENT MODEL (sensor rate)                                      │
│  • Derive ECG (McSharry 3-ODE) / PPG waveform from beat times        │
│  • IMU-state-gated motion artifact, heteroscedastic PPG noise,       │
│    device sampling/dropout                                           │
└─────────────────────────────────────────────────────────────────────┘
Data flow: slow→fast only (modulation). Fast→slow only via aggregated load
(exertion history feeds PEM/adaptation kernels). No fast state should be
required by slow layers — this keeps slow layers sampleable at low rate.
```

**Granularity rule (what to simulate vs sample):**
- *Simulate (integrate):* beat-to-beat core event-driven (effective 1–5 Hz output); ODE core 10–100 Hz only during active posture/exercise transients, otherwise bypass with steady-state algebraic map [E5 — computational engineering].
- *Sample (closed form):* circadian carrier, OU drift, kernels — all have analytic/closed-form updates; no integration needed [E5].
- *Derive, don't simulate:* ECG/PPG waveform morphology (from beat times), sleep stages (from two-process state + Markov stage machine), symptom scores (from episode states) [E5].

---

## 10. Consolidated validation-metric table (per timescale)

| Timescale | Metric | Real-data target | Evidence grade |
|---|---|---|---|
| Beats | DFA-α1 | ~1.0 rest (0.7–1.2); ↓ exercise | E1 |
| Beats | RR distribution | inverse-Gaussian (KS, time-rescaling) | E2 |
| Beats | LF/HF | ~1–2 rest; state-dependent | E0 |
| Beats | Multiscale entropy | matches real, not shuffled | E2 |
| Sec–min | Orthostatic ΔHR | +10–25 bpm healthy; ≥30 POTS | E0/E1 |
| Sec–min | Exercise τ_on / HRR | 10–45 s / bi-exponential | E2 |
| Min–hours | Postprandial HRV dip | HF ↓ ~1–2 h | E2 |
| 24 h | Cosinor HR acrophase/nadir | afternoon / ~03–05 | E0 |
| 24 h | Temp nadir vs wake | ~2 h before wake | E1 |
| 24 h | Sleep timing | S+C threshold consistency | E0 |
| Daily | lnRMSSD weekly CV | ~3–10% (2.8% stable) | E2 |
| Daily | Luteal vs follicular | T_skin +0.2–0.3 °C; RHR +2–5 bpm; RMSSD −~10% | E1–E2 |
| Weekly | Training block | RMSSD SMD 0.6–0.9 over 8–12 wk | E1 |
| Weekly | PEM lag | 12–72 h delay, peak day 1–2 | E1 |

## 11. Identified gaps (Pass 2 candidates)
1. Quantitative thermoregulatory transient parameters (time constants of skin/core temperature) — not pinned.
2. Wearable illness-episode effect sizes (HR/HRV/temp elevations during infection) — only E3 here.
3. Direct validation of OU vs. random-walk on wearable resting-HR baselines (searched; no direct hit — currently E5).
4. Sympathetic/vagal chronotropic latency numbers (sub-second vagal; 5–20 s sympathetic) — E4 only.
5. Meal-response HR magnitude from primary wearable studies (clinical-review E4 here).
