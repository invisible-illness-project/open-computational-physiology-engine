import os
import yaml
import numpy as np

class PerturbationManager:
    """
    Loads, processes, and applies composable disease perturbations.
    Supports resolving string expressions with '*' (e.g. 'neuropathic_pots * beta_blocker')
    and applying parameter shifts sequentially using multiplicative scaling to ensure
    physiologically sound composability.
    """
    def __init__(self, kb_path=None):
        if kb_path is None:
            self.kb_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_base")
        else:
            self.kb_path = kb_path
            
        self.phenotypes = {}
        self.load_all_disease_files()

    def load_all_disease_files(self):
        diseases_dir = os.path.join(self.kb_path, "diseases")
        if not os.path.exists(diseases_dir):
            return
            
        for file in os.listdir(diseases_dir):
            if file.endswith(".yaml"):
                filepath = os.path.join(diseases_dir, file)
                try:
                    with open(filepath, "r") as f:
                        data = yaml.safe_load(f)
                    
                    disease_info = data.get("disease", {})
                    for pheno in disease_info.get("phenotypes", []):
                        pheno_id = pheno.get("id")
                        self.phenotypes[pheno_id] = {
                            "name": pheno.get("name"),
                            "description": pheno.get("description"),
                            "parameters_perturbed": pheno.get("parameters_perturbed", []),
                            "disease_name": disease_info.get("name")
                        }
                except Exception as e:
                    print(f"[WARN] Failed to load disease file {file}: {e}")

    def apply_perturbations(self, base_params, phenotype_expr):
        """
        Applies a list or expression of perturbations.
        phenotype_expr: e.g. "neuropathic_pots * environmental_heat" or ["neuropathic_pots", "beta_blocker"]
        Returns a new dict of parameters.
        """
        if not phenotype_expr:
            return base_params.copy()
            
        # Parse expression
        if isinstance(phenotype_expr, str):
            pheno_ids = [p.strip() for p in phenotype_expr.split("*") if p.strip()]
        else:
            pheno_ids = list(phenotype_expr)
            
        perturbed_params = base_params.copy()
        applied_phenotypes = []
        
        for pid in pheno_ids:
            if pid not in self.phenotypes:
                print(f"[WARN] Unknown phenotype ID '{pid}' requested in perturbation.")
                continue
                
            pheno = self.phenotypes[pid]
            applied_phenotypes.append(pid)
            
            for pert in pheno.get("parameters_perturbed", []):
                symbol = pert["symbol"]
                normal_val = float(pert["normal_value"])
                pert_val = float(pert["perturbed_value"])
                
                # Compose parameter updates:
                # If the parameter is currently at its default, we set it.
                # If it has already been perturbed by a prior step, we scale it
                # based on the relative ratio: pert_val / normal_val.
                if symbol in perturbed_params:
                    current_val = perturbed_params[symbol]
                    if normal_val != 0.0:
                        scale = pert_val / normal_val
                        # Compound scale
                        perturbed_params[symbol] = current_val * scale
                    else:
                        # Fallback to overwrite
                        perturbed_params[symbol] = pert_val
                else:
                    perturbed_params[symbol] = pert_val
                    
        return perturbed_params, applied_phenotypes
