"""
Qiskit Aer Simulator for SHA-520 Grover Circuits

Provides interface to Qiskit Aer for realistic noise modeling
and resource estimation on current quantum devices.

Optional dependency: gracefully handles absence of Qiskit.
"""

from __future__ import annotations

import sys
import time
import math
from typing import Dict, Any, Optional, List, Tuple, TYPE_CHECKING

QISKIT_AVAILABLE = False
try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error, amplitude_damping_error
    QISKIT_AVAILABLE = True
except ImportError:
    QuantumCircuit = None  # type: ignore
    QuantumRegister = None  # type: ignore
    ClassicalRegister = None  # type: ignore
    AerSimulator = None  # type: ignore
    NoiseModel = None  # type: ignore
    depolarizing_error = None  # type: ignore
    amplitude_damping_error = None  # type: ignore
    QuantumRegister = None  # type: ignore
    NoiseModel = None  # type: ignore

if TYPE_CHECKING:
    from qiskit import QuantumCircuit, QuantumRegister
    from qiskit_aer.noise import NoiseModel


def run_grover_simulation(
    rounds: int = 4,
    target_bits: int = 32,
    noise_model: Optional[str] = None,
    shots: int = 1024,
    seed: int = 42,
) -> Dict[str, Any]:
    """Run Grover SHA-520 simulation with Qiskit Aer.

    Parameters
    ----------
    rounds : int
        SHA-520 round count
    target_bits : int
        Number of bits in search space
    noise_model : str, optional
        Noise model: None (ideal), 'depolarizing', 'realistic'
    shots : int
        Number of measurement shots
    seed : int
        Random seed

    Returns
    -------
    dict
        Simulation results including counts, timing, resource metrics

    Raises
    ------
    ImportError
        If Qiskit is not installed
    """
    if not QISKIT_AVAILABLE:
        raise ImportError(
            "Qiskit not available. Install with: pip install qiskit qiskit-aer"
        )

    # Build circuit
    circuit = _build_grover_circuit(target_bits, rounds)

    # Create simulator
    if noise_model is None:
        sim = AerSimulator(method='statevector', seed_simulator=seed)
    else:
        noise = _create_noise_model(noise_model)
        sim = AerSimulator(method='qasm', noise_model=noise, seed_simulator=seed)

    # Run simulation
    start_time = time.time()
    job = sim.run(circuit, shots=shots)
    result = job.result()
    elapsed = time.time() - start_time

    # Extract results
    counts = result.get_counts(circuit)

    # Analyze results
    analysis = _analyze_grover_results(counts, target_bits)

    return {
        "rounds": rounds,
        "target_bits": target_bits,
        "noise_model": noise_model,
        "shots": shots,
        "runtime_sec": elapsed,
        "circuit_depth": circuit.depth(),
        "circuit_width": circuit.num_qubits,
        "circuit_size": len(circuit.data),
        "counts": counts,
        "success_rate": analysis["success_rate"],
        "top_outcome": analysis["top_outcome"],
        "entropy": analysis["entropy"],
        "fidelity": analysis["fidelity"],
    }


def _build_grover_circuit(n_qubits: int, rounds: int) -> "QuantumCircuit":
    """Build Grover circuit for SHA-520 preimage search.

    Parameters
    ----------
    n_qubits : int
        Number of qubits in search space
    rounds : int
        SHA-520 rounds (for resource scaling)

    Returns
    -------
    QuantumCircuit
        Qiskit circuit implementing Grover
    """
    # Create quantum and classical registers
    q = QuantumRegister(n_qubits, 'q')
    c = ClassicalRegister(n_qubits, 'c')
    circuit = QuantumCircuit(q, c)

    # Compute Grover iterations
    iterations = int((math.pi / 4.0) * math.sqrt(2 ** n_qubits))

    # Initialize superposition
    for i in range(n_qubits):
        circuit.h(q[i])

    # Amplitude amplification iterations
    for _ in range(min(iterations, 5)):  # Cap iterations for practical simulation
        # Oracle (simplified: mark state |00...01⟩)
        circuit.barrier()
        _add_oracle(circuit, q, n_qubits)

        # Diffusion operator
        circuit.barrier()
        _add_diffusion(circuit, q, n_qubits)

    # Measurement
    circuit.measure(q, c)

    return circuit


