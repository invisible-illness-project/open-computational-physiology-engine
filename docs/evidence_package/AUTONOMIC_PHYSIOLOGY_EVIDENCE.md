# OCPE — Autonomic Physiology Evidence Base (Baroreflex / Autonomic Parameterization)

**Purpose:** Evidence-graded, quantitative autonomic physiology to parameterize OCPE baroreflex/autonomic equations for evidence-based synthetic multimodal wearable datasets (PPG/ECG, EDA, skin temperature, accelerometry-context).
**Evidence levels:** E0 hypothesis · E1 mechanistic/theoretical (incl. animal/established physiology) · E2 observational human · E3 controlled human experimental · E4 replicated quantitative (multiple independent human studies) · E5 meta-analysis/consensus.
**Discipline:** Only DOIs/PMIDs/PMCIDs actually seen in searches are cited. Uncertainty is preserved where data are sparse. Wearable-observable signatures are distinguished from mechanistic inference throughout.
**Date:** Pass 1 discovery scan.

---

## 1. Sympathetic / Parasympathetic / Vagal Physiology

### Claim 1.1 — Resting MSNA (microneurography) norms in healthy adults
- **Variables:** MSNA burst frequency (bursts/min), burst incidence (bursts/100 heartbeats), burst amplitude (% of max), total activity.
- **Quantitative values:** Young healthy adults (n=50, age 23±6 yr, HR 63±9 bpm, BP 106±9/64±6 mmHg): burst frequency **24 ± 6 bursts/min (range 9–41)**; burst incidence **38 ± 11 bursts/100 hb (range 16–75)**; mean burst amplitude 44 ± 8% of max. Within-session CV ~11% for 2-min windows (ICC 0.88–0.89); reliability degrades below 1-min windows (CV 20–30% at 30 s/15 s). Independent lab: lean controls 22 ± 4 bursts/min, 39 ± 7/100 hb; T2D 29 ± 3 bursts/min.
- **Timescale:** stable resting trait over minutes–months; large interindividual variability (~4-fold range) is a defining feature — **model as a distribution, not a point value**.
- **Population:** healthy young adults, predominantly male; MSNA rises with age and BMI, higher in men than young women.
- **Evidence level:** **E4** (replicated quantitative; standardized technique).
- **Source:** PMC5142246 (Validity/reliability of resting MSNA, 2017); PMC (ajpheart.00384.2016, T2D MSNA table); microneurography.org review material.
- **Contradictory/null:** Resting MSNA does **not** correlate with vasoconstrictor tone in young women (Hart et al., cited in Guelph thesis review) — sex-dependent transduction.
- **Limitations:** Peroneal/tibial nerve MSNA reflects muscle vasoconstrictor outflow only; does not equal cardiac or renal sympathetic drive; burst amplitude depends on electrode position (only burst frequency/incidence comparable across subjects).
- **Implementation recommendation:** Rest MSNA ~ lognormal-ish distribution, mean 20–25 bursts/min young, SD ~6; burst incidence ~ N(38, 11)/100 hb; impose pulse synchrony (bursts gated by baroreflex, latency ~1.3 s, see Claim 3.3). Age dependence: model MSNA_base increasing with age (qualitative; sparse quantitative gradients).
- **Validation:** Simulated sympathetic drive should reproduce published MSNA distributions and orthostatic doubling (Claim 1.2).

### Claim 1.2 — MSNA responses to orthostasis and exercise
- **Variables:** MSNA burst frequency/incidence under HUT, LBNP, static handgrip.
- **Quantitative values:**
  - Graded LBNP to presyncope (n=17): burst incidence rises **23 ± 3 → 42 ± 3 bursts/100 hb** (baseline → presyncope); total MSNA rises ~4×; R-wave-to-burst latency shortens 1.3 ± 0.03 → 1.04 ± 0.07 s (PMC2770161, Cooke 2009).
  - LBNP −40 mmHg: MSNA bursts per LF (~0.1 Hz) cycle 2.55 ± 0.68 → 5.44 ± 1.56 (PMC5492197).
  - 60° HUT (Fu et al. 2009, graphed in Front Physiol 2012;3389/fphys.2012.00278): progressive rise in burst frequency over 45 min of tilt, roughly doubling from supine (~15–20 → ~35–40 bursts/min by Tilt30–45), in both sexes.
  - Static handgrip 33% MVC × 2 min: **MSNA +130 ± 48%** (Ray 1994, PMID 8304526); first minute shows little/no increase at ≤30% MVC (metaboreflex-driven, not central command, at low intensity; Victor et al. data summarized in PMC970 review and PMC5866365). Non-hypotensive LBNP (−5 mmHg) alone: MSNA +92 ± 22%; combined with handgrip responses not additive (iris.unil.ch, Mark/Victor study).
  - Tilt-speed dependence: slow HUT (0.0167°/s) blunts MSNA rise vs. 1°/s and abolishes the 3-min overshoot seen after rapid tilt (PMID 19448145).
- **Timescale:** MSNA rises within seconds of baroreflex unloading; overshoot ~3 min after rapid tilt; metaboreflex component at minutes 2–3 of static exercise.
- **Population:** healthy young/mixed adults.
- **Evidence level:** **E4** (multiple controlled microneurography studies).
- **Contradictory:** Interindividual "responder types" exist (positive/negative MSNA responders to mental stress and early handgrip; PMC5866365) — include response-type heterogeneity in synthetic cohorts.
- **Implementation recommendation:** MSNA(t) = f(baroreflex sigmoid of DAP/MAP) with exercise metaboreflex additive term after ~60–90 s of static contraction; orthostatic target ≈ 1.5–2× baseline at 60° HUT; presyncope can reach ~2× burst incidence but with disrupted pulse synchrony.
- **Validation:** Against LBNP/HUT MSNA time series statistics above.

