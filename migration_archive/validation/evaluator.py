import numpy as np

class PhysiologicalEvaluator:
    """
    Evaluates simulation results for physiological plausibility,
    clinical diagnostic criteria compliance, and autonomic response dynamics.
    """
    def __init__(self, baseline_t_max=190.0, tilt_stabilized_t_min=240.0):
        self.baseline_t_max = baseline_t_max
        self.tilt_stabilized_t_min = tilt_stabilized_t_min

    def evaluate(self, sim_results, phenotype=None):
        """
        Runs validation checks on the simulation results.
        Returns a validation report with pass/fail outcomes.
        """
        time = sim_results["time"]
        pau = sim_results["pau"]
        Hc = sim_results["Hc"] # in bps
        
        hr_bpm = Hc * 60.0
        
        # 1. Identify baseline (supine) and tilt phases
        baseline_mask = time <= self.baseline_t_max
        tilt_stabilized_mask = time >= self.tilt_stabilized_t_min
        
        # Baseline metrics
        hr_baseline_mean = np.mean(hr_bpm[baseline_mask])
        pau_baseline = pau[baseline_mask]
        
        # Calculate Systolic and Diastolic pressure waves at baseline
        # (local peaks and troughs of the pulsatile pau waveform)
        sbp_baseline = np.max(pau_baseline)
        dbp_baseline = np.min(pau_baseline)
        map_baseline = np.mean(pau_baseline)
        
        # Tilt stabilized metrics
        hr_tilt_mean = np.mean(hr_bpm[tilt_stabilized_mask])
        pau_tilt = pau[tilt_stabilized_mask]
        sbp_tilt = np.max(pau_tilt)
        dbp_tilt = np.min(pau_tilt)
        map_tilt = np.mean(pau_tilt)
        
        # Peak heart rate in the first 60 seconds after tilt (tup=200s to 260s)
        tilt_transient_mask = (time >= 200.0) & (time <= 260.0)
        hr_tilt_peak = np.max(hr_bpm[tilt_transient_mask]) if np.any(tilt_transient_mask) else hr_baseline_mean
        
        # HR Increase (Clinical diagnostic metric)
        hr_increase = hr_tilt_peak - hr_baseline_mean
        
        # 2. Programmatic validation checks
        checks = {}
        
        # Check A: Physiological Bounds (extreme limits)
        checks["hr_within_bounds"] = {
            "pass": bool(np.all(hr_bpm >= 30.0) and np.all(hr_bpm <= 220.0)),
            "details": f"HR Range: [{np.min(hr_bpm):.1f}, {np.max(hr_bpm):.1f}] bpm"
        }
        
        checks["bp_within_bounds"] = {
            "pass": bool(np.all(pau >= 30.0) and np.all(pau <= 230.0)),
            "details": f"BP Range: [{np.min(pau):.1f}, {np.max(pau):.1f}] mmHg"
        }
        
        # Check B: Clinical Criteria (Diagnostic validation)
        if phenotype is None:  # Healthy Control
            # Healthy should not exceed 30 bpm increase on standing
            checks["clinical_pots_diagnostic"] = {
                "pass": bool(hr_increase < 30.0),
                "details": f"Healthy control HR rise is {hr_increase:.1f} bpm (< 30 bpm)"
            }
        else:  # POTS Phenotype
            # POTS should exceed 30 bpm increase on standing
            checks["clinical_pots_diagnostic"] = {
                "pass": bool(hr_increase >= 30.0),
                "details": f"POTS phenotype HR rise is {hr_increase:.1f} bpm (>= 30 bpm)"
            }
            
        # Check C: Autonomic Compensation (initial drop and recovery)
        # Sensed carotid pressure should drop initially at tilt and then recover
        post_tilt_initial_mask = (time >= 200.0) & (time <= 215.0)
        pau_initial_tilt_min = np.min(pau[post_tilt_initial_mask]) if np.any(post_tilt_initial_mask) else map_baseline
        bp_drop = map_baseline - pau_initial_tilt_min
        
        checks["baroreflex_compensation"] = {
            "pass": bool(bp_drop > 5.0 and map_tilt > (pau_initial_tilt_min - 2.0)),
            "details": f"Initial BP drop: {bp_drop:.1f} mmHg. Stabilized Map: {map_tilt:.1f} mmHg."
        }
        
        # Calculate overall status
        all_passed = all(check["pass"] for check in checks.values())
        
        report = {
            "phenotype": phenotype or "Healthy Control",
            "hr_baseline_mean_bpm": hr_baseline_mean,
            "hr_tilt_mean_bpm": hr_tilt_mean,
            "hr_tilt_peak_bpm": hr_tilt_peak,
            "hr_increase_bpm": hr_increase,
            "bp_baseline_sys_dia": (sbp_baseline, dbp_baseline),
            "bp_tilt_sys_dia": (sbp_tilt, dbp_tilt),
            "map_baseline_mmHg": map_baseline,
            "map_tilt_mmHg": map_tilt,
            "initial_bp_drop_mmHg": bp_drop,
            "validation_passed": all_passed,
            "checks": checks
        }
        
        return report

    def print_report(self, report):
        print(f"\n==========================================")
        print(f"  PHYSIOLOGICAL VALIDATION REPORT")
        print(f"  Cohort Phenotype: {report['phenotype'].upper()}")
        print(f"==========================================")
        print(f"Baseline HR (mean): {report['hr_baseline_mean_bpm']:.1f} bpm")
        print(f"Baseline BP (sys/dia): {report['bp_baseline_sys_dia'][0]:.1f}/{report['bp_baseline_sys_dia'][1]:.1f} mmHg")
        print(f"Peak Post-Tilt HR: {report['hr_tilt_peak_bpm']:.1f} bpm")
        print(f"HR Increase on Tilt: {report['hr_increase_bpm']:.1f} bpm")
        print(f"Stabilized Post-Tilt BP: {report['bp_tilt_sys_dia'][0]:.1f}/{report['bp_tilt_sys_dia'][1]:.1f} mmHg")
        print(f"Initial BP Drop on Tilt: {report['initial_bp_drop_mmHg']:.1f} mmHg")
        print(f"------------------------------------------")
        print(f"Validation Checks:")
        for name, chk in report["checks"].items():
            status = "\033[92m[PASS]\033[0m" if chk["pass"] else "\033[91m[FAIL]\033[0m"
            print(f"  {status} {name}: {chk['details']}")
        print(f"------------------------------------------")
        overall_status = "\033[92mPASSED\033[0m" if report["validation_passed"] else "\033[91mFAILED\033[0m"
        print(f"OVERALL PHYSIOLOGICAL VALIDATION: {overall_status}")
        print(f"==========================================\n")
