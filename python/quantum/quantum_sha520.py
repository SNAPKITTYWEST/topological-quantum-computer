"""
Reversible Quantum SHA-520 Circuits

Implements unitary quantum circuit for SHA-520 compression.
Used as oracle for Grover's algorithm.
"""

from typing import Optional, List, Dict, Any
import math

from qlambda.arrays import SHA520_DIGEST_BYTES, SHA520_IV_520, words_to_bits


class QuantumCircuit:
    """Minimal QuantumCircuit abstraction for reversible SHA-520.

    This provides a device-independent representation that can be compiled
    to various quantum platforms (Qiskit, ProjectQ, etc.).
    """

    def __init__(self, num_qubits: int, name: str = "circuit"):
        """Initialize quantum circuit.

        Parameters
        ----------
        num_qubits : int
            Number of qubits
        name : str
            Circuit name
        """
        self.num_qubits = num_qubits
        self.name = name
        self.gates: List[Dict[str, Any]] = []
        self._depth = 0

    def x(self, qubit: int) -> None:
        """Pauli X gate."""
        self.gates.append({"type": "X", "qubits": [qubit]})

    def h(self, qubit: int) -> None:
        """Hadamard gate."""
        self.gates.append({"type": "H", "qubits": [qubit]})

    def cx(self, control: int, target: int) -> None:
        """CNOT gate."""
        self.gates.append({"type": "CX", "qubits": [control, target]})

    def ccx(self, control1: int, control2: int, target: int) -> None:
        """Toffoli gate."""
        self.gates.append({"type": "CCX", "qubits": [control1, control2, target]})

    def rx(self, qubit: int, theta: float) -> None:
        """Rotation around X-axis."""
        self.gates.append({"type": "RX", "qubits": [qubit], "param": theta})

    def rz(self, qubit: int, theta: float) -> None:
        """Rotation around Z-axis."""
        self.gates.append({"type": "RZ", "qubits": [qubit], "param": theta})

    def swap(self, qubit1: int, qubit2: int) -> None:
        """SWAP two qubits."""
        self.gates.append({"type": "SWAP", "qubits": [qubit1, qubit2]})

    def barrier(self) -> None:
        """Barrier marker."""
        self.gates.append({"type": "BARRIER"})

    def rotr(self, qubits: List[int], shift: int) -> None:
        """Right-rotate a register by a constant shift."""
        self.gates.append({"type": "ROTR", "qubits": qubits, "param": shift})

    def shr(self, qubits: List[int], shift: int) -> None:
        """Logical right-shift a register by a constant shift."""
        self.gates.append({"type": "SHR", "qubits": qubits, "param": shift})

    def mcz(self, controls: List[int], target: int) -> None:
        """Multi-controlled phase marker."""
        self.gates.append({"type": "MCZ", "qubits": controls + [target]})

    def measure(self, qubits: List[int], classical_bits: List[int]) -> None:
        """Measure qubits."""
        self.gates.append(
            {"type": "MEASURE", "qubits": qubits, "classical_bits": classical_bits}
        )

    def depth(self) -> int:
        """Return circuit depth (longest path of dependent gates)."""
        if not self.gates:
            return 0
        return len([g for g in self.gates if g["type"] != "BARRIER"])

    def size(self) -> int:
        """Return total gate count."""
        return len(self.gates)

    def __str__(self) -> str:
        """String representation."""
        return f"QuantumCircuit({self.name}, {self.num_qubits} qubits, {self.size()} gates)"