### Claim 1.3 — Plasma norepinephrine kinetics and orthostatic response
- **Variables:** plasma NE (pg/mL), NE spillover, NE clearance.
- **Quantitative values:** Supine **181 ± 14 (SEM) pg/mL → standing 472 ± 35 pg/mL** (n=17/44; Fiorica 1985, PMID 4084169); NE rises proportionally with tilt angle (r=0.76). With 30 min standing: **NE spillover +80%, NE clearance −30%** (Jacob 1998, J Appl Physiol 84:914, doi 10.1152/jappl.1998.84.3.914). Plasma NE half-life ~2 min (established physiology; Esler tracer studies, as cited in PMC2290017) — E1/E4.
- **Timescale:** minutes (limited by sampling and ~2-min half-life).
- **Evidence level:** **E3–E4**.
- **Contradictory:** Plasma NE conflates spillover and clearance (standing reduces clearance ~30%), so it overestimates sympathetic activation change; MSNA correlates with NE spillover in men (Esler 1990) but not women.
- **Implementation recommendation:** For a humoral sympathetic variable: NE_plasma supine ~200 pg/mL (lognormal, CV ~30–40%), upright ~2.5× supine; first-order kinetics τ ≈ 2 min for NE changes; split clearance vs spillover effects during posture change.
- **Validation:** Compare synthetic posture transitions against Fiorica/Jacob magnitudes.

### Claim 1.4 — Pharmacological blockade: limb contributions to HR
- **Variables:** intrinsic heart rate (IHR) after double blockade; vagal vs sympathetic contributions.
- **Quantitative values:** Combined IV propranolol 0.2 mg/kg + atropine 0.04 mg/kg produces fixed IHR; observed range 57–126 bpm (Jose & Taylor 1969, J Clin Invest, jci.org/articles/view/106167). Age prediction: **IHR = 118.1 − 0.57 × age** (Jose & Collison 1970, as quoted in ESC syncope guidelines, sfmu.org PDF). Double blockade eliminates **>98%** of HRV (young and old; PMID 7733345). Post-blockade RR: young 677 ± 106 ms vs old 859 ± 176 ms.
- **Interpretation:** Resting HR < IHR in most healthy adults → resting state is **vagal-dominant**; resting sympathetic chronotropic contribution is small but non-zero.
- **Evidence level:** **E4** (replicated blockade studies).
- **Limitations:** Blockade doses vary across labs; partial muscarinic blockade affects BRS measures (see Claim 2.x).
- **Implementation recommendation:** SA node model: HR = IHR(age) × (1 − vagal_effect) × (1 + sympathetic_effect), with resting vagal effect dominant; IHR = 118.1 − 0.57·age.
- **Validation:** Simulated "double blockade" should collapse HRV >98% and yield HR = IHR.

### Claim 1.5 — Vagal indices: RMSSD, HF power, RSA
- **Quantitative values (5-min short-term, healthy adults, Nunan 2010 meta-review, 44 studies, 21,438 participants; PMID 20663071, DOI 10.1111/j.1540-8159.2010.02841.x):** IBI 926 ± 90 ms; **SDNN 50 ± 16 ms** (range 32–93); **RMSSD 42 ± 15 ms** (range 19–75); LF 519 ± 291 ms²; LF nu 52 ± 10; **HF 657 ± 777 ms²** (huge spread, range 83–3630); HF nu 40 ± 10; **LF/HF 2.8 ± 2.6** (range 1.1–11.6).
- **Task Force 1996 norms** (PMID 8598068; DOI 10.1161/01.CIR.93.5.1043) — 24-h: SDNN 141 ± 39 ms, SDANN 127 ± 35, RMSSD 27 ± 12, triangular index 37 ± 15; 5-min supine stationary: total power 3466 ± 1018 ms², LF 1170 ± 416 ms², HF 975 ± 203 ms², LF nu 54 ± 4, HF nu 29 ± 3, LF/HF ~1.5–2.0. Task Force itself flagged these as approximate, from small samples.
- **Evidence level:** **E5** (consensus + systematic review).
- **Contradictory/null:** Nunan et al. found post-1996 literature values **lower than Task Force norms** and interindividual variation up to 260,000% for spectral measures; values differ with paced vs free breathing and FFT vs AR methods — **never treat Task Force spectral norms as precise targets**.
- **Implementation recommendation:** Use Nunan 2010 distributions for resting synthetic cohorts; log-transform spectral powers (right-skewed). RMSSD is the most robust wearable vagal index (respiration-robust relative to HF; see Claim 6.3).
- **Validation:** Distributional match to Nunan Table; within-subject posture changes (RMSSD/HF fall upright) reproduced.

---

## 2. Baroreflex

### Claim 2.1 — Cardiovagal baroreflex sensitivity (BRS) norms by method
- **Quantitative values (La Rovere et al. review, PMC6931942, Table 1, healthy subjects, ms/mmHg):**
  - Phenylephrine (Oxford): ~**15 ms/mmHg average** across studies (Eckberg 16.0 ± 1.8 SEM; Robbe 18.1 ± 8.9; Raczak 16 ± 8.8; Davies 19.8 ± 11.5). Strong **age gradient** (Laitinen, n=117): 19.5 ± 1.4 (23–39 y) → 10.7 ± 1.2 (40–59 y) → 6.0 ± 0.6 (60–77 y).
  - Sequence method: Parati 7.6 ± 2 (up)/6.4 ± 1.5 (down); large population data (Kardos, n=1134, geometric means): 18–29 y 13.7 up/13.9 down → 50–60 y 6.2 up/7.0 down. Young athletic sample: 25 ± 16 (arteryresearch P6.11, n=28).
  - Spectral α-coefficients: α-LF 6.2–7 (Gerritsen, n=191, age 63) to 23 ± 2 (Lucini, age 42); α-HF 8.6–25.1; Gerritsen median transfer-function BRS 8.8 ms/mmHg, 10th centile 4.5; Tank 8 ± 5 (TP.brs). Chinese population study n=2092 consistent (Springer 2047-783x-19-8).
  - **Method bias:** all spontaneous methods **underestimate phenylephrine BRS by 33–67%** though correlated (PMC2745725, Lipman/comparison study). Valsalva-derived BRS correlates with phenylephrine only r=0.27–0.91.
- **Pathology anchors (for synthetic patient cohorts):** post-MI ~7–8 ms/mmHg (phenylephrine; ATRAMI n=1284: 7.2 ± 4.6); ATRAMI risk cutoff **BRS < 3 ms/mmHg → RR 2.8 (95% CI 1.40–6.16) cardiac mortality**; heart failure ~2–4 ms/mmHg (Mortara n=282: 3.9 ± 4.0); modified TF BRS ≤ 3.1 ms/mmHg → HR 3.2 for cardiac death in CHF (Pinna, n=228).
- **Evidence level:** **E4–E5** (large replicated datasets + prognostic validation).
- **Contradictory/null:** No single "normative value" exists; sequence/spectral BRS are not interchangeable with phenylephrine (fixed biases); BRS has large intrinsic within-subject lability (mood, respiration).
- **Implementation recommendation:** Logistic cardiovagal gain at operating point ~ **10–15 ms/mmHg** young supine (sequence/spectral), ~15–20 ms/mmHg (phenylephrine scale); halve per ~20 yr of age (use Laitinen/Kardos gradients); lognormal distribution (SD/mean ≈ 0.4–0.5). Asymmetry: down-sequences (depressor) slope ≈ up-sequences or slightly lower; keep separate up/down gains.
- **Validation:** Sequence-method analysis of simulated supine BP/HR should recover the prescribed operating-point gain within methodological bias (~33–67% below phenylephrine equivalent).

