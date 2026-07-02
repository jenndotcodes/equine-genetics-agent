# cli.py
"""
Equine Genetics Inheritance Simulator CLI
-----------------------------------------
A standalone command-line interface script allowing users to simulate equine Mendelian
crossovers and safety compliance audits using sire and dam genotype strings.
"""
import os
# Suppress Streamlit logger warnings at environment level before importing anything
os.environ["STREAMLIT_LOG_LEVEL"] = "error"

import warnings
warnings.filterwarnings("ignore")

import argparse
import sys
import logging

# Silence all library warnings (like Streamlit bare execution logs) globally
logging.disable(logging.WARNING)

# Ensure local imports work correctly under absolute search paths
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.genetics_engine import calculate_foal_probabilities
from tools.critique_agent import validate_safety_compliance

def parse_profile(profile_str: str) -> list:
    """
    Parses a genetic profile string (comma or space separated) into a list of 9 locus genotypes.
    """
    # Normalize delimiters and split
    parts = profile_str.replace(",", " ").split()
    if len(parts) != 9:
        raise ValueError(f"Expected exactly 9 locus genotypes, got {len(parts)}: {parts}")
    return parts

def main():
    """
    Main CLI entrypoint. Parses --sire and --dam inputs, computes probabilities,
    and prints results or veterinary safety warnings.
    """
    parser = argparse.ArgumentParser(
        description="Equine Inheritance Simulator CLI - Compute offspring coat color probabilities."
    )
    parser.add_argument(
        "--sire", 
        required=True, 
        help="Sire genotype profile (9 space or comma-separated loci: E A Cr D Z Ch prl G O)"
    )
    parser.add_argument(
        "--dam", 
        required=True, 
        help="Dam genotype profile (9 space or comma-separated loci: E A Cr D Z Ch prl G O)"
    )
    
    args = parser.parse_args()
    
    try:
        sire_loci = parse_profile(args.sire)
        dam_loci = parse_profile(args.dam)
    except ValueError as e:
        print(f"Error parsing input profiles: {e}", file=sys.stderr)
        sys.exit(1)
        
    try:
        results = calculate_foal_probabilities(
            sire_E=sire_loci[0], sire_A=sire_loci[1], sire_Cr=sire_loci[2], sire_D=sire_loci[3],
            sire_Z=sire_loci[4], sire_Ch=sire_loci[5], sire_prl=sire_loci[6], sire_G=sire_loci[7], sire_O=sire_loci[8],
            dam_E=dam_loci[0], dam_A=dam_loci[1], dam_Cr=dam_loci[2], dam_D=dam_loci[3],
            dam_Z=dam_loci[4], dam_Ch=dam_loci[5], dam_prl=dam_loci[6], dam_G=dam_loci[7], dam_O=dam_loci[8]
        )
        
        # Check safety/compliance via Critique Agent
        safety = validate_safety_compliance(results)
        if not safety["compliant"]:
            print("======================================================================")
            print("🚨 CRITICAL BREEDING WARNING (CRITIQUE AGENT INTERCEPT) 🚨")
            print("======================================================================")
            print(safety["message"])
            print("======================================================================")
        else:
            print("======================================================================")
            print("🧬 Equine Offspring Phenotype Probabilities")
            print("======================================================================")
            # Sort results descending by probability
            sorted_odds = sorted(results.items(), key=lambda x: float(x[1].replace("%", "")), reverse=True)
            for pheno, prob in sorted_odds:
                print(f"- {pheno}: {prob}")
            print("----------------------------------------------------------------------")
            print(f"🛡️ {safety['message']}")
            print("======================================================================")
            
    except Exception as e:
        print(f"Simulation Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