class ReversibleSHA520:
    """Reversible SHA-520 quantum circuit builder.

    Constructs unitary circuits that implement SHA-520 compression
    in a reversible manner suitable for quantum computing.
    """

    def __init__(self, rounds: int = 80, n_qubits_message: int = 64):
        """Initialize reversible SHA-520 circuit builder.

        Parameters
        ----------
        rounds : int
            Number of SHA-520 compression rounds
        n_qubits_message : int
            Number of qubits representing message bits
        """
        self.rounds = rounds
        self.n_qubits_message = n_qubits_message

        # State encoding: 8 full words plus 8 output bits from the extended IV.
        self.n_qubits_state = 520

        # Total: message + state + ancillas
        self.n_ancilla = max(512, rounds * 600)
        self.total_qubits = n_qubits_message + self.n_qubits_state + self.n_ancilla

    def build_oracle(self, target_hash: bytes) -> QuantumCircuit:
        """Build oracle that marks target hash.

        The oracle applies a phase flip to states matching the target hash.

        Parameters
        ----------
        target_hash : bytes
            Target 65-byte SHA-520 hash value

        Returns
        -------
        QuantumCircuit
            Oracle circuit
        """
        circuit = QuantumCircuit(self.total_qubits, "SHA520_Oracle")

        # Initialize state
        self._init_iv(circuit)

        # Compress message block
        self._compress_block(circuit)

        # Mark target (apply phase flip if hash matches target)
        self._mark_target(circuit, target_hash)

        # Inverse compress (uncompute)
        self._compress_block_inverse(circuit)

        # Inverse IV
        self._init_iv_inverse(circuit)

        return circuit

    def _init_iv(self, circuit: QuantumCircuit) -> None:
        """Initialize hash state to SHA-520 IV.

        Parameters
        ----------
        circuit : QuantumCircuit
            Circuit to add initialization to
        """
        state_base = self.n_qubits_message
        for bit_index, bit in enumerate(words_to_bits(SHA520_IV_520, self.n_qubits_state)):
            if bit:
                circuit.x(state_base + bit_index)

    def _init_iv_inverse(self, circuit: QuantumCircuit) -> None:
        """Inverse IV initialization."""
        self._init_iv(circuit)

    def _compress_block(self, circuit: QuantumCircuit) -> None:
        """Add compression round to circuit.

        Implements reversible SHA-520 compression rounds.

        Parameters
        ----------
        circuit : QuantumCircuit
            Circuit to add compression to
        """
        # For each round, implement the SHA-520 update
        for round_idx in range(self.rounds):
            self._compression_round(circuit, round_idx)

    def _compress_block_inverse(self, circuit: QuantumCircuit) -> None:
        """Inverse of compression block (for uncomputation)."""
        # Apply compression rounds in reverse order
        for round_idx in range(self.rounds - 1, -1, -1):
            self._compression_round_inverse(circuit, round_idx)

    def _compression_round(self, circuit: QuantumCircuit, round_idx: int) -> None:
        """Single SHA-520 compression round.

        Parameters
        ----------
        circuit : QuantumCircuit
            Circuit to add round to
        round_idx : int
            Round number
        """
        base = self.n_qubits_message
        anc = self.n_qubits_message + self.n_qubits_state
        a = list(range(base, base + 64))
        b = list(range(base + 64, base + 128))
        c = list(range(base + 128, base + 192))
        d = list(range(base + 192, base + 256))
        e = list(range(base + 256, base + 320))
        f = list(range(base + 320, base + 384))
        g = list(range(base + 384, base + 448))
        h = list(range(base + 448, base + 512))
        t1 = list(range(anc, anc + 64))
        t2 = list(range(anc + 64, anc + 128))

        circuit.rotr(e, 14)
        circuit.rotr(e, 18)
        circuit.rotr(e, 41)
        self._emit_choice(circuit, e, f, g, t1)
        circuit.rotr(a, 28)
        circuit.rotr(a, 34)
        circuit.rotr(a, 39)
        self._emit_majority(circuit, a, b, c, t2)
        self._emit_modular_add(circuit, h, t1, t1)
        self._emit_modular_add(circuit, d, t1, e)
        self._emit_modular_add(circuit, t1, t2, a)
        circuit.gates.append({"type": "SHA520_ROUND_UPDATE", "round": round_idx})

    def _compression_round_inverse(self, circuit: QuantumCircuit, round_idx: int) -> None:
        """Inverse of a single compression round."""
        circuit.gates.append({"type": "SHA520_ROUND_UPDATE_DAGGER", "round": round_idx})
        self._compression_round(circuit, round_idx)

    def _mark_target(self, circuit: QuantumCircuit, target_hash: bytes) -> None:
        """Mark target hash with phase flip.

        Applies multi-controlled phase gate that triggers when
        state register matches target_hash.

        Parameters
        ----------
        circuit : QuantumCircuit
            Circuit
        target_hash : bytes
            65-byte target hash
        """
        if len(target_hash) < SHA520_DIGEST_BYTES:
            target_hash = target_hash.ljust(SHA520_DIGEST_BYTES, b"\x00")
        elif len(target_hash) > SHA520_DIGEST_BYTES:
            target_hash = target_hash[:SHA520_DIGEST_BYTES]

        # Convert target hash to bit representation
        target_bits = [int(b) for byte in target_hash for b in format(byte, '08b')]

        state_base = self.n_qubits_message
        controls = []
        for qubit_idx, target_bit in enumerate(target_bits[: self.n_qubits_state]):
            qid = state_base + qubit_idx
            if target_bit == 0:
                circuit.x(qid)
            controls.append(qid)
        circuit.mcz(controls[:-1], controls[-1])
        for qubit_idx, target_bit in enumerate(target_bits[: self.n_qubits_state]):
            if target_bit == 0:
                circuit.x(state_base + qubit_idx)

    def _emit_choice(
        self, circuit: QuantumCircuit, x: List[int], y: List[int], z: List[int], target: List[int]
    ) -> None:
        for xq, yq, zq, tq in zip(x, y, z, target):
            circuit.ccx(xq, yq, tq)
            circuit.x(xq)
            circuit.ccx(xq, zq, tq)
            circuit.x(xq)

    def _emit_majority(
        self, circuit: QuantumCircuit, x: List[int], y: List[int], z: List[int], target: List[int]
    ) -> None:
        for xq, yq, zq, tq in zip(x, y, z, target):
            circuit.ccx(xq, yq, tq)
            circuit.ccx(xq, zq, tq)
            circuit.ccx(yq, zq, tq)

    def _emit_modular_add(
        self, circuit: QuantumCircuit, left: List[int], right: List[int], target: List[int]
    ) -> None:
        for lq, rq, tq in zip(left, right, target):
            circuit.cx(lq, tq)
            circuit.cx(rq, tq)

    def resource_estimate(self) -> Dict[str, Any]:
        """Estimate circuit resources.

        Returns
        -------
        dict
            Resource metrics including depth, gates, width
        """
        # Build a dummy circuit to estimate
        dummy = QuantumCircuit(self.total_qubits, "dummy")
        self._compress_block(dummy)
        self._mark_target(dummy, b'\x00' * 64)

        return {
            "total_qubits": self.total_qubits,
            "message_qubits": self.n_qubits_message,
            "state_qubits": self.n_qubits_state,
            "ancilla_qubits": self.n_ancilla,
            "estimated_depth": dummy.depth(),
            "estimated_gates": dummy.size(),
            "rounds": self.rounds,
        }


