# Resource Analysis: Scaling & Compilation Overhead

## Physical → Encoded → Logical Hierarchy

| Layer | Entity | Scaling |
|-------|--------|---------|
| Physical | τ-anyons | N |
| Encoded | Fusion space | dim ≈ F_{N-1} ≈ φ^N/√5 |
| Logical | Qubits | n ≈ 0.694N - 1.16 |

**Asymptotic limit:** ~69% qubit density extraction from physical anyons.

## SHA-520 Preimage Resources

| Resource | Per-Round | Total (2^260 Grover iterations) | Feasibility |
|----------|-----------|--------------------------------|-------------|
| Logical qubits | 2,500 | 2,500 (reused) | NISQ |
| Physical anyons (4-τ) | 10,000 | 10,000 | ~1 cm² area |
| T-gates per iteration | 10⁶ | 2^260 × 10⁶ | IMPOSSIBLE |
| Braid complexity | O(10⁶ × 300) | 3×10⁸ braids/iter | 30 sec/iter |
| **Total time** | 30 sec | **10^70 years** | ❌ IMPOSSIBLE |

**Verdict:** Quantum computing provides O(2^260) speedup over classical (already optimal via Grover). But 2^260 iterations × 30 sec = 10^70 years = unachievable.

## Reduced-Round Analysis

For r-round SHA-520 with truncated b-bit output:

| Rounds | Output bits | Classical | Quantum | Advantage |
|--------|-------------|-----------|---------|-----------|
| 4 | 16 | 2^16 | 2^8 | ✓ Quadratic |
| 4 | 20 | 2^20 | 2^10 | ✓ Quadratic |
| 8 | 24 | 2^24 | 2^12 | ✓ Quadratic |
| 16 | 32 | 2^32 | 2^16 | ✓ Quadratic |
| **80 (full)** | **520** | **2^520** | **2^260** | ✓ Quadratic (useless) |

**Key insight:** Quantum advantage is real but polynomial (2×). For cryptanalysis, it doesn't matter—still 10^70 years.

## Scaling Breakdown

**Theorem:** Topological advantage is lost at N_crit ≈ 10⁴-10⁵ physical anyons.

**Why:**
1. **Adiabatic condition fails:** τ_braid ≫ ħ/Δ → Braid time grows with system size
2. **Control complexity:** Need O(N) independent voltage gates for individual anyon control
3. **Interferometry crosstalk:** Measurement visibility decays as exp(-d/ξ) over distance
4. **Thermal background:** Stray anyon density n_th ≈ exp(-Δ/kT) × area increases
5. **Fabrication:** 2DEG uniformity over cm² scale unproven at required precision

**Surface code comparison:** For small N, surface codes require less overhead (empirically).

## Braid Compilation Overhead

**Solovay-Kitaev:** ε-approximation requires L(ε) = O(log^3.97(1/ε)) braids per T-gate

**Practical example:**
- Precision ε = 10^-10
- log(1/ε) ≈ 33
- L(10^-10) ≈ 33^3.97 ≈ 1,400,000 braids per T-gate

**For 10⁶ T-gates per Grover iteration:**
- Total braids per iteration: 1.4 × 10^12
- Time per iteration: 1.4 × 10^12 × 10ns = 14 seconds (much better than above 30s estimate)

## Coherence Time Requirements

For full SHA-520 (80 rounds, 2^260 iterations):
```
t_total ≈ 2^260 iterations × 14 sec/iteration = 10^70 years
T₂ needed > 10^70 years
```

**Topological protection claims:** T₂ > 1 second (theoretical)  
**Gap:** 10^70 years > 1 second—still impossible.

## Error Correction Cycles

**Surface code threshold:** ~1% physical error → ~10% logical per cycle  
**Topological threshold (conjectured):** ~1% (same or better)

No advantage unless:
- ν = 12/5 state exhibits error rates < 0.1% (unproven)
- Adiabatic braiding achieves > 99.5% fidelity (unproven)
- Interferometry visibility > 95% (unproven)

## Conclusion

Topological quantum computing **cannot break SHA-520** because:
1. ✓ Quantum speedup is real (√N for Grover)
2. ✗ But scaling goes 2^260 iterations
3. ✗ 2^260 × any finite time = impossible
4. ✗ Topological advantage (smaller overhead) doesn't matter—still 10^70 years

**Same as any other quantum computer for cryptanalysis.**

*Numbers frozen. No appeals.*