### Claim 2.2 — Sigmoid (4-parameter logistic) baroreflex model — canonical equation form
- **Equation (Kent et al. 1972 lineage; Kawada/Sugimachi open-loop form):**
  `y = P4 + P1 / (1 + exp(P2·(x − P3)))` (equivalently `y = (P1−P4)/(1+exp[P2(x−P3)]) + P4` with P1 = max, P4 = min)
  - P1 = response range of output (e.g., HR or MAP), P2 = slope (gain) coefficient, P3 = midpoint (centering point) pressure, P4 = lower plateau.
  - **Maximum gain Gmax = P1 × P2 / 4** (at the centering point).
  - Threshold/Saturation (5% of plateaus; PMID 16714364): Thr(5%) ≈ P3 − 2.944/P2·(corr.) — note the commonly used Thr = A3 − 2.0/A2 and Sat = A3 + 2.0/A2 **underestimate the true 5% operating range by ~32%**; use exact logistic solutions in code.
- **Human carotid baroreflex parameters (neck pressure/suction, rapid pulses; Ogoh/Raven lab, PMC1780016, n=9, rest):**
  - CBR–HR: A1 (range) = 17.1 ± 2.7 bpm, A2 = 0.15 ± 0.03, A3 (midpoint ECSP) = 99.9 ± 5.0 mmHg, A4 (min HR) = 55.6 ± 1.8 bpm → **Gmax ≈ −0.58 ± 0.10 bpm·mmHg⁻¹**. **Muscarinic blockade (glycopyrrolate) collapses Gmax to −0.06 ± 0.01** → the carotid-cardiac arc is ~90% vagally mediated at this timescale; β-blockade (metoprolol) leaves curve shape intact (shifts HR level).
  - CBR–MAP: A1 = 16.2 ± 2.2 mmHg, A2 = 0.10 ± 0.03, A3 = 103.4 ± 4.3 mmHg, A4 = 84.8 ± 4.9 mmHg → Gmax ≈ −0.4 mmHg/mmHg (consistent with parabolic-flight study: carotid-MAP Gmax −0.24 mmHg/mmHg at 1 g, −0.30 at 0 g; carotid-HR Gmax −0.53 → −0.80 bpm/mmHg).
  - Note: CBR parameters are from the *carotid* reflex only (neck chamber); whole-baroreflex (carotid + aortic) gain is larger.
- **Evidence level:** **E3–E4** (controlled human experiments; replicated technique).
- **Implementation recommendation:** Implement cardiovagal arc as logistic in mean arterial (or estimated carotid sinus) pressure with P3 ≈ resting MAP (~90–100 mmHg), HR range ≈ 15–20 bpm around operating region for the fast vagal limb, Gmax ≈ −0.5 to −0.6 bpm/mmHg (carotid-only scale). Vasomotor arc: separate logistic/linear efferent element (SNA→MAP), Gmax ≈ −0.25 to −0.4 mmHg/mmHg carotid-only. Use exact 5% Thr/Sat.
- **Validation:** Neck-suction impulse response simulation reproducing CBR–HR Gmax and glycopyrrolate sensitivity.

### Claim 2.3 — Operating point vs gain; baroreflex resetting (exercise, orthostasis)
- **Findings:** During exercise the entire sigmoid resets **upward and rightward** (higher pressures and HR) in proportion to intensity, **maximal gain is preserved**, and the **operating point moves from the centering point toward threshold** — improving buffering of hypertensive stimuli (Raven et al. 2006, PMID 16210446; Ogoh 2002 J Physiol central command study, doi 10.1113/jphysiol.2002.019943; review PMC962 figure). Resting also occurs with orthostasis (cardiovagal OP shifts into the more linear portion with vagal withdrawal; Front Physiol 2012 fphys.2012.00461). Mechanisms: **central command resets the carotid–cardiac arc; central command OR exercise pressor reflex resets the carotid–vasomotor arc** (Ogoh 2002, n=8, patellar tendon vibration paradigm).
- **Dynamic (closed-loop) data:** At exercise onset BRS falls almost immediately (vagal withdrawal) while OP resetting is slower/delayed (Bringard et al., summarized in Springer s00421-022-05011-4); during isometric handgrip, spontaneous BRS drops rapidly within first 2 min then stabilizes (fphys.2017.00246).
- **Timescale:** gain decrease: seconds (vagal withdrawal at onset); OP reset: tens of seconds–minutes, graded with intensity.
- **Evidence level:** **E4**.
- **Implementation recommendation:** Model resetting as intensity-dependent shift of P3 (midpoint) and P4 (HR floor) of the cardiovagal logistic — NOT as gain reduction; operating-point gain falls as a geometric consequence of OP moving toward threshold. Central-command drive = feedforward input scaling with effort/RPE; metaboreflex input activates after ~1 min of static work.
- **Validation:** Steady-state exercise: HR and BP rise in parallel with preserved spontaneous sequence counts displaced rightward.

### Claim 2.4 — Cardiovagal vs sympathetic baroreflex limbs
- **Quantitative values (Eckberg lab; modified Oxford NP+PE; ajpheart.1999.276.5.H1691):** **Sympathetic baroreflex gain −12.6 ± 7.8 %MSNA/mmHg** (NP then PE); **vagal gain 8.3 ± 5.1 – 18.9 ± 12.0 ms/mmHg** depending on method (PE ramps 12.8 ± 7.2; sequences up 13.2 ± 10.5, down 14.5 ± 10.3; cross-spectral 0.1 Hz 18.9 ± 12.0). Vasodepressor (NP) responses are weaker than pressor (PE) responses — **asymmetric reflex** (nitroglycerin slopes lower than phenylephrine; La Rovere review).
- **Frequency domain:** Baroreflex behaves as a **low-pass system: full operation at ~0.01 Hz, ineffective above ~0.1 Hz** (animal transfer data applied to human 30-min BP recordings; PLoS One 2021, pone.0248428).
- **Loop-opening evidence:** sinoaortic denervation drops spontaneous sequences −89% (cats) and increases BP variability without changing mean BP level (Cowley lineage, cited in PMC6931942) — the baroreflex buffers **variability, not set-point** over the long term. E1/E4.
- **Implementation recommendation:** Separate vagal cardiac limb (fast, ms/mmHg gain, operating beat-by-beat) from sympathetic cardiac+vasomotor limbs (slow, %MSNA/mmHg gain ~ −12 ± 8, low-pass filtered); include up/down asymmetry.