def _add_oracle(
    circuit: "QuantumCircuit",
    qubits: "QuantumRegister",
    n_qubits: int,
) -> None:
    """Add oracle that marks |00...01⟩ state.

    Parameters
    ----------
    circuit : QuantumCircuit
        Circuit to modify
    qubits : QuantumRegister
        Quantum register
    n_qubits : int
        Number of qubits
    """
    # Mark |00...01⟩: apply Z only if all qubits except last are 0
    # and last qubit is 1

    # Flip last qubit (so we mark |00...00⟩ in computational basis)
    circuit.x(qubits[n_qubits - 1])

    # Multi-controlled Z
    if n_qubits <= 3:
        # For small n, use direct implementation
        for i in range(n_qubits - 1):
            circuit.x(qubits[i])

        # Apply multi-controlled-Z (decomposed from Toffoli chain if needed)
        if n_qubits == 2:
            circuit.h(qubits[1])
            circuit.cx(qubits[0], qubits[1])
            circuit.h(qubits[1])
        elif n_qubits == 3:
            circuit.h(qubits[2])
            circuit.mcx(list(qubits[:2]), qubits[2])
            circuit.h(qubits[2])
        else:
            # Multi-controlled Z via decomposition
            circuit.mcp(math.pi, list(qubits[:-1]), qubits[-1])

        for i in range(n_qubits - 1):
            circuit.x(qubits[i])

    circuit.x(qubits[n_qubits - 1])


def _add_diffusion(
    circuit: "QuantumCircuit",
    qubits: "QuantumRegister",
    n_qubits: int,
) -> None:
    """Add Grover diffusion operator.

    Implements D = 2|s⟩⟨s| - I.

    Parameters
    ----------
    circuit : QuantumCircuit
        Circuit to modify
    qubits : QuantumRegister
        Quantum register
    n_qubits : int
        Number of qubits
    """
    # Hadamard
    for i in range(n_qubits):
        circuit.h(qubits[i])

    # X
    for i in range(n_qubits):
        circuit.x(qubits[i])

    # Multi-controlled Z
    if n_qubits == 2:
        circuit.h(qubits[1])
        circuit.cx(qubits[0], qubits[1])
        circuit.h(qubits[1])
    elif n_qubits <= 4:
        circuit.h(qubits[-1])
        circuit.mcx(list(qubits[:-1]), qubits[-1])
        circuit.h(qubits[-1])
    else:
        circuit.mcp(math.pi, list(qubits[:-1]), qubits[-1])

    # X
    for i in range(n_qubits):
        circuit.x(qubits[i])

    # Hadamard
    for i in range(n_qubits):
        circuit.h(qubits[i])


def _create_noise_model(noise_type: str) -> Optional["NoiseModel"]:
    """Create noise model for simulation.

    Parameters
    ----------
    noise_type : str
        Type: 'depolarizing', 'realistic', or None

    Returns
    -------
    NoiseModel or None
        Qiskit NoiseModel
    """
    if noise_type is None:
        return None

    noise = NoiseModel()

    if noise_type == 'depolarizing':
        # Single-qubit depolarizing noise (1% error)
        p_sq = 0.01
        noise.add_all_qubit_quantum_error(
            depolarizing_error(p_sq, 1), ['h', 'x', 'y', 'z', 'rx', 'ry', 'rz']
        )

        # Two-qubit depolarizing noise (2% error)
        p_2q = 0.02
        noise.add_all_qubit_quantum_error(
            depolarizing_error(p_2q, 2), ['cx', 'cz', 'swap']
        )

    elif noise_type == 'realistic':
        # Depolarizing + amplitude damping
        p_sq = 0.005
        p_2q = 0.01
        decay_rate = 0.001

        # Single-qubit errors
        error_1q = depolarizing_error(p_sq, 1).compose(
            amplitude_damping_error(decay_rate)
        )
        noise.add_all_qubit_quantum_error(
            error_1q, ['h', 'x', 'y', 'z', 'rx', 'ry', 'rz']
        )

        # Two-qubit errors
        error_2q = depolarizing_error(p_2q, 2)
        noise.add_all_qubit_quantum_error(error_2q, ['cx', 'cz', 'swap'])

    return noise


