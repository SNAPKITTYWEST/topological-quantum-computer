# User Guide: Topological Quantum Computer SHA-520 Research Repo

This repository is a research scaffold for studying a hypothetical
Fibonacci-anyon topological quantum computer and its use as a simulation target
for SHA-520-style reduced-round cryptanalysis experiments.

It is not a physical quantum computer, not a production cryptanalysis tool, and
not a claim that SHA-512 or SHA-3 are broken.

## What This Repository Is

The repo combines four layers:

| Layer | Purpose | Evidence status |
| --- | --- | --- |
| Lean 4 formalization | Fibonacci anyon and braid-theory proof surface | Stubbed; Lake project config still required |
| Python classical model | SHA-520-r reference and classical complexity baselines | Syntax-valid; runtime smoke tests required |
| Python quantum model | Reversible SHA-520 oracle and Grover resource estimates | Framework-level; placeholders remain |
| Experiment scripts | Four-phase validation pipeline | Runnable after environment setup; some phases are estimate-only |

`SHA-520` is the repository's research label. The current
`python/classical/sha520_ref.py` implementation returns a 64-byte, 512-bit
digest and should be described as SHA-512-family research code rather than a
NIST SHA standard.

## Setup

Run from the repository root:

```bash
cd C:\Users\jessi\Desktop\topological-quantum-computer
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
```

Optional simulator dependencies:

```bash
python -m pip install ".[quantum,simulation]"
```

Lean is required only for the formal layer:

```bash
cd lean
lake build
```

Current audit note: `lean/` needs a `lakefile.lean` or `lakefile.toml` before
`lake build` can serve as a real Lean gate.

## CORTO Analysis

Use this repo with the CORTO frame: Claims, Objectives, Risks, Tests, Outputs.

| Area | Repo meaning |
| --- | --- |
| Claims | Topological compilation can be modeled; Grover-style search remains the prior-art quantum bound for generic preimage search |
| Objectives | Build a falsifiable simulation and documentation harness, not a deployed attack |
| Risks | Overstating placeholder simulations, confusing SHA-520 with NIST SHA, or treating Lean stubs as closed proofs |
| Tests | Python syntax/import checks, Phase 1 reference checks, optional Qiskit simulation, resource-estimate comparison, Lean build |
| Outputs | JSON experiment reports, resource tables, braid-count estimates, and audit notes |

## Algorithms in Scope

| Algorithm or model | Role in repo | Boundary |
| --- | --- | --- |
| Classical brute force | Baseline preimage search | Reduced output sizes only |
| Birthday collision search | Classical collision baseline | Toy/reduced targets only |
| Grover search | Quantum preimage baseline | No full-scale real-world attack |
| BHT collision search | Prior-art quantum collision reference | Documentation comparison only |
| Topological amplitude estimation | Topological-gate framing of amplitude methods | Not claimed as a new asymptotic break |
| Fibonacci anyon braid compilation | Topological gate model | Theoretical; no hardware construction |
| Solovay-Kitaev compilation | Gate-to-braid approximation model | Resource estimate, not measured hardware evidence |

## Running the Audit Checks

Read-only syntax checks:

```bash
python -c "import ast,pathlib; files=[p for r in [pathlib.Path('python'),pathlib.Path('experiments')] for p in r.rglob('*.py')]; [ast.parse(p.read_text(encoding='utf-8'), filename=str(p)) for p in files]; print('PYTHON_SYNTAX_OK', len(files), 'files')"
python -c "import pathlib,tomllib; tomllib.loads(pathlib.Path('pyproject.toml').read_text(encoding='utf-8')); print('PYPROJECT_TOML_OK')"
git diff --check
```

Runtime smoke checks:

```bash
python -c "import sys; sys.path.insert(0, 'python'); import classical, quantum, simulators; print('IMPORT_OK')"
python experiments\phase1_classical_validation.py
python experiments\phase2_quantum_simulation.py
python experiments\phase3_resource_validation.py
python experiments\phase4_topological_compilation.py
```

Lean gate:

```bash
cd lean
lake build
```

Do not mark the repo production-ready until the runtime checks and Lean gate
match the status claimed in `BUILD_STATUS.md`.

## Prior-Art and Novelty Boundaries

This repository should be positioned as an integration and falsification
framework over known quantum-computing ideas, not as a claim of first discovery
of those ideas.

Prior art that should be acknowledged:

- Grover search gives the generic quadratic search speedup for unstructured
  search: [Grover 1996](https://doi.org/10.1145/237814.237866).
- Tight bounds on Grover-style quantum search are prior art:
  [Boyer, Brassard, Hoyer, Tapp 1998](https://doi.org/10.1002/%28SICI%291521-3978%28199806%2946%3A4/5%3C493%3A%3AAID-PROP493%3E3.0.CO%3B2-P).
- Amplitude amplification and estimation are prior art:
  [Brassard, Hoyer, Mosca, Tapp](https://arxiv.org/abs/quant-ph/0005055).
- Anyon-based fault-tolerant computation is prior art:
  [Kitaev 2003](https://doi.org/10.1016/S0003-4916%2802%2900018-0).
- Density/universality results for Jones braid representations are prior art:
  [Freedman, Larsen, Wang 2002](https://doi.org/10.1007/s002200200636).
- Solovay-Kitaev compilation overhead is prior art:
  [Dawson and Nielsen 2006](https://doi.org/10.26421/QIC6.1-6).
- NIST Secure Hash Standard names and SHA-512 status come from
  [FIPS 180-4](https://doi.org/10.6028/NIST.FIPS.180-4).

Novelty claims should therefore be limited to this repository's specific
combination of Lean proof scaffolding, SHA-520-r simulation harness, resource
auditing, and topological-compilation documentation.

## Safety Boundary

Allowed:

- reduced-round experiments,
- toy-output preimage/collision tests,
- theoretical braid compilation,
- resource estimation,
- documentation and formalization.

Forbidden:

- full-round cryptanalysis against real systems,
- key recovery attempts,
- physical hardware construction,
- claims that SHA-512, SHA-3, or NIST hash standards are broken,
- publishing placeholder simulation output as measured evidence.
