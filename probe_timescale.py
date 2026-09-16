import sys, json
import numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, 'tools')
from models.baroreflex_model import BaroreflexPOTSModel
from simulation.engine import SimulationEngine
from validation.levels import band_powers, peak_freq, dfa_alpha1
GATE_SEED = 20260915
eng = SimulationEngine(BaroreflexPOTSModel(), dt=0.02, seed=GATE_SEED)
res = eng.run({"tup": 9e9, "tend": 9e9, "height": 25.0, "angle": 60.0, "tsim_end": 600.0})
hrv_in = eng.get_hrv_inputs()
rr = np.asarray(res["rr_intervals_ms"], dtype=float)
resp_scalar = float(np.mean(hrv_in["respiration_rate_brpm"]))
freqs, P, lf, hf = band_powers(rr)
pk = peak_freq(freqs, P, 0.15, 0.40) if freqs.size else float("nan")
a1 = dfa_alpha1(rr)
hr = np.asarray(res["Hc"])*60.0
out = {"n_beats": int(rr.size), "hf_peak_hz": pk, "resp_hz": resp_scalar/60.0,
       "abs_dev": abs(pk - resp_scalar/60.0), "dfa_alpha1": a1,
       "lf_hf": float(lf/hf), "supine_hr_std": float(np.std(hr)),
       "supine_hr_mean": float(np.mean(hr)),
       "resp_sd_brpm": float(np.std(hrv_in["respiration_rate_brpm"]))}
print(json.dumps(out), flush=True)
