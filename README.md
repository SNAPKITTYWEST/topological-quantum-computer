# Topological Quantum Computer: Fibonacci Anyon Model

[![release](https://img.shields.io/badge/release-v1.0.1-blue)](RELEASE_NOTES.md)
[![license](https://img.shields.io/badge/license-BSL--1.1%20%2F%20AGPL--3.0%20%2F%20MPL--2.0-green)](LICENSE.tri)
[![status](https://img.shields.io/badge/status-staged%20research%20release-purple)](PACKAGE.md)
[![python](https://img.shields.io/badge/python-3.9%2B-3776ab)](pyproject.toml)
[![lean](https://img.shields.io/badge/Lean%204-formal%20surfaces-8c6d1f)](lean/)
[![safety](https://img.shields.io/badge/safety-no%20real%20cryptanalysis-critical)](docs/THREAT_MODEL.md)

**Staged research package for Fibonacci-anyon topological quantum computing, SHA-520 boundary analysis, and proof-directed search.**

This is a mathematical formalization and simulation framework. Not a physical implementation. Not a claim that SHA is broken.

---

## What This Is

A formal model of topological quantum computing using the Fibonacci anyon category (SU(2)_3 Chern-Simons theory), connected to a Q-Lambda reversible oracle compiler and resource estimation backend.

The central question: does a Fibonacci-anyon topological quantum computer provide practical advantage for SHA-style cryptanalysis?

**Current answer: No.** Generic SHA preimage search has no advantage beyond Grover-style square-root speedup. Reversible oracle costs, braid compilation overhead, coherence requirements, and error-correction costs dominate long before full-round attack relevance. The negative result is the contribution.

---

## What Is Actually Built

### Lean 4 Formalization

| File | What it proves |
|------|---------------|
| `FibonacciAnyon.lean` | Fusion rules (tau x tau = 1 + tau), Fibonacci dimension counts, fusion theorem |
| `LogicalQubits.lean` | Encoding definitions (3-tau, 4-tau), physical anyon accounting theorems |
| `BraidCompilation.lean` | BraidOp structure, H/X/S/CNOT/CCX braid words, length theorems |
| `QuantumGates.lean` | QIR gate enum, braid cost function, cost theorems |
| `Main.lean` | Integration |

All theorems compile. The braid universality (density) theorem is cited to Freedman-Larsen-Wang (2002) -- not proved in this repo.

### Python

| Module | What it does |
|--------|-------------|
| `qlambda/compiler.py` | Full Q-Lambda lexer, parser, QIR synthesizer, uncompute pass |
| `qlambda/arrays.py` | SHA-520 IV/K constants, falsification arrays, DSL primitives |
| `qlambda/programs.py` | SHA-520-r Q-Lambda source programs |
| `topological/braid_backend.py` | QIR-to-Fibonacci-braid gate compiler |
| `topological/resource_estimates.py` | Anyon and braid resource estimates |
| `quantum/quantum_sha520.py` | Reversible SHA-520 oracle construction |
| `quantum/grover_sha520.py` | Grover search implementation |
| `classical/sha520_ref.py` | SHA-520 reference (reduced-round) |

### Experiments

Four validation phases in `experiments/`:
1. Classical validation -- SHA-520-r test vectors
2. Quantum simulation -- reduced-round Grover (Qiskit Aer, optional)
3. Resource validation -- estimated vs actual braid/anyon counts
4. Topological compilation -- braid sequence generation (theory only)

---

## Key Facts

**Fibonacci anyon fusion:**
```
tau x tau = 1 + tau
1 x tau   = tau
1 x 1     = 1
```
Quantum dimension of tau: phi = (1+sqrt(5))/2

**Braid costs (QuantumGates.lean):**
- H: 5 braid ops
- T: 300 braid ops (Solovay-Kitaev approximation)
- CNOT: 5 braid ops
- CCX (Toffoli): 16 braid ops

**Cryptanalytic result:**
Grover search on SHA-520 requires 2^260 oracle calls.
Topological compilation adds overhead, no asymptotic advantage.
Full-round attack is physically impractical.

---

## What This Does Not Claim

| Claim | Status |
|-------|--------|
| Fibonacci anyons physically exist | UNPROVEN |
| Topological quantum computer can be built | UNPROVEN |
| This breaks SHA-520 | FALSE |
| All Lean proofs are closed | NO -- universality cites external proof |
| This beats surface codes | UNPROVEN |

---

## Falsification Criteria

Algorithm falsified if braid compilation overhead is superpolynomial in log(1/epsilon) or oracle cost dominates.

Architecture falsified if nu=12/5 FQH state not realized or interferometric visibility < 90%.

Status: all criteria open.

---

## Running It

```bash
pip install -e .
python experiments/phase1_classical_validation.py
python experiments/phase2_quantum_simulation.py
python experiments/phase3_resource_validation.py
python experiments/phase4_topological_compilation.py
cd lean && lake build
```

---

## Project Structure

```
topological-quantum-computer/
├── lean/                     # Lean 4 formal surfaces
│   ├── FibonacciAnyon.lean
│   ├── LogicalQubits.lean
│   ├── BraidCompilation.lean
│   ├── QuantumGates.lean
│   └── Main.lean
├── python/
│   ├── qlambda/              # Q-Lambda DSL + arrays + policy
│   ├── topological/          # QIR-to-braid backend
│   ├── classical/            # SHA-520 reference
│   ├── quantum/              # Reversible oracle + Grover
│   └── simulators/           # MPS + Qiskit
├── experiments/              # Four validation phases
├── docs/                     # Architecture, falsification, threat model
├── ABOUT.md
├── CODEX_AUDIT.md
└── LICENSE.tri
```

---

## References

- Kitaev, A. (2003). Fault-tolerant quantum computation by anyons. *Annals of Physics*.
- Freedman, M. H.; Larsen, M. J.; Wang, Z. (2002). The two-eigenvalue problem and density of Jones representation of braid groups. *Communications in Mathematical Physics*.
- Preskill, J. (2004). Lecture Notes on Topological Quantum Computation. Chapter 9.

---

## Author

**Ahmad Ali Parr** -- design, architecture, mathematical foundation

---

## License

Tri-license: BSL-1.1 / AGPL-3.0 / MPL-2.0. See `LICENSE.tri`.

No license path authorizes claims of physical hardware, full theorem closure, full-round SHA cryptanalysis, or key recovery.

---

*Falsifiable by design. Honest by construction.*