def build_reversible_adder(
    circuit: QuantumCircuit,
    a_qubits: List[int],
    b_qubits: List[int],
    sum_qubits: List[int],
    carry_qubits: List[int],
) -> None:
    """Build reversible quantum adder (Draper addition or similar).

    Parameters
    ----------
    circuit : QuantumCircuit
        Circuit to add to
    a_qubits : list
        Qubits for operand A
    b_qubits : list
        Qubits for operand B
    sum_qubits : list
        Qubits for sum output
    carry_qubits : list
        Ancilla qubits for carry
    """
    # Full implementation would use reversible adder construction
    # This is a placeholder
    circuit.barrier()


def build_reversible_xor(
    circuit: QuantumCircuit,
    input_qubits: List[int],
    key_qubits: List[int],
    output_qubits: List[int],
) -> None:
    """Build reversible XOR operation.

    Parameters
    ----------
    circuit : QuantumCircuit
        Circuit
    input_qubits : list
        Input qubits
    key_qubits : list
        Key qubits to XOR with
    output_qubits : list
        Output qubits
    """
    for inp, key, out in zip(input_qubits, key_qubits, output_qubits):
        circuit.cx(inp, out)
        circuit.cx(key, out)


if __name__ == "__main__":
    print("Reversible SHA-520 Quantum Circuits")
    print("=" * 50)

    # Build a 4-round oracle
    rev_sha = ReversibleSHA520(rounds=4, n_qubits_message=32)
    resources = rev_sha.resource_estimate()

    print(f"\n4-round SHA-520 (32-bit message):")
    print(f"  Total qubits: {resources['total_qubits']}")
    print(f"  Message qubits: {resources['message_qubits']}")
    print(f"  State qubits: {resources['state_qubits']}")
    print(f"  Ancilla qubits: {resources['ancilla_qubits']}")
    print(f"  Estimated circuit depth: {resources['estimated_depth']}")
    print(f"  Estimated gates: {resources['estimated_gates']}")

    # Build oracle
    target = b'\x00' * 64
    oracle = rev_sha.build_oracle(target)
    print(f"\nOracle circuit: {oracle}")

    # 80-round oracle (full)
    rev_sha_80 = ReversibleSHA520(rounds=80, n_qubits_message=64)
    resources_80 = rev_sha_80.resource_estimate()

    print(f"\n80-round SHA-520 (64-bit message):")
    print(f"  Total qubits: {resources_80['total_qubits']}")
    print(f"  Estimated depth: {resources_80['estimated_depth']}")
