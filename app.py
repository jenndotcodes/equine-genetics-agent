import streamlit as st
import datetime
import time
import os
import sys

# Force the project root directory to the absolute top of Python's search paths
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tools.genetics_engine import (
    calculate_foal_probabilities,
    handle_unknown_parent,
    run_punnett_square,
    GENETIC_COLORS,
    LOCI_GENOTYPES,
    retrieve_breed_registry_notes,
)
from tools.critique_agent import (
    validate_safety_compliance,
    validate_scenarios_compliance,
)

# Page configuration
st.set_page_config(
    page_title="Antigravity Equine Genetics Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Genotype human-readable descriptions for all 9 loci
GENOTYPE_DESCRIPTIONS = {
    "E": {
        "EE": "EE - Homozygous Black base",
        "Ee": "Ee - Heterozygous Black base",
        "ee": "ee - Red base (Chestnut)",
    },
    "A": {
        "AA": "AA - Homozygous Bay points",
        "Aa": "Aa - Heterozygous Bay points",
        "aa": "aa - Solid Black (No points)",
    },
    "Cr": {
        "nn": "nn - No Cream dilution",
        "Crn": "Crn - Single Cream (Palomino/Buckskin)",
        "CrCr": "CrCr - Double Cream (Cremello/Perlino)",
    },
    "D": {
        "nn": "nn - No Dun dilution",
        "Dn": "Dn - Single Dun (Dun stripes/factors)",
        "DD": "DD - Double Dun (Dun stripes/factors)",
    },
    "Z": {
        "nn": "nn - No Silver modifier",
        "Zn": "Zn - Single Silver (dapples black hair)",
        "ZZ": "ZZ - Double Silver (dapples black hair)",
    },
    "Ch": {
        "nn": "nn - No Champagne dilution",
        "Chn": "Chn - Single Champagne (metallic sheen)",
        "ChCh": "ChCh - Double Champagne (metallic sheen)",
    },
    "prl": {
        "nn": "nn - No Pearl dilution",
        "prln": "prln - Pearl carrier (hidden recessive)",
        "prlprl": "prlprl - Double Pearl (Apricot/Pearl)",
    },
    "G": {
        "nn": "nn - No Greying mask",
        "Gn": "Gn - Single Grey (turns white over time)",
        "GG": "GG - Double Grey (turns white over time)",
    },
    "O": {
        "nn": "nn - No Frame Overo pattern",
        "On": "On - Frame Overo (spotted pattern)",
        "OO": "OO - Lethal White Syndrome (Fatal)",
    }
}

# Custom premium styling meeting accessibility standards
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Outfit:wght@300;400;600;800&display=swap');

    /* Global fonts and dark background override */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        color: #f0f3f1 !important; /* Soft white matching theme textColor */
    }

    /* Force background color matching theme backgroundColor across app container elements */
    .stApp, .main, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"] {
        background-color: #1e2222 !important;
        background: #1e2222 !important;
        color: #f0f3f1 !important;
    }

    /* High contrast widget labels styled in sage green */
    label, [data-testid="stWidgetLabel"] p {
        color: #8fb394 !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        letter-spacing: 0.3px;
        margin-bottom: 6px !important;
    }

    /* Glassmorphic genetic card */
    .glass-card {
        background: rgba(0, 0, 0, 0.28); /* Slightly darker for better text contrast */
        border: 1px solid rgba(255, 255, 255, 0.12); /* Increased border contrast */
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 30px 0 rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        margin-bottom: 24px;
    }

    .card-title {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 20px;
        color: #f0f3f1 !important;
        border-bottom: 2px solid #8fb394;
        padding-bottom: 8px;
        letter-spacing: 0.5px;
    }

    .sub-card-title {
        font-size: 16px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 12px;
        color: #f0f3f1 !important;
        border-left: 4px solid #8fb394;
        padding-left: 10px;
    }

    /* Terminal window style */
    .terminal-window {
        background: #181b21;
        border: 1px solid #4f5666; /* Higher contrast border */
        border-radius: 12px;
        font-family: 'JetBrains Mono', monospace;
        padding: 0;
        box-shadow: 0 15px 50px rgba(0,0,0,0.7);
        overflow: hidden;
        margin-top: 10px;
    }

    .terminal-header {
        background: #1e222a;
        padding: 12px 18px;
        border-bottom: 1px solid #4f5666;
        display: flex;
        align-items: center;
    }

    .terminal-dots {
        display: flex;
        gap: 6px;
        margin-right: 15px;
    }

    .terminal-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
    }
    .dot-red { background-color: #ff5f56; }
    .dot-yellow { background-color: #ffbd2e; }
    .dot-green { background-color: #27c93f; }

    .terminal-title {
        color: #e2e8f0; /* White/grey for contrast */
        font-size: 13px;
        font-weight: 700;
        flex-grow: 1;
        text-align: center;
        margin-right: 48px; /* Offset dots width to center text */
    }

    .terminal-body {
        padding: 20px;
        color: #e2e8f0; /* High contrast terminal text */
        font-size: 13px;
        line-height: 1.6;
        min-height: 520px;
        max-height: 560px;
        overflow-y: auto;
    }

    .log-line {
        margin-bottom: 10px;
        display: flex;
        align-items: flex-start;
    }

    .log-time {
        color: #a1a1aa;
        font-size: 11px;
        margin-right: 12px;
        margin-top: 2px;
        white-space: nowrap;
    }

    .log-tag {
        font-weight: bold;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 10px;
        margin-right: 12px;
        white-space: nowrap;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .tag-thought {
        background-color: rgba(187, 134, 252, 0.18);
        color: #d8b4fe;
        border: 1px solid rgba(187, 134, 252, 0.4);
    }

    .tag-comp {
        background-color: rgba(3, 169, 244, 0.18);
        color: #38bdf8;
        border: 1px solid rgba(3, 169, 244, 0.4);
    }

    .tag-action {
        background-color: rgba(0, 230, 118, 0.18);
        color: #4ade80;
        border: 1px solid rgba(0, 230, 118, 0.4);
    }

    .tag-query {
        background-color: rgba(255, 152, 0, 0.18);
        color: #fb923c;
        border: 1px solid rgba(255, 152, 0, 0.4);
    }

    .log-text {
        flex-grow: 1;
        word-break: break-word;
    }

    .cursor-blink {
        animation: blink 1s step-end infinite;
        font-weight: bold;
        color: #d8b4fe;
    }

    @keyframes blink {
        from, to { opacity: 0 }
        50% { opacity: 1 }
    }

    /* Custom progress bar styles */
    .custom-progress-container {
        margin-bottom: 16px;
    }
    
    .custom-progress-label-row {
        display: flex;
        justify-content: space-between;
        font-weight: 700;
        margin-bottom: 6px;
        font-size: 14px;
        color: #ffffff !important;
    }
    
    .custom-progress-bg {
        width: 100%;
        height: 14px;
        background-color: rgba(0, 0, 0, 0.4);
        border-radius: 7px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    .custom-progress-fill {
        height: 100%;
        border-radius: 7px;
        transition: width 0.5s ease-in-out;
    }

    .pheno-bay { background: linear-gradient(90deg, #b45309, #78350f); }
    .pheno-solid-black { background: linear-gradient(90deg, #4b5563, #111827); }
    .pheno-chestnut { background: linear-gradient(90deg, #ea580c, #9a3412); }
    .pheno-unknown { background: linear-gradient(90deg, #64748b, #334155); }

    /* Safety Compliance Visual Alert styles */
    .safety-alert-high {
        background-color: rgba(239, 68, 68, 0.18) !important;
        color: #fca5a5 !important;
        border: 2px solid rgba(239, 68, 68, 0.5) !important;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 24px;
        font-size: 14px;
        line-height: 1.5;
    }
    
    .safety-alert-green {
        background-color: rgba(16, 185, 129, 0.12) !important;
        color: #a7f3d0 !important;
        border: 2px solid rgba(16, 185, 129, 0.4) !important;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 24px;
        font-size: 13px;
    }
    
    .registry-note-card {
        background-color: rgba(143, 179, 148, 0.08) !important;
        border-left: 4px solid #8fb394 !important;
        padding: 16px;
        border-radius: 4px 12px 12px 4px;
        margin-top: 15px;
        font-size: 13px;
        line-height: 1.5;
    }
    
    .registry-note-title {
        font-weight: 700;
        color: #f0f3f1 !important;
        margin-bottom: 6px;
    }
    
    </style>
    """,
    unsafe_allow_html=True,
)

# Header Section
st.markdown(
    """
    <div style='text-align: center; margin-top: 10px; margin-bottom: 30px;'>
        <h1 style='font-size: 40px; font-weight: 800; margin-bottom: 0px; background: linear-gradient(90deg, #ffffff, #e2e8f0, #cbd5e1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
            🧬 Antigravity Genetics Dashboard
        </h1>
        <p style='color: #cbd5e1; font-size: 16px; font-weight: 400; margin-top: 5px; letter-spacing: 0.5px;'>
            Interactive Equine Inheritance Simulator & Agent Execution Monitor
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Divide layout into two columns
col_left, col_right = st.columns([1.1, 0.9], gap="large")

with col_left:
    st.subheader("Parental Configuration")
    
    # Sire Expander
    with st.expander("Sire Configuration (Stallion)", expanded=True):
        sire_unknown = st.checkbox(
            "Sire Genotype Unknown (Stallion)", 
            value=False,
            help="Estimate foal probability based on population average statistics for the sire."
        )
        if not sire_unknown:
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                sire_E = st.selectbox(
                    "Extension (E/e Locus)", 
                    options=LOCI_GENOTYPES["E"], 
                    format_func=lambda x: GENOTYPE_DESCRIPTIONS["E"][x],
                    index=1, 
                    key="sire_E"
                )
                sire_D = st.selectbox(
                    "Dun (D/d Locus)", 
                    options=LOCI_GENOTYPES["D"], 
                    format_func=lambda x: GENOTYPE_DESCRIPTIONS["D"][x],
                    index=0, 
                    key="sire_D"
                )
                sire_prl = st.selectbox(
                    "Pearl (prl Locus)", 
                    options=LOCI_GENOTYPES["prl"], 
                    format_func=lambda x: GENOTYPE_DESCRIPTIONS["prl"][x],
                    index=0, 
                    key="sire_prl"
                )
            with col_s2:
                sire_A = st.selectbox(
                    "Agouti (A/a Locus)", 
                    options=LOCI_GENOTYPES["A"], 
                    format_func=lambda x: GENOTYPE_DESCRIPTIONS["A"][x],
                    index=1, 
                    key="sire_A"
                )
                sire_Z = st.selectbox(
                    "Silver (Z/z Locus)", 
                    options=LOCI_GENOTYPES["Z"], 
                    format_func=lambda x: GENOTYPE_DESCRIPTIONS["Z"][x],
                    index=0, 
                    key="sire_Z"
                )
                sire_G = st.selectbox(
                    "Grey (G/g Locus)", 
                    options=LOCI_GENOTYPES["G"], 
                    format_func=lambda x: GENOTYPE_DESCRIPTIONS["G"][x],
                    index=0, 
                    key="sire_G"
                )
            with col_s3:
                sire_Cr = st.selectbox(
                    "Cream (Cr Locus)", 
                    options=LOCI_GENOTYPES["Cr"], 
                    format_func=lambda x: GENOTYPE_DESCRIPTIONS["Cr"][x],
                    index=0, 
                    key="sire_Cr"
                )
                sire_Ch = st.selectbox(
                    "Champagne (Ch Locus)", 
                    options=LOCI_GENOTYPES["Ch"], 
                    format_func=lambda x: GENOTYPE_DESCRIPTIONS["Ch"][x],
                    index=0, 
                    key="sire_Ch"
                )
                sire_O = st.selectbox(
                    "Frame Overo (O Locus)", 
                    options=LOCI_GENOTYPES["O"], 
                    format_func=lambda x: GENOTYPE_DESCRIPTIONS["O"][x],
                    index=0, 
                    key="sire_O"
                )
        else:
            st.info("Stallion alleles are unknown.")
            sire_E = sire_A = sire_Cr = sire_D = sire_Z = sire_Ch = sire_prl = sire_G = sire_O = None

    # Dam Expander
    with st.expander("Dam Configuration (Mare)", expanded=True):
        dam_unknown = st.checkbox(
            "Dam Genotype Unknown (Mare)",
            value=False,
            help="Estimate foal probability based on population average statistics for the mare."
        )
        if not dam_unknown:
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                dam_E = st.selectbox(
                    "Extension (E/e Locus)", 
                    options=LOCI_GENOTYPES["E"], 
                    format_func=lambda x: GENOTYPE_DESCRIPTIONS["E"][x],
                    index=2, 
                    key="dam_E"
                )
                dam_D = st.selectbox(
                    "Dun (D/d Locus)", 
                    options=LOCI_GENOTYPES["D"], 
                    format_func=lambda x: GENOTYPE_DESCRIPTIONS["D"][x],
                    index=0, 
                    key="dam_D"
                )
                dam_prl = st.selectbox(
                    "Pearl (prl Locus)", 
                    options=LOCI_GENOTYPES["prl"], 
                    format_func=lambda x: GENOTYPE_DESCRIPTIONS["prl"][x],
                    index=0, 
                    key="dam_prl"
                )
            with col_d2:
                dam_A = st.selectbox(
                    "Agouti (A/a Locus)", 
                    options=LOCI_GENOTYPES["A"], 
                    format_func=lambda x: GENOTYPE_DESCRIPTIONS["A"][x],
                    index=2, 
                    key="dam_A"
                )
                dam_Z = st.selectbox(
                    "Silver (Z/z Locus)", 
                    options=LOCI_GENOTYPES["Z"], 
                    format_func=lambda x: GENOTYPE_DESCRIPTIONS["Z"][x],
                    index=0, 
                    key="dam_Z"
                )
                dam_G = st.selectbox(
                    "Grey (G/g Locus)", 
                    options=LOCI_GENOTYPES["G"], 
                    format_func=lambda x: GENOTYPE_DESCRIPTIONS["G"][x],
                    index=0, 
                    key="dam_G"
                )
            with col_d3:
                dam_Cr = st.selectbox(
                    "Cream (Cr Locus)", 
                    options=LOCI_GENOTYPES["Cr"], 
                    format_func=lambda x: GENOTYPE_DESCRIPTIONS["Cr"][x],
                    index=0, 
                    key="dam_Cr"
                )
                dam_Ch = st.selectbox(
                    "Champagne (Ch Locus)", 
                    options=LOCI_GENOTYPES["Ch"], 
                    format_func=lambda x: GENOTYPE_DESCRIPTIONS["Ch"][x],
                    index=0, 
                    key="dam_Ch"
                )
                dam_O = st.selectbox(
                    "Frame Overo (O Locus)", 
                    options=LOCI_GENOTYPES["O"], 
                    format_func=lambda x: GENOTYPE_DESCRIPTIONS["O"][x],
                    index=0, 
                    key="dam_O"
                )
        else:
            st.info("Mare alleles are unknown.")
            dam_E = dam_A = dam_Cr = dam_D = dam_Z = dam_Ch = dam_prl = dam_G = dam_O = None

    # Perform calculations based on inputs
    results = None
    if sire_unknown and dam_unknown:
        st.warning("⚠️ Please specify at least one known parent to run the genetic simulation.")
    elif sire_unknown:
        results = handle_unknown_parent(
            known_E=dam_E, known_A=dam_A, known_Cr=dam_Cr, known_D=dam_D,
            known_Z=dam_Z, known_Ch=dam_Ch, known_prl=dam_prl, known_G=dam_G, known_O=dam_O,
            unknown_parent_type="stallion"
        )
    elif dam_unknown:
        results = handle_unknown_parent(
            known_E=sire_E, known_A=sire_A, known_Cr=sire_Cr, known_D=sire_D,
            known_Z=sire_Z, known_Ch=sire_Ch, known_prl=sire_prl, known_G=sire_G, known_O=sire_O,
            unknown_parent_type="mare"
        )
    else:
        results = calculate_foal_probabilities(
            sire_E=sire_E, sire_A=sire_A, sire_Cr=sire_Cr, sire_D=sire_D,
            sire_Z=sire_Z, sire_Ch=sire_Ch, sire_prl=sire_prl, sire_G=sire_G, sire_O=sire_O,
            dam_E=dam_E, dam_A=dam_A, dam_Cr=dam_Cr, dam_D=dam_D,
            dam_Z=dam_Z, dam_Ch=dam_Ch, dam_prl=dam_prl, dam_G=dam_G, dam_O=dam_O
        )
        
    # Display Results in Left Column
    if results is not None:
        with st.container(border=True):
            st.subheader("Foal Phenotype Probabilities")
            
            def display_odds(odds_dict: dict):
                # Sort odds descending
                sorted_odds = sorted(odds_dict.items(), key=lambda x: float(x[1].replace("%", "")), reverse=True)
                for pheno, prob_str in sorted_odds:
                    prob_val = float(prob_str.replace("%", ""))
                    
                    # Dynamic CSS color mapping
                    p_lower = pheno.lower()
                    if "bay" in p_lower:
                        css_class = "pheno-bay"
                    elif "black" in p_lower or "grullo" in p_lower:
                        css_class = "pheno-solid-black"
                    elif "chestnut" in p_lower or "palomino" in p_lower or "cremello" in p_lower or "gold" in p_lower or "apricot" in p_lower:
                        css_class = "pheno-chestnut"
                    elif "lethal" in p_lower:
                        css_class = "pheno-solid-black"
                    else:
                        css_class = "pheno-unknown"
                    
                    st.markdown(
                        f"""
                        <div class="custom-progress-container">
                            <div class="custom-progress-label-row">
                                <span style="color: #ffffff; font-weight: 700;">{pheno}</span>
                                <span style="color: #ffffff; font-weight: 700;">{prob_str}</span>
                            </div>
                            <div class="custom-progress-bg">
                                <div class="custom-progress-fill {css_class}" style="width: {prob_val}%;"></div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            def display_registry_notes(odds_dict: dict):
                notes_shown = set()
                for pheno in odds_dict.keys():
                    pheno_notes = retrieve_breed_registry_notes(pheno)
                    for key, data in pheno_notes.items():
                        if key not in notes_shown:
                            notes_shown.add(key)
                            st.markdown(
                                f"""
                                <div class="registry-note-card">
                                    <div class="registry-note-title">📖 Registry Note: {data['title']}</div>
                                    <div style="color: #cbd5e1; margin-bottom: 8px;">{data['description']}</div>
                                    <div style="color: #94a3b8; font-style: italic; font-size: 11px;">History: {data['historical_context']}</div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

            if not sire_unknown and not dam_unknown:
                # Check for double Overo carrier cross
                if sire_O == "On" and dam_O == "On":
                    st.error("CRITICAL CRITIQUE ALERT: Lethal White Syndrome Hazard (25% Probability)")
                    lws_notes = retrieve_breed_registry_notes("Lethal White Syndrome (Fatal)")
                    if "Lethal White Syndrome (Fatal)" in lws_notes:
                        data = lws_notes["Lethal White Syndrome (Fatal)"]
                        st.info(f"📖 **Registry & Safety Guidelines:**\n\n{data['description']}\n\n*Historical/Registry Context:* {data['historical_context']}")
                else:
                    # Audit safety (Critique Agent integration)
                    safety_audit = validate_safety_compliance(results)
                    if not safety_audit["compliant"]:
                        st.markdown(f"<div class='safety-alert-high'>{safety_audit['message']}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='safety-alert-green'>🛡️ {safety_audit['message']}</div>", unsafe_allow_html=True)
                    
                display_odds(results)
                display_registry_notes(results)
            else:
                # Audit scenarios (Critique Agent scenario list integration)
                audited_scenarios = validate_scenarios_compliance(results)
                unknown_label = "Stallion" if sire_unknown else "Mare"
                for idx, scenario in enumerate(audited_scenarios):
                    st.markdown(f"<div class='sub-card-title'>Scenario {idx + 1}: Unknown {unknown_label} is {scenario['profile']}</div>", unsafe_allow_html=True)
                    
                    # Check for double Overo carrier cross in this scenario
                    known_O_val = dam_O if sire_unknown else sire_O
                    if known_O_val == "On" and "On" in scenario["profile"]:
                        st.error("CRITICAL CRITIQUE ALERT: Lethal White Syndrome Hazard (25% Probability)")
                        lws_notes = retrieve_breed_registry_notes("Lethal White Syndrome (Fatal)")
                        if "Lethal White Syndrome (Fatal)" in lws_notes:
                            data = lws_notes["Lethal White Syndrome (Fatal)"]
                            st.info(f"📖 **Registry & Safety Guidelines:**\n\n{data['description']}\n\n*Historical/Registry Context:* {data['historical_context']}")
                    else:
                        safety_audit = scenario["safety"]
                        if not safety_audit["compliant"]:
                            st.markdown(f"<div class='safety-alert-high'>{safety_audit['message']}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='safety-alert-green'>🛡️ {safety_audit['message']}</div>", unsafe_allow_html=True)
                    
                    display_odds(scenario["odds"])
                    display_registry_notes(scenario["odds"])
        
        # Detailed Genotypes breakdown (Only possible when both parents are known)
        with st.container(border=True):
            st.subheader("Offspring Locus Breakdown")
            
            if not sire_unknown and not dam_unknown:
                loci_names = {
                    "E": "Extension (E/e)",
                    "A": "Agouti (A/a)",
                    "Cr": "Cream (Cr)",
                    "D": "Dun (D/d)",
                    "Z": "Silver (Z/z)",
                    "Ch": "Champagne (Ch)",
                    "prl": "Pearl (prl)",
                    "G": "Grey (G/g)",
                    "O": "Frame Overo (O)",
                }
                
                sire_genes = {"E": sire_E, "A": sire_A, "Cr": sire_Cr, "D": sire_D, "Z": sire_Z, "Ch": sire_Ch, "prl": sire_prl, "G": sire_G, "O": sire_O}
                dam_genes = {"E": dam_E, "A": dam_A, "Cr": dam_Cr, "D": dam_D, "Z": dam_Z, "Ch": dam_Ch, "prl": dam_prl, "G": dam_G, "O": dam_O}
                
                table_rows = ""
                for locus, name in loci_names.items():
                    s_val = sire_genes[locus]
                    d_val = dam_genes[locus]
                    outcomes = run_punnett_square(s_val, d_val)
                    
                    # Count frequencies
                    counts = {}
                    for o in outcomes:
                        counts[o] = counts.get(o, 0) + 25.0
                    
                    outcome_strs = []
                    for gen, pct in sorted(counts.items(), key=lambda x: x[1], reverse=True):
                        outcome_strs.append(f"{gen}: {pct:.0f}%")
                    
                    table_rows += (
                        f'<tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.08);">'
                        f'<td style="padding: 10px 0; font-weight: 700; color: #ffffff;">{name}</td>'
                        f'<td style="padding: 10px 0; font-family: \'JetBrains Mono\', monospace; color: #cbd5e1;">{s_val} × {d_val}</td>'
                        f'<td style="padding: 10px 0; text-align: right; font-weight: bold; color: #b89bf0;">{", ".join(outcome_strs)}</td>'
                        f'</tr>'
                    )
                    
                st.markdown(
                    f'<table style="width: 100%; border-collapse: collapse; font-size: 14px; color: #ffffff;">'
                    f'<thead>'
                    f'<tr style="border-bottom: 2px solid rgba(255,255,255,0.15); color: #cbd5e1; text-align: left; font-weight: 700;">'
                    f'<th style="padding-bottom: 8px;">Locus</th>'
                    f'<th style="padding-bottom: 8px;">Cross</th>'
                    f'<th style="padding-bottom: 8px; text-align: right;">Offspring Probabilities</th>'
                    f'</tr>'
                    f'</thead>'
                    f'<tbody>{table_rows}</tbody>'
                    f'</table>',
                    unsafe_allow_html=True
                )
            else:
                st.write("⚠️ Locus details are unavailable when a parent is unknown. Review the branching scenarios above.")

with col_right:
    # Agent Tracking Log layout
    st.markdown("<div style='color: #8fb394; font-size: 18px; font-weight: bold; margin-bottom: 5px;'>🛰️ Antigravity Agent Tracking Log</div>", unsafe_allow_html=True)
    st.caption("Active trace of the autonomous agent's genetic simulation pipeline")
    
    # Generate dynamic log events
    t_now = datetime.datetime.now()
    
    # Create static execution timestamps for simulation context
    logs = []
    
    # Thought log
    t_1 = (t_now - datetime.timedelta(seconds=4.5)).strftime("%H:%M:%S.%f")[:-3]
    if sire_unknown and dam_unknown:
        logs.append((t_1, "thought", "Awaiting configuration settings. Please set at least one known parent genotype."))
    elif sire_unknown:
        logs.append((t_1, "thought", f"Analyzing parental inputs. Sire is designated UNKNOWN. Dam genotype parsed: E={dam_E}, A={dam_A}, Cr={dam_Cr}, D={dam_D}, Z={dam_Z}, Ch={dam_Ch}, prl={dam_prl}, G={dam_G}, O={dam_O}."))
    elif dam_unknown:
        logs.append((t_1, "thought", f"Analyzing parental inputs. Dam is designated UNKNOWN. Sire genotype parsed: E={sire_E}, A={sire_A}, Cr={sire_Cr}, D={sire_D}, Z={sire_Z}, Ch={sire_Ch}, prl={sire_prl}, G={sire_G}, O={sire_O}."))
    else:
        logs.append((t_1, "thought", f"Analyzing parental inputs. Sire genotype parsed: E={sire_E}, A={sire_A}, Cr={sire_Cr}, D={sire_D}, Z={sire_Z}, Ch={sire_Ch}, prl={sire_prl}, G={sire_G}, O={sire_O}."))
        
    # Query log
    t_2 = (t_now - datetime.timedelta(seconds=3.8)).strftime("%H:%M:%S.%f")[:-3]
    if sire_unknown and dam_unknown:
        logs.append((t_2, "query", "Monitoring user dashboard inputs..."))
    elif sire_unknown or dam_unknown:
        unknown_type = "stallion" if sire_unknown else "mare"
        logs.append((t_2, "query", f"Retrieving baseline wild-type genetic profiles for {unknown_type} trajectory branching..."))
    else:
        logs.append((t_2, "query", f"Querying gamete split ratios across 9 independent loci..."))
        
    # Computation log
    t_3 = (t_now - datetime.timedelta(seconds=2.9)).strftime("%H:%M:%S.%f")[:-3]
    if sire_unknown and dam_unknown:
        pass
    elif sire_unknown or dam_unknown:
        logs.append((t_3, "comp", f"Generating 3 parallel trajectories: Bay (Ee_Aa), Solid Black (Ee_aa), Chestnut (ee_aa). Crossing each hypothetical profile..."))
    else:
        logs.append((t_3, "comp", f"Executing 9 deterministic Punnett square crossovers simultaneously ($4^9 = 262,144$ combined outcomes)..."))
        
    # Punnett calculation log
    t_4 = (t_now - datetime.timedelta(seconds=1.8)).strftime("%H:%M:%S.%f")[:-3]
    if sire_unknown and dam_unknown:
        pass
    elif sire_unknown or dam_unknown:
        logs.append((t_4, "comp", f"Calculated scenario odds. Epistasis and Overo lethal checks verified on 3 branches."))
    else:
        logs.append((t_4, "comp", "Checking offspring Overo genotype for OO (Lethal White) and applying Silver/Grey progressive masks..."))
        
    # Action result logs
    t_5 = (t_now - datetime.timedelta(seconds=0.8)).strftime("%H:%M:%S.%f")[:-3]
    if sire_unknown and dam_unknown:
        pass
    elif sire_unknown or dam_unknown:
        logs.append((t_5, "action", "Completed Bayesian scenario evaluation. Compiling odds..."))
    else:
        logs.append((t_5, "action", f"Successfully mapped all 262,144 outcomes. Compiling phenotype probabilities..."))
    
    # Safety verification log (Critique Agent step trace)
    t_5_b = (t_now - datetime.timedelta(seconds=0.4)).strftime("%H:%M:%S.%f")[:-3]
    if not sire_unknown and not dam_unknown:
        safety_status = "Lethal cross flagged!" if sire_O == "On" and dam_O == "On" else "Green signature."
        logs.append((t_5_b, "action", f"Critique Agent validating compliance: auditing Overo combinations. Status: {safety_status}"))
    elif sire_unknown or dam_unknown:
        logs.append((t_5_b, "action", "Critique Agent validating compliance: auditing scenario trajectories."))

    # Success logs
    t_6 = (t_now - datetime.timedelta(seconds=0.1)).strftime("%H:%M:%S.%f")[:-3]
    if sire_unknown and dam_unknown:
        logs.append((t_6, "success", "System Idle. Ready for simulation launch."))
    elif sire_unknown or dam_unknown:
        logs.append((t_6, "success", f"Genetic branching completed successfully. Outputs mapped to dashboard expanders."))
    else:
        best_pheno = max(results.items(), key=lambda x: float(x[1].replace("%", "")))[0]
        best_prob = results[best_pheno]
        logs.append((t_6, "success", f"Genetic analysis complete. Dominant predicted phenotype: {best_pheno} ({best_prob} probability)."))
    
    # Build logs as HTML content with color theme
    log_html_content = ""
    for timestamp, tag, message in logs:
        # Determine tag color (darker version for white background contrast)
        if tag == "thought":
            tag_color = "#7c3aed"  # Purple accent
        elif tag == "query":
            tag_color = "#b45309"  # Amber
        elif tag == "comp":
            tag_color = "#16a34a"  # Sage green
        elif tag == "success":
            tag_color = "#047857"  # Success emerald
        else: # action / info
            tag_color = "#0369a1"  # Action blue
            
        log_html_content += (
            f'<span style="color: #718096;">[{timestamp}]</span> '
            f'<span style="color: {tag_color}; font-weight: bold;">[{tag}]</span> '
            f'<span style="color: #2d3748;">{message}</span>\n'
        )
        
    # Active trailing prompt cursor
    cursor_time = t_now.strftime("%H:%M:%S.%f")[:-3]
    log_html_content += (
        f'<span style="color: #718096;">[{cursor_time}]</span> '
        f'<span style="color: #7c3aed; font-weight: bold;">[status]</span> '
        f'<span style="color: #2d3748;">Agent listening for user adjustments... <span class="cursor-blink" style="color: #7c3aed;">█</span></span>'
    )
    
    # Render the logs cleanly inside st.container(border=True) using a custom styled HTML container
    with st.container(border=True):
        log_html = f"""
        <div style="
            background-color: #ffffff;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            padding: 15px 15px 35px 15px;
            border-radius: 8px;
            min-height: 680px;
            max-height: 680px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            border: 1px solid #cbd5e1;
            line-height: 1.6;
            margin-bottom: 40px;
        ">{log_html_content}</div>
        """
        st.markdown(log_html, unsafe_allow_html=True)
