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
    def __init__(self, kb_path=None, include_experimental=False):
        if kb_path is None:
            self.kb_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_base")
        else:
            self.kb_path = kb_path

        # Canonical mode (default) applies ONLY `parameters_perturbed` blocks
        # (adversarially reviewed values). When include_experimental=True, the
        # phenotype's `unverified_parameters` (tier-D, machine-proposed,
        # UNRESOLVED review status) are applied as well, and the application is
        # marked EXPERIMENTAL in the provenance metadata (self.last_application).
        self.include_experimental = include_experimental
        self.last_application = None

        self.phenotypes = {}
        self.load_all_disease_files()

    def load_all_disease_files(self):
        diseases_dir = os.path.join(self.kb_path, "diseases")
        if not os.path.exists(diseases_dir):
            return

        for file in os.listdir(diseases_dir):
            # Exclude ADR 0001 sidecar review manifests (<file>.review.yaml);
            # they are governance metadata, not disease data files.
            if file.endswith(".yaml") and not file.endswith(".review.yaml"):
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
                            "unverified_parameters": pheno.get("unverified_parameters", []),
                            "disease_name": disease_info.get("name")
                        }
                except Exception as e:
                    print(f"[WARN] Failed to load disease file {file}: {e}")

    def apply_perturbations(self, base_params, phenotype_expr, include_experimental=None):
        """
        Applies a list or expression of perturbations.
        phenotype_expr: e.g. "neuropathic_pots * environmental_heat" or ["neuropathic_pots", "beta_blocker"]
        include_experimental: if True, also apply each phenotype's
            `unverified_parameters` (tier-D, machine-proposed values pending
            human review). None falls back to the instance default
            (self.include_experimental). Canonical default is False.
        Returns (perturbed_params, applied_phenotypes). Per-parameter
        provenance (which values are canonical vs experimental) is recorded in
        self.last_application.
        """
        if include_experimental is None:
            include_experimental = self.include_experimental

        self.last_application = {
            "mode": "EXPERIMENTAL" if include_experimental else "canonical",
            "phenotypes": {},
        }

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
            provenance = {"canonical": {}, "experimental": {}}

            for pert in pheno.get("parameters_perturbed", []):
                self._apply_single_perturbation(perturbed_params, pert)
                provenance["canonical"][pert["symbol"]] = perturbed_params[pert["symbol"]]

            if include_experimental:
                unverified = pheno.get("unverified_parameters", [])
                if unverified:
                    print(f"[EXPERIMENTAL] Phenotype '{pid}': applying {len(unverified)} "
                          f"unverified (tier-D) parameter(s) pending human review: "
                          f"{[p['symbol'] for p in unverified]}")
                for pert in unverified:
                    self._apply_single_perturbation(perturbed_params, pert)
                    provenance["experimental"][pert["symbol"]] = perturbed_params[pert["symbol"]]

            self.last_application["phenotypes"][pid] = provenance

        return perturbed_params, applied_phenotypes

    @staticmethod
    def _apply_single_perturbation(perturbed_params, pert):
        """Applies one parameter perturbation with multiplicative compounding:
        if the parameter is currently at its default, set it; if it has already
        been perturbed by a prior step, scale it by perturbed/normal."""
        symbol = pert["symbol"]
        normal_val = float(pert["normal_value"])
        pert_val = float(pert["perturbed_value"])

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


def enable_experimental_mode(model):
    """
    Re-applies a constructed BaroreflexPOTSModel's phenotype perturbations in
    EXPERIMENTAL mode: in addition to the canonical `parameters_perturbed`, the
    phenotype's `unverified_parameters` (tier-D values pending human review)
    are applied, and the steady state is re-initialized against the new
    parameter set (parameters themselves are never modified afterwards).

    Replays the model's own load pipeline (KB nominals -> VirtualSubject priors
    -> perturbations) using public model attributes only. Attaches
    `model.perturbation_provenance` marking which applied values are canonical
    vs experimental, and returns the model for chaining.
    """
    pm = PerturbationManager(kb_path=model.kb_path, include_experimental=True)
    params = dict(model.kb_nominal_params)
    if getattr(model, "subject", None) is not None:
        params = model.subject.adjust_parameters(params)
    params, applied = pm.apply_perturbations(params, model.phenotype)
    model.params = params
    model.initialize_steady_state()
    model.perturbation_provenance = pm.last_application
    print(f"[EXPERIMENTAL] Model re-initialized with unverified (tier-D) parameters "
          f"for phenotypes: {applied}. Results are hypothesis-illustrative, not canonical.")
    return model
