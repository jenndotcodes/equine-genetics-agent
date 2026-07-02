# tools/genetics_engine.py
import os
import json
import streamlit as st
from typing import Dict, Tuple, List

# ==============================================================================
# GROUNDING DATA LAYER & CONFIG
# ==============================================================================

# Genotype options for each locus
LOCI_GENOTYPES = {
    "E": ["EE", "Ee", "ee"],          # Extension (Black vs Red base)
    "A": ["AA", "Aa", "aa"],          # Agouti (Bay vs Black points)
    "Cr": ["nn", "Crn", "CrCr"],      # Cream Dilution (Single/Double dilution)
    "D": ["nn", "Dn", "DD"],          # Dun (Dominant dilution with dun factors)
    "Z": ["nn", "Zn", "ZZ"],          # Silver (Dominant modifier, black-based only)
    "Ch": ["nn", "Chn", "ChCh"],      # Champagne (Dominant dilution)
    "prl": ["nn", "prln", "prlprl"],  # Pearl Dilution (Recessive / cream-co-dominant)
    "G": ["nn", "Gn", "GG"],          # Grey (Dominant progressive greying mask)
    "O": ["nn", "On", "OO"],          # Frame Overo (Incomplete lethal dominant white pattern)
}

# Legacy Base Genetic Colors for backward compatibility
GENETIC_COLORS = {
    "EE_aa": "Solid Black",
    "Ee_aa": "Solid Black",
    "EE_AA": "Bay",
    "EE_Aa": "Bay",
    "Ee_AA": "Bay",
    "Ee_Aa": "Bay",
    "ee_AA": "Chestnut",
    "ee_Aa": "Chestnut",
    "ee_aa": "Chestnut"
}

# ==============================================================================
# DETAILED GENETIC SPLITTING & SORTING HELPERS
# ==============================================================================

def split_genotype(genotype: str) -> Tuple[str, str]:
    """
    Deconstructs a two-allele genotype string into its two component alleles.
    Accurately manages multi-character alleles (e.g., 'Cr', 'Ch', 'prl') alongside standard single characters.
    
    Parameters:
        genotype (str): The genotype representing a specific locus (e.g., "Ee", "Crn", "CrCr").
        
    Returns:
        Tuple[str, str]: A tuple containing the two segregated alleles.
    """
    if genotype in ("CrCr", "ChCh", "prlprl"):
        half = len(genotype) // 2
        return genotype[:half], genotype[half:]
    elif genotype.endswith("n") and genotype != "nn":
        # Segregate carriers from wild-type (e.g., "Crn" -> "Cr" and "n")
        return genotype[:-1], "n"
    else:
        # Standard 2-character alleles (e.g. "EE" -> "E" and "E")
        return genotype[0], genotype[1]


def sort_alleles(al1: str, al2: str) -> List[str]:
    """
    Sorts two segregated alleles by biological precedence: dominant/mutant alleles first, 
    and recessive wild-type ('n') alleles last.
    
    Parameters:
        al1 (str): First allele.
        al2 (str): Second allele.
        
    Returns:
        List[str]: A list of sorted alleles, e.g., ["E", "e"] or ["Cr", "n"].
    """
    if al1 == "n":
        return [al2, al1]
    if al2 == "n":
        return [al1, al2]
    if al1.lower() == al2.lower():
        # Handle cases like 'e' and 'E' -> dominant 'E' comes first
        if al1.isupper():
            return [al1, al2]
        else:
            return [al2, al1]
    return sorted([al1, al2])

# ==============================================================================
# DETERMINISTIC AGENT TOOLS
# ==============================================================================

def run_punnett_square(parent1: str, parent2: str) -> List[str]:
    """
    Executes a standard 2x2 Punnett square Mendelian crossover logic for a single locus.
    
    Parameters:
        parent1 (str): Genotype of the first parent (e.g., "Ee").
        parent2 (str): Genotype of the second parent (e.g., "ee").
        
    Returns:
        List[str]: A list of all four possible offspring genotypes from this cross.
    """
    p1_a1, p1_a2 = split_genotype(parent1)
    p2_a1, p2_a2 = split_genotype(parent2)
    
    combinations = []
    for a1 in (p1_a1, p1_a2):
        for a2 in (p2_a1, p2_a2):
            sorted_alleles = sort_alleles(a1, a2)
            combinations.append("".join(sorted_alleles))
    return combinations


