"""Quantum simulators for SHA-520 cryptanalysis."""

from .tn_simulator import TensorNetworkSimulator, simulate_grover_4round_32bit

try:
    from .qiskit_simulation import (
        run_grover_simulation,
        estimate_circuit_resources,
        QISKIT_AVAILABLE,
    )
except ImportError:
    QISKIT_AVAILABLE = False

__all__ = [
    "TensorNetworkSimulator",
    "simulate_grover_4round_32bit",
    "run_grover_simulation",
    "estimate_circuit_resources",
    "QISKIT_AVAILABLE",
]
