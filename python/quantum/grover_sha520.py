"""
Grover's Algorithm for SHA-520 Preimage Search

Implements Grover oracle and amplitude amplification for quantum preimage attacks.
"""

import math
from typing import Dict, Any, List, Tuple, Optional
from quantum_sha520 import ReversibleSHA520, QuantumCircuit


class GroverSHA520:
    """Grover's algorithm applied to SHA-520 preimage search.

    Uses reversible SHA-520 as oracle within Grover amplitude amplification.
    """

    def __init__(
        self,
        rounds: int = 80,
        target_hash: bytes = b'\x00' * 64,
        n_qubits_message: int = 64,
    ):
        """Initialize Grover SHA-520 solver.

        Parameters
        ----------
        rounds : int
            SHA-520 round count
        target_hash : bytes
            Target 64-byte hash
        n_qubits_message : int
            Qubits representing message space
        """
        self.rounds = rounds
        self.target_hash = target_hash
        self.n_qubits_message = n_qubits_message

        # Search space size
        self.search_space = 2 ** n_qubits_message

        # Reversible SHA-520 oracle
        self.rev_sha = ReversibleSHA520(rounds, n_qubits_message)

    def optimal_iterations(self) -> int:
        """Compute optimal number of Grover iterations.

        Returns
        -------
        int
            Number of iterations ≈ π/4 * √(search_space / solutions)

        Notes
        -----
        Assumes 1 solution (preimage of target hash).
        """
        # For 1 solution: iterations ≈ (π/4) * √N
        return int((math.pi / 4.0) * math.sqrt(self.search_space))

    def build_grover_preimage(self) -> QuantumCircuit:
        """Build complete Grover circuit for SHA-520 preimage search.

        Returns
        -------
        QuantumCircuit
            Full Grover algorithm circuit
        """
        total_qubits = self.rev_sha.total_qubits + 1  # +1 for ancilla phase qubit
        circuit = QuantumCircuit(total_qubits, "Grover_SHA520_Preimage")

        iterations = self.optimal_iterations()

        # Initialize superposition (message qubits)
        for i in range(self.n_qubits_message):
            circuit.h(i)

        # Initialize phase ancilla
        circuit.x(total_qubits - 1)
        circuit.h(total_qubits - 1)

        # Amplitude amplification loop
        for iteration in range(iterations):
            # Oracle: mark target hash
            self._apply_oracle(circuit)

            # Diffusion operator
            self._apply_diffusion(circuit)

        # Measurement
        message_bits = list(range(self.n_qubits_message))
        classical_bits = list(range(self.n_qubits_message))
        circuit.measure(message_bits, classical_bits)

        return circuit

    def _apply_oracle(self, circuit: QuantumCircuit) -> None:
        """Apply SHA-520 oracle.

        The oracle applies a phase flip to states that hash to target_hash.

        Parameters
        ----------
        circuit : QuantumCircuit
            Circuit to add oracle to
        """
        oracle = self.rev_sha.build_oracle(self.target_hash)

        # Append oracle gates to main circuit
        for gate in oracle.gates:
            circuit.gates.append(gate)

    def _apply_diffusion(self, circuit: QuantumCircuit) -> None:
        """Apply Grover diffusion operator.

        D = 2|s⟩⟨s| - I, where |s⟩ is the uniform superposition.

        This amplifies amplitude of marked states.

        Parameters
        ----------
        circuit : QuantumCircuit
            Circuit to add diffusion to
        """
        # H on all message qubits
        for i in range(self.n_qubits_message):
            circuit.h(i)

        # X on all message qubits
        for i in range(self.n_qubits_message):
            circuit.x(i)

        # Multi-controlled Z (if all qubits are 0, apply phase)
        # This is the inversion about average operation
        self._multi_controlled_z(circuit, list(range(self.n_qubits_message)))

        # X on all message qubits (uncompute)
        for i in range(self.n_qubits_message):
            circuit.x(i)

        # H on all message qubits (uncompute)
        for i in range(self.n_qubits_message):
            circuit.h(i)

    def _multi_controlled_z(self, circuit: QuantumCircuit, control_qubits: List[int]) -> None:
        """Apply multi-controlled Z gate.

        Applies Z to last qubit when all controls are 1.

        Parameters
        ----------
        circuit : QuantumCircuit
            Circuit
        control_qubits : list
            Control qubits
        """
        # For small numbers of controls, decompose into Toffoli + single qubit gates
        n_controls = len(control_qubits)

        if n_controls == 0:
            circuit.rz(0, math.pi)
        elif n_controls == 1:
            circuit.rz(control_qubits[0], math.pi)
        elif n_controls == 2:
            # Two-controlled Z via Toffoli decomposition
            c1, c2 = control_qubits[:2]
            circuit.ccx(c1, c2, c1)  # Placeholder; actual CCZ is more complex
        else:
            # For larger counts, would use linear decomposition
            # This is a simplified placeholder
            pass

    def estimate_resources(self) -> Dict[str, Any]:
        """Estimate circuit resources for Grover attack.

        Returns
        -------
        dict
            Resource metrics
        """
        iterations = self.optimal_iterations()
        oracle_resources = self.rev_sha.resource_estimate()

        # Diffusion depth ≈ 4 * H-layers + MCZ
        diffusion_depth = 40 + (2 ** self.n_qubits_message)

        total_depth = iterations * (oracle_resources["estimated_depth"] + diffusion_depth)

        return {
            "target_bits": self.n_qubits_message,
            "search_space": self.search_space,
            "grover_iterations": iterations,
            "oracle_depth": oracle_resources["estimated_depth"],
            "diffusion_depth": diffusion_depth,
            "total_circuit_depth": total_depth,
            "total_qubits": oracle_resources["total_qubits"] + 1,
            "estimated_gates": iterations * (oracle_resources["estimated_gates"] + 100),
        }


