# About Topological Quantum Computer

## What This Repository Does

Topological Quantum Computer is a staged research package for modeling a
Fibonacci-anyon topological quantum-computing stack and testing its limits
against SHA-style cryptanalytic questions.

The repository connects four surfaces:

1. **Lean 4 formalization** for Fibonacci anyon categories, logical qubits,
   braid compilation, and gate universality surfaces.
2. **Python reference code** for reduced-round SHA-family toy models,
   classical baselines, reversible-oracle scaffolding, Grover-style search,
   and resource estimates.
3. **Experiment scripts** that separate classical validation, quantum
   simulation, resource validation, and topological compilation.
4. **Documentation** that states falsification criteria, safety boundaries,
   threat model, prior-art context, and staged release status.

## What It Is Not

This is not a physical quantum computer, not a claim that SHA is broken, and
not a production cryptanalytic deployment. The current package conclusion is
that generic SHA-style preimage search does not gain more than the known
Grover-style square-root speedup, and that resource costs dominate long before
full-round attack relevance.

## Why It Exists

The project is useful because it draws a clean boundary between:

- invariant-preserving quantum models,
- braid compilation and logical-qubit accounting,
- constraint/proof-directed search,
- and real cryptanalytic claims that require much stronger evidence.

The goal is not hype. The goal is a falsifiable research artifact that can be
audited, extended, rejected, or archived based on explicit gates.

## Package Status

Version `1.0.0` is a staged research release. Python syntax/import checks and
the reduced-round classical validation path have been exercised locally. Lean
kernel verification, Qiskit-backed quantum simulation, and hardware execution
remain separate gates documented in `CODEX_AUDIT.md` and `PACKAGE.md`.

## License

This repository follows the same tri-license structure used by the PAX stack:
BSL-1.1, AGPL-3.0, MPL-2.0, and commercial licensing paths selected through
`backends/license_policy.pl`.
