# tools/critique_agent.py
"""
Critique Agent Module
---------------------
Responsible for compliance auditing, safety validation, and flagging hazardous
genetic combinations (e.g., Lethal White Syndrome) within calculated offspring scenarios.
"""

def validate_safety_compliance(probabilities: dict) -> dict:
    """
    Audits the calculated offspring genetic probability distribution to detect lethal genotypes.
    
    Parameters:
        probabilities (dict): A dictionary mapping phenotypes/outcomes (str) to their 
                              percentage probabilities (str, e.g., "25.0%").
                              
    Returns:
        dict: A compliance audit dictionary containing:
              - "compliant" (bool): True if safe, False if a lethal cross is identified.
              - "alert_level" (str): "GREEN" (safe) or "HIGH-PRIORITY" (warning).
              - "message" (str): Human-readable audit findings and veterinary context.
    """
    lethal_key = "Lethal White Syndrome (Fatal)"
    
    # Check if Lethal White Syndrome has a probability greater than 0%
    if lethal_key in probabilities:
        prob_str = probabilities[lethal_key]
        prob_val = float(prob_str.replace("%", ""))
        if prob_val > 0:
            # Breed registry rules strongly penalize mating two Overo (On) carriers
            return {
                "compliant": False,
                "alert_level": "HIGH-PRIORITY",
                "message": (
                    f"⚠️ CRITICAL BREEDING WARNING: This cross has a {prob_str} probability of producing "
                    "Lethal White Syndrome (LWS). Mating two Frame Overo (On) carriers leads to ileocolonic aganglionosis, "
                    "a fatal defect where the foal's intestinal tract fails to develop. This breeding is "
                    "highly discouraged by veterinary authorities and major breed registries. DO NOT BREED."
                )
            }
            
    return {
        "compliant": True,
        "alert_level": "GREEN",
        "message": "Compliance Verification: Passed. No lethal genetic crosses detected."
    }


def validate_scenarios_compliance(scenarios: list) -> list:
    """
    Audits a list of baseline trajectory scenarios when one parent is unknown.
    Appends safety compliance reviews to each calculated outcome trajectory.
    
    Parameters:
        scenarios (list): A list of dictionaries containing scenario profiles and computed odds.
        
    Returns:
        list: Audited scenarios containing detailed safety validation profiles.
    """
    audited = []
    for s in scenarios:
        # Run safety audits for every scenario path
        safety_audit = validate_safety_compliance(s["odds"])
        audited.append({
            "profile": s["profile"],
            "odds": s["odds"],
            "safety": safety_audit
        })
    return audited