def get_phenotype(g: dict) -> str:
    """
    Resolves the visual phenotype of a horse by running its 9-locus genotype 
    through sequential epistatic masks, dilution interactions, and patterns.
    
    Order of Epistatic Precedence:
      1. Lethal White Syndrome (Homozygous Overo OO check)
      2. Base Coat Determination (Extension & Agouti)
      3. Cream & Pearl Dilution (Co-dominant interaction model)
      4. Champagne Dilution (Dominant modifier)
      5. Dun Dilution (Dominant dilution with primitive markings)
      6. Silver Modifier (Dominant modifier targeting black pigment only)
      7. Frame Overo Pattern (Heterozygous white spotting)
      8. Progressive Greying Mask (Dominant grey mask over born color)
      
    Parameters:
        g (dict): A dictionary containing keys "E", "A", "Cr", "D", "Z", "Ch", "prl", "G", "O" 
                  mapped to their corresponding genotypes.
                  
    Returns:
        str: Human-readable phenotype name.
    """
    # 1. Lethal White Syndrome (Fatal)
    # Homozygous Overo (OO) leads to incomplete intestinal development and is fatal at birth.
    if g["O"] == "OO":
        return "Lethal White Syndrome (Fatal)"
        
    # Determine base color
    # Extension: EE/Ee = black base pigment, ee = red base pigment (Chestnut)
    is_black_base = g["E"] in ("EE", "Ee")
    
    if is_black_base:
        # Agouti: AA/Aa restricts black pigment to points (Bay), aa leaves horse Solid Black
        is_bay = g["A"] in ("AA", "Aa")
        base = "Bay" if is_bay else "Solid Black"
    else:
        base = "Chestnut"
        
    color = base
    
    # 2. Cream (Cr) and Pearl (prl) Dilutions (Co-dominant locus interaction)
    has_double_pearl = g["prl"] == "prlprl"
    has_single_pearl = g["prl"] == "prln"
    has_double_cream = g["Cr"] == "CrCr"
    has_single_cream = g["Cr"] == "Crn"
    
    if has_double_pearl:
        if base == "Chestnut":
            color = "Apricot (Pearl)"
        elif base == "Bay":
            color = "Bay Pearl"
        else:
            color = "Black Pearl"
    elif has_single_pearl and has_single_cream:
        # Cream and Pearl interact co-dominantly to create pseudodiploid dilution phenotypes
        if base == "Chestnut":
            color = "Chestnut Cream-Pearl"
        elif base == "Bay":
            color = "Bay Cream-Pearl"
        else:
            color = "Black Cream-Pearl"
    elif has_double_cream:
        if base == "Chestnut":
            color = "Cremello"
        elif base == "Bay":
            color = "Perlino"
        else:
            color = "Smoky Cream"
    elif has_single_cream:
        if base == "Chestnut":
            color = "Palomino"
        elif base == "Bay":
            color = "Buckskin"
        else:
            color = "Smoky Black"
            
    # 3. Champagne Dilution (Dominant Ch)
    has_champagne = g["Ch"] in ("ChCh", "Chn")
    if has_champagne:
        if color == "Chestnut":
            color = "Gold Champagne"
        elif color == "Bay":
            color = "Amber Champagne"
        elif color == "Solid Black":
            color = "Classic Champagne"
        elif color in ("Palomino", "Cremello", "Chestnut Cream-Pearl", "Apricot (Pearl)"):
            color = "Gold Cream Champagne (Ivory)"
        elif color in ("Buckskin", "Perlino", "Bay Cream-Pearl", "Bay Pearl"):
            color = "Amber Cream Champagne (Ivory)"
        elif color in ("Smoky Black", "Smoky Cream", "Black Cream-Pearl", "Black Pearl"):
            color = "Classic Cream Champagne (Ivory)"
        else:
            color = f"{color} Champagne"
            
    # 4. Dun Dilution (Dominant D)
    has_dun = g["D"] in ("DD", "Dn")
    if has_dun:
        if color == "Chestnut":
            color = "Red Dun"
        elif color == "Bay":
            color = "Bay Dun"
        elif color == "Solid Black":
            color = "Grullo"
        elif color == "Palomino":
            color = "Dunalino"
        elif color == "Buckskin":
            color = "Dunskin"
        elif color == "Smoky Black":
            color = "Smoky Grullo"
        else:
            color = f"{color} Dun"
            
    # 5. Silver Modifier (Dominant Z)
    # Silver only affects eumelanin (black base) and is hidden on pheomelanin (red/chestnut)
    has_silver = g["Z"] in ("ZZ", "Zn")
    if has_silver and is_black_base:
        if color == "Bay":
            color = "Silver Bay"
        elif color == "Solid Black":
            color = "Silver Black (Dapple)"
        elif color == "Buckskin":
            color = "Silver Buckskin"
        elif color == "Smoky Black":
            color = "Silver Smoky Black"
        elif color == "Bay Dun":
            color = "Silver Bay Dun"
        elif color == "Grullo":
            color = "Silver Grullo"
        else:
            color = f"Silver {color}"
            
    # 6. Patterns: Frame Overo (On)
    # Adds white patches to the horse's coat (spotted layout)
    if g["O"] == "On":
        color = f"{color} Frame Overo"
        
    # 7. Grey Mask (Dominant G)
    # Progressive greying overrides all visual coat colors over time
    has_grey = g["G"] in ("GG", "Gn")
    if has_grey:
        color = f"Grey (Born {color})"
        
    return color


