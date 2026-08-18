"""Quantum circuit modules for SHA-520 cryptanalysis."""

from .quantum_sha520 import ReversibleSHA520, QuantumCircuit
from .grover_sha520 import (
    GroverSHA520,
    optimal_iterations,
    estimate_resources,
    grover_speedup_vs_classical,
)

__all__ = [
    "ReversibleSHA520",
    "QuantumCircuit",
    "GroverSHA520",
    "optimal_iterations",
    "estimate_resources",
    "grover_speedup_vs_classical",
]
