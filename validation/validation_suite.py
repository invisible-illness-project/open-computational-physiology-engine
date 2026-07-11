import numpy as np

class AdvancedValidationSuite:
    """
    Advanced validation framework for evaluating the physiological plausibility,
    symptom emergence, circadian rhythms, and intervention efficacy in virtual patient cohorts.
    """
    def __init__(self):
        pass

    def run_suite(self, sim_results, subject_info, phenotype_name):
        """
        Executes a comprehensive validation suite.
        Returns a dictionary of results.
        """
        time = sim_results["time"]
        hr = sim_results["Hc"] * 60.0  # bpm
        pau = sim_results["pau"]       # mmHg
        
        checks = {}
        
        # 1. Hemodynamic Bounds Check
        checks["hemodynamics_valid"] = {
            "pass": bool(np.all(hr >= 30.0) and np.all(hr <= 220.0) and np.all(pau >= 30.0) and np.all(pau <= 240.0)),
            "details": f"HR: [{np.min(hr):.1f}, {np.max(hr):.1f}] bpm, BP: [{np.min(pau):.1f}, {np.max(pau):.1f}] mmHg"
        }
        
        # 2. Circadian Amplitude Check (if simulation is long enough or demonstrates time variation)
        circadian = sim_results.get("circadian_drive", None)
        if circadian is not None and len(circadian) > 1:
            circ_range = np.max(circadian) - np.min(circadian)
            checks["circadian_variation"] = {
                "pass": bool(circ_range > 0.1),
                "details": f"Circadian drive variation range: {circ_range:.2f}"
            }
            
        # 3. Symptom-Hemodynamics Association Check
        # Dizziness should align with drops in carotid pressure
        diz = sim_results.get("dizziness", None)
        pc = sim_results.get("carotid_pressure", None)
        if diz is not None and pc is not None:
            max_diz = np.max(diz)
            min_pc = np.min(pc)
            # If carotid pressure drops below 75, dizziness should be elevated (>0.2)
            if min_pc < 75.0:
                oi_ok = max_diz > 0.2
            else:
                oi_ok = max_diz < 0.3
            checks["symptom_coupling"] = {
                "pass": bool(oi_ok),
                "details": f"Max dizziness: {max_diz:.2f} at Min Carotid Pressure: {min_pc:.1f} mmHg"
            }
            
        # 4. Medication Efficacy Check (if beta_blocker was used, peak HR should be blunted)
        if phenotype_name and "beta_blocker" in phenotype_name:
            peak_hr = np.max(hr)
            # Beta blockers should cap HR at 145 bpm in this model
            checks["beta_blocker_efficacy"] = {
                "pass": bool(peak_hr < 145.0),
                "details": f"Medicated peak HR is blunted: {peak_hr:.1f} bpm (< 145 bpm)"
            }
            
        # 5. Hydration Influence Check
        hydr = sim_results.get("hydration", None)
        vol = sim_results.get("blood_volume", None)
        if hydr is not None and vol is not None:
            vol_range = np.max(vol) - np.min(vol)
            # Blood volume should fluctuate based on hydration state
            checks["volume_hydration_regulation"] = {
                "pass": bool(vol_range > 50.0 or np.std(hydr) < 1e-4),
                "details": f"Blood volume variation: {vol_range:.1f} ml based on hydration state."
            }
            
        all_passed = all(chk["pass"] for chk in checks.values())
        
        return {
            "phenotype": phenotype_name,
            "subject": subject_info,
            "checks": checks,
            "passed": all_passed
        }

    def print_validation_report(self, report):
        print(f"\n==========================================")
        print(f"  ADVANCED COHORT VALIDATION REPORT")
        print(f"  Subject: Age {report['subject']['age']}, Sex {report['subject']['sex']}, Fitness {report['subject']['fitness']}")
        print(f"  Perturbations: {report['phenotype'].upper()}")
        print(f"==========================================")
        for name, chk in report["checks"].items():
            status = "\033[92m[PASS]\033[0m" if chk["pass"] else "\033[91m[FAIL]\033[0m"
            print(f"  {status} {name}: {chk['details']}")
        print(f"------------------------------------------")
        overall = "\033[92mPASSED\033[0m" if report["passed"] else "\033[91mFAILED\033[0m"
        print(f"OVERALL VALIDATION STATUS: {overall}")
        print(f"==========================================\n")