---

## 3. Autonomic Gain and Latency (Wearable-Critical Timescales)

### Claim 3.1 — Vagal cardiac latency ≪ 1 s; sympathetic cardiac latency ~2–5 s
- **Quantitative values:**
  - Vagal baroreflex HR response to an abrupt pressure rise: **200–600 ms** (i.e., effective within the same or next cardiac cycle) — La Rovere review (PMC6931942, refs 5–7). Classic vagal stimulation (dogs): HR falls >50% **within 1 s** of stimulation onset (Warner & Cox 1962, digitized in Pierpont review PMC6932299).
  - Sympathetic cardiac/vasomotor baroreflex response: **2–3 s delay**, maximal effect substantially slower (PMC6931942); canine transfer function: sympathetic path has **~1.7 s pure delay + low-pass filter with much lower corner frequency than vagal** (Berger 1989, PMID 2912176).
  - Practical frequency consequence (humans): vagal modulation of RR operates up to ≥0.4–0.5 Hz (respiratory band); sympathetic modulation cannot follow fluctuations faster than **~0.1–0.15 Hz** (Saul et al. 1991 transfer analysis, cited in PMC2269357). This is the physiological basis of the HF(vagal)/LF(mixed) split.
- **Evidence level:** **E4** (replicated across species and humans).
- **Implementation recommendation:** SA node: vagal input → pure delay 0.2–0.6 s, first-order dynamics τ_v ≈ 0.5–1.5 s, bandwidth to 0.5 Hz; sympathetic input → pure delay ~1.5–2 s (human range 2–5 s onset), first-order/second-order low-pass τ_s ≈ 5–15 s (corner ~0.01–0.02 Hz for steady fluctuations), bandwidth ≤0.1 Hz. Beat-by-beat HRV >0.15 Hz must be generated by the vagal limb (+ respiration gating) only.
- **Validation:** Simulated phenylephrine ramp: RR lengthening begins within 1 beat; simulated sympathetic step: HR rise begins after ~2 s, reaches 63% in ~10–20 s.

### Claim 3.2 — Sympathetic nerve/vascular latencies
- **MSNA burst latency:** integrated MSNA bursts appear **~1.3 s** after the triggering R-wave (baroreflex loop conduction; Fagius & Wallin 1980; Sundlöf & Wallin 1978; peroneal nerve at fibular head; PMC2290575). Latency inversely related to burst size (Wallin 1994) and shortens to ~1.04 s at presyncope (Cooke 2009). Skin SNA conduction ~40% faster than MSNA (PMC3286698).
- **Neurovascular transduction:** MSNA burst → nadir of femoral arterial compliance after **4.2 ± 0.6 cardiac cycles** (~4 s; burst vs non-burst compliance −5.1 ± 0.6% vs −0.8 ± 0.2%; UT Arlington abstract — provisional, E2). Beat-to-beat DAP↔MSNA transduction slopes: ~8.3%/s MSNA change per mmHg in normotensives vs 25%/s in untreated hypertensives (Nature J Hum Hypertens 2021, s41371-021-00578-5). Sympathetic transduction review: PMC7988755.
- **Implementation recommendation:** Vascular effector: MSNA burst train → convolution with a ~4–6 s latency, low-pass (seconds) vascular response kernel driving regional resistance/conductance; modulate transduction gain by sex (attenuated in young women/OCP users; PMID 39763373), age, hypertension.
- **Evidence level:** **E3–E4** (burst latency E4; transduction dynamics E2–E3).

### Claim 3.3 — Recovery time constants (post-exercise, post-standing)
- **Post-exercise HRR:** Biphasic — fast vagal reactivation (first 30–60 s) + slow sympathetic withdrawal/metabolic clearance (minutes; catecholamine/thermal effects up to ~30 min). **HRR1 ≤ 12 bpm (active recovery) = abnormal; adjusted RR 2.0 for mortality** (Cole 1999 NEJM, PMID 10536127, n=2428); ≤22 bpm at 2 min also abnormal; healthy HRR1 typically 18–25 bpm (passive recovery >21 bpm normal; Akyuz 2014 via thesis). HRR follows inverse-exponential kinetics with a vagal time constant (Pierpont 2013, PMC6932299); Imai 1994 (JACC): vagally mediated HRR accelerated in athletes, blunted in CHF. Meta-analysis (Qiu 2017, 9 studies, 41,000 participants): attenuated HRR → pooled HR 1.68 for all-cause mortality (E5).
- **Post-standing:** HR rises within ~3 s of standing, peaks around beat ~15, relative bradycardia by beat ~30 (30:15 physiology, Ewing; PMC13068710 systematic review). Initial BP dip on active standing recovers within ~20–30 s in healthy subjects; abnormal if >40/20 mmHg within 15 s (initial OH; Freeman 2011; Wieling 2007 via JACC 2018 review, jacc.org 10.1016/j.jacc.2018.05.079).
- **Implementation recommendation:** HRR model: HR(t) = HR_end − ΔHR_vagal·(1 − e^(−t/τ_v)) − ΔHR_sym·(1 − e^(−t/τ_s)), τ_v ≈ 15–30 s, τ_s ≈ 90–180 s; scale τ_v by fitness/age. Orthostatic HR: initial peak +10–20 bpm within ~15 beats, settling +10–15 bpm steady-state standing.
- **Evidence level:** **E4–E5**.

---

## 4. Orthostatic Compensation — Full Reflex Arc (Standing / HUT)

