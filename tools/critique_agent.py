# tools/critique_agent.py

def validate_safety_compliance(probabilities: dict) -> dict:
    """
    Audits the calculated genetic probability payload.
    If Lethal White Syndrome (Fatal) is detected, raises a high-priority safety alert.
    """
    lethal_key = "Lethal White Syndrome (Fatal)"
    
    if lethal_key in probabilities:
        prob_str = probabilities[lethal_key]
        prob_val = float(prob_str.replace("%", ""))
        if prob_val > 0:
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
    Audits a collection of trajectory scenarios, adding safety validation to each.
    """
    audited = []
    for s in scenarios:
        safety_audit = validate_safety_compliance(s["odds"])
        audited.append({
            "profile": s["profile"],
            "odds": s["odds"],
            "safety": safety_audit
        })
    return audited
