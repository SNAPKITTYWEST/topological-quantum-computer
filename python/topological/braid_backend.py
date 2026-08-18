"""Resource-level QIR to Fibonacci braid backend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from qlambda.compiler import QIRInstruction


@dataclass(frozen=True)
class BraidOp:
    sigma: int
    forward: bool = True


class TopologicalBraidBackend:
    """Compile QIR gate names to Fibonacci braid words.

    This is a resource-level backend. It emits braid-word schedules for
    accounting and falsification tests; it is not a matrix-equivalence proof.
    """

    H_BRAID = (BraidOp(0), BraidOp(1), BraidOp(0), BraidOp(1), BraidOp(0))
    X_BRAID = (BraidOp(0), BraidOp(0))
    S_BRAID = (BraidOp(0), BraidOp(0))
    CNOT_BRAID = (BraidOp(2), BraidOp(1), BraidOp(0), BraidOp(1), BraidOp(2))
    CCX_BRAID = (
        BraidOp(4), BraidOp(5), BraidOp(4), BraidOp(5), BraidOp(4),
        BraidOp(2), BraidOp(3), BraidOp(4), BraidOp(2), BraidOp(3), BraidOp(4),
        BraidOp(4), BraidOp(5), BraidOp(4), BraidOp(5), BraidOp(4),
    )

    def __init__(self, sk_t_length: int = 300):
        self.sk_t_length = sk_t_length

    def compile(self, qir: Iterable[QIRInstruction]) -> List[BraidOp]:
        braids: List[BraidOp] = []
        for inst in qir:
            braids.extend(self.compile_gate(inst))
        return braids

    def compile_gate(self, inst: QIRInstruction) -> List[BraidOp]:
        gate = inst.gate.upper()
        if gate == "X":
            return list(self.X_BRAID)
        if gate == "H":
            return list(self.H_BRAID)
        if gate == "S":
            return list(self.S_BRAID)
        if gate in {"T", "TDG"}:
            forward = gate == "T"
            return [BraidOp(0, forward=forward) for _ in range(self.sk_t_length)]
        if gate == "CX":
            return list(self.CNOT_BRAID)
        if gate == "CCX":
            return list(self.CCX_BRAID)
        if gate in {"ROTR", "SHR", "BARRIER"}:
            return []
        if gate.endswith("_DAGGER"):
            base = QIRInstruction(gate[:-7], inst.controls, inst.targets, inst.params)
            return [BraidOp(op.sigma, not op.forward) for op in reversed(self.compile_gate(base))]
        raise NotImplementedError(f"Gate {inst.gate!r} has no topological braid mapping")