### Claim 4.1 — Thoracic blood shift and venous pooling
- **Quantitative values:** On standing, **0.5–1.0 L of thoracic blood transfers below the diaphragm** (Asmussen 1943; Sjöstrand 1952; Self 1996 — as reviewed in Smit/Wieling review PMC2269496; J Intern Med review joim.12021). **Bulk of pooling occurs within the first 10 s** (Ludbrook 1966; Kirsch 1980; Ebert 1986); total transfer nearly complete in **3–5 min**. Additional slow stress-relaxation of dependent veins may continue (little human quantitative data — flag as E1/sparse).
- **Transcapillary refill (Starling):** plasma volume falls **~10% (≈500 mL) by 5 min** and **15–20% (≈700 mL) by 10 min**, then virtually complete (Lundvall 1994/1996, correcting earlier underestimates; PMC2269496). Standing hemoconcentration ~10–15% in earlier studies.
- **Cardiac output:** falls **~20%** on continued standing; MAP preserved by sympathetic vasoconstriction in splanchnic/musculocutaneous/renal beds (joim.12021).
- **Evidence level:** **E4** (classic replicated human measurements) for pooling/refill; stress-relaxation E1.
- **Implementation recommendation:** Central blood volume dynamics: fast pooling exponential τ ≈ 5–10 s toward ~600 mL (range 300–1000 mL), slow transcapillary term τ ≈ 3–5 min removing ~15% plasma volume asymptote; posture-graded by tilt angle/speed (slow tilt blunts, PMID 19448145).

### Claim 4.2 — Reflex engagement timeline (seconds)
- **Sequence on active standing:** (i) muscle contraction/abdominal compression transiently raises venous return; (ii) hydrostatic pooling begins immediately; (iii) baroreflex unloading → vagal withdrawal within **1–2 beats** (HR up) and MSNA increase within seconds; (iv) TPR rises, HR +10–20 bpm, BP nadir at ~5–10 s then recovery by 20–30 s; (v) steady-state: HR +10–15 bpm, DBP +~5 mmHg, SV ↓, CO ↓ ~20%, MSNA ~1.5–2×, NE ~2.5× (Sections 1–3 sources).
- **Hemodynamic norms (clinical):** OH = SBP ↓ ≥20 or DBP ↓ ≥10 mmHg within 3 min of standing/60° HUT (Freeman 2011 consensus, Clin Auton Res 21:69; ≥30 mmHg if supine HTN); **initial OH = transient ↓ ≥40/≥20 mmHg within 15 s** (active standing); delayed OH beyond 3 min (up to 45 min). Early (30–60 s) measurements carry the best prognostic association (Juraschek 2017, n=11,249; NEJM JW summary).
- **Evidence level:** **E5** (consensus definitions) / E4 (timeline).
- **Implementation recommendation:** Healthy synthetic stand: SBP dip 10–30 mmHg transient (nadir ~7–15 s), recovery by ≤30 s; generate OH phenotypes by scaling baroreflex gain and venous pooling volume.

### Claim 4.3 — Renal-hormonal timescales (RAAS, AVP)
- **RAAS is the third line of defense, engaged after a delay of minutes, acting over minutes–hours** (Physiol Rev syncope review 2025, doi 10.1152/physrev.00007.2024). Standing: NE spillover +80%/30 min; plasma renin activity rises (blunted in reflex syncope with cardioinhibitory pattern; Jardine/Vanderheyden as cited); post-tilt PRA 2.2 ± 2.4 → 5.2 ± 4.5 ng/mL/h (2.5×; Gajek 2005, via science.gov) and aldosterone 90 → 179 pg/mL. Aldosterone effects persist minutes–hours.
- **Evidence level:** **E3** (controlled tilt studies) with **ambiguous/contradictory syncope findings** (explicitly preserved).
- **Implementation recommendation:** Humoral layer: renin→angiotensin II first-order lag τ ≈ 5–15 min with vasoconstrictor gain small relative to neural limb; aldosterone/volume layer τ ≈ hours — include only in long-duration simulation modes; do not attribute acute (first 60 s) standing compensation to RAAS.

---

## 5. Vascular Response

### Claim 5.1 — Sympathetic control of resistance and venomotor tone
- Arterial resistance: MSNA bursts gate regional vasoconstriction beat-to-beat (transduction kernel ~4–6 s, Claim 3.2); resting sympathetic vasoconstrictor tone present in muscle and skin; baroreflex modulates around set-point.
- Venous side: baroreflex control of venous return is **sluggish** (slowest component; La Rovere review). Leg venous compliance (occlusion plethysmography): **0.048 ± 0.007 mL·100 mL⁻¹·mmHg⁻¹** (healthy; falls to 0.033 ± 0.007 after 18-day bed rest — **but compliance change unrelated to orthostatic tolerance change**; Bleeker 2004, PMID 14657040, DOI 10.1152/japplphysiol.00835.2003). Leg venous outflow resistance 1.73 ± 1.08 mmHg·mL⁻¹·100 mL·min (rises after bed rest).
- Hydrostatics: motionless standing → foot venous pressure ~90 mmHg; functioning muscle pump + valves reduce dependent venous pressure to ~10–20 mmHg during walking (Advan Physiol Educ 2018, doi 10.1152/advan.00182.2018; cvphysiology.com).
- **Muscle pump:** essential during ambulation; inadequate pump → pooling, ↓venous return, ↓CO, ↓MAP (E1–E4).
- **Implementation recommendation:** Venous compartment: compliance ~0.05 mL/100 mL/mmHg (legs), sympathetic venoconstriction shifts unstressed volume centrally with slow dynamics (τ tens of seconds–minutes); add muscle-pump term proportional to step rate/calf EMG proxy from accelerometer for ambulatory synthetic data.
- **Evidence level:** E3–E4 (compliance), E1 (pump quantification sparse).

### Claim 5.2 — Skin circulation (skin-temperature wearable link)
- Dual sympathetic control of human skin: **noradrenergic vasoconstrictor system** (tonically active in thermoneutrality; ↑ with cold/arousal; NE + cotransmitters NPY/ATP) and **cholinergic active vasodilator system** (no resting tone; activated by heat/exercise; ACh/VIP/NO cotransmission) — glabrous skin (palms, fingers, plantar) has **only noradrenergic constrictor** innervation (Charkoudian reviews: PMC2963327; J Appl Physiol doi 10.1152/japplphysiol.01071.2005). Skin blood flow ≈ 5% of CO normothermia, up to ~60% in severe heat stress.
- **Wearable signature:** finger/palmar skin temperature falls with sympathetic vasoconstrictor activation (stress, cold, orthostasis) and rises with active vasodilation/heat; confounded by ambient temperature and local effects. Demonstrated = directional covariation; quantitative transfer gains sparse (E2).
- **Implementation recommendation:** Skin temp channel: slow sympathetic vasoconstrictor drive (τ minutes, ambient-temperature-confounded) on distal sites; do not map skin temperature to "sympathetic tone" linearly.

