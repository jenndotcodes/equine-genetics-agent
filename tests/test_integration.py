# tests/test_integration.py
"""
Integration Testing Suite
-------------------------
Validates end-to-end genetic probability calculations, unknown parent trajectory routing,
and execution speed constraints to satisfy the 15-second Cloud Run runtime guardrail.
"""
import pytest
import time
from tools.genetics_engine import calculate_foal_probabilities, handle_unknown_parent
from tools.critique_agent import validate_scenarios_compliance

def test_foal_calculation_pipeline_integration():
    """
    Validates end-to-end probability calculation pipeline across all 9 loci.
    Exercises the full Cartesian combination product ($4^9 = 262,144$ options)
    and verifies that the execution completes well within the 15-second timeout constraint.
    """
    # Record starting time to check performance constraint
    start_time = time.time()
    
    # Run a full heterozygous cross across all 9 loci (worst-case computation space)
    results = calculate_foal_probabilities(
        sire_E="Ee", sire_A="Aa", sire_Cr="Crn", sire_D="Dn", sire_Z="Zn", sire_Ch="Chn", sire_prl="prln", sire_G="Gn", sire_O="On",
        dam_E="Ee", dam_A="Aa", dam_Cr="Crn", dam_D="Dn", dam_Z="Zn", dam_Ch="Chn", dam_prl="prln", dam_G="Gn", dam_O="On"
    )
    
    elapsed_time = time.time() - start_time
    
    # Assert computation is correct and contains expected phenotypes
    assert results is not None
    assert "Lethal White Syndrome (Fatal)" in results
    
    # Verify execution satisfies the 15-second Cloud Run timeout constraint
    assert elapsed_time < 15.0, f"Simulation pipeline took {elapsed_time:.2f}s, exceeding the 15-second limit!"

def test_unknown_parent_trajectory_integration():
    """
    Verifies the trajectory scenario routing pipeline when a parent is unknown.
    Ensures that three baseline genotype scenarios are generated, audited by the
    Critique Agent compliance logic, and returned within the 15-second timeout limit.
    """
    start_time = time.time()
    
    # Calculate baseline scenarios for unknown parent Stallion
    scenarios = handle_unknown_parent(
        known_E="Ee", known_A="Aa", known_Cr="Crn", known_D="Dn", known_Z="Zn", known_Ch="Chn", known_prl="prln", known_G="Gn", known_O="On",
        unknown_parent_type="stallion"
    )
    
    # Audit scenarios using Critique Agent compliance pipeline
    audited = validate_scenarios_compliance(scenarios)
    
    elapsed_time = time.time() - start_time
    
    # Assert that all baseline scenarios (Bay, Black, Chestnut) are evaluated and audited
    assert len(audited) == 3
    for scenario in audited:
        assert "profile" in scenario
        assert "odds" in scenario
        assert "safety" in scenario
        
    # Verify execution satisfies the 15-second Cloud Run timeout constraint
    assert elapsed_time < 15.0, f"Trajectory scenario evaluation took {elapsed_time:.2f}s, exceeding the 15-second limit!"
