# Topological Quantum Computer: Fibonacci Anyon Model

[![release](https://img.shields.io/badge/release-v1.0.1-blue)](RELEASE_NOTES.md)
[![license](https://img.shields.io/badge/license-BSL--1.1%20%2F%20AGPL--3.0%20%2F%20MPL--2.0-green)](LICENSE.tri)
[![status](https://img.shields.io/badge/status-staged%20research%20release-purple)](PACKAGE.md)
[![python](https://img.shields.io/badge/python-3.9%2B-3776ab)](pyproject.toml)
[![lean](https://img.shields.io/badge/Lean%204-toolchain--gated-8c6d1f)](CODEX_AUDIT.md)
[![safety](https://img.shields.io/badge/safety-no%20real%20cryptanalysis-critical)](docs/THREAT_MODEL.md)

**Research-grade theoretical design from first principles.**

A mathematical formalization and simulation framework for a hypothetical topological quantum computer based on the Fibonacci anyon model (SU(2)₃ Chern-Simons theory). This is **not a physical implementation**—it is a rigorous mathematical model with falsifiable criteria and explicit conjectures about physical realizability.

---

## Status

**Mathematical Model Only.** No Fibonacci anyon system has been physically realized. The ν = 12/5 fractional quantum Hall state is a theoretical candidate; experimental confirmation remains open.

---

## v1.0 Package Status

Version `1.0.1` is a staged research release. It is packaged for audit,
reproduction, licensing review, and further development. It is not a claim of
physical hardware availability, full theorem closure, or full-round
cryptanalytic deployment.

| Surface | Package role | Status |
|---------|--------------|--------|
| `README.md` | Institutional entry point | Present |
| `ABOUT.md` | Short project overview | Present |
| `LICENSE.tri` | Tri-license terms | Present |
| `python/qlambda/arrays.py` | SHA-520 constants, falsification arrays, DSL primitive arrays | Present |
| `python/qlambda/compiler.py` | Q-Lambda lexer/parser/QIR synthesizer | Present |
| `python/topological/` | QIR-to-braid resource backend | Present |
| `python/qlambda/license_policy.py` | Array-backed license policy engine | Present |
| `PACKAGE.md` | Release/package manifest | Present |
| `RELEASE_NOTES.md` | v1.0.1 staged release notes | Present |
| `CODEX_AUDIT.md` | Audit findings and residual gates | Present |
| `lean/` | Lean 4 formalization surfaces | Local named targets build |
| `python/` | Classical, quantum, simulator modules | Syntax/import checked |
| `experiments/` | Four validation phases | Reduced-round / staged |
| `docs/` | Architecture, falsification, threat model, user guide | Present |

---

## Purpose of This Repository

This repository exists to answer a hard question directly:

> If we build the most disciplined topological quantum-computing model we can,
> does it create a practical advantage for SHA-style cryptanalysis?

The current answer is **no for generic hash cryptanalysis**, and that negative
result is part of the value of the repo. Quantum computers are not magic
parallel brute-force machines. They only help when the problem has mathematical
structure that quantum interference can exploit. For random-looking hash
preimage search, the best generic quantum advantage remains Grover-style
square-root speedup, and the reversible oracle, braid compilation, coherence,
and error-correction costs still dominate.

So the repo is not a claim that topological quantum computers "break" hashes.
It is a falsifiable framework for showing exactly where the advantage stops:

- what a Fibonacci-anyon architecture would need,
- what the logical circuit would cost,
- what the braid compiler would have to preserve,
- what cryptanalytic speedup is actually available,
- and where physical/runtime resources make the attack impractical.

This also explains why constraint systems matter. For many structured problems,
a constraint solver, proof engine, SAT/SMT system, Q-Lambda compiler, or Lean-backed
search can do the useful part more directly: encode rules, eliminate impossible
states, propagate consequences, and produce witnesses or contradictions.

Quantum search is amplitude-directed search. Constraint systems are
proof-directed search. For this stack, the practical architecture is often the
constraint/proof system: deterministic audit trails, explicit failure reasons,
reproducible witnesses, and no dependence on unavailable physical qubits.

The useful outcome is therefore not "quantum wins at everything." The useful
outcome is a clean boundary:

- use topological quantum models to study invariant-preserving computation,
  braid compilation, and resource limits;
- use constraint systems for proof-directed pruning, program synthesis,
  verification, and reproducible search;
- do not confuse either with a practical full-round hash-breaking machine.

---

## Architecture at a Glance

```
PHYSICAL LAYER          LOGICAL LAYER           APPLICATION LAYER
─────────────           ────────────            ─────────────────
2DEG / FQH ν=12/5  ←→  Fusion Space  ←→  Cryptanalytic Algorithm
                        (τ anyons)           (SHA-520 preimage)
                        Braiding Gates
                        (F-moves, R-moves)
                        
Error Correction: Topological protection + Active syndrome measurement
Measurement: Interferometric anyon charge detection
Scaling: Physical anyons → Encoded qubits → Logical qubits
```

### Key Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| Anyon type | Fibonacci (τ) | SU(2)₃ model |
| Quantum dimension | φ = (1+√5)/2 | Golden ratio |
| Physical anyons per logical qubit | 4 (minimal) | 4-τ encoding |
| Logical qubits extractable | 0.694N - 1.16 | From N physical anyons |
| Scaling breakdown | ~10⁴-10⁵ anyons | Topological advantage lost |
| Topological gap | Δ ≈ 0.1-1 K | Theory; unproven |
| Temperature | T = 10 mK | Dilution fridge |

---

## Project Structure

```
topological-quantum-computer/
├── lean/                          # Lean 4 formalization
│   ├── FibonacciAnyon.lean       # Core definitions (SU(2)₃ category)
│   ├── LogicalQubits.lean        # Encoding schemes (3-τ, 4-τ, 2n-τ)
│   ├── BraidCompilation.lean     # Braid group operations
│   ├── QuantumGates.lean         # Gate universality theorems
│   └── Main.lean                 # Integration & main results
│
├── python/
│   ├── qlambda/                  # Q-Lambda DSL, arrays, policy engine
│   │   ├── arrays.py             # SHA-520 IV/K arrays and falsification arrays
│   │   ├── compiler.py           # Lexer, parser, QIR synthesizer
│   │   ├── programs.py           # SHA-520-r Q-Lambda source programs
│   │   └── license_policy.py     # Python tri-license selector
│   │
│   ├── topological/              # QIR-to-Fibonacci-braid resource backend
│   │   ├── braid_backend.py      # Gate-to-braid mapping
│   │   └── resource_estimates.py # Anyon/braid estimates and flags
│   │
│   ├── classical/                # Classical cryptographic reference
│   │   ├── sha520_ref.py         # SHA-520 implementation (reduced-round)
│   │   ├── classical_baselines.py # Brute-force & birthday attacks
│   │   └── toy_permutations.py   # Ultra-reduced SHA-520 for testing
│   │
│   ├── quantum/                  # Quantum circuit construction
│   │   ├── quantum_sha520.py     # Reversible SHA-520 oracle
│   │   └── grover_sha520.py      # Grover search implementation
│   │
│   └── simulators/               # Simulation & validation
│       ├── tn_simulator.py       # MPS-based tensor network simulator
│       └── qiskit_simulation.py  # Qiskit Aer runner with noise models
│
├── experiments/
│   ├── phase1_classical_validation.py      # SHA-520-r test vectors
│   ├── phase2_quantum_simulation.py        # Reduced-round Grover tests
│   ├── phase3_resource_validation.py       # Estimate vs. actual comparison
│   └── phase4_topological_compilation.py   # Braid compilation (theory)
│
├── docs/
│   ├── ARCHITECTURE.md              # System design & theory
│   ├── FALSIFICATION.md             # Explicit test criteria
│   ├── RESOURCE_ANALYSIS.md         # Scaling & resource estimates
│   ├── THREAT_MODEL.md              # Security boundaries
│   ├── EXPERIMENTAL_PROTOCOL.md     # 4-phase validation plan
│   ├── CRYPTANALYSIS_NOTES.md       # Algorithm details & comparisons
│   └── USER_GUIDE.md                # Setup, CORTO analysis, prior-art map
│
├── README.md                        # This file
├── ABOUT.md                         # Short project positioning
├── LICENSE.tri                      # Tri-license structure
├── PACKAGE.md                       # Package manifest
├── RELEASE_NOTES.md                 # v1.0.1 release notes
├── VERSION                          # Version marker
├── CODEX_AUDIT.md                   # Codex audit notes and gates
├── CLAUDE.md                        # Integrity gates & vision
├── pyproject.toml                   # Python build config
└── .gitignore                       # Git exclusions
```

---

## Key Results (Theoretical)

### 1. Fibonacci Anyon Category (SU(2)₃)

**Fusion rules:**
```
τ × τ = 1 + τ
1 × τ = τ
1 × 1 = 1
```

**Quantum dimensions:**
```
d₁ = 1
d_τ = φ = (1+√5)/2 ≈ 1.618
D = √(1 + φ²) ≈ 1.902
```

**Braiding eigenvalues:**
```
R^{ττ}_1 = e^{-4πi/5}   (vacuum channel)
R^{ττ}_τ = e^{3πi/5}    (τ channel)
```

### 2. Logical Qubit Encoding

**4-τ Standard Encoding** (vacuum total charge):
```
|0⟩_L = |((ττ)₁ (ττ)₁)₁⟩
|1⟩_L = |((ττ)_τ (ττ)_τ)₁⟩
```

- Physical anyons: 4 per logical qubit
- Fusion space dimension: 2
- Measurement advantage: Interferometric detection possible

### 3. Braid Group Universality

**Theorem 3.1 (Density):** The braid group representation on 4 τ-anyons generates a dense subgroup of SU(2).

*Proof sketch:* Eigenvalues are 10th roots of unity, F-moves are non-commuting. By Freedman-Larsen-Wang (2002). ∎

**Compilation overhead:** Solovay-Kitaev, L(ε) = O(log^c(1/ε)) with c ≈ 3.97.

### 4. Cryptanalytic Algorithm: TAE (Topological Amplitude Estimation)

**No asymptotic advantage over Grover/BHT.**

| Algorithm | Preimage | Collision | Status |
|-----------|----------|-----------|--------|
| Classical | 2^520 | 2^260 | Proven optimal |
| Grover | 2^260 | N/A | Proven optimal |
| BHT | N/A | 2^173 | Proven optimal |
| TAE (this) | **2^260** | **2^173** | **Same as Grover/BHT** |

**Conclusion:** TAE is a reformulation of amplitude estimation using topological gates, not a new algorithmic primitive.

---

## Falsification Criteria

### Algorithm: Does TAE Provide Advantage?

**NO if any holds:**
- [ ] Braid compilation overhead > polynomial in log(1/ε)
- [ ] Oracle implementation cost dominates (TRUE for SHA-520)
- [ ] Fusion space QFT requires exponential braid depth
- [ ] Topological protection doesn't reduce logical error rate below surface codes
- [ ] Anyon creation/measurement time > 1ms (makes 2^260 iterations impossible)

### Architecture: Is This Physically Realizable?

**IMPRACTICAL if any holds:**
- [ ] ν = 12/5 state not realized in 2DEG by 2035
- [ ] Thermal anyon density > 10⁻⁶ per μm² at 10mK
- [ ] Braid adiabatic time > 1μs (limits clock speed)
- [ ] Interferometric visibility < 90% for 4-anyon measurement
- [ ] Individual anyon addressing requires > 10 voltage gates per anyon

**Status:** All criteria remain open. None falsified, none confirmed.

---

## What This Does NOT Prove

| Claim | Status |
|-------|--------|
| Fibonacci anyons exist physically | **UNPROVEN** |
| Topological quantum computer can be built | **UNPROVEN** |
| TAE algorithm breaks SHA-520 | **FALSE** (no advantage) |
| SHA-520 is a real standard | **FALSE** (repository-defined SHA-512-family research label; current implementation returns 520-bit digests) |
| "Qubit stealing" creates free qubits | **FALSE** (basis reallocation) |
| Architecture scales to millions of qubits | **UNPROVEN** (likely breaks at ~10⁴) |
| Topological protection eliminates error correction | **FALSE** (still need syndrome measurement) |
| Braiding alone gives universal gates | **TRUE (math only)** |
| Lean 4 formalization completes all proofs | **NO** (many `sorry`s) |
| This beats surface codes | **UNPROVEN** |
| Quantum search replaces constraint/proof systems | **FALSE** (constraint systems remain the practical engine for many structured problems) |

---

## Getting Started

For a setup-oriented walkthrough, claim boundary, algorithm map, and prior-art
positioning, read [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md).

### Prerequisites

- Python 3.9+
- Lean 4 (for formal proofs)
- Qiskit (optional, for quantum simulation)
- TensorNetwork (optional, for MPS simulation)

### Installation

```bash
cd topological-quantum-computer
pip install -e .
```

### Running Experiments

#### Phase 1: Classical Validation
```bash
python experiments/phase1_classical_validation.py
# Outputs: classical_baseline_report.json
```

#### Phase 2: Quantum Simulation (Reduced Rounds)
```bash
python experiments/phase2_quantum_simulation.py
# Outputs: quantum_simulation_report.json
# Tests: SHA-520-4 (16-bit), SHA-520-8 (32-bit), toy 4-round
```

#### Phase 3: Resource Validation
```bash
python experiments/phase3_resource_validation.py
# Compares estimated vs. actual resources
```

#### Phase 4: Topological Compilation (Theory Only)
```bash
python experiments/phase4_topological_compilation.py
# Generates braid sequences (no physical hardware)
```

### Formal Verification

```bash
cd lean
lake build

# Check specific theorems
lake env leanc FibonacciAnyon.lean
lake env leanc BraidCompilation.lean
```

---

## Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** — System design, fusion rules, encoding schemes
- **[FALSIFICATION.md](docs/FALSIFICATION.md)** — Explicit test criteria & what can falsify this work
- **[RESOURCE_ANALYSIS.md](docs/RESOURCE_ANALYSIS.md)** — Scaling, resource estimates, breakdown points
- **[THREAT_MODEL.md](docs/THREAT_MODEL.md)** — Security boundaries, dual-use mitigations
- **[EXPERIMENTAL_PROTOCOL.md](docs/EXPERIMENTAL_PROTOCOL.md)** — Four-phase validation plan
- **[CRYPTANALYSIS_NOTES.md](docs/CRYPTANALYSIS_NOTES.md)** — Algorithm comparisons, oracle model
- **[USER_GUIDE.md](docs/USER_GUIDE.md)** — Setup, CORTO analysis, algorithms, prior-art boundaries

---

## Key References

- **Kitaev, A.** (2003). "Fault-tolerant quantum computation by anyons." *Annals of Physics*.
- **Freedman, M. H.; Larsen, M. J.; Wang, Z.** (2002). "The two-eigenvalue problem and density of Jones representation of braid groups." *Communications in Mathematical Physics*.
- **Shor, P. W.** (1994). "Algorithms for quantum computation: discrete logarithms and factoring." *FOCS*.
- **Brassard, G.; Høyer, P.; Tapp, A.** (1998). "Quantum amplitude amplification and estimation." *SODA*.

---

## Safety Boundaries

1. **No physical hardware construction** — This is pure mathematics and simulation.
2. **No full-scale cryptanalysis** — Only reduced-round (≤16/80) toy models on simulators.
3. **No key recovery** — Generic preimage/collision on public test vectors only.
4. **No deployment** — All code remains in research repository.
5. **Responsible disclosure** — If any weakness discovered (extremely unlikely), follow standard disclosure procedures.

---

## Production Boundary

For this repository, "production" means a packaged, versioned, auditable
research release with setup docs, license routing, release notes, and explicit
verification gates. It does **not** mean:

- a physical topological quantum computer exists,
- every Lean theorem is kernel-closed,
- Qiskit/noise simulation has run in every environment,
- resource estimates are hardware measurements,
- SHA-style full-round cryptanalysis has been demonstrated or authorized.

Any stronger deployment claim requires a separate gate: license selection via
`python -m qlambda.license_policy`, safety review, dependency/hardware evidence, and
the relevant Lean/Qiskit/resource checks.

---

## Integrity Gates

**This work requires review by:**
- [ ] Formal verification: Lean 4 soundness check (0 sorry goals critical theorems)
- [ ] Quantum simulation: Phase 2 success rate > 80% on reduced rounds
- [ ] Classical baseline: SHA-520-r vectors are self-consistent with the
      repository reference implementation
- [ ] Resource validation: Estimated vs. actual deviation < 20%

**Falsification triggers immediate archival & no further development.**

---

## Author & Lineage

**Design:** Ahmad (Megtron architecture, DMZ reduction, quantum monad)  
**Formalization:** Claude Code (Lean 4, Python, experimental framework)  
**Vision:** Topological quantum computing for cryptanalysis as a **mathematical exercise in universality, not a threat**.

---

## License

This repository uses the same tri-license structure as the PAX stack. See
[`LICENSE.tri`](LICENSE.tri).

| Path | Meaning |
|------|---------|
| BSL-1.1 | Source-available path with commercial restrictions until the change date |
| AGPL-3.0 | Strong network-copyleft path |
| MPL-2.0 | File-level copyleft path |
| Commercial | Commercial license path for copyleft bypass |

Use the policy engine:

```bash
PYTHONPATH=python python -m qlambda.license_policy select saas_wrapper
PYTHONPATH=python python -m qlambda.license_policy select enterprise_restricted
PYTHONPATH=python python -m qlambda.license_policy select file_level_mod
PYTHONPATH=python python -m qlambda.license_policy select copyleft_bypass
```

No license path authorizes false claims of physical hardware, full theorem
closure, full-round SHA breaks, key recovery, or unsafe deployment.

---

*Built with topological rigor. Falsifiable by design.*