---

## 6. HRV as Autonomic Proxy — Established vs Contested

### Claim 6.1 — What is established (consensus)
- Task Force 1996 (PMID 8598068; Eur Heart J 17:354–381; Circulation 93:1043–65) standardizes bands (ULF, VLF, LF 0.04–0.15 Hz, HF 0.15–0.40 Hz) and time-domain metrics; **E5**.
- **HF power / RMSSD / pNN50 are vagally mediated** (abolished by atropine; correlate with vagal maneuvers): E4. Double autonomic blockade removes >98% of HRV (PMID 7733345): HRV is almost entirely autonomically generated.
- Low HRV predicts mortality post-MI and in CHF (Task Force; ATRAMI lineage): E5.

### Claim 6.2 — The LF/HF "sympathovagal balance" controversy (must cover explicitly)
- **Critique (Billman 2013, Front Physiol 4:26, DOI 10.3389/fphys.2013.00026, PMC3576706):** LF/HF rests on four false assumptions — (1) LF is mainly sympathetic (false: LF is produced by baroreflex-buffered, predominantly parasympathetic modulation); (2) HF is exclusively parasympathetic (respiration confounds); (3) sympathetic and parasympathetic activities are reciprocally related (false — e.g., post-exercise sympathetic stays high while vagal drive reactivates; diving reflex raises SNA with bradycardia); (4) interactions are linear (false — accentuated antagonism, §7.1). **Identical LF/HF can arise from different autonomic states.** Eckberg 1997 earlier showed SNS↔LF and PNS↔HF inconsistencies. Goldstein 2011 (Exp Physiol 96:1255, doi 10.1113/expphysiol.2011.050529): **LF power is not a measure of cardiac sympathetic tone** (at best a modulatory index). Boyett 2019 CrossTalk (J Physiol 597:2599): "HRV as a measure of cardiac autonomic responsiveness is fundamentally flawed" (opposing view exists in same forum). Normalized units (LF nu, HF nu) and LF/HF require constant total power to be interpretable — violated by respiration changes alone (PMC9309192).
- **Counterpoint/usage:** LF/HF still correlates with posture/tilt group-level changes; some authors defend HF (paced) and RMSSD as vagal indices. Scatter LF-HF plots proposed to disambiguate (fphys.2017.00360).
- **Evidence level of the critique:** **E4–E5** (expert consensus-level critical synthesis widely accepted).
- **Implementation recommendation (OCPE):** **Never generate LF/HF as a direct "sympathetic/vagal ratio" label.** Generate sympathetic and vagal drive signals independently (possibly co-activated), pass them through the latency/filter model (§3) plus baroreflex and respiratory gating, then compute HRV metrics from the resulting RR series. Validate that LF/HF *emerges* with the documented covariation and its known failure modes (e.g., slow breathing raises LF → LF/HF rises with no sympathetic change).

### Claim 6.3 — Respiratory confounds
- RSA amplitude falls ~**20 dB/decade** with breathing frequency above 0.1 Hz (Hirsch & Bishop 1981; via aerospace review). Breathing frequency alone (0.03–0.5 Hz, constant HR) changes: SDNN up to 33%, RMSSD up to 37%, pNN50 up to 75%, LF power up to 72%, HF up to 36% (Schipke et al.). Unpaced vs paced breathing (n=59 SCI): LF 1292 vs 573 ms²; LF% 64 vs 42%; LF/HF 3.2 vs 1.1; RMSSD statistically unchanged (PMC9309192). Breathing <9/min shifts respiratory power into the LF band, corrupting LF/HF and HF.
- **Respiratory gating of the baroreflex:** inspiration decreases, expiration increases baroreflex stimulation of vagal motoneurons (Eckberg "respiratory gate"; La Rovere review) — RSA is a vagal-modulation phenomenon gated centrally and via baroreflex.
- **Implementation recommendation:** Synthetic engine must co-simulate respiration (rate + tidal volume) as a driver of HF/RMSSD amplitude; at 0.1 Hz (6/min) breathing, LF-band RSA inflates LF/HF — a required test case.

### Claim 6.4 — What HRV can and cannot claim (synthetic-data guidance)
- **Can:** index cardiac vagal modulation (RMSSD, HF with respiratory control), global autonomic flexibility (SDNN), baroreflex engagement (sequence/α indices), prognostic risk strata.
- **Cannot:** read out sympathetic nerve traffic (LF, LF/HF invalid); distinguish sympathetic vs vagal contributions at high HR without context (HR-HRV mathematical coupling — van Roon 2016 Hypertension 68:e63, Sacha/Gasior HR-dependence work; correct or stratify by HR); infer "stress" univariately.
- **Wearable-specific:** pulse-rate variability (PPG) approximates HRV at rest but degrades with motion; artifact editing dominates real-world accuracy (Nunan 2010 flagged editing failures as systematic error source).

---

## 7. Interactions and Non-Cardiac Autonomic Signals

### Claim 7.1 — Accentuated antagonism (sympathetic–parasympathetic co-activation)
- Vagal HR effect is **augmented by background sympathetic activity** (Levy 1971, Circ Res 29:437–445, PMID 4330524, DOI 10.1161/01.RES.29.5.437); mechanisms: β-adrenergic cAMP elevation sensitizes muscarinic effect; M2 activation inhibits cAMP/↑PDE2; presynaptic α2-adrenergic inhibition of vagal ACh release partially counteracts (rat/human data summarized in S1566070218303084 review; MDPI 2308-3425/7/4/54). Demonstrated in conscious dogs during exercise (Stramba-Badiale 1991) and humans (Uijtdehaage & Thayer 2000, Clin Auton Res 10:107–110). Any vagal traffic can nullify sympathetic SA-node influence (Samaan 1935, cited in PMC2269357).
- **Evidence level:** **E4** (replicated, mechanistically grounded; quantitative human gains sparse).
- **Implementation recommendation:** HR = f(vagal, symp) with interaction term: vagal gain scaled by (1 + k·symp_level), k ≈ 1–3 (uncertain, E1–E2 for exact k; treat as tunable with sensitivity analysis). Do not model branches as additive-independent.

