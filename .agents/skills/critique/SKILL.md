# Skill: Critique Agent Safety Validator

## Description
A specialized validation and verification agent that audits the output payloads of genetic crosses. Its sole responsibility is to intercept the calculations from the genetics engine and check for lethal genetic combinations. If it flags a fatal cross—specifically a homozygous Frame Overo (OO) genotype which leads to Lethal White Syndrome (LWS)—it halts standard reporting, raises a high-priority safety warning, and provides compliance advice to prevent this breeding.

## Manifest
```json
{
  "name": "critique_agent",
  "version": "1.0.0",
  "tools": [
    {
      "name": "validate_safety_compliance",
      "description": "Reviews the genetic probability payload. Intercepts and raises a high-priority compliance warning if a lethal cross is detected.",
      "parameters": {
        "type": "object",
        "properties": {
          "probabilities": {
            "type": "object",
            "description": "The phenotype probability mapping (e.g., {'Lethal White Syndrome (Fatal)': '25.0%'})"
          }
        },
        "required": ["probabilities"]
      }
    }
  ]
}
```

## Instructions

1. When receiving the calculated offspring phenotype probability payload, immediately scan the keys for `"Lethal White Syndrome (Fatal)"`.
2. If `"Lethal White Syndrome (Fatal)"` is found and has a probability greater than `0.0%`:
   - Intercept the state and format a **HIGH-PRIORITY SAFETY COMPLIANCE ALERT**.
   - Explain that breeding two Frame Overo carriers (`On` x `On`) results in a 25% chance of LWS, causing severe suffering and death to the foal.
   - Advise the breeder that this specific cross violates veterinary and breed registry safety recommendations and should not be completed.
3. If no lethal cross is detected, return the payload with a green light compliance signature: `"Compliance Verification: Passed"`.
