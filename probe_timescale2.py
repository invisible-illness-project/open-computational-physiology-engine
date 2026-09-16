import sys, json
import numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, 'tools')
from models.baroreflex_model import BaroreflexPOTSModel
from simulation.engine import SimulationEngine
GATE_SEED = 20260915
eng = SimulationEngine(BaroreflexPOTSModel(), dt=0.02, seed=GATE_SEED)
res = eng.run({"tup": 9e9, "tend": 9e9, "height": 25.0, "angle": 60.0, "tsim_end": 600.0})
hrv_in = eng.get_hrv_inputs()
np.savez('/tmp/ts_inputs.npz',
         time_s=hrv_in["time_s"], mean_hr_bpm=hrv_in["mean_hr_bpm"],
         vagal=hrv_in["vagal_drive"], symp=hrv_in["sympathetic_drive"],
         resp=hrv_in["respiration_rate_brpm"],
         stage=hrv_in["sleep_stage_code"],
         rr=res["rr_intervals_ms"], bt=res["beat_times_s"])
print("dumped", flush=True)