### Claim 7.2 — EDA = purely sympathetic cholinergic (wearable channel)
- Eccrine sweat glands are innervated by **sympathetic cholinergic sudomotor fibers only** (ACh, not NE); simultaneous nerve recordings show EDA transients track skin sympathetic bursts (encyclopedia.pub/entry/277; Boucsein 2012). **EDA is thus the cleanest wearable-specific sympathetic index — but it indexes sudomotor/emotional arousal, NOT cardiac or vasomotor sympathetic tone** (low correlation with MSNA/HRV sympathetic metrics across conditions — treat channels as dissociable).
- **SCR dynamics (Boucsein et al. 2012 committee report, Psychophysiology, DOI 10.1111/j.1469-8986.2012.01384.x):** onset latency **1–4 s** (1–3 s recommended window, Levinson & Edelberg 1985); rise time **0.5–5 s**; minimum amplitude **0.01–0.05 μS**; SCL typical 2–16 μS (range 1–40); non-specific SCRs 1–3/min at rest (up to ~10/min; ~20–25/min high arousal); recovery half-time ~2–10 s.
- **Evidence level:** **E4–E5** (consensus standards).
- **Implementation recommendation:** EDA model: sudomotor burst input (rate-modulated by arousal state) → impulse response with delay 1–3 s, rise 1–3 s, exponential recovery τ_rec 3–10 s; amplitude distribution 0.05–2 μS event-related.

### Claim 7.3 — Pupil and skin temperature (secondary wearable links)
- Pupil: resting diameter mainly sympathetic; constriction amplitude/velocity parasympathetic; light-reflex latency ~200–250 ms; dilation after stimulus end latency ~0.8–0.9 s (healthy controls, Fabry pupillometry study, Sci Rep 2021, s41598-021-87589-x); redilation slow (tens of s). Relevant only to camera-based wearables; **E2** for quantitative norms.
- Skin temperature: see §5.2 — distal temperature tracks noradrenergic cutaneous vasoconstriction (arousal/cold) with minutes-scale dynamics, heavily confounded by environment. **E2–E3.**

---

## 8. Model-Ready Autonomic Parameters (Master Table)

| # | Parameter | Value / distribution | Units | Evidence | Source |
|---|-----------|----------------------|-------|----------|--------|
| 1 | Rest MSNA burst frequency (young adult) | 24 ± 6 (range 9–41) | bursts/min | E4 | PMC5142246 |
| 2 | Rest MSNA burst incidence | 38 ± 11 (range 16–75) | bursts/100 hb | E4 | PMC5142246 |
| 3 | MSNA increase, 60° HUT (45 min) | ~1.5–2× baseline (→ ~35–40 bursts/min) | bursts/min | E3 | Fu 2009 / fphys.2012.00278 |
| 4 | MSNA increase, presyncopal LBNP | 23±3 → 42±3 | bursts/100 hb | E3 | PMC2770161 |
| 5 | MSNA increase, 2-min handgrip 33% MVC | +130 ± 48% | % | E3 | PMID 8304526 |
| 6 | MSNA burst latency (R-wave→burst) | 1.3 ± 0.03 (→1.04 presyncope) | s | E4 | Fagius & Wallin 1980; PMC2770161 |
| 7 | Plasma NE supine → standing | 181±14 → 472±35 (SEM) | pg/mL | E3 | PMID 4084169 |
| 8 | NE spillover/clearance change, 30-min stand | +80% / −30% | % | E3 | doi 10.1152/jappl.1998.84.3.914 |
| 9 | Plasma NE half-life | ~2 | min | E1/E4 | Esler lineage (via PMC2290017) |
| 10 | Intrinsic HR (double blockade) | IHR = 118.1 − 0.57·age | bpm | E4 | Jose & Collison (ESC syncope guideline quote); jci.org/106167 |
| 11 | HRV remaining after double blockade | <2% | % | E3 | PMID 7733345 |
| 12 | Cardiovagal BRS, young supine (phenylephrine) | ~15–20 (16.0±1.8; 18.1±8.9) | ms/mmHg | E4 | PMC6931942 Table 1 |
| 13 | Cardiovagal BRS age gradient (phenylephrine) | 19.5 → 10.7 → 6.0 (23–39/40–59/60–77 y) | ms/mmHg | E4 | Laitinen (in PMC6931942) |
| 14 | Sequence BRS population (up/down, geometric mean) | 13.7/13.9 (18–29 y) → 6.2/7.0 (50–60 y) | ms/mmHg | E4 | Kardos n=1134 (in PMC6931942) |
| 15 | Spontaneous vs phenylephrine BRS bias | underestimate 33–67% | % | E3 | PMC2745725 |
| 16 | BRS prognostic cutoff (post-MI) | <3 ms/mmHg → RR 2.8 | ms/mmHg | E5 | ATRAMI (in PMC6931942) |
| 17 | Sympathetic (MSNA) baroreflex gain | −12.6 ± 7.8 | %/mmHg | E3 | doi 10.1152/ajpheart.1999.276.5.H1691 |
| 18 | CBR–HR logistic (rest, human) | A1 17.1±2.7 bpm; A2 0.15±0.03; A3 99.9±5.0 mmHg; A4 55.6±1.8 bpm; Gmax −0.58±0.10 | mixed | E3 | PMC1780016 |
| 19 | CBR–HR Gmax after muscarinic blockade | −0.06 ± 0.01 (≈90% vagal) | bpm/mmHg | E3 | PMC1780016 |
| 20 | CBR–MAP Gmax | ≈ −0.24 to −0.4 | mmHg/mmHg | E3 | PMC1780016; Ogoh 2018 parabolic |
| 21 | Baroreflex max gain formula | Gmax = P1·P2/4 | — | E1 | Kent/Kawada logistic; PMID 16714364 |
| 22 | Baroreflex frequency range | full at ~0.01 Hz; ineffective >0.1 Hz | Hz | E3 | pone.0248428 (and animal transfer data) |
| 23 | Vagal cardiac latency | 200–600 ms (>50% HR effect <1 s) | s | E4 | PMC6931942; Warner & Cox via PMC6932299 |
| 24 | Sympathetic cardiac latency / pure delay | onset 2–3 s (canine pure delay 1.7 s); peak slower | s | E4 | PMC6931942; PMID 2912176 |
| 25 | Sympathetic SA-node bandwidth | ≤0.1–0.15 Hz (vagal ≥0.4–0.5 Hz) | Hz | E3 | Saul 1991 via PMC2269357 |
| 26 | Neurovascular transduction latency | nadir ~4.2 ± 0.6 cardiac cycles post-burst | cycles (~4 s) | E2 | UT Arlington abstract (Bohrium); PMC7988755 (review) |
| 27 | Thoracic blood shift on standing | 500–1000 mL below diaphragm; bulk <10 s; complete 3–5 min | mL | E4 | PMC2269496; joim.12021 |
| 28 | Transcapillary plasma loss, standing | −10% (≈500 mL) at 5 min; −15–20% (≈700 mL) at 10 min | mL | E4 | Lundvall (in PMC2269496) |
| 29 | Cardiac output, continued standing | −20% | % | E4 | joim.12021 |
| 30 | Standing HR response | peak ~beat 15 (+10–20), settle +10–15 | bpm | E4 | Ewing 30:15 physiology; PMC13068710 |
| 31 | OH / initial OH criteria | ≥20/10 mmHg ≤3 min; ≥40/20 ≤15 s | mmHg | E5 | Freeman 2011 (Clin Auton Res 21:69) |
| 32 | RAAS engagement delay | minutes (PRA 2.5× post-tilt); aldosterone minutes–hours | — | E3 | physrev.00007.2024; Gajek 2005 |
| 33 | Leg venous compliance | 0.048 ± 0.007 | mL/100 mL/mmHg | E3 | PMID 14657040 |
| 34 | Foot venous pressure, motionless standing | ~90 (→10–20 with muscle pump) | mmHg | E1/E4 | doi 10.1152/advan.00182.2018 |
| 35 | HRR1 abnormal cutoff | ≤12 bpm (adj. RR 2.0); meta pooled HR 1.68 | bpm | E5 | PMID 10536127; Qiu 2017 |
| 36 | HRR vagal/sympathetic time constants | τ_v ≈ 15–30 s; τ_s ≈ 90–180 s (fit-dependent) | s | E3/E1 | PMC6932299 (Pierpont) |
| 37 | 5-min HRV norms (healthy) | SDNN 50±16; RMSSD 42±15; HF 657±777; LF/HF 2.8±2.6 | ms / ms² | E5 | PMID 20663071 (Nunan) |
| 38 | 24-h HRV norms | SDNN 141±39; RMSSD 27±12 | ms | E5 | Task Force 1996, PMID 8598068 |
| 39 | Valsalva ratio normal | ≥1.21 (age-graded 1.42→1.15) | ratio | E5 | Ewing; PMC13068710 |
| 40 | 30:15 ratio normal | ≥1.04 (age-graded 1.15→1.00) | ratio | E5 | Ewing; PMC13068710 |
| 41 | Deep-breathing E/I and HR range | ≥10–15 bpm diff; age-graded | bpm | E5 | Ewing; PMC13068710 |
| 42 | Handgrip ΔDBP normal | ≥16 mmHg | mmHg | E5 | Ewing; PMC13068710 |
| 43 | SCR latency / rise / recovery | 1–4 s / 0.5–5 s / τ_rec 3–10 s | s | E5 | Boucsein 2012, doi 10.1111/j.1469-8986.2012.01384.x |
| 44 | SCR min amplitude / typical SCL | 0.01–0.05 μS / 2–16 μS | μS | E5 | Boucsein 2012 |
| 45 | NS-SCR rate | 1–3/min rest (≤10; 20–25 high arousal) | /min | E4 | Boucsein 2012 (compiled) |
| 46 | Skin blood flow share of CO | ~5% normothermia → ≤60% heat stress | % | E4 | doi 10.1152/japplphysiol.01071.2005 |
| 47 | Pupil light-reflex latency | ~200–250 ms (dilation latency ~0.8–0.9 s) | ms | E2 | s41598-021-87589-x |
| 48 | Respiration confound magnitude | SDNN ±33%; RMSSD ±37%; LF ±72% (0.03–0.5 Hz breathing) | % | E3 | Schipke (via indjaerospacemed review); PMC9309192 |
| 49 | RSA amplitude vs breathing frequency | −20 dB/decade above 0.1 Hz | dB/dec | E3 | Hirsch & Bishop 1981 (via review) |
| 50 | Accentuated antagonism | vagal HR gain amplified by sympathetic background (interaction term required) | — | E4 | PMID 4330524; Uijtdehaage & Thayer 2000 |