def optimal_iterations(search_space: int, solutions: int = 1) -> int:
    """Compute optimal Grover iterations for given search space.

    Parameters
    ----------
    search_space : int
        Total size of search space (2^n)
    solutions : int
        Number of solutions (marked states)

    Returns
    -------
    int
        Number of amplitude amplification iterations

    Notes
    -----
    Formula: iterations = π/4 * √(N/M)
    where N = search_space, M = solutions
    """
    if solutions >= search_space:
        return 1

    return max(1, int((math.pi / 4.0) * math.sqrt(search_space / solutions)))


def estimate_resources(
    rounds: int,
    target_bits: int,
    solutions: int = 1,
) -> Dict[str, Any]:
    """Estimate Grover resources for SHA-520 variant.

    Parameters
    ----------
    rounds : int
        SHA-520 round count
    target_bits : int
        Number of bits in search space
    solutions : int
        Number of solutions (typically 1 for preimage)

    Returns
    -------
    dict
        Resource estimates for Grover attack
    """
    search_space = 2 ** target_bits
    iterations = optimal_iterations(search_space, solutions)

    # Oracle depth scales with rounds and target bits
    # Rough estimate: 100 + 2*rounds gates for oracle
    oracle_depth = 100 + 2 * rounds

    # Diffusion: ~40 + 2^n for multi-controlled Z
    diffusion_depth = 40 + max(20, 2 ** min(target_bits, 10))

    # Total depth = iterations * (oracle + diffusion)
    total_depth = iterations * (oracle_depth + diffusion_depth)

    # Qubits needed
    data_qubits = target_bits
    ancilla_qubits = max(100, 3 * target_bits + rounds)
    total_qubits = data_qubits + ancilla_qubits

    return {
        "rounds": rounds,
        "target_bits": target_bits,
        "search_space": search_space,
        "solutions": solutions,
        "grover_iterations": iterations,
        "oracle_depth": oracle_depth,
        "diffusion_depth": diffusion_depth,
        "total_circuit_depth": total_depth,
        "data_qubits": data_qubits,
        "ancilla_qubits": ancilla_qubits,
        "total_logical_qubits": total_qubits,
        "estimated_total_gates": iterations * (oracle_depth + diffusion_depth),
    }


def grover_speedup_vs_classical(
    target_bits: int,
    rounds: int = 80,
    gate_time_us: float = 100.0,
) -> Dict[str, Any]:
    """Compare Grover quantum attack to classical preimage search.

    Parameters
    ----------
    target_bits : int
        Bits of hash output being targeted
    rounds : int
        SHA-520 round count
    gate_time_us : float
        Quantum gate time in microseconds

    Returns
    -------
    dict
        Speedup factors and absolute times
    """
    # Grover iterations
    search_space = 2 ** target_bits
    iterations = optimal_iterations(search_space, 1)

    # Circuit depth
    resources = estimate_resources(rounds, target_bits)
    circuit_depth = resources["total_circuit_depth"]

    # Grover time estimate (in seconds)
    grover_time_sec = (circuit_depth * gate_time_us) * 1e-6

    # Classical preimage: 2^target_bits hash evaluations
    # Assume 1 μs per hash (SHA-520 is slow, but this is conservative)
    classical_time_sec = search_space * 1e-6

    # Speedup
    speedup = classical_time_sec / max(grover_time_sec, 1e-9)

    return {
        "target_bits": target_bits,
        "rounds": rounds,
        "search_space": search_space,
        "grover_iterations": iterations,
        "circuit_depth": circuit_depth,
        "gate_time_us": gate_time_us,
        "grover_time_sec": grover_time_sec,
        "classical_time_sec": classical_time_sec,
        "speedup_factor": speedup,
        "classical_advantage": classical_time_sec < grover_time_sec,
    }


if __name__ == "__main__":
    print("Grover's Algorithm for SHA-520 Preimage Search")
    print("=" * 60)

    # Test 4-round SHA-520 with 32-bit target
    grover = GroverSHA520(rounds=4, target_hash=b'\x00' * 64, n_qubits_message=32)

    print(f"\n4-round SHA-520, 32-bit search space:")
    print(f"  Search space: 2^32 = {grover.search_space:,}")
    print(f"  Optimal iterations: {grover.optimal_iterations()}")

    resources = grover.estimate_resources()
    print(f"  Circuit depth: {resources['total_circuit_depth']}")
    print(f"  Total qubits: {resources['total_qubits']}")
    print(f"  Estimated gates: {resources['estimated_gates']}")

    # Build circuit
    circuit = grover.build_grover_preimage()
    print(f"\n  Circuit: {circuit}")

    # Speedup comparison
    print("\n" + "=" * 60)
    print("Quantum vs Classical Speedup:")

    for bits in [16, 32, 48, 64]:
        speedup = grover_speedup_vs_classical(bits, rounds=80)
        print(
            f"\n{bits}-bit target:"
            f"\n  Grover time: {speedup['grover_time_sec']:.2e} sec"
            f"\n  Classical time: {speedup['classical_time_sec']:.2e} sec"
            f"\n  Speedup: {speedup['speedup_factor']:.2e}x"
        )
