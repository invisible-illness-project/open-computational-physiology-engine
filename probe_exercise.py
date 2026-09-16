import sys, time, json
import numpy as np
REPO = '/home/kimi/work-fix-gate-remediation'
sys.path.insert(0, REPO); sys.path.insert(0, REPO + '/tools')
from models.baroreflex_model import BaroreflexPOTSModel
from simulation.event_kernels import make_exercise_kernel
from simulation.engine import SimulationEngine

GATE_SEED = 20260915


def variant_kernel(start, dur, dp2h=0.0, dhm=0.0, intensity=0.7):
    k = make_exercise_kernel(start, duration_s=dur, intensity=intensity)
    if dp2h:
        k.affected_parameters.append(
            {"symbol": "p2H", "mode": "additive", "magnitude": dp2h * intensity})
    if dhm:
        k.affected_parameters.append(
            {"symbol": "Hm", "mode": "additive", "magnitude": dhm * intensity})
    return k


def probe(dp2h, dhm, start=60.0, dur=120.0):
    eng = SimulationEngine(BaroreflexPOTSModel(), seed=GATE_SEED + 3)
    eng.behavior.kernels.add_kernel(variant_kernel(start, dur, dp2h, dhm),
                                    np.random.default_rng(GATE_SEED))
    res = eng.run({"tup": 9e9, "tend": 9e9, "height": 25.0, "angle": 60.0,
                   "tsim_end": 320.0})
    t = np.asarray(res["time"]); hr = np.asarray(res["Hc"]) * 60.0

    def wm(lo, hi):
        m = (t >= lo) & (t < hi)
        return float(np.mean(hr[m]))
    base = wm(start - 60, start)
    plateau = wm(start + 40.0, start + 30.0 + dur - 10.0)
    rec = wm(start + 30.0 + dur + 80.0, start + 30.0 + dur + 110.0)
    return {"dp2h": dp2h, "dhm": dhm, "baseline": base,
            "bout_dhr": plateau - base, "rec_dhr": rec - base}


out = []
for dp2h, dhm in [(5, 0), (10, 0), (15, 0), (0, 0.3), (10, 0.2)]:
    t0 = time.time()
    r = probe(dp2h, dhm)
    r["sec"] = round(time.time() - t0, 1)
    out.append(r)
    print(json.dumps(r), flush=True)
with open('/tmp/probe_exercise.json', 'w') as f:
    json.dump(out, f, indent=1)
