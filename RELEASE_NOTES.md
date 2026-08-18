# Topological Quantum Computer v1.0.1

Release type: staged research package
Release date: 2026-08-18

## v1.0.1 Correction

- Removed the temporary non-Python policy backend that skewed repository
  language metrics.
- Added the Q-Lambda DSL implementation in `python/qlambda/compiler.py`.
- Added explicit SHA-520 arrays in `python/qlambda/arrays.py`.
- Updated SHA-520 to emit a 65-byte, 520-bit digest from the 9-word IV surface.
- Added the QIR-to-Fibonacci-braid resource backend in `python/topological/`.
- Added focused tests for arrays, DSL compilation, policy selection, and braid
  resource estimates.

## Summary

This release packages the topological quantum-computing research repository for
public review. It presents a Fibonacci-anyon model, reduced-round SHA-family
experiments, a constraint/proof-search boundary, explicit falsification
criteria, tri-license terms, and audit notes.

The core claim is deliberately bounded: generic SHA-style preimage search does
not gain more than Grover-style square-root speedup, and the model does not
demonstrate a practical full-round cryptanalytic attack.

## Included

- Lean 4 formalization surfaces for Fibonacci anyons, logical qubits, braid
  compilation, and quantum gates.
- Python modules for reduced-round classical validation, toy permutations,
  Q-Lambda reversible-oracle synthesis, Grover-style search, tensor-network
  simulation, and Qiskit integration paths.
- Four experiment phases covering classical validation, quantum simulation,
  resource validation, and theoretical topological compilation.
- Documentation for architecture, falsification, resource analysis, threat
  model, experiment protocol, cryptanalysis notes, and setup.
- PAX-style tri-license file and array-backed Python license-policy backend.
- Package manifest and About metadata for GitHub release hygiene.

## Validation Snapshot

Observed locally during the v1.0.1 correction pass:

| Check | Result |
| --- | --- |
| Python AST syntax scan | PASS |
| `pyproject.toml` parse | PASS |
| Module import smoke test | PASS |
| Phase 1 classical validation | PASS |
| Phase 2 quantum simulation | RESOURCE_ESTIMATE_NO_QISKIT when Qiskit is unavailable |
| Phase 3 resource validation | ESTIMATE_ONLY |
| Phase 4 topological compilation | PASS-THEORETICAL |
| Lean/Lake build | PASS-LOCAL for staged Lean modules |

## Production Boundary

For this release, "production" means packaged, auditable, and documented as a
research artifact. It does not mean physical topological quantum hardware,
machine-checked closure of every theorem, full-round cryptanalysis, or
commercial deployment.

## License

This release follows `LICENSE.tri`:

- BSL-1.1 source-available path with commercial restrictions until `2028-08-08`.
- AGPL-3.0 network-copyleft path.
- MPL-2.0 file-level copyleft path.
- Commercial license path for copyleft bypass.

Use the policy engine:

```bash
PYTHONPATH=python python -m qlambda.license_policy select saas_wrapper
PYTHONPATH=python python -m qlambda.license_policy select enterprise_restricted
PYTHONPATH=python python -m qlambda.license_policy select file_level_mod
PYTHONPATH=python python -m qlambda.license_policy select copyleft_bypass
```
