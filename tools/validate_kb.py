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
    vars_file = os.path.join(kb_dir, "knowledge_base", "variables", "definitions.yaml")
    if not os.path.exists(vars_file):
        print_err(f"definitions.yaml not found at {vars_file}")
        sys.exit(1)
        
    try:
        with open(vars_file, 'r', encoding='utf-8') as f:
            vars_data = yaml.safe_load(f)
        defined_vars = {v['symbol']: v for v in vars_data.get('variables', [])}
        print_ok(f"Loaded {len(defined_vars)} central variable definitions.")
    except Exception as e:
        print_err(f"Failed to parse definitions.yaml: {e}")
        sys.exit(1)
        
    # 2. Load relationships
    rel_file = os.path.join(kb_dir, "knowledge_base", "relationships", "mechanistic_links.yaml")
    if not os.path.exists(rel_file):
        print_err(f"mechanistic_links.yaml not found at {rel_file}")
        sys.exit(1)
        
    try:
        with open(rel_file, 'r', encoding='utf-8') as f:
            rel_data = yaml.safe_load(f)
        relations = rel_data.get('relationships', [])
        print_ok(f"Loaded {len(relations)} central relationships.")
        
        # Validate cause/effect variables exist in registry
        for rel in relations:
            rid = rel.get('relationship_id', 'unknown')
            cause = rel.get('cause')
            effect = rel.get('effect')
            if cause not in defined_vars:
                print_err(f"Relationship '{rid}': Cause variable '{cause}' is not defined in definitions.yaml")
                errors += 1
            if effect not in defined_vars:
                print_err(f"Relationship '{rid}': Effect variable '{effect}' is not defined in definitions.yaml")
                errors += 1
    except Exception as e:
        print_err(f"Failed to parse mechanistic_links.yaml: {e}")
        sys.exit(1)

    # 3. Load mathematical models
    model_file = os.path.join(kb_dir, "knowledge_base", "models", "mathematical_models.yaml")
    if not os.path.exists(model_file):
        print_err(f"mathematical_models.yaml not found at {model_file}")
        sys.exit(1)
        
    try:
        with open(model_file, 'r', encoding='utf-8') as f:
            model_data = yaml.safe_load(f)
        models = model_data.get('models', [])
        print_ok(f"Loaded {len(models)} central mathematical models.")
        
        # Validate model variables/parameters
        for model in models:
            mid = model.get('model_id', 'unknown')
            for param in model.get('parameters', []):
                sym = param.get('symbol')
                units = param.get('units')
                if not sym:
                    print_err(f"Model '{mid}': Parameter missing symbol")
                    errors += 1
                if units is None:
                    print_err(f"Model '{mid}', Parameter '{sym}': Missing units (set to empty string if dimensionless)")
                    errors += 1
    except Exception as e:
        print_err(f"Failed to parse mathematical_models.yaml: {e}")
        sys.exit(1)

    # 4. Load and validate publication reviews
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
                if sym not in defined_vars:
                    print_err(f"{pub_file}: Variable '{sym}' is used but not defined in definitions.yaml")
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
