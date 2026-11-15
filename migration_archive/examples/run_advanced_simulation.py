import os
import sys
import numpy as np

# Ensure project directories are in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.baroreflex_model import BaroreflexPOTSModel
from simulation.engine import SimulationEngine
from simulation.population import VirtualSubject
from simulation.perturbations import enable_experimental_mode
from validation.validation_suite import AdvancedValidationSuite

def run_advanced_scenario(subject, phenotype, behavior_trigger, label, include_experimental=False):
    print("======================================================================")
    print(f"  SCENARIO: {label}")
    print(f"  Subject: Age={subject.age}, Sex={subject.sex}, Fitness={subject.fitness}")
    print(f"  Composed Phenotype: {phenotype or 'Healthy Baseline'}")
    print(f"  Active Behavior: {behavior_trigger}")
    if include_experimental:
        print("  Mode: EXPERIMENTAL (includes tier-D unverified parameters; "
              "hypothesis-illustrative, not canonical)")
    else:
        print("  Mode: canonical (reviewed parameters only)")
    print("======================================================================")

    # 1. Initialize the Mechanistic Model with Demographic Priors and Composed Phenotypes
    model = BaroreflexPOTSModel(phenotype=phenotype, subject=subject)

    # 1b. Optionally enable experimental perturbations (tier-D unverified parameters)
    if include_experimental:
        enable_experimental_mode(model)

    # 2. Configure Simulation Engine (fixed seed for reproducible HRV noise)
    engine = SimulationEngine(model, dt=0.01, hrv_noise=0.02, seed=42)
    
    # Define tilt protocol and behavioral parameters
    tilt_params = {
        "tup": 100.0,            # Standing transition start at 100s
        "tend": 200.0,           # End simulation at 200s
        "height": 25.0,          # cm
        "angle": 60.0,           # degrees
        "active_behavior": behavior_trigger
    }
    
    # 3. Execute Continuous Simulation
    sim_results = engine.run(tilt_params)
    
    # 4. Perform Advanced Multi-Cohort Physiological Validation
    subject_info = {"age": subject.age, "sex": subject.sex, "fitness": subject.fitness}
    validator = AdvancedValidationSuite()
    report = validator.run_suite(sim_results, subject_info, phenotype or "Healthy Baseline")
    validator.print_validation_report(report)
    
    # Save results to disk
    os.makedirs("results", exist_ok=True)
    filename = label.lower().replace(" ", "_").replace("+", "plus").replace("/", "_")
    np.savez(
        f"results/{filename}_advanced.npz",
        time=sim_results["time"],
        pau=sim_results["pau"],
        Hc=sim_results["Hc"],
        sympathetic_tone=sim_results.get("sympathetic_tone", []),
        parasympathetic_tone=sim_results.get("parasympathetic_tone", []),
        fatigue=sim_results.get("fatigue", []),
        brain_fog=sim_results.get("brain_fog", []),
        dizziness=sim_results.get("dizziness", []),
        palpitations=sim_results.get("palpitations", []),
        metabolic_reserve=sim_results.get("metabolic_reserve", []),
        blood_volume=sim_results.get("blood_volume", [])
    )
    print(f"[OK] Telemetry saved to results/{filename}_advanced.npz\n")
    return report

def main():
    print("======================================================================")
    print("  OPEN COMPUTATIONAL PHYSIOLOGY ENGINE: ADVANCED SIMULATION PIPELINE")
    print("======================================================================")
    
    # Define virtual patient cases
    scenarios = [
        {
            "subject": VirtualSubject(age=24, sex="female", bmi=21.5, fitness="average"),
            "phenotype": "neuropathic_pots * environmental_heat",
            "behavior": "rest",
            "label": "Neuropathic POTS + Heat Stress"
        },
        {
            "subject": VirtualSubject(age=35, sex="male", bmi=24.0, fitness="athletic"),
            "phenotype": "hyperadrenergic_pots * beta_blocker",
            "behavior": "exercise",
            "label": "Hyperadrenergic POTS + Beta-Blocker under Exercise"
        },
        {
            "subject": VirtualSubject(age=28, sex="female", bmi=20.0, fitness="sedentary"),
            "phenotype": "mecfs_metabolic_dysfunction * sleep_deprivation",
            "behavior": "rest",
            "label": "ME_CFS + Sleep Deprivation",
            # sleep_deprivation is tier-D/unverified: requires experimental mode
            "include_experimental": True
        },
        {
            "subject": VirtualSubject(age=45, sex="female", bmi=25.5, fitness="average"),
            "phenotype": "heds_venous_pooling * fludrocortisone",
            "behavior": "meal",
            "label": "hEDS + Splanchnic Postprandial Pooling + Fludrocortisone",
            # heds_venous_pooling is tier-D/unverified: requires experimental mode
            "include_experimental": True
        }
    ]

    np.random.seed(42)  # reproducibility for any downstream stochastic layers
    reports = []
    for sc in scenarios:
        rep = run_advanced_scenario(
            sc["subject"], sc["phenotype"], sc["behavior"], sc["label"],
            include_experimental=sc.get("include_experimental", False)
        )
        reports.append(rep)
        
    print("======================================================================")
    print("  ADVANCED COHORT VALIDATION SUMMARY")
    print("======================================================================")
    print(f"{'Scenario Name':<42} | {'Checks Passed':<15} | {'Overall'}")
    print("-" * 70)
    for r in reports:
        passed_count = sum(1 for chk in r["checks"].values() if chk["pass"])
        total_count = len(r["checks"])
        status = "PASSED" if r["passed"] else "FAILED"
        print(f"{r['phenotype']:<42} | {passed_count}/{total_count} passed     | {status}")
    print("======================================================================\n")

if __name__ == "__main__":
    main()
