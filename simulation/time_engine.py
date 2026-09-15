"""
Temporal physiology engine (G-P0-06 rewrite).

Carries a continuous wall-time clock (seconds since simulation start, plus
day index and hour-of-day), a cosinor circadian driver (24 h + optional 12 h
harmonic), a sleep/wake state machine with stage-conditioned autonomic
shifts, an Ornstein-Uhlenbeck day-to-day baseline drift process, and a real
exertion-history channel (fixing the dead-code PEM trigger path of G-P0-02).

Evidence anchors
----------------
* Circadian HR rhythm: cosinor amplitude ~13.5 bpm (half-range), acrophase
  ~14:40 lab / ~16:30-17:00 free-living (EVD-HLTH-003; HEALTHY dossier §2.1,
  E2).  Nocturnal SBP dip 14.1 +/- 4.6% (EVD-HLTH-003, E2/E5).
* Endogenous period ~24.18 h (EVD-TEMP-006); the entrained 24.0 h carrier is
  used by default (free-running period only matters for misalignment studies).
* Sleep architecture: NREM parasympathetic predominance, REM sympathetic
  surges on a vagal background; absolute stage-HR differences are SMALL
  (~2 bpm vs recumbent wake; n=1,047, EVD-HLTH-007).  Respiration: N3 ~13
  brpm low CV, REM ~16 brpm high CV, awake N(15.5, 2.3) (EVD-HLTH-010).
* Day-to-day within-person RHR CV ~= 4.6% (n=92,457; EVD-POP-004) reproduced
  by an OU process with tau ~3-7 d (TEMPORAL dossier §5, structure E5).
* Menstrual modulator (hook, OFF by default): luteal RHR +2-5 bpm, skin temp
  +0.2-0.3 C, RMSSD ~-10% (Alzueta 2022, PMID 35422659; EVD-TEMP-008, E2).

The old PEM constants (fixed 12-h delay, exertion>0.6 trigger, 2-h
resolution "for simulation speed demo") are REMOVED; PEM now lives in
evidence-anchored kernels (simulation/event_kernels.py, G-P0-02) driven by
the exertion history recorded here.
"""

import numpy as np


# Sleep-stage codes used throughout the engine and the HRV-module contract.
SLEEP_STAGE_CODES = {"awake": 0, "N1": 1, "N2": 2, "N3": 3, "REM": 4}
SLEEP_STAGE_NAMES = {v: k for k, v in SLEEP_STAGE_CODES.items()}


class SleepWakeStateMachine:
    """Scheduled sleep/wake machine with a 90-min ultradian stage cycle.

    Granularity: awake / N1 / N2 / N3 / REM ("REM-lite").  N3 predominates in
    the first third of the sleep window, REM in the last third (standard
    hypnogram structure, E4).  Sleep fragmentation is supported via a
    per-epoch awakening probability.  An OSA modulation hook exists but is
    EXPERIMENTAL and OFF by default (E3).
    """

    def __init__(self, sleep_start_hour=23.0, wake_hour=7.0,
                 fragmentation_prob_per_hour=0.0, osa_enabled=False, rng=None):
        self.sleep_start_hour = float(sleep_start_hour)
        self.wake_hour = float(wake_hour)
        self.fragmentation_prob_per_hour = float(fragmentation_prob_per_hour)
        # OSA hook (E3): experimental only, engine-inert unless enabled.
        self.osa_enabled = bool(osa_enabled)
        self.rng = rng if rng is not None else np.random.default_rng(0)
        self._stage = "awake"
        self._stage_time_s = 0.0
        self._awakening_remaining_s = 0.0

    def in_sleep_window(self, hour_of_day):
        if self.sleep_start_hour > self.wake_hour:  # e.g. 23 -> 7
            return hour_of_day >= self.sleep_start_hour or hour_of_day < self.wake_hour
        return self.sleep_start_hour <= hour_of_day < self.wake_hour

    def sleep_fraction_elapsed(self, hour_of_day):
        """Fraction of the sleep window elapsed, in [0, 1)."""
        window = (self.wake_hour - self.sleep_start_hour) % 24.0
        if window <= 0:
            return 0.0
        elapsed = (hour_of_day - self.sleep_start_hour) % 24.0
        return min(0.999, elapsed / window)

    def update(self, hour_of_day, dt_seconds):
        """Advance the state machine; returns the current stage name."""
        self._stage_time_s += dt_seconds
        if not self.in_sleep_window(hour_of_day):
            self._stage = "awake"
            self._stage_time_s = 0.0
            return self._stage

        # Brief spontaneous awakenings (sleep fragmentation capability)
        if self._awakening_remaining_s > 0.0:
            self._awakening_remaining_s -= dt_seconds
            return "awake"
        if (self.fragmentation_prob_per_hour > 0.0
                and self.rng.uniform() < self.fragmentation_prob_per_hour * dt_seconds / 3600.0):
            self._awakening_remaining_s = float(self.rng.uniform(60.0, 300.0))
            return "awake"

        frac = self.sleep_fraction_elapsed(hour_of_day)
        # 90-minute ultradian cycle; stage composition shifts across the night
        cycle_phase = (self._stage_time_s % (90.0 * 60.0)) / (90.0 * 60.0)
        if frac < 0.33:      # early night: deep NREM predominates
            stage = "N3" if cycle_phase < 0.55 else ("N2" if cycle_phase < 0.9 else "REM")
        elif frac < 0.67:    # mid night: N2 core
            stage = "N2" if cycle_phase < 0.6 else ("N3" if cycle_phase < 0.75 else "REM")
        else:                # late night: REM predominates
            stage = "REM" if cycle_phase < 0.4 else ("N2" if cycle_phase < 0.85 else "N1")
        if stage != self._stage:
            self._stage = stage
        return self._stage

    @property
    def stage(self):
        return self._stage

    def is_sleeping(self):
        return self._stage != "awake"


