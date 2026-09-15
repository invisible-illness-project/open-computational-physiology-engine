import copy
import numpy as np
from scipy.integrate import solve_ivp
from simulation.latent_physiology import LatentPhysiologyState
from simulation.behavior import BehaviorModel
from simulation.symptoms import SymptomFramework
from simulation.time_engine import TimeEngine, SLEEP_STAGE_CODES, SLEEP_STAGE_NAMES
from simulation.event_kernels import (
    EventKernelManager, pem_symptom_kernel, slowed_recovery_kernel,
    pem_second_wave_kernel,
)


class SimulationEngine:
    """
    Simulates the closed-loop cardiovascular system beat by beat,
    reproducing the original MATLAB solver structure but with Pythonic
    extensions, latent state extraction, behavioral/symptom loops, and
    temporal tracking.

    G-P0-01 (compounding fix): the engine snapshots an IMMUTABLE
    ``baseline_params`` at the start of every run.  Each beat the effective
    parameter set is recomputed as f(baseline, active event kernels,
    circadian/sleep overlay, t) -- never from already-modified parameters --
    so multiplicative behavior perturbations cannot compound across beats,
    and parameters return EXACTLY to baseline after event recovery.

    G-P0-02 (PEM): exertion state is wired into the time engine (previously
    dead code) and PEM is realized as two decoupled, evidence-anchored
    kernels (symptom kernel, E2 timing; slowed-recovery kernel, E2 long-COVID
    proxy).  A physiological "second wave" exists only as an E0 hypothesis,
    OFF by default (honesty flag ``extrapolated_E0`` when enabled).

    G-P0-06 (circadian/sleep): the time engine carries wall time + day
    index; a cosinor (24 h, optional 12 h harmonic) couples into model
    parameters (Hm/HM chronotropic set point, defended-pressure set point
    p2Ru/p2Ra) and a sleep/wake state machine provides a REAL ``is_sleeping``
    (previously hardcoded False) with stage-conditioned autonomic shifts.

    Wave-2 contract (W2-E HRV module): :meth:`get_hrv_inputs` exposes the
    mean-HR trajectory plus autonomic state (vagal/sympathetic drive,
    respiration rate) -- see the method docstring for the API.

    G-P0-05 (structured HRV): ``hrv_model="structured"`` (default) replaces
    the legacy uniform +/-hrv_noise beat perturbation with the mechanistic
    IPFM generator of :mod:`simulation.hrv` (RSA + Mayer 0.1 Hz + 1/f
    fractal + Bernoulli ectopy), generated from the noise-free mean-HR
    trajectory after the run and attached to the results as
    ``beat_times_s`` / ``rr_intervals_ms`` / ``beat_types`` /
    ``hrv_provenance``.  ``hrv_model="legacy"`` keeps the old uniform-noise
    path for regression comparison (no structured outputs attached).

    NOTE (noise-sensitivity finding, reported to orchestrator): the legacy
    uniform +/-2% cycle-length noise is NOT benign -- it feeds back through
    the stiff baroreflex loop and depresses the healthy 100-s-tilt
    sustained dHR from ~27.6 to ~18.5 bpm (frozen HUT reference direction:
    passive tilt > active stand ~+25).  The noise-free structured
    trajectory is the more physiological one; two noise-sensitive
    orthostatic sanity tests that previously passed on a lucky noise draw
    (neuropathic-POTS and hyperadrenergic-pressor comparisons, both
    already documented engine-falsified regimes per G-P0-03) now expose
    those documented limitations.  Re-baselining those fixtures is W1-C
    scope (tests/test_orthostatic_response.py is outside W2-E ownership).
    """

    def __init__(self, model, dt=0.01, hrv_noise=0.02, seed=None,
                 start_hour=8.6667, circadian_enabled=True, second_harmonic=False,
                 ou_enabled=True, menstrual_enabled=False,
                 circadian_gain_modulation=0.0,
                 sleep_start_hour=23.0, wake_hour=7.0,
                 fragmentation_prob_per_hour=0.0, osa_enabled=False,
                 pem_enabled=None, pem_second_wave_E0=False,
                 hrv_model="structured", hrv_config=None):
        self.model = model
        self.dt = dt
        self.hrv_noise = hrv_noise
        if hrv_model not in ("structured", "legacy"):
            raise ValueError(
                f"hrv_model must be 'structured' or 'legacy', got {hrv_model!r}")
        self.hrv_model = hrv_model
        self.hrv_config = hrv_config
        # Optional RNG seed for reproducible HRV noise. seed=None (default)
        # preserves the previous non-deterministic behavior.
        self.seed = seed

        # start_hour default = 08:40, the morning ZERO-CROSSING (mesor) of
        # the HR cosinor (acrophase 14:40, EVD-HLTH-003): the KB nominal
        # parameter set is treated as the circadian mesor, so legacy
        # minute-scale ODE protocols run at the reference phase (circadian
        # offset ~0) unless the caller explicitly selects a time of day.
        # Circadian coupling remains fully active; pass start_hour (e.g.
        # 14.0 / 2.0) or use run_multiday() to study circadian effects.
        self.start_hour = float(start_hour)

        self.circadian_enabled = bool(circadian_enabled)
        # Circadian modulation of baroreflex Hill gains (kR/kH), per
        # docs/validation_strategy.md §3.  The MAGNITUDE is unresolved in the
        # evidence package (E5): default 0.0 (OFF) until an anchor exists;
        # the channel is implemented and configurable.
        self.circadian_gain_modulation = float(circadian_gain_modulation)
        # Fraction of the ABPM nocturnal-dip factor actually coupled into
        # p2Ru/p2Ra in the ODE core.  Default 0.0 (OFF): defended-pressure
        # shifts drive HR inversely in this 0-D baroreflex and destabilize
        # the stiff loop (see _circadian_param_overlay docstring).  The full
        # dip is exposed in the multiday slow-layer "bp_setpoint_factor".
        self.circadian_bp_coupling = 0.0

        # PEM configuration.  None (default) = auto: PEM symptom kernel only
        # for ME/CFS phenotypes; slowed-recovery physiology applies to all
        # subjects.  pem_second_wave_E0 is the explicit E0 opt-in (default
        # OFF per SPEC).
        self.pem_enabled = pem_enabled
        self.pem_second_wave_E0 = bool(pem_second_wave_E0)

        # Instantiate architectural subsystems
        self.latent_state = LatentPhysiologyState()
        self.behavior = BehaviorModel()
        self.symptoms = SymptomFramework()
        self.time_engine = TimeEngine(
            start_hour=self.start_hour, circadian_enabled=circadian_enabled,
            second_harmonic=second_harmonic, ou_enabled=ou_enabled,
            menstrual_enabled=menstrual_enabled, seed=seed,
            sleep_start_hour=sleep_start_hour, wake_hour=wake_hour,
            fragmentation_prob_per_hour=fragmentation_prob_per_hour,
            osa_enabled=osa_enabled)

        # Engine-level physiological event kernels (PEM symptom layer,
        # slowed autonomic recovery).  Separate from the behavior kernels.
        self.kernels = EventKernelManager()
        self._pem_processed_exertions = 0

        # Immutable per-run baseline parameter snapshot (set in run())
        self.baseline_params = None

        # Wave-2 HRV contract buffers (populated during run/run_multiday)
        self._hrv_inputs = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _is_mecfs(self):
        return self.model.phenotype is not None and "mecfs" in self.model.phenotype

    def _pem_symptom_enabled(self):
        if self.pem_enabled is not None:
            return bool(self.pem_enabled)
        return self._is_mecfs()

    def _current_exertion(self):
        """Real exertion channel: behavior 'exercise' maps to its configured
        intensity (0..1); everything else is 0 (G-P0-02 wiring fix)."""
        if self.behavior.current_activity == "exercise":
            return float(self.behavior.exertion_intensity)
        return 0.0

    def _schedule_pending_pem_kernels(self, rng, pem_symptom=None, second_wave=None):
        """Turn newly closed exertion episodes into PEM/recovery kernels."""
        pem_symptom = self._pem_symptom_enabled() if pem_symptom is None else bool(pem_symptom)
        second_wave = self.pem_second_wave_E0 if second_wave is None else bool(second_wave)
        hist = self.time_engine.exertion_history
        while self._pem_processed_exertions < len(hist):
            ep = hist[self._pem_processed_exertions]
            self._pem_processed_exertions += 1
            end_s = ep.get("end_s", self.time_engine.wall_seconds)
            intensity = ep.get("intensity", 0.7)
            # Physiological slowed-recovery kernel: ALL subjects (healthy
            # 3-6 h; post-VT1 patient 9-13 h, E2 long-COVID proxy).
            self.kernels.add_kernel(
                slowed_recovery_kernel(end_s, is_patient=self._is_mecfs(),
                                       intensity=intensity, rng=rng))
            # PEM symptom kernel: ME/CFS only (disease-defining feature).
            if pem_symptom:
                self.kernels.add_kernel(
                    pem_symptom_kernel(end_s, rng=rng))
                if second_wave:
                    # E0 hypothesis -- explicit opt-in only, honesty-flagged.
                    self.kernels.add_kernel(
                        pem_second_wave_kernel(end_s, rng=rng))

    def _circadian_param_overlay(self, params):
        """Couple circadian/sleep state into model parameters (G-P0-06).

        Channels (all computed against the values passed in, which trace
        back to the immutable baseline -- no compounding):

        * Chronotropic set point (p2H): the 24-h cosinor HR offset
          (amplitude 13.5 bpm, acrophase ~14:40, EVD-HLTH-003) + OU
          day-to-day drift (EVD-POP-004) + optional menstrual hook is
          applied as an EXACT re-targeting of the HR controller's Hill
          half-saturation pressure p2H, solved at the supine operating
          point pcm0 = 93.333 mmHg.  RATIONALE (validated empirically,
          2025-11): an additive Hm/HM shift of +-13.5 bpm moves the
          operating point onto the steep flank of the kH=25 Hill curve and
          triggers the model's documented intrinsic limit cycle; the p2H
          re-targeting produces the anchored swing (day ~+13 / night ~-13
          bpm) without destabilizing the loop.
        * Defended-pressure set point (p2Ru/p2Ra): multiplicative factor
          reproducing the nocturnal dip.  ATTENUATED BY DEFAULT
          (self.circadian_bp_coupling, fraction of the ABPM dip actually
          applied, default 0.0): in this 0-D model HR is purely
          baroreflex-driven, so defended-pressure shifts drive HR
          INVERSELY and even +-2.5% p2R shifts destabilize the stiff
          resistance loop -- coupling the full 14% ABPM dip through p2R
          falsifies the HR rhythm direction.  The full dip is therefore
          represented in the slow-layer output channel
          ("bp_setpoint_factor" in run_multiday results), and this ODE
          coupling fraction is left configurable pending a model revision
          (same model-adequacy class as the SBP-pressor xfail).
        * kR/kH: OPTIONAL gain modulation (validation_strategy.md §3);
          magnitude unresolved (E5) -> default OFF (factor 1.0).
        """
        if not self.circadian_enabled:
            return params
        p = dict(params)

        # Chronotropic set point via exact p2H re-targeting
        shift_bpm = self.time_engine.circadian_hr_offset_bpm()
        if shift_bpm != 0.0:
            pcm0 = 93.333  # supine operating point (state-init heuristic)
            kH, HM, Hm, p2H = p["kH"], p["HM"], p["Hm"], p["p2H"]
            s = (p2H / pcm0) ** kH
            g = s / (1.0 + s)
            g2 = min(0.95, max(0.05, g + (shift_bpm / 60.0) / max(1e-6, HM - Hm)))
            s2 = g2 / (1.0 - g2)
            p["p2H"] = pcm0 * s2 ** (1.0 / kH)

        # Defended-pressure set point (attenuated; see docstring)
        if self.circadian_bp_coupling != 0.0:
            f_full = self.time_engine.circadian_bp_factor()
            f = 1.0 + self.circadian_bp_coupling * (f_full - 1.0)
            p["p2Ru"] = p["p2Ru"] * f
            p["p2Ra"] = p["p2Ra"] * f

        if self.circadian_gain_modulation != 0.0:
            g = 1.0 + self.circadian_gain_modulation * self.time_engine.get_circadian_drive()
            p["kR"] = p["kR"] * g
            p["kH"] = p["kH"] * g
        return p

    def _effective_latent_state(self, t):
        """Latent state + transient kernel offsets (PEM etc.), composed
        additively in effect space.  Offsets are applied to a COPY so the
        evolving latent dynamics never integrate them (no compounding)."""
        offsets = self.kernels.compute_latent_offsets(t)
        if not offsets:
            return self.latent_state
        eff = self.latent_state.copy()
        bounds = {"sympathetic_tone": (0.0, 1.0), "parasympathetic_tone": (0.0, 1.0),
                  "stress_load": (0.0, 1.0), "metabolic_reserve": (0.0, 1.0),
                  "sleep_pressure": (0.0, 1.0), "inflammatory_burden": (0.0, 10.0),
                  "autonomic_recovery_capacity": (0.0, 1.0)}
        for name, off in offsets.items():
            lo, hi = bounds.get(name, (-10.0, 10.0))
            eff.set(name, min(hi, max(lo, eff.get(name) + off)))
        return eff

    # ------------------------------------------------------------------
    # Main beat-by-beat ODE loop
    # ------------------------------------------------------------------
    def run(self, tilt_params):
        """
        Runs the simulation.
        tilt_params: dict containing:
          - tup: start of tilt (s)
          - tend: end of simulation (s)
          - height: hydrostatic height (cm)
          - angle: tilt angle (degrees)
          - active_behavior: optional string trigger (e.g. 'exercise', 'meal')
          - exercise_duration_s: optional exercise-bout duration (s)
          - exertion_intensity: optional exercise intensity in [0, 1]
        """
        # Seed the RNG for reproducible HRV noise if requested
        if self.seed is not None:
            np.random.seed(self.seed)
        pem_rng = np.random.default_rng(None if self.seed is None else self.seed + 7)

        # Immutable baseline parameter snapshot for this run (G-P0-01).
        self.baseline_params = copy.deepcopy(self.model.params)

        # Set up behavior if specified in tilt_params
        active_behavior = tilt_params.get("active_behavior", "rest")
        self.behavior.trigger_behavior(
            active_behavior, start_s=0.0, rng=pem_rng,
            exercise_duration_s=tilt_params.get("exercise_duration_s", 300.0),
            exertion_intensity=tilt_params.get("exertion_intensity", 0.7),
            kernel_time_scale=tilt_params.get("kernel_time_scale", 1.0))

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
        # Wave-2 HRV contract channels (per evaluated point)
        hrv_keys = ["mean_hr_bpm", "vagal_drive", "sympathetic_drive",
                    "respiration_rate_brpm", "sleep_stage"]

        output_series = {k: [] for k in (latent_keys + symptom_keys + hrv_keys)}

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

            # --- Temporal updates for this cardiac cycle -----------------
            # Advance the wall clock with the REAL exertion channel
            # (G-P0-02 fix: current_exertion was never passed -> PEM could
            # never trigger).
            self.time_engine.step(T, current_exertion=self._current_exertion())
            is_sleeping = self.time_engine.is_sleeping()  # REAL state (was hardcoded False)

            # Update homeostatic sleep pressure
            sleep_pres = self.time_engine.update_sleep_pressure(
                self.latent_state.get("sleep_pressure"),
                is_sleeping=is_sleeping,
                dt_seconds=T
            )
            self.latent_state.set("sleep_pressure", sleep_pres)
            self.latent_state.set("circadian_drive", self.time_engine.get_circadian_drive())

            # Update sleep-dependent recovery (PEM itself lives in kernels)
            self.time_engine.update_recovery_and_pem(
                self.latent_state, T, is_sleeping=is_sleeping)

            # Schedule PEM / slowed-recovery kernels for newly closed
            # exertion episodes (G-P0-02).
            self._schedule_pending_pem_kernels(pem_rng)

            # Modulate latent states with current behavior
            self.behavior.modulate_latent_states(self.latent_state, current_ts, dt_seconds=T)

            # --- Effective parameters for the NEXT beat ------------------
            # f(baseline, behavior kernels, circadian/sleep overlay, t) --
            # NEVER from already-modified params (G-P0-01 fix).
            effective = self.behavior.modulate_parameters(
                self.baseline_params, self.latent_state, time_s=current_ts)
            effective = self._circadian_param_overlay(effective)
            self.model.params = effective

            # Transient latent offsets from physiological event kernels
            eff_latent = self._effective_latent_state(current_ts)

            # Autonomic state for the HRV contract (circadian + sleep stage)
            vagal_drive, symp_drive, resp_rate = self.time_engine.autonomic_state()
            # PEM / slowed-recovery latent offsets suppress vagal drive
            pem_offsets = self.kernels.compute_latent_offsets(current_ts)
            vagal_drive = float(min(1.0, max(0.0,
                vagal_drive + pem_offsets.get("parasympathetic_tone", 0.0))))
            stage_code = SLEEP_STAGE_CODES[self.time_engine.sleep_stage]

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
                eff_latent.update_derived_states(pcm, self.model.params)

                # Compute symptoms probabilistically from updated state
                current_hr = y_val[9] * 60.0  # bpm
                symptom_scores = self.symptoms.compute_symptoms(eff_latent, current_hr, pcm)

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
                output_series["sympathetic_tone"].append(eff_latent.get("sympathetic_tone"))
                output_series["parasympathetic_tone"].append(eff_latent.get("parasympathetic_tone"))
                output_series["baroreflex_gain"].append(self.model.params["kR"])
                output_series["blood_volume"].append(self.model.params["TotalVol"])
                output_series["left_ventricular_pressure"].append(plv)
                output_series["aortic_flow"].append(qav)
                output_series["mitral_flow"].append(qmv)
                output_series["carotid_pressure"].append(pc)
                output_series["circadian_drive"].append(eff_latent.get("circadian_drive"))
                output_series["sleep_pressure"].append(eff_latent.get("sleep_pressure"))
                output_series["hydration"].append(eff_latent.get("hydration"))
                output_series["stress_load"].append(eff_latent.get("stress_load"))
                output_series["inflammatory_burden"].append(eff_latent.get("inflammatory_burden"))
                output_series["metabolic_reserve"].append(eff_latent.get("metabolic_reserve"))
                output_series["hormonal_state"].append(eff_latent.get("hormonal_state"))
                output_series["autonomic_recovery_capacity"].append(eff_latent.get("autonomic_recovery_capacity"))

                # Log all symptom states
                for sk in symptom_keys:
                    output_series[sk].append(symptom_scores[sk])

                # Log HRV-contract channels
                output_series["mean_hr_bpm"].append(current_hr)
                output_series["vagal_drive"].append(vagal_drive)
                output_series["sympathetic_drive"].append(symp_drive)
                output_series["respiration_rate_brpm"].append(resp_rate)
                output_series["sleep_stage"].append(stage_code)

            # Set initial conditions for next cycle
            y_init = sol.y[:, -1]
            current_ts = sol.t[-1]

            # Determine next cycle length T from the heart rate Hc at the end of the beat
            # Legacy mode: uniform +/-hrv_noise beat noise (kept for
            # regression comparison).  Structured mode (G-P0-05): the ODE
            # trajectory stays noise-free so mean_hr_bpm is the clean IPFM
            # baseline; structured beats are generated post-run by
            # simulation.hrv (see below).
            H_end = y_init[9] # Hc
            base_T = 1.0 / H_end
            if self.hrv_model == "legacy":
                noise = np.random.uniform(-1.0, 1.0) * self.hrv_noise
            else:
                noise = 0.0
            T = round((base_T * (1.0 + noise)) / self.dt) * self.dt

        # Add last point
        time_series.append(current_ts)
        state_series.append(y_init)

        # Carry over final states to ensure array length matches
        for k in output_series.keys():
            output_series[k].append(output_series[k][-1])

        # Close any open exertion episode and schedule its kernels
        self.time_engine.close_exertion()
        self._schedule_pending_pem_kernels(pem_rng)

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
            "honesty_flags": self.kernels.honesty_flags() + self.behavior.kernels.honesty_flags(),
        }

        # Cycle 2 venomotor / stress-relaxation states and the resulting lower
        # venous pressure (effective capacity = VMvl - Vvm + Vsr).
        if state_arr.shape[1] >= 12:
            Vvm_arr = state_arr[:, 10]
            Vsr_arr = state_arr[:, 11]
            VMvl_eff = (self.model.params["VMvl"] - Vvm_arr + Vsr_arr)
            results["Vvm"] = Vvm_arr
            results["Vsr"] = Vsr_arr
            results["pvl"] = (1.0 / self.model.params["mvl"]) * np.log(
                VMvl_eff / np.maximum(1.0, VMvl_eff - state_arr[:, 3])
            )

        for k, v in output_series.items():
            results[k] = np.array(v)

        # Populate the wave-2 HRV contract from this run
        self._hrv_inputs = {
            "time_s": time_arr.copy(),
            "mean_hr_bpm": results["mean_hr_bpm"],
            "vagal_drive": results["vagal_drive"],
            "sympathetic_drive": results["sympathetic_drive"],
            "respiration_rate_brpm": results["respiration_rate_brpm"],
            "sleep_stage_code": results["sleep_stage"].astype(int),
            "sleep_stage_names": [SLEEP_STAGE_NAMES[int(c)] for c in results["sleep_stage"].astype(int)],
            "source": "ode_beat_loop",
            "honesty_flags": list(results["honesty_flags"]),
        }

        # G-P0-05: structured beat generation from the noise-free mean-HR
        # trajectory (W2-E output contract; deterministic under self.seed).
        if self.hrv_model == "structured":
            from simulation.hrv import generate_rr_series
            rr_out = generate_rr_series(
                self._hrv_inputs, seed=self.seed, config=self.hrv_config)
            results["beat_times_s"] = rr_out["beat_times_s"]
            results["rr_intervals_ms"] = rr_out["rr_intervals_ms"]
            results["beat_types"] = rr_out["beat_types"]
            results["hrv_provenance"] = rr_out["provenance"]

        # Restore the sacred parameter set: after the run, model.params is
        # bit-identical to the pre-run (KB + perturbation + prior) values,
        # regardless of which events fired during the run (G-P0-01).
        self.model.params = copy.deepcopy(self.baseline_params)

        return results

    # ------------------------------------------------------------------
    # Multi-day slow-layer simulation (circadian/sleep/OU/PEM timescales)
    # ------------------------------------------------------------------
    def resting_hr_bpm(self, params=None):
        """Model-consistent resting heart rate (bpm): the HR controller's
        Hill target at the supine mean-carotid operating point used by
        initialize_steady_state (pcm0 = 93.333 mmHg)."""
        p = params if params is not None else self.model.params
        pcm0 = 93.333  # supine operating point (state-init heuristic)
        kH = p["kH"]
        hf = (p["HM"] - p["Hm"]) * (p["p2H"] ** kH) / (pcm0 ** kH + p["p2H"] ** kH) + p["Hm"]
        return float(hf * 60.0)

    def run_multiday(self, days, step_s=60.0, exertion_schedule=None,
                     pem_enabled=None, include_second_wave_E0=False, seed=None):
        """Day-scale simulation of the SLOW layers (G-P0-02/G-P0-06):
        circadian cosinor, sleep/wake stages, OU baseline drift, exertion
        episodes, and PEM kernels -- sampled at ``step_s`` (default 60 s).

        Per the multi-timescale architecture (TEMPORAL dossier §9,
        granularity rule), the stiff ODE core is BYPASSED outside active
        posture/exercise transients and replaced by its model-consistent
        resting steady state; event kernels and circadian/sleep/OU
        modulators set the mean-HR trajectory and autonomic state.  This is
        the supported path for circadian amplitude, multi-day drift, and PEM
        dynamics (integrating days at beat resolution is computationally
        infeasible and physiologically unnecessary).

        exertion_schedule: list of dicts {"day": int, "hour": float,
        "duration_min": float, "intensity": 0..1}.  include_second_wave_E0
        is the explicit E0 physiological-second-wave opt-in (default OFF).
        """
        days = int(days)
        if days < 1:
            raise ValueError("run_multiday requires days >= 1")
        rng = np.random.default_rng(seed if seed is not None else self.seed)
        pem_enabled = self._pem_symptom_enabled() if pem_enabled is None else bool(pem_enabled)

        # Reset temporal state for a clean multi-day horizon
        self.time_engine.wall_seconds = 0.0
        self.kernels.clear()
        self._pem_processed_exertions = 0
        self.baseline_params = copy.deepcopy(self.model.params)

        rest_hr = self.resting_hr_bpm(self.baseline_params)
        hrmax_bpm = 60.0 * self.baseline_params["HM"]

        # Expand the exertion schedule into (start_s, end_s, intensity)
        events = []
        for ev in (exertion_schedule or []):
            start_s = (ev.get("day", 0) * 24.0 + ev.get("hour", 12.0)) * 3600.0
            end_s = start_s + ev.get("duration_min", 30.0) * 60.0
            events.append((start_s, end_s, float(ev.get("intensity", 0.7))))
        events.sort()

        n_steps = int(days * 86400.0 / step_s)
        time_s = np.empty(n_steps)
        hr = np.empty(n_steps)
        vagal = np.empty(n_steps)
        symp = np.empty(n_steps)
        resp = np.empty(n_steps)
        stage = np.empty(n_steps, dtype=int)
        pem_env = np.empty(n_steps)
        rec_env = np.empty(n_steps)
        bp_factor = np.empty(n_steps)

        for i in range(n_steps):
            t = i * step_s
            # Exertion channel: active event?
            intensity = 0.0
            for (s0, s1, inten) in events:
                if s0 <= t < s1:
                    intensity = inten
                    break
            self.time_engine.step(step_s, current_exertion=intensity)
            self._schedule_pending_pem_kernels(rng, pem_symptom=pem_enabled,
                                               second_wave=include_second_wave_E0)
            t = self.time_engine.wall_seconds  # post-step timestamp (aligned
            # with the state recorded below)
            time_s[i] = t
            bp_factor[i] = self.time_engine.circadian_bp_factor()

            v, s, rr = self.time_engine.autonomic_state()
            offsets = self.kernels.compute_latent_offsets(t)
            v = min(1.0, max(0.0, v + offsets.get("parasympathetic_tone", 0.0)))
            vagal[i] = v
            symp[i] = s
            resp[i] = rr
            stage[i] = SLEEP_STAGE_CODES[self.time_engine.sleep_stage]

            # Mean HR trajectory: resting baseline + circadian/OU offset +
            # sleep-stage offset + exertion elevation + PEM/recovery effects.
            h = rest_hr
            h += self.time_engine.circadian_hr_offset_bpm()
            h += self.time_engine.sleep_stage_hr_offset_bpm()
            if intensity > 0.0:
                # steady-state exercise HR ≈ rest + intensity*(HRmax - rest)
                # (HEALTHY dossier §4.2 implementation recommendation, E4)
                h += intensity * (hrmax_bpm - rest_hr)
            # PEM symptom-kernel envelope (0..severity): weakly elevates
            # resting/nocturnal HR (EVD-MECFS claim 4.6, E2 weak) -- flagged.
            pem_e = 0.0
            rec_e = 0.0
            for k in self.kernels.active_kernels(t):
                e = k.envelope(t)
                if k.event_id == "pem_symptom_episode":
                    pem_e = max(pem_e, e)
                elif k.event_id == "slowed_autonomic_recovery":
                    rec_e = max(rec_e, e)
                elif k.event_id == "pem_physiological_second_wave_E0":
                    pem_e = max(pem_e, 0.5 * e)
            pem_env[i] = pem_e
            rec_env[i] = rec_e
            h += 4.0 * pem_e   # E2-weak PEM resting-HR elevation (flagged)
            h += 4.0 * rec_e   # post-exercise HR elevation during slowed recovery
            hr[i] = h

        self.time_engine.close_exertion()
        self._schedule_pending_pem_kernels(rng, pem_symptom=pem_enabled,
                                           second_wave=include_second_wave_E0)

        honesty = self.kernels.honesty_flags()
        if pem_enabled and "pem_evidence_mode_extrapolation" not in honesty:
            honesty.append("pem_evidence_mode_extrapolation")

        self._hrv_inputs = {
            "time_s": time_s,
            "mean_hr_bpm": hr,
            "vagal_drive": vagal,
            "sympathetic_drive": symp,
            "respiration_rate_brpm": resp,
            "sleep_stage_code": stage,
            "sleep_stage_names": [SLEEP_STAGE_NAMES[c] for c in stage],
            "day_index": (time_s // 86400.0).astype(int),
            "hour_of_day": (self.time_engine.start_hour + time_s / 3600.0) % 24.0,
            "pem_symptom_envelope": pem_env,
            "slowed_recovery_envelope": rec_env,
            "bp_setpoint_factor": bp_factor,
            "source": "slow_layer_multiday",
            "honesty_flags": honesty,
        }
        return self._hrv_inputs

    # ------------------------------------------------------------------
    # Wave-2 contract getter (W2-E structured HRV module)
    # ------------------------------------------------------------------
    def get_hrv_inputs(self):
        """Wave-2 HRV-module contract (W2-E, G-P0-05).

        Returns a dict with the mean-HR trajectory and autonomic state that
        the IPFM beat generator consumes:

          "time_s"                 float64 [N], seconds since simulation start
          "mean_hr_bpm"            float64 [N], instantaneous MEAN heart rate
                                   (no beat noise; the IPFM m0 baseline)
          "vagal_drive"            float64 [N] in [0, 1], combined
                                   circadian/sleep/PEM vagal drive
          "sympathetic_drive"      float64 [N] in [0, 1]
          "respiration_rate_brpm"  float64 [N], state-conditioned respiration
                                   rate (drives RSA gating)
          "sleep_stage_code"       int [N], 0=awake 1=N1 2=N2 3=N3 4=REM
          "sleep_stage_names"      list[str] [N]
          "source"                 "ode_beat_loop" | "slow_layer_multiday"
          "honesty_flags"          list[str] (e.g. "extrapolated_E0",
                                   "pem_evidence_mode_extrapolation")
        Multi-day runs additionally carry "day_index", "hour_of_day",
        "pem_symptom_envelope" and "slowed_recovery_envelope".

        Populated by run() (beat-resolution, short transients) and by
        run_multiday() (coarse slow-layer horizon).  Returns None if no
        simulation has been executed yet.
        """
        return self._hrv_inputs
