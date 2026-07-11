import os
import sys
import numpy as np

# Ensure project directories are in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.baroreflex_model import BaroreflexPOTSModel
from simulation.engine import SimulationEngine
from sensor_models.wearable_sensors import PolarH10SensorModel, PPGWearableSensorModel
from validation.evaluator import PhysiologicalEvaluator

def run_single_cohort(phenotype=None):
    print(f"Running simulation for: {phenotype or 'Healthy Control'}")
    
    # 1. Initialize model loading equations & parameters from Knowledge Base
    model = BaroreflexPOTSModel(phenotype=phenotype)
    
    # 2. Run simulation engine
    engine = SimulationEngine(model, dt=0.01, hrv_noise=0.02)
    tilt_params = {
        "tup": 200.0,       # Start tilt at 200s
        "tend": 300.0,      # End tilt/simulation at 300s
        "height": 25.0,     # Hydrostatic height between compartments (cm)
        "angle": 60.0       # Max tilt angle (degrees)
    }
    sim_results = engine.run(tilt_params)
    
    # 3. Feed physical signals into wearable sensor models
    print("Generating synthetic wearable data streams...")
    polar_h10 = PolarH10SensorModel()
    ppg_sensor = PPGWearableSensorModel()
    
    # Polar H10 ECG strap RR telemetry
    h10_data = polar_h10.generate_telemetry(sim_results["time"], sim_results["Hc"])
    
    # PPG sensor optical green-light signal
    ppg_time, ppg_signal = ppg_sensor.generate_ppg_signal(
        sim_results["time"], 
        sim_results["pau"], 
        sim_results["sympathetic_tone"]
    )
    
    # 4. Evaluate physiological outcomes against clinical gold standards
    evaluator = PhysiologicalEvaluator()
    report = evaluator.evaluate(sim_results, phenotype=phenotype)
    evaluator.print_report(report)
    
    # Save simulated telemetry to a results folder for open science reproducibility
    os.makedirs("results", exist_ok=True)
    filename_prefix = phenotype if phenotype else "healthy_control"
    np.savez(
        f"results/{filename_prefix}_telemetry.npz",
        time=sim_results["time"],
        pau=sim_results["pau"],
        pal=sim_results["pal"],
        pvu=sim_results["pvu"],
        Vau=sim_results["Vau"],
        Vvu=sim_results["Vvu"],
        Val=sim_results["Val"],
        Vvl=sim_results["Vvl"],
        Vlv=sim_results["Vlv"],
        pcm=sim_results["pcm"],
        Raup=sim_results["Raup"],
        Ralp=sim_results["Ralp"],
        Ed=sim_results["Ed"],
        Hc=sim_results["Hc"],
        sympathetic_tone=sim_results["sympathetic_tone"],
        parasympathetic_tone=sim_results["parasympathetic_tone"],
        h10_times=h10_data["times"],
        h10_rr=h10_data["rr_intervals"],
        h10_hr=h10_data["heart_rate"],
        ppg_time=ppg_time,
        ppg_signal=ppg_signal
    )
    print(f"[OK] Telemetry saved to results/{filename_prefix}_telemetry.npz\n")
    return report

def main():
    print("======================================================================")
    print("  OPEN COMPUTATIONAL PHYSIOLOGY SIMULATION PIPELINE")
    print("======================================================================")
    
    cohorts = [
        None,                   # Healthy Control
        "neuropathic_pots",     # Neuropathic POTS Phenotype
        "hyperadrenergic_pots", # Hyperadrenergic POTS Phenotype
        "hypovolemic_pots"      # Hypovolemic POTS Phenotype
    ]
    
    reports = []
    for cohort in cohorts:
        rep = run_single_cohort(phenotype=cohort)
        reports.append(rep)
        
    print("======================================================================")
    print("  SIMULATION COHORT SUMMARY TABLE")
    print("======================================================================")
    print(f"{'Cohort':<22} | {'Base HR':<8} | {'Peak HR':<8} | {'HR Rise':<8} | {'Base MAP':<8} | {'Tilt MAP':<8} | {'Status':<6}")
    print("-" * 80)
    for r in reports:
        p_name = r["phenotype"]
        base_hr = r["hr_baseline_mean_bpm"]
        peak_hr = r["hr_tilt_peak_bpm"]
        hr_rise = r["hr_increase_bpm"]
        base_map = r["map_baseline_mmHg"]
        tilt_map = r["map_tilt_mmHg"]
        status = "PASSED" if r["validation_passed"] else "FAILED"
        print(f"{p_name:<22} | {base_hr:<8.1f} | {peak_hr:<8.1f} | {hr_rise:<8.1f} | {base_map:<8.1f} | {tilt_map:<8.1f} | {status:<6}")
    print("======================================================================\n")

if __name__ == "__main__":
    main()