@st.cache_data
def calculate_foal_probabilities(
    sire_E: str, sire_A: str, sire_Cr: str, sire_D: str, sire_Z: str, sire_Ch: str, sire_prl: str, sire_G: str, sire_O: str,
    dam_E: str, dam_A: str, dam_Cr: str, dam_D: str, dam_Z: str, dam_Ch: str, dam_prl: str, dam_G: str, dam_O: str
) -> dict:
    """
    Simulates multi-locus Mendelian segregation and inheritance across all 9 loci 
    simultaneously, mapping the final probability distribution of all possible foal phenotypes.
    
    Parameters:
        sire_E to sire_O (str): Genotypes of the sire at all 9 loci.
        dam_E to dam_O (str): Genotypes of the dam at all 9 loci.
        
    Returns:
        dict: A dictionary mapping resolved phenotype strings to their percentage probabilities
              (e.g., {"Bay": "37.5%", "Cremello": "12.5%"}).
    """
    # Run independent Mendelian crosses for all nine loci
    e_res = run_punnett_square(sire_E, dam_E)
    a_res = run_punnett_square(sire_A, dam_A)
    cr_res = run_punnett_square(sire_Cr, dam_Cr)
    d_res = run_punnett_square(sire_D, dam_D)
    z_res = run_punnett_square(sire_Z, dam_Z)
    ch_res = run_punnett_square(sire_Ch, dam_Ch)
    prl_res = run_punnett_square(sire_prl, dam_prl)
    g_res = run_punnett_square(sire_G, dam_G)
    o_res = run_punnett_square(sire_O, dam_O)
    
    # Efficiently aggregate combination probabilities using state expansion (Cartesian product)
    states = {(): 1.0}
    loci_results = [e_res, a_res, cr_res, d_res, z_res, ch_res, prl_res, g_res, o_res]
    
    for locus_res in loci_results:
        # Calculate frequency weights of each segregated genotype option
        locus_counts = {}
        for gen in locus_res:
            locus_counts[gen] = locus_counts.get(gen, 0) + 0.25
            
        new_states = {}
        for current_tuple, prob in states.items():
            for gen, l_prob in locus_counts.items():
                new_tuple = current_tuple + (gen,)
                new_prob = prob * l_prob
                new_states[new_tuple] = new_states.get(new_tuple, 0.0) + new_prob
        states = new_states
        
    # Translate final multi-locus genotypes into phenotypes, summing up probabilities of matches
    phenotype_probs = {}
    for genotype_tuple, prob in states.items():
        g_dict = {
            "E": genotype_tuple[0],
            "A": genotype_tuple[1],
            "Cr": genotype_tuple[2],
            "D": genotype_tuple[3],
            "Z": genotype_tuple[4],
            "Ch": genotype_tuple[5],
            "prl": genotype_tuple[6],
            "G": genotype_tuple[7],
            "O": genotype_tuple[8],
        }
        phenotype = get_phenotype(g_dict)
        phenotype_probs[phenotype] = phenotype_probs.get(phenotype, 0.0) + prob
        
    return {pheno: f"{prob * 100:.1f}%" for pheno, prob in phenotype_probs.items() if prob > 0}


# ==============================================================================
# ADVANCED STATE ROUTING
# ==============================================================================

