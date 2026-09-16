import sys, time, json
import numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, 'tools')
from models.baroreflex_model import BaroreflexPOTSModel
from simulation.event_kernels import make_exercise_kernel
from simulation.engine import SimulationEngine
GATE_SEED = 20260915
start, dur = 60.0, 120.0
eng = SimulationEngine(BaroreflexPOTSModel(), seed=GATE_SEED + 3)
eng.behavior.kernels.add_kernel(make_exercise_kernel(start, duration_s=dur),
                                np.random.default_rng(GATE_SEED))
res = eng.run({"tup": 9e9, "tend": 9e9, "height": 25.0, "angle": 60.0, "tsim_end": 320.0})
t = np.asarray(res["time"]); hr = np.asarray(res["Hc"]) * 60.0
def wm(lo, hi):
    m = (t >= lo) & (t < hi); return float(np.mean(hr[m]))
base = wm(start-60, start)
plateau = wm(start+40.0, start+30.0+dur-10.0)
rec = wm(start+30.0+dur+80.0, start+30.0+dur+110.0)
out = {"baseline": base, "bout_dhr": plateau-base, "rec_dhr": rec-base,
       "rec_below_plateau": (rec-base) < (plateau-base)}
print(json.dumps(out), flush=True)
# also via behavior trigger path (active_behavior=exercise) to test engine wiring
eng2 = SimulationEngine(BaroreflexPOTSModel(), seed=42)
res2 = eng2.run({"tup": 1.0e30, "tend": 200.0, "height": 25.0, "angle": 60.0,
                 "active_behavior": "exercise", "exercise_duration_s": 60.0})
t2 = np.asarray(res2["time"]); hr2 = np.asarray(res2["Hc"])*60.0
m_b = t2 < 30.0
m_p = (t2 >= 70.0) & (t2 < 85.0)
print(json.dumps({"behavior_path_pre": float(np.mean(hr2[m_b])),
                  "behavior_path_bout": float(np.mean(hr2[m_p]))}), flush=True)
