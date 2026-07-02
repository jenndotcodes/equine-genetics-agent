# Skill: Equine Coat Color Genetics Engine

## Description
A specialized biological calculation engine that computes deterministic foal coat color probabilities using multi-gene Punnett square matrices. This skill converts informal parent descriptions into exact mathematical inheritance percentages and handles incomplete records.

## Manifest
```json
{
  "name": "equine_genetics",
  "version": "3.0.0",
  "tools": [
    {
      "name": "calculate_foal_probabilities",
      "description": "Calculates the exact percentage odds of a foal's coat color when both parents' genotypes are known across 9 loci.",
      "parameters": {
        "type": "object",
        "properties": {
          "sire_E": { "type": "string", "description": "Sire Extension gene: 'EE', 'Ee', or 'ee'." },
          "sire_A": { "type": "string", "description": "Sire Agouti gene: 'AA', 'Aa', or 'aa'." },
          "sire_Cr": { "type": "string", "description": "Sire Cream gene: 'nn', 'Crn', or 'CrCr'." },
          "sire_D": { "type": "string", "description": "Sire Dun gene: 'nn', 'Dn', or 'DD'." },
          "sire_Z": { "type": "string", "description": "Sire Silver gene: 'nn', 'Zn', or 'ZZ'." },
          "sire_Ch": { "type": "string", "description": "Sire Champagne gene: 'nn', 'Chn', or 'ChCh'." },
          "sire_prl": { "type": "string", "description": "Sire Pearl gene: 'nn', 'prln', or 'prlprl'." },
          "sire_G": { "type": "string", "description": "Sire Grey gene: 'nn', 'Gn', or 'GG'." },
          "sire_O": { "type": "string", "description": "Sire Frame Overo gene: 'nn', 'On', or 'OO'." },
          "dam_E": { "type": "string", "description": "Dam Extension gene: 'EE', 'Ee', or 'ee'." },
          "dam_A": { "type": "string", "description": "Dam Agouti gene: 'AA', 'Aa', or 'aa'." },
          "dam_Cr": { "type": "string", "description": "Dam Cream gene: 'nn', 'Crn', or 'CrCr'." },
          "dam_D": { "type": "string", "description": "Dam Dun gene: 'nn', 'Dn', or 'DD'." },
          "dam_Z": { "type": "string", "description": "Dam Silver gene: 'nn', 'Zn', or 'ZZ'." },
          "dam_Ch": { "type": "string", "description": "Dam Champagne gene: 'nn', 'Chn', or 'ChCh'." },
          "dam_prl": { "type": "string", "description": "Dam Pearl gene: 'nn', 'prln', or 'prlprl'." },
          "dam_G": { "type": "string", "description": "Dam Grey gene: 'nn', 'Gn', or 'GG'." },
          "dam_O": { "type": "string", "description": "Dam Frame Overo gene: 'nn', 'On', or 'OO'." }
        },
        "required": [
          "sire_E", "sire_A", "sire_Cr", "sire_D", "sire_Z", "sire_Ch", "sire_prl", "sire_G", "sire_O",
          "dam_E", "dam_A", "dam_Cr", "dam_D", "dam_Z", "dam_Ch", "dam_prl", "dam_G", "dam_O"
        ]
      }
    },
    {
      "name": "handle_unknown_parent",
      "description": "Invoked when either the stallion or the mare is marked as unknown. Tracks 3 parallel wild-type trajectories.",
      "parameters": {
        "type": "object",
        "properties": {
          "known_E": { "type": "string", "description": "The known parent's Extension gene." },
          "known_A": { "type": "string", "description": "The known parent's Agouti gene." },
          "known_Cr": { "type": "string", "description": "The known parent's Cream gene." },
          "known_D": { "type": "string", "description": "The known parent's Dun gene." },
          "known_Z": { "type": "string", "description": "The known parent's Silver gene." },
          "known_Ch": { "type": "string", "description": "The known parent's Champagne gene." },
          "known_prl": { "type": "string", "description": "The known parent's Pearl gene." },
          "known_G": { "type": "string", "description": "The known parent's Grey gene." },
          "known_O": { "type": "string", "description": "The known parent's Frame Overo gene." },
          "unknown_parent_type": { "type": "string", "enum": ["stallion", "mare"], "description": "Specifies which parent is missing." }
        },
        "required": [
          "known_E", "known_A", "known_Cr", "known_D", "known_Z", "known_Ch", "known_prl", "known_G", "known_O",
          "unknown_parent_type"
        ]
      }
    }
  ]
}
```

## Instructions

1. When a user asks about horse breeding or coat color projections, look for the genotypes or colors of the Sire and Dam.
2. If both parents are explicitly provided, map their profiles to the correct alleles and invoke `calculate_foal_probabilities`.
3. If the user states that a parent is a mystery, unknown, or has missing papers, immediately invoke `handle_unknown_parent` to map out the baseline trajectories.
4. Always present the calculation output array clearly to the user, and maintain a professional, encouraging tone appropriate for agricultural specialists.