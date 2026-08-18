"""
Topological Quantum Computer SHA-520 Cryptanalysis Package

Complete Python modules for quantum attack analysis on SHA-520 hash function.

Modules
-------
classical.sha520_ref : SHA-520 reference implementation
classical.classical_baselines : Classical attack baselines
classical.toy_permutations : Reduced-round toy SHA-520 for testing
quantum.quantum_sha520 : Reversible quantum circuits
quantum.grover_sha520 : Grover's algorithm implementation
simulators.tn_simulator : Tensor network MPS simulator
simulators.qiskit_simulation : Qiskit Aer wrapper
"""

__version__ = "0.1.0"
__author__ = "Quantum Cryptanalysis Team"

try:
    from .classical.sha520_ref import SHA520
    from .classical.classical_baselines import (
        brute_force_preimage,
        birthday_collision,
        measure_classical_complexity,
    )
    from .classical.toy_permutations import ToySHA520, build_toy_grover_circuit
    from .quantum.quantum_sha520 import ReversibleSHA520, QuantumCircuit
    from .quantum.grover_sha520 import GroverSHA520, optimal_iterations, estimate_resources

    __all__ = [
        "SHA520",
        "ToySHA520",
        "ReversibleSHA520",
        "QuantumCircuit",
        "GroverSHA520",
        "brute_force_preimage",
        "birthday_collision",
        "measure_classical_complexity",
        "optimal_iterations",
        "estimate_resources",
        "build_toy_grover_circuit",
    ]
except ImportError as exc:
    raise ImportError(
        "Failed to import mandatory topological quantum computer modules. "
        "Run the Codex audit import smoke test to locate the broken module."
    ) from exc
