# mcp_server.py
"""
Equine Genetics Model Context Protocol (MCP) Server
---------------------------------------------------
Exposes deterministic genetics simulation tools and compliance safety resource models.
"""
import os
import sys

# Ensure local imports work correctly under absolute search paths
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp.server.fastmcp import FastMCP
from tools.genetics_engine import calculate_foal_probabilities
from tools.critique_agent import validate_safety_compliance

# Initialize the FastMCP server
mcp = FastMCP("Equine Genetics Server")

@mcp.tool()
def calculate_equine_genetics(
    sire_E: str, sire_A: str, sire_Cr: str, sire_D: str, sire_Z: str, sire_Ch: str, sire_prl: str, sire_G: str, sire_O: str,
    dam_E: str, dam_A: str, dam_Cr: str, dam_D: str, dam_Z: str, dam_Ch: str, dam_prl: str, dam_G: str, dam_O: str
) -> dict:
    """
    Computes offspring coat color probabilities and flags compliance safety audits.
    
    Parameters:
        sire_E (str): Sire extension genotype (EE, Ee, ee).
        sire_A (str): Sire agouti genotype (AA, Aa, aa).
        sire_Cr (str): Sire cream genotype (nn, Crn, CrCr).
        sire_D (str): Sire dun genotype (nn, Dn, DD).
        sire_Z (str): Sire silver genotype (nn, Zn, ZZ).
        sire_Ch (str): Sire champagne genotype (nn, Chn, ChCh).
        sire_prl (str): Sire pearl genotype (nn, prln, prlprl).
        sire_G (str): Sire grey genotype (nn, Gn, GG).
        sire_O (str): Sire overo genotype (nn, On, OO).
        dam_E (str): Dam extension genotype.
        dam_A (str): Dam agouti genotype.
        dam_Cr (str): Dam cream genotype.
        dam_D (str): Dam dun genotype.
        dam_Z (str): Dam silver genotype.
        dam_Ch (str): Dam champagne genotype.
        dam_prl (str): Dam pearl genotype.
        dam_G (str): Dam grey genotype.
        dam_O (str): Dam overo genotype.
        
    Returns:
        dict: Computed probability distribution and safety warnings.
    """
    try:
        results = calculate_foal_probabilities(
            sire_E=sire_E, sire_A=sire_A, sire_Cr=sire_Cr, sire_D=sire_D,
            sire_Z=sire_Z, sire_Ch=sire_Ch, sire_prl=sire_prl, sire_G=sire_G, sire_O=sire_O,
            dam_E=dam_E, dam_A=dam_A, dam_Cr=dam_Cr, dam_D=dam_D,
            dam_Z=dam_Z, dam_Ch=dam_Ch, dam_prl=dam_prl, dam_G=dam_G, dam_O=dam_O
        )
        safety_audit = validate_safety_compliance(results)
        return {
            "probabilities": results,
            "safety_audit": safety_audit
        }
    except Exception as e:
        return {"error": f"Failed to compute genetics: {str(e)}"}

@mcp.resource("equine://standards/lethal-white")
def get_lethal_white_standards() -> str:
    """
    Returns the veterinary compliance rules for Lethal White Syndrome (LWS) safety standards.
    """
    try:
        # Evaluate standard compliance parameters for an LWS cross
        audit = validate_safety_compliance({"Lethal White Syndrome (Fatal)": "100.0%"})
        return audit["message"]
    except Exception as e:
        return f"Error retrieving safety standards: {str(e)}"

if __name__ == "__main__":
    mcp.run()
