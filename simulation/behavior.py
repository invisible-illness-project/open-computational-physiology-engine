"""
Behavioral model (G-P0-01 refactor).

Patient behaviors (rest / exercise / meal / sleep / stress) are expressed as
explicit :class:`~simulation.event_kernels.EventKernel` objects applied
against the engine's IMMUTABLE baseline parameter snapshot -- never against
already-modified parameters.  This removes the multiplicative per-heartbeat
compounding bug (5 beats of ``meal`` drove RalpM 17.88 -> 4.24 instead of the
one-shot 13.41; exercise ``Es x1.30``/beat was unbounded).

Latent-state nudges are additive offsets with explicit exponential decay
toward zero (they no longer accumulate to a clamp), per the G-P0-01
implementation note.
"""

from simulation.event_kernels import (
    EventKernelManager, make_meal_kernel, make_exercise_kernel,
    make_stress_kernel,
)


class BehaviorModel:
    """
    Simulates patient behaviors and lifestyle factors.
    Updates latent states (via decaying additive offsets) and applies
    kernel-based transient parameter overlays against baseline,
    capturing bidirectional feedback between behavioral choice and
    physical capacity.
    """

    # Decay time constant for latent nudges (s): behavioral autonomic nudges
    # relax back over ~1 min once the behavior stops (structure E5).
    LATENT_OFFSET_TAU_S = 60.0

    def __init__(self):
        self.current_activity = "rest"  # "rest", "exercise", "meal", "sleep", "stress"
        self.kernels = EventKernelManager()
        self._latent_offsets = {}
        self._activity_start_s = 0.0
        self.exertion_intensity = 0.7

    def trigger_behavior(self, activity, start_s=0.0, rng=None,
                         exercise_duration_s=300.0, exertion_intensity=0.7,
                         kernel_time_scale=1.0):
        """Switch behavior.  Non-rest behaviors register an event kernel at
        ``start_s`` (absolute simulation seconds).  ``kernel_time_scale``
        compresses kernel timing for short protocol runs (timing only,
        never magnitudes)."""
        if activity not in ["rest", "exercise", "meal", "sleep", "stress"]:
            return
        if activity == self.current_activity and activity != "rest":
            return
        self.current_activity = activity
        self._activity_start_s = float(start_s)
        self.exertion_intensity = float(exertion_intensity)
        if activity == "meal":
            self.kernels.add_kernel(make_meal_kernel(start_s, time_scale=kernel_time_scale), rng)
        elif activity == "exercise":
            self.kernels.add_kernel(
                make_exercise_kernel(start_s, duration_s=exercise_duration_s,
                                     intensity=exertion_intensity), rng)
        elif activity == "stress":
            self.kernels.add_kernel(make_stress_kernel(start_s), rng)

    # ------------------------------------------------------------------
    # Latent-state channel (additive offsets with explicit decay)
    # ------------------------------------------------------------------
    def modulate_latent_states(self, latent_state, time_sec, dt_seconds=1.0):
        """Apply behavioral nudges to latent state variables as decaying
        additive offsets (no accumulation-to-clamp, no compounding)."""
        decay = pow(2.718281828459045, -dt_seconds / self.LATENT_OFFSET_TAU_S)
        for k in list(self._latent_offsets):
            self._latent_offsets[k] *= decay

        def nudge(name, delta):
            self._latent_offsets[name] = self._latent_offsets.get(name, 0.0) + delta

        if self.current_activity == "exercise":
            # Exertion depletes metabolic reserve and raises stress load
            nudge("stress_load", +0.002)
            nudge("metabolic_reserve", -0.005 * dt_seconds)
            latent_state.set(
                "hydration",
                max(0.0, latent_state.get("hydration") - 0.002 * dt_seconds))
        elif self.current_activity == "sleep":
            nudge("stress_load", -0.005)
            nudge("metabolic_reserve", +0.005 * dt_seconds)
        elif self.current_activity == "stress":
            nudge("stress_load", +0.01)
        elif self.current_activity == "meal":
            nudge("parasympathetic_tone", +0.01)

        # Apply (decayed) offsets additively, clamped to each state's range
        bounds = {"sympathetic_tone": (0.0, 1.0), "parasympathetic_tone": (0.0, 1.0),
                  "stress_load": (0.0, 1.0), "metabolic_reserve": (0.0, 1.0),
                  "sleep_pressure": (0.0, 1.0)}
        for name, off in self._latent_offsets.items():
            lo, hi = bounds.get(name, (-10.0, 10.0))
            latent_state.set(name, min(hi, max(lo, latent_state.get(name) + off)))

    # ------------------------------------------------------------------
    # Parameter channel (kernel overlay against BASELINE)
    # ------------------------------------------------------------------
    def modulate_parameters(self, base_params, latent_state, time_s=None):
        """Effective parameters = kernel overlays applied to ``base_params``.

        ``base_params`` MUST be the engine's immutable baseline snapshot.
        The hydration->TotalVol additive shift is also computed against
        baseline, so repeated calls are idempotent (G-P0-01).
        """
        t = self._activity_start_s if time_s is None else float(time_s)
        params = self.kernels.compute_parameter_overlay(base_params, t)

        # Hydration state affects blood volume (additive vs baseline):
        # 0.0 dehydrated (-500 ml) .. 1.0 hydrated (+200 ml).  Provisional
        # (tier C, repo-legacy magnitudes; direction standard physiology).
        hydr = latent_state.get("hydration")
        volume_delta = -500.0 + 700.0 * hydr
        if "TotalVol" in params:
            params["TotalVol"] = base_params.get("TotalVol", params["TotalVol"]) + volume_delta

        return params

    # ------------------------------------------------------------------
    def check_behavioral_feedback(self, symptoms):
        """Bidirectional feedback: high symptoms can force behavior changes
        (e.g., extreme fatigue or dizziness aborts exercise)."""
        fatigue = symptoms.get("fatigue", 0.0)
        dizziness = symptoms.get("dizziness", 0.0)

        if fatigue > 0.8 and self.current_activity == "exercise":
            print("[INFO] Physiological feedback loop: Exercise aborted due to severe fatigue.")
            self.current_activity = "rest"

        if dizziness > 0.7 and self.current_activity == "exercise":
            print("[INFO] Physiological feedback loop: Exercise stopped due to orthostatic dizziness.")
            self.current_activity = "rest"
