# Threat Model & Safety Boundaries

## Scope & Context

This is **mathematical research** with **no physical implementation**. Safety boundaries prevent misuse and clarify what can and cannot be harmed.

## Assets

| Asset | Current Threat | Mitigation | Status |
|-------|----------------|-----------|--------|
| **SHA-512/SHA-3** | Hypothetical quantum preimage | Reduced-round only (r ≤ 16) | ✓ Safe |
| **RSA/ECDSA keys** | Not in scope | No number-theoretic algorithms | ✓ Safe |
| **Cryptanalytic algorithm** | Misuse on real protocols | Research-only toy model | ✓ Safe |
| **Quantum architecture** | Dual-use computing | Theoretical only; ν=12/5 unproven | ✓ Safe |
| **Formal proofs** | False confidence | Explicit `axiom`s for unproven claims | ✓ Safe |

## Safety Boundaries (Strictly Enforced)

### Allowed

✓ Classical brute-force on **reduced-round** SHA-520 (r ≤ 16)
✓ Quantum simulation on **toy models** (16-bit output, 4-round)
✓ Theoretical braid compilation (no physical generation)
✓ Academic publication & GitHub distribution

### Forbidden

✗ Full-round (r=80) cryptanalysis
✗ Key recovery attempts on real protocols
✗ Hardware construction without explicit authorization
✗ Public deployment of any "attack"
✗ Claims of breaking SHA-512/SHA-3

## What This Work is NOT

- ❌ A deployed attack system
- ❌ A production cryptanalysis tool
- ❌ An escape from classical computational limits
- ❌ A threat to modern cryptography

## Responsible Disclosure

**For academic use:**
- Cite as "research model"
- Clarify "no physical implementation"
- Include falsification criteria in publications

**For security professionals:**
- This is NOT a threat to current systems
- Focus on post-quantum migration
- This is educational about topological QC

*Boundaries frozen. Disclosure locked. No exceptions.*
