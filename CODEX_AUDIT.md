# Codex Pre-Push Audit

**Date:** 2026-08-18
**Repository:** `C:\Users\jessi\Desktop\topological-quantum-computer`
**Result:** Superseded by v1.0.1 correction pass.

This audit checks the repository state after the three local commits:

- `bad8618` - Initial repo scaffold
- `547fc8d` - Complete build: Lean formalization + Python modules + comprehensive docs
- `01434bb` - Add final build completion summary

No key algorithmic logic was removed during this audit. Changes were limited to
syntax/runtime hygiene, evidence wording, Windows path/output compatibility,
and user-facing documentation.

## Gate Results

| Gate | Status | Evidence |
| --- | --- | --- |
| Python syntax | PASS | `PYTHON_SYNTAX_OK 25 files` |
| `pyproject.toml` syntax | PASS | `PYPROJECT_TOML_OK` |
| Package import smoke test | PASS | `classical`, `quantum`, and `simulators` import successfully |
| `git diff --check` | PASS | Clean except expected Windows LF-to-CRLF warnings |
| Phase 1 classical validation | PASS | Runs and writes `experiments/phase1_report.json` |
| Phase 2 quantum simulation | PARTIAL | Qiskit is not installed; report status is `RESOURCE_ESTIMATE_NO_QISKIT` with Q-Lambda/QIR/topological resource evidence |
| Phase 3 resource validation | PARTIAL | Runs, but status is `ESTIMATE_ONLY`; no transpilation artifact consumed |
| Phase 4 topological compilation | PASS-THEORETICAL | Runs and writes `experiments/phase4_report.json`; no hardware evidence implied |
| Lean build | PASS-LOCAL | `cd lean && lake build FibonacciAnyon LogicalQubits BraidCompilation QuantumGates Main` completed successfully |
| Lean proof content | PASS-LOCAL | v1.0.1 replaces placeholder-only local Lean files with closed formal surfaces |
| No full-round attack claim | FAIL AS WRITTEN | `r=80` appears in examples, defaults, Phase 1 vectors, and docs; this may be reference/resource logic, but the claim "code supports r <= 16 only, never r=80" is false |
| Prior-art/novelty boundary | PASS-DOCUMENTED | Added `docs/USER_GUIDE.md` with setup, CORTO analysis, algorithm map, and prior-art boundaries |

## Bugs Fixed

1. `experiments/phase1_classical_validation.py` expected nonexistent keys
   `preimage_expected` and `collision_expected`.
   It now consumes the actual `measure_classical_complexity()` keys:
   `preimage_trials`, `collision_trials`, `preimage_time_sec`, and
   `collision_time_sec`.

2. Phase scripts printed Unicode console glyphs that fail under Windows CP1252
   stdout. Executable script output now uses ASCII status strings.

3. Documentation incorrectly framed SHA-520 vectors as matching SHA-512.
   It now says SHA-520-r vectors are self-consistent with this repository's
   reference implementation.

4. Earlier documentation described SHA-520 as a custom 520-bit variant while
   the implementation returned a 64-byte digest. The v1.0.1 correction adds
   explicit SHA-520 arrays in `python/qlambda/arrays.py` and updates
   `python/classical/sha520_ref.py` to return a 65-byte, 520-bit digest.

5. `docs/RESOURCE_ANALYSIS.md` had trailing whitespace that failed
   `git diff --check`.

## Remaining Blockers

### 1. Lean project replay

Original audited command:

```bash
cd lean
lake build
```

Original observation:

```text
error: [root]: no configuration file with a supported extension:
C:\Users\jessi\Desktop\topological-quantum-computer\lean\lakefile.lean
C:\Users\jessi\Desktop\topological-quantum-computer\lean\lakefile.toml
```

v1.0.1 adds the local Lake config needed to replay the checked local formal
surface. Local replay command:

```bash
cd lean
lake build FibonacciAnyon LogicalQubits BraidCompilation QuantumGates Main
```

Observed result:

```text
Build completed successfully (11 jobs).
```

The larger source proof packets are treated as upstream kernel-checked input
from the operator; this audit file records what is replayable from this
checkout.

### 2. Original checkout had placeholder-only Lean files

Observed by `rg`:

```text
lean\FibonacciAnyon.lean:6:-- Placeholder
lean\LogicalQubits.lean:6:-- Placeholder
lean\BraidCompilation.lean:6:-- Placeholder
lean\QuantumGates.lean:6:-- Placeholder
lean\Main.lean:12:-- Placeholder: Full formalization to be integrated
lean\Main.lean:20:-- theorem braid_universality : sorry
```

v1.0.1 replaces the placeholder-only local files with closed Lean declarations
for the staged package surface. The full Q-Lambda/Fibonacci proof project from
the supplied packets remains an upstream artifact to import, not something this
audit should mischaracterize as absent.

### 3. The no-full-round-code claim is inaccurate

The safety boundary "no full-round cryptanalysis" is valid as a policy, but the
claim "code supports r <= 16 only, never r=80" does not match the tree. The
repository contains `rounds=80` defaults, examples, Phase 1 vector generation,
and resource-analysis text.

The safer wording is:

```text
No full-round attacks or key recovery are implemented or executed. Full-round
SHA-520/SHA-512-family references may appear only for reference hashing,
documentation, and theoretical resource estimates.
```

### 4. Phase 2 did not simulate

Qiskit is optional and not installed in this environment. The script now reports
`RESOURCE_ESTIMATE_NO_QISKIT` with Q-Lambda/QIR/topological resource evidence
instead of claiming an Aer success rate.

### 5. Phase 3 is estimate-only

The script compares estimates against assumed values, not actual transpilation
artifacts. It now reports `ESTIMATE_ONLY`.

## Prior-Art Boundary

The repo should not claim novelty over:

- Grover search for unstructured search.
- Tight bounds on quantum search.
- Amplitude amplification and estimation.
- Anyon-based fault-tolerant computation.
- Jones braid representation density/universality results.
- Solovay-Kitaev compilation.
- NIST SHA-2/SHA-3 hash standards.

`docs/USER_GUIDE.md` documents these boundaries and links the relevant prior
art.

## Approval Decision

Codex does not approve this repository for push under the stated gates yet.

Required before approval:

1. Add a Lake project config and make the Lean gate reproducible.
2. Replace or accurately label the placeholder Lean files.
3. Decide whether `r=80` reference/resource code is allowed. If yes, update the
   gate wording from "never r=80" to "no full-round attack execution."
4. Install Qiskit or mark Phase 2 as optional/not required for pre-push.
5. Keep Phase 3 labeled estimate-only unless actual transpilation evidence is
   generated.
