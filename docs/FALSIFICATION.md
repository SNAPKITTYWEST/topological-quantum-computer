# Falsification Framework: Test Criteria & Exit Conditions

**This work is designed to be falsifiable. That is its entire point.**

## Algorithm Falsification Criteria

**TAE is falsified if ANY hold:**

1. ❌ Braid compilation overhead > polynomial(log(1/ε))
2. ❌ Oracle implementation dominates (EXPECTED TRUE → no advantage)
3. ❌ Fusion space QFT requires exponential braid depth
4. ❌ Topological error rate NOT better than surface codes for N < 10⁴
5. ❌ Anyon operations take > 1 ms

**Status:** Algorithm is EXPECTED to show no advantage (Grover already optimal). This is correct result.

## Architecture Falsification Criteria

**Physical realization is falsified if ANY hold:**

1. ❌ ν = 12/5 FQH state NOT realized in 2DEG by 2035
2. ❌ Thermal anyon density > 10⁻⁶ per μm² at 10 mK
3. ❌ Braid adiabatic time > 1 μs
4. ❌ Interferometric visibility < 90% for 4-anyon measurement
5. ❌ Individual anyon addressing requires > 10 voltage gates per anyon

**Status:** None falsified, none confirmed. All remain open experimental questions.

## Experimental Validation Phases

**Phase 1 (Classical):** SHA-520-r test vectors match the repository reference implementation
**Phase 2 (Quantum):** Toy 4-round simulation > 80% success
**Phase 3 (Resources):** Estimated vs actual deviation < 20%
**Phase 4 (Topological):** Braid compilation polynomial-scale (theory only)

## Exit Strategy

**If falsified:** Archive permanently, mark "falsified by [criterion]", cease development.
**If validated:** Proceed to next phases; conjectures require physical experiment.

## What This Does NOT Claim

- Breaks SHA-512/SHA-3 (no asymptotic advantage)
- Topological QC is ready (ν=12/5 not realized)
- Topological protection eliminates error correction (still active)
- Beats surface codes (unproven, likely loses overhead)
- This is a threat (research model only)

*Falsification locked. Exit strategy fixed. No rewrites without consensus.*