class TimeEngine:
    """Continuous wall-time + circadian + sleep + drift engine.

    Parameters
    ----------
    start_hour : float
        Hour-of-day at simulation start (default 08:00).
    circadian_enabled : bool
        Master switch for circadian coupling (default True).
    second_harmonic : bool
        Include the optional 12-h cosinor harmonic (default False; HR/temp
        rhythms are non-sinusoidal, TEMPORAL dossier §4, E5 structure).
    ou_enabled : bool
        Day-to-day OU baseline drift (default True; only matters on
        multi-day horizons).
    ou_tau_days : float
        OU mean-reversion time, evidence range 3-7 d (default 5 d; E5).
    ou_rhr_sd_bpm : float
        Stationary SD of the resting-HR drift, default 3.03 bpm (CV ~= 4.6%
        on a ~66 bpm mesor; EVD-POP-004).
    menstrual_enabled : bool
        Luteal-phase modulation hook; OFF unless a cohort config enables it
        (population-level toggle; E2 magnitudes, EVD-TEMP-008).
    seed : int or None
        Seed for the OU/fragmentation randomness.
    """

    def __init__(self, start_hour=8.0, circadian_enabled=True,
                 second_harmonic=False, ou_enabled=True, ou_tau_days=5.0,
                 ou_rhr_sd_bpm=3.03, menstrual_enabled=False,
                 menstrual_cycle_day=1.0, seed=None,
                 sleep_start_hour=23.0, wake_hour=7.0,
                 fragmentation_prob_per_hour=0.0, osa_enabled=False):
        self.start_hour = float(start_hour)
        self.wall_seconds = 0.0
        self.circadian_enabled = bool(circadian_enabled)
        self.second_harmonic = bool(second_harmonic)
        self.ou_enabled = bool(ou_enabled)
        self.ou_tau_days = float(ou_tau_days)
        self.ou_rhr_sd_bpm = float(ou_rhr_sd_bpm)
        self.menstrual_enabled = bool(menstrual_enabled)
        self.menstrual_cycle_day = float(menstrual_cycle_day)
        self.rng = np.random.default_rng(seed)

        # Circadian parameters (EVD-HLTH-003)
        self.hr_acrophase_h = 14.0 + 40.0 / 60.0   # ~14:40
        self.hr_amplitude_bpm = 13.5               # half-range of 24-h rhythm
        self.bp_acrophase_h = 14.25                # ~14:15
        self.bp_nocturnal_dip = 0.141              # 14.1 +/- 4.6% SBP dip

        # OU baseline-drift state (bpm, additive on resting HR)
        self.ou_state_bpm = 0.0

        # Exertion history: list of dicts (start_s, end_s, intensity, dose)
        self.exertion_history = []
        self._open_exertion = None

        self.sleep = SleepWakeStateMachine(
            sleep_start_hour=sleep_start_hour, wake_hour=wake_hour,
            fragmentation_prob_per_hour=fragmentation_prob_per_hour,
            osa_enabled=osa_enabled, rng=self.rng)

        # Backward-compatible legacy attributes (kept so external readers do
        # not break; the PEM logic that used pem_active/pem_onset_time was
        # removed in G-P0-02 -- see simulation/event_kernels.py).
        self.pem_active = False
        self.pem_onset_time = None

    # ------------------------------------------------------------------
    # Clock
    # ------------------------------------------------------------------
    @property
    def day_index(self):
        return int(self.wall_seconds // 86400.0)

    @property
    def hour_of_day(self):
        return (self.start_hour + self.wall_seconds / 3600.0) % 24.0

    @property
    def current_time_hours(self):
        """Backward-compatible alias for hour_of_day."""
        return self.hour_of_day

    def step(self, dt_seconds, is_sleeping=None, current_exertion=0.0):
        """Advance the wall clock, sleep machine, and OU drift.

        is_sleeping is now DERIVED from the sleep state machine when None
        (the engine no longer hardcodes False).  current_exertion > 0 opens/
        extends an exertion episode; 0 closes it (G-P0-02 wiring fix).
        """
        dt_seconds = float(dt_seconds)
        self.wall_seconds += dt_seconds
        stage = self.sleep.update(self.hour_of_day, dt_seconds)

        # OU baseline drift (exact discrete OU update)
        if self.ou_enabled:
            tau_s = self.ou_tau_days * 86400.0
            a = np.exp(-dt_seconds / tau_s)
            sd = self.ou_rhr_sd_bpm
            self.ou_state_bpm = (a * self.ou_state_bpm
                                 + sd * np.sqrt(max(0.0, 1.0 - a * a))
                                 * self.rng.standard_normal())

        # Exertion bookkeeping (real channel; fixes dead-code PEM trigger)
        if current_exertion > 0.0:
            if self._open_exertion is None:
                self._open_exertion = {"start_s": self.wall_seconds - dt_seconds,
                                       "intensity": float(current_exertion),
                                       "dose": 0.0}
            self._open_exertion["dose"] += float(current_exertion) * dt_seconds
            self._open_exertion["intensity"] = max(self._open_exertion["intensity"],
                                                   float(current_exertion))
        elif self._open_exertion is not None:
            self._open_exertion["end_s"] = self.wall_seconds
            self.exertion_history.append(self._open_exertion)
            self._open_exertion = None

        return self.hour_of_day

    def close_exertion(self):
        """Force-close any open exertion episode (call at end of a run)."""
        if self._open_exertion is not None:
            self._open_exertion["end_s"] = self.wall_seconds
            self.exertion_history.append(self._open_exertion)
            self._open_exertion = None

    def is_sleeping(self):
        return self.sleep.is_sleeping()

    @property
    def sleep_stage(self):
        return self.sleep.stage

    # ------------------------------------------------------------------
    # Circadian drivers
    # ------------------------------------------------------------------
    def _cosinor(self, acrophase_h):
        phase = 2.0 * np.pi * (self.hour_of_day - acrophase_h) / 24.0
        c = np.cos(phase)
        if self.second_harmonic:
            # 12-h harmonic at 25% relative amplitude, phase-locked (E5
            # structure; sharpens the night trough, TEMPORAL dossier §4)
            c = c + 0.25 * np.cos(2.0 * phase)
            c /= 1.25
        return float(c)

    def get_circadian_drive(self):
        """Sympathetic-dominance carrier: +1 at ~14:40, -1 at ~02:40."""
        if not self.circadian_enabled:
            return 0.0
        return self._cosinor(self.hr_acrophase_h)

    def circadian_hr_offset_bpm(self):
        """Circadian resting-HR offset (bpm): amplitude 13.5 bpm half-range,
        acrophase ~14:40 (EVD-HLTH-003, E2), plus OU day-to-day drift
        (EVD-POP-004) and the OPTIONAL menstrual luteal offset (OFF by
        default; +2-5 bpm luteal, EVD-TEMP-008, E2)."""
        if not self.circadian_enabled:
            return 0.0
        offset = self.hr_amplitude_bpm * self._cosinor(self.hr_acrophase_h)
        offset += self.ou_state_bpm
        if self.menstrual_enabled:
            offset += self._menstrual_rhr_offset_bpm()
        return float(offset)

    def circadian_bp_factor(self):
        """Multiplicative factor on the defended-pressure set point (p2Ru/
        p2Ra): symmetric cosinor with half-amplitude = dip/2 around the
        mesor, so the asleep trough sits ~14% below the awake peak
        (EVD-HLTH-003).  Magnitude E2; application channel (set-point vs
        resistance) is structure E5."""
        if not self.circadian_enabled:
            return 1.0
        # factor = 1 + (dip/2)*c: trough at night (c=-1 -> 1-dip/2), peak in
        # the early afternoon (c=+1 -> 1+dip/2); peak-to-trough = dip.
        return float(1.0 + 0.5 * self.bp_nocturnal_dip * self._cosinor(self.bp_acrophase_h))

    def _menstrual_rhr_offset_bpm(self):
        """Luteal RHR offset +2-5 bpm (use +3.5 mid-range; Alzueta 2022,
        PMID 35422659, E2).  Luteal window ~ cycle days 15-28 of 28."""
        day = self.menstrual_cycle_day % 28.0
        return 3.5 if 15.0 <= day < 28.0 else 0.0

    def menstrual_vagal_factor(self):
        """RMSSD multiplier ~0.9 luteal (EVD-TEMP-008); 1.0 otherwise/OFF."""
        if not self.menstrual_enabled:
            return 1.0
        day = self.menstrual_cycle_day % 28.0
        return 0.9 if 15.0 <= day < 28.0 else 1.0

    # ------------------------------------------------------------------
    # Stage-conditioned autonomic state (for coupling + HRV contract)
    # ------------------------------------------------------------------
    def autonomic_state(self):
        """Return (vagal_drive, sympathetic_drive, respiration_rate_brpm)
        combining circadian carrier + sleep-stage shifts.

        Scales: drives in [0, 1].  N3 = highest vagal gain; REM = sympathetic
        surges on a vagal background (EVD-HLTH-007, E4 structure/E2 anchors).
        """
        c = self.get_circadian_drive()
        vagal = 0.5 - 0.20 * c          # vagal peak ~02:40, trough ~14:40
        symp = 0.5 + 0.20 * c
        stage = self.sleep.stage
        if stage == "N1":
            vagal += 0.10
        elif stage == "N2":
            vagal += 0.15
        elif stage == "N3":
            vagal += 0.30; symp -= 0.20
        elif stage == "REM":
            vagal += 0.05; symp += 0.15  # surges on vagal background
        vagal *= self.menstrual_vagal_factor()
        vagal = float(min(1.0, max(0.0, vagal)))
        symp = float(min(1.0, max(0.0, symp)))

        # Respiration: awake N(15.5, 2.3); N3 ~13 low CV; REM ~16 high CV
        # (EVD-HLTH-010 / PARAMETER_SPEC respiration_rate, E2-E3)
        if stage in ("N2", "N3"):
            rr = self.rng.normal(13.0, 1.2) if stage == "N3" else self.rng.normal(14.0, 1.5)
        elif stage == "REM":
            rr = self.rng.normal(16.0, 3.0)
        elif stage == "N1":
            rr = self.rng.normal(14.5, 1.8)
        else:
            rr = self.rng.normal(15.5, 2.3)
        rr = float(min(24.0, max(8.0, rr)))
        return vagal, symp, rr

    def sleep_stage_hr_offset_bpm(self):
        """Stage-conditioned HR offset vs recumbent wake.  Magnitudes are
        SMALL (~2 bpm) per the n=1,047 cohort (EVD-HLTH-007): stage means
        wake 62.3 / N2 62.9 / N3 64.2 / REM 64.6 with only 13.5% of subjects
        dipping >=10%.  Offsets here are conservative (E4 structure)."""
        return {"awake": 0.0, "N1": 0.5, "N2": 0.0, "N3": -2.0,
                "REM": 1.0}[self.sleep.stage]

    # ------------------------------------------------------------------
    # Homeostatic sleep pressure (two-process S, simplified)
    # ------------------------------------------------------------------
    def update_sleep_pressure(self, sleep_pressure, is_sleeping=None, dt_seconds=1.0):
        """Accumulate sleep pressure while awake, dissipate during sleep.
        is_sleeping defaults to the real state-machine output."""
        if is_sleeping is None:
            is_sleeping = self.is_sleeping()
        dt_hours = dt_seconds / 3600.0
        if is_sleeping:
            decay_const = 0.3  # half-life ~2.3 h
            return float(sleep_pressure * np.exp(-decay_const * dt_hours))
        accum_rate = 0.05  # reaches 1.0 after 20 h awake
        return float(min(1.0, sleep_pressure + accum_rate * dt_hours))

    # ------------------------------------------------------------------
    # Recovery (sleep-dependent restoration; PEM moved to event kernels)
    # ------------------------------------------------------------------
    def update_recovery_and_pem(self, latent_state, dt_seconds, is_sleeping=None,
                                is_mecfs=False):
        """Sleep-dependent recovery of metabolic reserve / inflammatory
        burden.  The delayed PEM state transition itself now lives in
        evidence-anchored kernels (simulation/event_kernels.py,
        pem_symptom_kernel / slowed_recovery_kernel) driven by
        self.exertion_history; this method keeps only the continuous
        recovery dynamics.  is_mecfs is accepted for backward compatibility
        and no longer gates a 2-h pseudo-PEM."""
        if is_sleeping is None:
            is_sleeping = self.is_sleeping()
        dt_hours = dt_seconds / 3600.0

        rec_capacity = latent_state.get("autonomic_recovery_capacity")
        metab = latent_state.get("metabolic_reserve")
        infl = latent_state.get("inflammatory_burden")

        if is_sleeping:
            metab = min(1.0, metab + 0.08 * rec_capacity * dt_hours)
            infl = max(0.1, infl - 0.2 * rec_capacity * dt_hours)
        else:
            metab = max(0.0, metab - 0.01 * dt_hours)

        latent_state.set("metabolic_reserve", metab)
        latent_state.set("inflammatory_burden", infl)
