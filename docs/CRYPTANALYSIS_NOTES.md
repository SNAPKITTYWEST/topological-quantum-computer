# Cryptanalysis Notes: TAE vs. Grover vs. Classical

## Complexity Comparison

| Algorithm | Problem | Complexity | Notes |
|-----------|---------|-----------|-------|
| Classical brute-force | Preimage | O(2^n) | Generic lower bound |
| Grover | Preimage | O(2^(n/2)) | Quantum optimal (proven) |
| BHT | Collision | O(2^(n/3)) | Quantum birthday attack |
| **TAE** | **Preimage** | **O(2^(n/2))** | **Same as Grover** |

## Why TAE Provides NO Advantage

**Root cause:** Amplitude estimation gives quadratic speedup for **counting**, but preimage search is **search**.

**Mathematically:**
- Amplitude estimation: √N → O(√N) queries
- Grover search: √N → O(√N) queries
- Both optimal for unstructured search (proven)

**Conclusion:** TAE is just Grover in topological gates. No advantage.

## SHA-520 Oracle Model

Reversible circuit O_f: |x⟩|y⟩ → |x⟩|y ⊕ f(x)⟩

**Complexity:**
- Input: 512 qubits (message)
- Output: 520 bits (digest)
- Work qubits: ~2,000 ancillas
- T-gates: ~10⁶ per oracle call

## Quantum Advantage (Real, But Useless)

For truncated b-bit SHA-520:
- Classical: ~2^b operations
- Quantum: ~2^(b/2) oracle calls

**Time comparison:**

| Bits | Classical | Quantum | Wall-clock | Reality |
|------|-----------|---------|-----------|---------|
| 16 | 2^16 | 2^8 | 0.1 sec | ✓ Feasible |
| 32 | 2^32 | 2^16 | 6 hours | ✓ Feasible |
| **256** | **2^256** | **2^128** | **10^31 years** | ✗ Useless |
| **512** | **2^512** | **2^256** | **10^70 years** | ✗ Useless |

**Verdict:** Quantum advantage exists but is meaningless for security.

*Frozen by theory. No appeals to physics will help.*
