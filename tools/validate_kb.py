#!/usr/bin/env python3
import os
import re
import sys
import yaml

def print_err(msg):
    print(f"\033[91m[ERROR]\033[0m {msg}", file=sys.stderr)

def print_ok(msg):
    print(f"\033[92m[OK]\033[0m {msg}")

def print_warn(msg):
    print(f"\033[93m[WARN]\033[0m {msg}")

def parse_frontmatter(filepath):
    """Parses YAML frontmatter from a Markdown file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    parts = content.split('---')
    if len(parts) < 3:
        raise ValueError("Missing YAML frontmatter markers '---'")
    
    frontmatter_text = parts[1]
    data = yaml.safe_load(frontmatter_text)
    return data

def main():
    kb_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Validating Knowledge Base in: {kb_dir}")
    
    errors = 0
    warnings = 0
    
    # 1. Load variable definitions
    vars_file = os.path.join(kb_dir, "knowledge_base", "physiology", "variables.yaml")
    if not os.path.exists(vars_file):
        print_err(f"variables.yaml not found at {vars_file}")
        sys.exit(1)
        
    try:
        with open(vars_file, 'r', encoding='utf-8') as f:
            vars_data = yaml.safe_load(f)
        defined_vars = {v['symbol']: v for v in vars_data.get('variables', [])}
        print_ok(f"Loaded {len(defined_vars)} central variable definitions from physiology/variables.yaml.")
    except Exception as e:
        print_err(f"Failed to parse variables.yaml: {e}")
        sys.exit(1)

    # 2. Load latent variable definitions
    latent_file = os.path.join(kb_dir, "knowledge_base", "physiology", "latent_states.yaml")
    if not os.path.exists(latent_file):
        print_err(f"latent_states.yaml not found at {latent_file}")
        sys.exit(1)
        
    try:
        with open(latent_file, 'r', encoding='utf-8') as f:
            latent_data = yaml.safe_load(f)
        defined_latent = {v['symbol']: v for v in latent_data.get('latent_variables', [])}
        print_ok(f"Loaded {len(defined_latent)} latent state variables from physiology/latent_states.yaml.")
    except Exception as e:
        print_err(f"Failed to parse latent_states.yaml: {e}")
        sys.exit(1)

    # Merge variables for relationship/equation checks
    all_vars = {**defined_vars, **defined_latent}

    # 3. Load ontology concepts
    concepts_file = os.path.join(kb_dir, "knowledge_base", "ontology", "concepts.yaml")
    if not os.path.exists(concepts_file):
        print_err(f"concepts.yaml not found at {concepts_file}")
        errors += 1
    else:
        try:
            with open(concepts_file, 'r', encoding='utf-8') as f:
                concepts_data = yaml.safe_load(f)
            concepts = concepts_data.get('concepts', [])
            print_ok(f"Loaded {len(concepts)} ontology concepts.")
        except Exception as e:
            print_err(f"Failed to parse concepts.yaml: {e}")
            errors += 1

    # 4. Load semantic relationships
    semantic_rel_file = os.path.join(kb_dir, "knowledge_base", "ontology", "relationships.yaml")
    if not os.path.exists(semantic_rel_file):
        print_err(f"relationships.yaml not found at {semantic_rel_file}")
        errors += 1
    else:
        try:
            with open(semantic_rel_file, 'r', encoding='utf-8') as f:
                semantic_rel_data = yaml.safe_load(f)
            sem_rels = semantic_rel_data.get('semantic_relationships', [])
            print_ok(f"Loaded {len(sem_rels)} semantic relationships.")
        except Exception as e:
            print_err(f"Failed to parse relationships.yaml: {e}")
            errors += 1

    # 5. Load mechanistic relationships
    rel_file = os.path.join(kb_dir, "knowledge_base", "ontology", "mechanistic_links.yaml")
    if not os.path.exists(rel_file):
        print_err(f"mechanistic_links.yaml not found at {rel_file}")
        sys.exit(1)
        
    try:
        with open(rel_file, 'r', encoding='utf-8') as f:
            rel_data = yaml.safe_load(f)
        relations = rel_data.get('relationships', [])
        print_ok(f"Loaded {len(relations)} central mechanistic links.")
        
        # Validate cause/effect variables exist in registry
        for rel in relations:
            rid = rel.get('relationship_id', 'unknown')
            cause = rel.get('cause')
            effect = rel.get('effect')
            if cause not in all_vars:
                print_err(f"Mechanistic Link '{rid}': Cause variable '{cause}' is not registered.")
                errors += 1
            if effect not in all_vars:
                print_err(f"Mechanistic Link '{rid}': Effect variable '{effect}' is not registered.")
                errors += 1
    except Exception as e:
        print_err(f"Failed to parse mechanistic_links.yaml: {e}")
        sys.exit(1)

    # 6. Load mathematical models and parameters
    model_file = os.path.join(kb_dir, "knowledge_base", "equations", "mathematical_models.yaml")
    if not os.path.exists(model_file):
        print_err(f"mathematical_models.yaml not found at {model_file}")
        sys.exit(1)
        
    try:
        with open(model_file, 'r', encoding='utf-8') as f:
            model_data = yaml.safe_load(f)
        models = model_data.get('models', [])
        print_ok(f"Loaded {len(models)} central mathematical models.")
        
        # Validate model variables/parameters
        model_params = {}
        for model in models:
            mid = model.get('model_id', 'unknown')
            for param in model.get('parameters', []):
                sym = param.get('symbol')
                units = param.get('units')
                model_params[sym] = param
                if not sym:
                    print_err(f"Model '{mid}': Parameter missing symbol")
                    errors += 1
                if units is None:
                    print_err(f"Model '{mid}', Parameter '{sym}': Missing units (set to empty string if dimensionless)")
                    errors += 1
    except Exception as e:
        print_err(f"Failed to parse mathematical_models.yaml: {e}")
        sys.exit(1)

    # 7. Load diseases
    diseases_dir = os.path.join(kb_dir, "knowledge_base", "diseases")
    if not os.path.exists(diseases_dir):
        print_err(f"diseases/ directory not found at {diseases_dir}")
        errors += 1
    else:
        try:
            d_files = [f for f in os.listdir(diseases_dir) if f.endswith('.yaml')]
            print_ok(f"Found {len(d_files)} disease registrations.")
            for df in d_files:
                dpath = os.path.join(diseases_dir, df)
                with open(dpath, 'r', encoding='utf-8') as f:
                    disease_data = yaml.safe_load(f)
                phenotypes = disease_data.get('disease', {}).get('phenotypes', [])
                print_ok(f"  Loaded disease: {disease_data.get('disease', {}).get('name')} ({df}) with {len(phenotypes)} phenotypes.")
                for pheno in phenotypes:
                    pid = pheno.get('id')
                    for pert in pheno.get('parameters_perturbed', []):
                        psym = pert.get('symbol')
                        if psym not in model_params and psym != 'TotalVol':
                            print_err(f"  Disease phenotype '{pid}' perturbs unregistered parameter '{psym}'")
                            errors += 1
        except Exception as e:
            print_err(f"Failed to parse disease files: {e}")
            errors += 1

    # 8. Load interventions
    int_file = os.path.join(kb_dir, "knowledge_base", "interventions", "tilt_test.yaml")
    if not os.path.exists(int_file):
        print_err(f"tilt_test.yaml not found at {int_file}")
        errors += 1
    else:
        try:
            with open(int_file, 'r', encoding='utf-8') as f:
                int_data = yaml.safe_load(f)
            print_ok(f"Loaded intervention: {int_data.get('intervention', {}).get('name')}.")
        except Exception as e:
            print_err(f"Failed to parse tilt_test.yaml: {e}")
            errors += 1

    # 9. Load populations
    pop_file = os.path.join(kb_dir, "knowledge_base", "populations", "cohorts.yaml")
    if not os.path.exists(pop_file):
        print_err(f"cohorts.yaml not found at {pop_file}")
        errors += 1
    else:
        try:
            with open(pop_file, 'r', encoding='utf-8') as f:
                pop_data = yaml.safe_load(f)
            cohorts = pop_data.get('cohorts', [])
            print_ok(f"Loaded populations: {len(cohorts)} cohorts registered.")
        except Exception as e:
            print_err(f"Failed to parse cohorts.yaml: {e}")
            errors += 1

    # 10. Load wearables
    wearables_dir = os.path.join(kb_dir, "knowledge_base", "wearables")
    if os.path.exists(wearables_dir):
        w_files = [f for f in os.listdir(wearables_dir) if f.endswith('.yaml')]
        print_ok(f"Found {len(w_files)} wearable sensor registrations.")
        for wf in w_files:
            try:
                with open(os.path.join(wearables_dir, wf), 'r', encoding='utf-8') as f:
                    w_data = yaml.safe_load(f)
                print_ok(f"  Validated wearable specification: {w_data.get('sensor', {}).get('name')}")
            except Exception as e:
                print_err(f"Failed to parse wearable file {wf}: {e}")
                errors += 1
    else:
        print_err("wearables/ directory not found")
        errors += 1

    # 11. Load and validate publication reviews
    pub_dir = os.path.join(kb_dir, "knowledge_base", "publications")
    if not os.path.exists(pub_dir):
        print_err(f"publications/ directory not found at {pub_dir}")
        sys.exit(1)
        
    pub_files = [f for f in os.listdir(pub_dir) if f.endswith('.md')]
    print(f"Found {len(pub_files)} publication reviews to validate.")
    
    for pub_file in pub_files:
        filepath = os.path.join(pub_dir, pub_file)
        try:
            pub_data = parse_frontmatter(filepath)
            pub_meta = pub_data.get('publication', {})
            title = pub_meta.get('title', pub_file)
            doi = pub_meta.get('doi')
            
            if not doi:
                print_err(f"{pub_file}: Missing DOI in publication metadata")
                errors += 1
                
            # Validate cohort sample sizes and demographics
            population = pub_data.get('population', {})
            cohorts = population.get('cohorts', [])
            for cohort in cohorts:
                cid = cohort.get('cohort_id', 'unknown')
                sz = cohort.get('sample_size')
                if sz is None and cohort.get('health_status') != "unspecified":
                    print_warn(f"{pub_file} [Cohort '{cid}']: Sample size is null")
                    warnings += 1
            
            # Validate publication variables
            pub_vars = pub_data.get('variables', [])
            for pvar in pub_vars:
                sym = pvar.get('symbol')
                if sym not in all_vars:
                    print_err(f"{pub_file}: Variable '{sym}' is used but not defined in variables/latent_states registries")
                    errors += 1
                    
            print_ok(f"Validated review: '{title}' ({pub_file})")
            
        except Exception as e:
            print_err(f"Failed to parse frontmatter of {pub_file}: {e}")
            errors += 1
            
    print("\n--- Validation Summary ---")
    print(f"Total Errors: {errors}")
    print(f"Total Warnings: {warnings}")
    
    if errors > 0:
        print_err("Knowledge Base validation FAILED.")
        sys.exit(1)
    else:
        print_ok("Knowledge Base validation PASSED.")
        sys.exit(0)

if __name__ == "__main__":
    main()
