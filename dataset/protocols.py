"""Protocol scheduler (G-P0-07 build item 2).

Declarative protocol definitions (YAML; researcher-facing) compiled to
engine inputs.  Two families:

  * ``tilt_first`` -- supine baseline -> 60-70 deg head-up tilt (~10 min
    canonical; shorter bench variants are flagged by the evaluator's
    ``sustained_window_kind``) -> optional prolonged standing (honest
    approximation, see below) -> supine recovery.  Compiles to
    ``SimulationEngine.run`` tilt_params: ``tup`` (tilt onset), ``tend``
    (tilt offset), ``angle``, ``height`` and ``tsim_end`` (total
    simulation horizon including recovery; additive engine API, see
    simulation/engine.py changelog note for W2-F).
  * ``multiday`` -- slow-layer day-scale horizons via
    ``SimulationEngine.run_multiday`` (circadian/sleep/OU/PEM layers;
    exertion schedule -> PEM kernels).

Event scheduling (meals / exercise / stress) uses the engine's public
EventKernel factories (simulation.event_kernels.make_*_kernel) injected
into ``engine.behavior.kernels`` before ``run()``; the engine composes
them against its immutable baseline (G-P0-01 semantics).  NOTE: latent
nudge channels (BehaviorModel.modulate_latent_states) and the PEM
exertion channel are driven by ``current_activity``; kernel-scheduled
events therefore act through their documented PARAMETER overlays only.
Exercise events in short ODE runs carry the honesty flag
``exercise_pem_channel_inactive_in_ode_runs`` (PEM lives in the multiday
family, where the exertion schedule is first-class).

Metric semantics are the FROZEN evaluator semantics (G-P0-09):
``validation/evaluator.py::compute_orthostatic_metrics`` is the single
implementation; this module only supplies onset/duration/covariates.
Mandatory protocol covariates per validation/healthy_reference.yaml.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import yaml

#: Canonical HUT angle band (validation/healthy_reference.yaml hut_60_70_10min).
CANONICAL_HUT_ANGLE_RANGE = (60.0, 70.0)
#: The model's tilt ramp is hard-coded at 14 s (models/baroreflex_model.py).
MODEL_TILT_RAMP_S = 14.0


@dataclass
class ProtocolEvent:
    type: str                       # meal | exercise | stress
    at_s: float
    params: Dict[str, Any] = field(default_factory=dict)

    def to_record(self) -> Dict[str, Any]:
        return {"type": self.type, "t_start_s": float(self.at_s),
                "params": {k: v for k, v in self.params.items()}}


@dataclass
class ProtocolSpec:
    protocol_id: str
    family: str                     # tilt_first | multiday
    phases: List[Dict[str, Any]] = field(default_factory=list)
    events: List[ProtocolEvent] = field(default_factory=list)
    covariates: Dict[str, Any] = field(default_factory=dict)
    days: int = 1
    step_s: float = 60.0
    exertion_schedule: List[Dict[str, Any]] = field(default_factory=list)

    # ------------------------------------------------------------------
    def _phase(self, name_part: str) -> Optional[Dict[str, Any]]:
        for ph in self.phases:
            if name_part in str(ph.get("name", "")):
                return ph
        return None

    @property
    def onset_s(self) -> float:
        """Tilt/stand onset = end of the supine baseline phase."""
        base = self._phase("baseline") or {}
        return float(base.get("duration_s", 0.0))

    @property
    def tilt_duration_s(self) -> float:
        tilt = self._phase("tilt") or self._phase("stand") or {}
        d = float(tilt.get("duration_s", 0.0))
        # Optional prolonged-standing phase extends the upright stress
        # (approximation: same hydrostatic load as tilt; flagged).
        stand = self._phase("standing")
        if stand is not None and "tilt" not in str(stand.get("name", "")):
            d += float(stand.get("duration_s", 0.0))
        return d

    @property
    def recovery_duration_s(self) -> float:
        rec = self._phase("recovery") or {}
        return float(rec.get("duration_s", 0.0))

    @property
    def total_duration_s(self) -> float:
        if self.family == "multiday":
            return self.days * 86400.0
        return self.onset_s + self.tilt_duration_s + self.recovery_duration_s

    @property
    def angle_degrees(self) -> float:
        tilt = self._phase("tilt") or {}
        return float(tilt.get("angle_degrees", 60.0))

    @property
    def method(self) -> str:
        tilt = self._phase("tilt")
        if tilt is not None:
            return "head_up_tilt"
        if self._phase("stand") is not None:
            return "active_stand"
        return "supine_rest"

    # ------------------------------------------------------------------
    def to_engine_tilt_params(self) -> Dict[str, Any]:
        """Compile to SimulationEngine.run() tilt_params."""
        if self.family != "tilt_first":
            raise ValueError(f"protocol {self.protocol_id} is not tilt_first")
        params = {
            "tup": self.onset_s,
            "tend": self.onset_s + self.tilt_duration_s,
            "angle": self.angle_degrees,
            "height": float(self.covariates.get("height_cm", 25.0)),
            # total horizon incl. supine recovery (additive engine key
            # ``tsim_end``; defaults to ``tend`` when absent -> legacy
            # behavior preserved for all existing call sites).
            "tsim_end": self.total_duration_s,
        }
        return params

    def metric_semantics(self) -> Dict[str, Any]:
        """Inputs for validation/evaluator.compute_orthostatic_metrics."""
        return {
            "onset_s": self.onset_s,
            "tilt_duration_s": self.tilt_duration_s,
            "baseline_window_s": min(300.0, max(10.0, self.onset_s - 10.0)),
        }

    def mandatory_covariates(self) -> Dict[str, Any]:
        """Covariates required by validation/healthy_reference.yaml."""
        return {
            "method": self.method,
            "tilt_angle_degrees": self.angle_degrees if self.method != "supine_rest" else 0.0,
            "upright_duration_s": self.tilt_duration_s,
            "supine_rest_duration_s": self.onset_s,
            "fasting_state": self.covariates.get("fasting", "unresolved"),
            "time_of_day": self.covariates.get("time_of_day", "unresolved"),
            "ramp_s": MODEL_TILT_RAMP_S,
        }

    def honesty_flags(self) -> List[str]:
        flags: List[str] = []
        if self._phase("standing") is not None:
            flags.append("prolonged_standing_approximated_as_extended_tilt")
        if any(ev.type == "exercise" for ev in self.events) and self.family != "multiday":
            flags.append("exercise_pem_channel_inactive_in_ode_runs")
        if 0.0 < self.tilt_duration_s < 600.0:
            flags.append("short_protocol_sustained_window_proxy")
        return flags

    def validate(self) -> List[str]:
        """Structural + scientific-contract problems (empty list = ok)."""
        errors: List[str] = []
        if self.family not in ("tilt_first", "multiday"):
            errors.append(f"unknown protocol family {self.family!r}")
        if self.family == "tilt_first":
            if self._phase("baseline") is None:
                errors.append("tilt_first family requires a supine baseline phase")
            if self.method != "supine_rest" and self.tilt_duration_s <= 0.0:
                errors.append("upright phase duration must be > 0")
            if (self.method == "head_up_tilt"
                    and not (CANONICAL_HUT_ANGLE_RANGE[0] <= self.angle_degrees
                             <= CANONICAL_HUT_ANGLE_RANGE[1])):
                errors.append(
                    f"HUT angle {self.angle_degrees} outside the canonical "
                    f"{CANONICAL_HUT_ANGLE_RANGE} deg band")
        if self.family == "multiday" and self.days < 1:
            errors.append("multiday protocol requires days >= 1")
        for ev in self.events:
            if ev.type not in ("meal", "exercise", "stress"):
                errors.append(f"unknown event type {ev.type!r}")
            if ev.at_s < 0 or ev.at_s >= max(1.0, self.total_duration_s):
                errors.append(f"event {ev.type}@{ev.at_s}s outside protocol horizon")
        return errors

    def to_record(self) -> Dict[str, Any]:
        return {
            "protocol_id": self.protocol_id,
            "family": self.family,
            "phases": self.phases,
            "events": [ev.to_record() for ev in self.events],
            "covariates": self.mandatory_covariates(),
            "total_duration_s": self.total_duration_s,
        }


def _parse_event(raw: Dict[str, Any]) -> ProtocolEvent:
    return ProtocolEvent(type=raw["type"], at_s=float(raw.get("at_s", 0.0)),
                         params={k: v for k, v in raw.items()
                                 if k not in ("type", "at_s")})


def parse_protocol(raw: Dict[str, Any]) -> ProtocolSpec:
    """Parse one protocol block of a dataset config."""
    spec = ProtocolSpec(
        protocol_id=raw["protocol_id"],
        family=raw.get("family", "tilt_first"),
        phases=list(raw.get("phases", []) or []),
        events=[_parse_event(e) for e in (raw.get("events") or [])],
        covariates=dict(raw.get("covariates", {}) or {}),
        days=int(raw.get("days", 1)),
        step_s=float(raw.get("step_s", 60.0)),
        exertion_schedule=list(raw.get("exertion_schedule", []) or []),
    )
    errors = spec.validate()
    if errors:
        raise ValueError(f"protocol {spec.protocol_id}: " + "; ".join(errors))
    return spec


def load_protocol_config(path: str) -> List[ProtocolSpec]:
    """Load protocol definitions from a YAML config."""
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    protos = cfg.get("protocols") if isinstance(cfg, dict) else None
    if not protos:
        raise ValueError(f"protocol config {path} must define a 'protocols' list")
    return [parse_protocol(p) for p in protos]