def _analyze_grover_results(
    counts: Dict[str, int],
    target_bits: int,
) -> Dict[str, Any]:
    """Analyze Grover measurement results.

    Parameters
    ----------
    counts : dict
        Measurement counts from Qiskit
    target_bits : int
        Number of qubits used

    Returns
    -------
    dict
        Analysis metrics
    """
    total_shots = sum(counts.values())

    # Find outcome with highest probability
    max_outcome = max(counts, key=counts.get)
    max_count = counts[max_outcome]

    # Compute entropy
    import math
    probs = [c / total_shots for c in counts.values()]
    entropy = -sum(p * math.log2(p) for p in probs if p > 0)

    # Success rate: assume marked state is |00...01⟩
    marked_state = '0' * (target_bits - 1) + '1'
    marked_count = counts.get(marked_state, 0)
    success_rate = marked_count / total_shots

    # Fidelity: uniformity in marked state vs others
    # For ideal Grover with one marked state, expect concentrated probability
    expected_prob = 1.0 / (2 ** target_bits)
    actual_prob_marked = marked_count / total_shots
    fidelity = min(1.0, actual_prob_marked / max(expected_prob, 0.01))

    return {
        "success_rate": success_rate,
        "top_outcome": max_outcome,
        "top_probability": max_count / total_shots,
        "entropy": entropy,
        "fidelity": fidelity,
        "n_unique_outcomes": len(counts),
    }


def estimate_circuit_resources(
    rounds: int,
    target_bits: int,
) -> Dict[str, Any]:
    """Estimate circuit resources without running simulation.

    Parameters
    ----------
    rounds : int
        SHA-520 rounds
    target_bits : int
        Bits in search space

    Returns
    -------
    dict
        Resource estimates
    """
    iterations = int((math.pi / 4.0) * math.sqrt(2 ** target_bits))

    # Oracle resources scale with rounds
    oracle_gates = 50 + rounds * 10
    oracle_depth = 20 + rounds

    # Diffusion resources
    diffusion_gates = 4 * target_bits + 10
    diffusion_depth = target_bits + 10

    # Total for one iteration
    iter_gates = oracle_gates + diffusion_gates
    iter_depth = oracle_depth + diffusion_depth

    # Total
    total_gates = iterations * iter_gates + target_bits  # +target_bits for initialization
    total_depth = iterations * iter_depth + target_bits

    return {
        "rounds": rounds,
        "target_bits": target_bits,
        "grover_iterations": iterations,
        "oracle_gates": oracle_gates,
        "oracle_depth": oracle_depth,
        "diffusion_gates": diffusion_gates,
        "diffusion_depth": diffusion_depth,
        "total_gates": total_gates,
        "total_depth": total_depth,
        "total_qubits": target_bits,
    }


if __name__ == "__main__":
    print("Qiskit Aer Simulator for SHA-520 Grover")
    print("=" * 60)

    if not QISKIT_AVAILABLE:
        print("Qiskit not available. Install with:")
        print("  pip install qiskit qiskit-aer")
        print("\nDisplaying resource estimates instead...")

    # Resource estimates
    for bits in [8, 16, 32]:
        resources = estimate_circuit_resources(rounds=4, target_bits=bits)
        print(f"\n4-round SHA-520, {bits}-bit search:")
        print(f"  Grover iterations: {resources['grover_iterations']}")
        print(f"  Total circuit depth: {resources['total_depth']}")
        print(f"  Total gates: {resources['total_gates']}")
        print(f"  Qubits: {resources['total_qubits']}")

    # Try simulation if Qiskit available
    if QISKIT_AVAILABLE:
        print("\n" + "=" * 60)
        print("Running simulations...")

        try:
            result = run_grover_simulation(
                rounds=4,
                target_bits=8,
                noise_model=None,
                shots=1024,
            )

            print(f"\nSimulation completed ({result['runtime_sec']:.2f}s):")
            print(f"  Circuit depth: {result['circuit_depth']}")
            print(f"  Circuit width: {result['circuit_width']}")
            print(f"  Success rate: {result['success_rate']:.2%}")
            print(f"  Top outcome: {result['top_outcome']}")
            print(f"  Fidelity: {result['fidelity']:.3f}")

        except Exception as e:
            print(f"Simulation failed: {e}")
