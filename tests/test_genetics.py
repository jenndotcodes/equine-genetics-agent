# tests/test_genetics.py
import pytest
from tools.genetics_engine import (
    split_genotype,
    sort_alleles,
    run_punnett_square,
    get_phenotype,
)
from tools.critique_agent import validate_safety_compliance

def test_split_genotype():
    # Test multi-character genotypes
    assert split_genotype("CrCr") == ("Cr", "Cr")
    assert split_genotype("Crn") == ("Cr", "n")
    assert split_genotype("prln") == ("prl", "n")
    # Test standard single/double character genotypes
    assert split_genotype("Ee") == ("E", "e")
    assert split_genotype("ee") == ("e", "e")
    assert split_genotype("nn") == ("n", "n")

def test_sort_alleles():
    # Dominant alleles first
    assert sort_alleles("e", "E") == ["E", "e"]
    assert sort_alleles("n", "Cr") == ["Cr", "n"]
    assert sort_alleles("a", "A") == ["A", "a"]
    # Reversal checks
    assert sort_alleles("E", "e") == ["E", "e"]
    assert sort_alleles("Cr", "n") == ["Cr", "n"]

def test_run_punnett_square():
    # Ee x Ee heterozygous cross should yield 4 combinations
    res1 = run_punnett_square("Ee", "Ee")
    assert len(res1) == 4
    assert sorted(res1) == ["EE", "Ee", "Ee", "ee"]

    # EE x ee homozygous cross should yield all Ee
    res2 = run_punnett_square("EE", "ee")
    assert res2 == ["Ee", "Ee", "Ee", "Ee"]

def test_get_phenotype():
    # Solid black base (EE, aa, and no dilutions/modifiers)
    assert get_phenotype({
        "E": "EE", "A": "aa", "Cr": "nn", "D": "nn", "Z": "nn", "Ch": "nn", "prl": "nn", "G": "nn", "O": "nn"
    }) == "Solid Black"

    # Bay base (Ee, Aa, no dilutions)
    assert get_phenotype({
        "E": "Ee", "A": "Aa", "Cr": "nn", "D": "nn", "Z": "nn", "Ch": "nn", "prl": "nn", "G": "nn", "O": "nn"
    }) == "Bay"

    # Chestnut base (ee, aa, no dilutions)
    assert get_phenotype({
        "E": "ee", "A": "aa", "Cr": "nn", "D": "nn", "Z": "nn", "Ch": "nn", "prl": "nn", "G": "nn", "O": "nn"
    }) == "Chestnut"

    # Cream-Pearl co-dominant chestnut
    assert get_phenotype({
        "E": "ee", "A": "aa", "Cr": "Crn", "D": "nn", "Z": "nn", "Ch": "nn", "prl": "prln", "G": "nn", "O": "nn"
    }) == "Chestnut Cream-Pearl"

    # Progressive greying bay
    assert get_phenotype({
        "E": "EE", "A": "AA", "Cr": "nn", "D": "nn", "Z": "nn", "Ch": "nn", "prl": "nn", "G": "Gn", "O": "nn"
    }) == "Grey (Born Bay)"

    # Silver Black (dapples black hair)
    assert get_phenotype({
        "E": "EE", "A": "aa", "Cr": "nn", "D": "nn", "Z": "Zn", "Ch": "nn", "prl": "nn", "G": "nn", "O": "nn"
    }) == "Silver Black (Dapple)"

    # Lethal White Syndrome (Homozygous Overo)
    assert get_phenotype({
        "E": "EE", "A": "aa", "Cr": "nn", "D": "nn", "Z": "nn", "Ch": "nn", "prl": "nn", "G": "nn", "O": "OO"
    }) == "Lethal White Syndrome (Fatal)"

def test_validate_safety_compliance():
    # Safe outcome
    safe_odds = {"Bay": "75.0%", "Chestnut": "25.0%"}
    assert validate_safety_compliance(safe_odds)["compliant"] is True

    # Dangerous outcome
    lws_odds = {"Lethal White Syndrome (Fatal)": "25.0%", "Bay Frame Overo": "50.0%", "Bay": "25.0%"}
    audit = validate_safety_compliance(lws_odds)
    assert audit["compliant"] is False
    assert audit["alert_level"] == "HIGH-PRIORITY"
