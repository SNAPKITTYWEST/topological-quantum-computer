"""Classical cryptanalysis modules for SHA-520."""

from .sha520_ref import SHA520
from .classical_baselines import (
    brute_force_preimage,
    birthday_collision,
    measure_classical_complexity,
    timing_benchmark,
    estimate_grover_advantage,
)
from .toy_permutations import ToySHA520, build_toy_grover_circuit

__all__ = [
    "SHA520",
    "ToySHA520",
    "brute_force_preimage",
    "birthday_collision",
    "measure_classical_complexity",
    "timing_benchmark",
    "estimate_grover_advantage",
    "build_toy_grover_circuit",
]