---

## 9. Validation Strategy (Engine-Level)

1. **Bench-top reflex tests (in silico replications):** phenylephrine ramp → BRS within prescribed distribution; neck-suction pulse → CBR–HR Gmax ≈ −0.5 bpm/mmHg; Valsalva → 4-phase waveform with VR ≥ 1.21 in "healthy" cohort.
2. **Orthostatic scenario:** active stand reproduces pooling (<10 s), BP dip/recovery (<30 s), HR 30:15 ≥ 1.04, MSNA-equivalent ~2×, NE ~2.5× over 5 min, plasma-volume drift −10%/5 min.
3. **Exercise scenario:** intensity-graded logistic resetting (P3, P4 shift, Gmax preserved), BRS fall at onset, HRR1 > 12 bpm "healthy", ≤12 bpm "deconditioned/disease".
4. **HRV battery:** supine 5-min distributions match Nunan 2010; paced 0.1-Hz breathing test must inflate LF and LF/HF without sympathetic change (confound reproduction); double-blockade test collapses HRV >98%.
5. **Disease phenotypes:** post-MI (BRS ~7), CHF (BRS ~2–4, HRR blunted), autonomic failure (no MSNA rise, OH criteria met), aging (BRS and IHR gradients).
6. **Cross-channel coherence:** EDA events (sympathetic cholinergic) need NOT covary with cardiac sympathetic metrics — validated dissociation is a feature; skin temperature follows distal vasoconstriction on slow timescale.

---

## 10. Key Uncertainties / Sparse-Evidence Flags

- Exact human sympathetic SA-node time constant (canine pure delay 1.7 s; human corner frequencies inferred, not directly measured) — treat τ_s as prior with wide bounds.
- Neurovascular transduction kernel values (4.2-cycle nadir from a single abstract) — provisional.
- Venous stress-relaxation kinetics in humans — acknowledged as quantitatively unknown (PMC2269496).
- Accentuated antagonism interaction coefficient k in humans — direction certain, magnitude sparse.
- Sex differences in sympathetic transduction (attenuated in young women) — replicated but effect-size distributions incomplete.
- PPG-based pulse-rate variability vs ECG-HRV equivalence under motion — known degradation, not quantified here (Pass 2 candidate).
