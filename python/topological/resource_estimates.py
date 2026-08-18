"""Topological resource estimates for SHA-520-r experiments."""

from __future__ import annotations

from dataclasses import dataclass, asdict
import math
from typing import Dict

from qlambda.arrays import FALSIFICATION_CRITERIA


@dataclass(frozen=True)
class TopologicalEstimate:
    rounds: int
    target_bits: int
    logical_qubits: int
    physical_anyons: int
    grover_iterations: int
    qir_gates_per_round: int
    braids_per_round: int
    total_braids: int
    braid_time_ns: float
    total_time_sec: float
    oracle_dominates: bool
    falsification_flags: Dict[str, str]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def estimate_sha520_r_topological(
    rounds: int,
    target_bits: int,
    braid_time_ns: float = 10.0,
    sk_factor: int = 300,
) -> TopologicalEstimate:
    if rounds <= 0:
        raise ValueError("rounds must be positive")
    if target_bits <= 0:
        raise ValueError("target_bits must be positive")

    logical_qubits = 1024 + 520 + max(600 * rounds, 100)
    physical_anyons = logical_qubits * 4
    grover_iterations = int((math.pi / 4.0) * math.sqrt(2**target_bits))
    qir_gates_per_round = 1000
    braids_per_round = 35000
    total_braids = grover_iterations * rounds * braids_per_round
    total_time_sec = total_braids * braid_time_ns * 1e-9

    flags: Dict[str, str] = {}
    if sk_factor > 10000:
        flags["braid_overhead_excessive"] = FALSIFICATION_CRITERIA["braid_overhead_excessive"]
    if qir_gates_per_round > 900:
        flags["oracle_dominates"] = FALSIFICATION_CRITERIA["oracle_dominates"]
    if braid_time_ns > 1000.0:
        flags["adiabatic_too_slow"] = FALSIFICATION_CRITERIA["adiabatic_too_slow"]

    return TopologicalEstimate(
        rounds=rounds,
        target_bits=target_bits,
        logical_qubits=logical_qubits,
        physical_anyons=physical_anyons,
        grover_iterations=grover_iterations,
        qir_gates_per_round=qir_gates_per_round,
        braids_per_round=braids_per_round,
        total_braids=total_braids,
        braid_time_ns=braid_time_ns,
        total_time_sec=total_time_sec,
        oracle_dominates="oracle_dominates" in flags,
        falsification_flags=flags,
    )