def handle_unknown_parent(
    known_E: str, known_A: str, known_Cr: str, known_D: str, known_Z: str, known_Ch: str, known_prl: str, known_G: str, known_O: str,
    unknown_parent_type: str = "stallion"
) -> list:
    """
    Evaluates probability trajectories when one parent is unknown. Computes crosses
    against three common baseline genotypes (Bay, Black, Chestnut) for the missing parent.
    All other modifier loci for the unknown parent default to wild-type 'nn' (unmodified).
    
    Parameters:
        known_E to known_O (str): Known parent genotypes.
        unknown_parent_type (str): "stallion" (sire is unknown) or "mare" (dam is unknown).
        
    Returns:
        list: A list of dictionaries representing trajectory scenarios:
              [{"profile": "Bay (Ee_Aa)", "odds": {...}}, ...]
    """
    mystery_profiles = [
        {"name": "Bay (Ee_Aa)", "E": "Ee", "A": "Aa", "Cr": "nn", "D": "nn", "Z": "nn", "Ch": "nn", "prl": "nn", "G": "nn", "O": "nn"},
        {"name": "Solid Black (Ee_aa)", "E": "Ee", "A": "aa", "Cr": "nn", "D": "nn", "Z": "nn", "Ch": "nn", "prl": "nn", "G": "nn", "O": "nn"},
        {"name": "Chestnut (ee_aa)", "E": "ee", "A": "aa", "Cr": "nn", "D": "nn", "Z": "nn", "Ch": "nn", "prl": "nn", "G": "nn", "O": "nn"}
    ]
    
    scenarios = []
    for profile in mystery_profiles:
        if unknown_parent_type == "stallion":
            # Mystery sire, known dam
            odds = calculate_foal_probabilities(
                sire_E=profile["E"], sire_A=profile["A"], sire_Cr=profile["Cr"], sire_D=profile["D"],
                sire_Z=profile["Z"], sire_Ch=profile["Ch"], sire_prl=profile["prl"], sire_G=profile["G"], sire_O=profile["O"],
                dam_E=known_E, dam_A=known_A, dam_Cr=known_Cr, dam_D=known_D,
                dam_Z=known_Z, dam_Ch=known_Ch, dam_prl=known_prl, dam_G=known_G, dam_O=known_O
            )
        else:
            # Known sire, mystery dam
            odds = calculate_foal_probabilities(
                sire_E=known_E, sire_A=known_A, sire_Cr=known_Cr, sire_D=known_D,
                sire_Z=known_Z, sire_Ch=known_Ch, sire_prl=known_prl, sire_G=known_G, sire_O=known_O,
                dam_E=profile["E"], dam_A=profile["A"], dam_Cr=profile["Cr"], dam_D=profile["D"],
                dam_Z=profile["Z"], dam_Ch=profile["Ch"], dam_prl=profile["prl"], dam_G=profile["G"], dam_O=profile["O"]
            )
            
        scenarios.append({
            "profile": profile["name"],
            "odds": odds
        })
    return scenarios

# ==============================================================================
# BIOLOGICAL HISTORICAL DOCUMENT RETRIEVAL
# ==============================================================================

@st.cache_data
def retrieve_breed_registry_notes(phenotype: str) -> dict:
    """
    Queries breed_registry_notes.json to retrieve historical and biological 
    descriptions/notes associated with alleles identified in the final phenotype.
    
    Parameters:
        phenotype (str): Resolved coat phenotype (e.g., "Silver Bay Dun Frame Overo").
        
    Returns:
        dict: A dictionary containing matched registry rules and historical details.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    notes_path = os.path.join(base_dir, "breed_registry_notes.json")
    if not os.path.exists(notes_path):
        return {}
        
    try:
        with open(notes_path, "r") as f:
            notes = json.load(f)
    except Exception:
        return {}
        
    matched_notes = {}
    p_lower = phenotype.lower()
    
    for key, data in notes.items():
        k_lower = key.lower()
        # Perform matches for specific modifiers
        if k_lower == "grey" and "grey" in p_lower:
            matched_notes[key] = data
        elif k_lower == "silver" and "silver" in p_lower:
            matched_notes[key] = data
        elif k_lower == "cream" and any(w in p_lower for w in ("cream", "cremello", "perlino", "palomino", "buckskin")):
            matched_notes[key] = data
        elif k_lower == "dun" and any(w in p_lower for w in ("dun", "grullo", "dunalino", "dunskin")):
            matched_notes[key] = data
        elif k_lower == "champagne" and "champagne" in p_lower:
            matched_notes[key] = data
        elif k_lower == "pearl" and any(w in p_lower for w in ("pearl", "apricot")):
            matched_notes[key] = data
        elif "lethal" in k_lower and "lethal" in p_lower:
            matched_notes[key] = data
            
    return matched_notes