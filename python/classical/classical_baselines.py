"""
Classical Cryptanalysis Baselines for SHA-520

Implements preimage, collision, and timing benchmarks.
Used to establish classical lower bounds for quantum advantage.
"""

import os
import time
import random
from typing import Callable, Dict, Any, Tuple, Optional
from collections import defaultdict
import hashlib


def brute_force_preimage(
    target: bytes,
    hash_fn: Callable[[bytes], bytes],
    max_trials: int = 1000000,
    timeout_sec: Optional[float] = None,
) -> Tuple[Optional[bytes], int, float]:
    """Brute force preimage search.

    Parameters
    ----------
    target : bytes
        Target hash value
    hash_fn : Callable
        Hash function that takes bytes and returns bytes
    max_trials : int
        Maximum number of hash computations to attempt
    timeout_sec : float, optional
        Timeout in seconds

    Returns
    -------
    tuple
        (preimage, trials_used, elapsed_time)
        preimage is None if not found
    """
    start_time = time.time()
    trials = 0

    try:
        for trials in range(max_trials):
            if timeout_sec and (time.time() - start_time) > timeout_sec:
                break

            # Generate random message
            message = os.urandom(random.randint(1, 128))
            digest = hash_fn(message)

            if digest == target:
                return message, trials, time.time() - start_time

            trials += 1

        return None, trials, time.time() - start_time

    except KeyboardInterrupt:
        return None, trials, time.time() - start_time


def birthday_collision(
    hash_fn: Callable[[bytes], bytes],
    max_trials: int = 1000000,
    timeout_sec: Optional[float] = None,
) -> Tuple[Optional[Tuple[bytes, bytes]], int, float]:
    """Birthday attack collision search.

    Uses hash table to detect collision with O(sqrt(N)) expected time.

    Parameters
    ----------
    hash_fn : Callable
        Hash function
    max_trials : int
        Maximum number of trials
    timeout_sec : float, optional
        Timeout in seconds

    Returns
    -------
    tuple
        ((m1, m2), trials, elapsed_time) or (None, trials, elapsed_time)
    """
    start_time = time.time()
    hash_table: Dict[bytes, bytes] = {}
    trials = 0

    try:
        for trials in range(max_trials):
            if timeout_sec and (time.time() - start_time) > timeout_sec:
                break

            message = os.urandom(random.randint(1, 128))
            digest = hash_fn(message)

            if digest in hash_table:
                return (hash_table[digest], message), trials, time.time() - start_time

            hash_table[digest] = message
            trials += 1

        return None, trials, time.time() - start_time

    except KeyboardInterrupt:
        return None, trials, time.time() - start_time


def measure_classical_complexity(
    rounds: int,
    target_bits: int,
) -> Dict[str, Any]:
    """Estimate classical complexity for SHA-520 variants.

    Parameters
    ----------
    rounds : int
        Number of hash rounds
    target_bits : int
        Output bits being targeted

    Returns
    -------
    dict
        Complexity metrics:
        - preimage_trials: Expected trials for preimage
        - collision_trials: Expected trials for collision (birthday bound)
        - preimage_time_sec: Estimated time on reference hardware
        - collision_time_sec: Estimated time for collision
    """
    # Classical preimage: 2^n operations
    preimage_trials = 2 ** target_bits

    # Birthday collision: 2^(n/2) operations
    collision_trials = 2 ** (target_bits // 2)

    # Approximate timing on modern CPU (~10^9 ops/sec)
    ops_per_sec = 1e9
    preimage_time = preimage_trials / ops_per_sec
    collision_time = collision_trials / ops_per_sec

    # Adjust for round count (more rounds = slower)
    round_factor = max(1.0, rounds / 80.0)
    preimage_time *= round_factor
    collision_time *= round_factor

    return {
        "target_bits": target_bits,
        "rounds": rounds,
        "preimage_trials": int(preimage_trials),
        "collision_trials": int(collision_trials),
        "preimage_time_sec": preimage_time,
        "collision_time_sec": collision_time,
        "preimage_time_years": preimage_time / (365.25 * 24 * 3600),
        "collision_time_years": collision_time / (365.25 * 24 * 3600),
    }


def timing_benchmark(
    hash_fn: Callable[[bytes], bytes],
    message_size: int = 128,
    iterations: int = 10000,
) -> Dict[str, Any]:
    """Benchmark hash function performance.

    Parameters
    ----------
    hash_fn : Callable
        Hash function to benchmark
    message_size : int
        Size of test messages in bytes
    iterations : int
        Number of iterations

    Returns
    -------
    dict
        Timing statistics
    """
    test_message = os.urandom(message_size)

    # Warm up
    for _ in range(100):
        hash_fn(test_message)

    # Measure
    start = time.time()
    for _ in range(iterations):
        hash_fn(test_message)
    elapsed = time.time() - start

    per_call = elapsed / iterations
    throughput = message_size * iterations / elapsed  # bytes/sec

    return {
        "total_time_sec": elapsed,
        "iterations": iterations,
        "time_per_call_us": per_call * 1e6,
        "throughput_mbps": throughput / (1024 * 1024),
        "message_size_bytes": message_size,
    }


def estimate_grover_advantage(
    classical_trials: int,
    grover_circuits: int,
    circuit_depth: int,
    gate_time_us: float = 100.0,
) -> Dict[str, Any]:
    """Estimate Grover algorithm advantage over classical.

    Parameters
    ----------
    classical_trials : int
        Classical trials needed
    grover_circuits : int
        Number of Grover iterations
    circuit_depth : int
        Depth of each Grover iteration circuit
    gate_time_us : float
        Average gate time in microseconds

    Returns
    -------
    dict
        Speedup factors and absolute times
    """
    classical_time = classical_trials * 1e-3  # Assume 1ms per classical hash

    grover_time = grover_circuits * circuit_depth * gate_time_us * 1e-6

    speedup = classical_time / max(grover_time, 1e-9)

    return {
        "classical_time_sec": classical_time,
        "grover_time_sec": grover_time,
        "speedup_factor": speedup,
        "grover_iterations": grover_circuits,
        "circuit_depth": circuit_depth,
    }


def collision_resistance_margin(
    hash_output_bits: int,
    security_bits: int = 128,
) -> Dict[str, Any]:
    """Analyze collision resistance margin.

    Parameters
    ----------
    hash_output_bits : int
        Output size in bits
    security_bits : int
        Target security level in bits

    Returns
    -------
    dict
        Security margin analysis
    """
    # Birthday bound: 2^(n/2) for collision resistance
    collision_security = hash_output_bits // 2

    # Preimage resistance: 2^n
    preimage_security = hash_output_bits

    margin_collision = collision_security - security_bits
    margin_preimage = preimage_security - security_bits

    return {
        "output_bits": hash_output_bits,
        "target_security_bits": security_bits,
        "collision_security_bits": collision_security,
        "preimage_security_bits": preimage_security,
        "collision_margin_bits": max(0, margin_collision),
        "preimage_margin_bits": max(0, margin_preimage),
        "collision_margin_satisfied": collision_security >= security_bits,
        "preimage_margin_satisfied": preimage_security >= security_bits,
    }


def estimate_required_qubits(
    target_bits: int,
    grover_factor: float = 0.25,
) -> Dict[str, Any]:
    """Estimate qubits needed for quantum attack.

    Parameters
    ----------
    target_bits : int
        Bits of the hash to target
    grover_factor : float
        Factor of target space requiring qubits (0-1)

    Returns
    -------
    dict
        Qubit requirements and feasibility
    """
    # Grover needs sqrt(N) amplitude amplification steps
    # Reversible circuit needs log2(N) qubits for search space
    search_space = 2 ** target_bits
    grover_iterations = int((3.14159 / 4) * (search_space ** 0.5))

    # Qubits for search space (input)
    data_qubits = target_bits

    # Ancilla qubits for reversible compression (typically 2-3x data)
    ancilla_qubits = data_qubits * 3

    # Total logical qubits
    total_logical = data_qubits + ancilla_qubits

    # Physical qubits with surface code error correction (~1000:1)
    physical_per_logical = 1000
    total_physical = total_logical * physical_per_logical

    feasible_128bit_machine = total_physical < 1e7

    return {
        "target_bits": target_bits,
        "search_space": search_space,
        "grover_iterations": grover_iterations,
        "data_qubits": data_qubits,
        "ancilla_qubits": ancilla_qubits,
        "total_logical_qubits": total_logical,
        "total_physical_qubits": int(total_physical),
        "feasible_on_128bit_machine": feasible_128bit_machine,
    }


if __name__ == "__main__":
    print("Classical Cryptanalysis Baselines")
    print("=" * 50)

    # Complexity analysis
    for rounds in [4, 8, 16, 80]:
        for bits in [32, 64]:
            metrics = measure_classical_complexity(rounds, bits)
            print(f"\nSHA-520-{rounds}, targeting {bits} bits:")
            print(f"  Preimage trials: {metrics['preimage_trials']:.2e}")
            print(f"  Collision trials: {metrics['collision_trials']:.2e}")
            print(f"  Preimage time (years): {metrics['preimage_time_years']:.2e}")

    # Collision resistance
    print("\n" + "=" * 50)
    print("Collision Resistance Analysis (SHA-520 = 512 bits)")
    margins = collision_resistance_margin(512, security_bits=128)
    print(f"Collision security: {margins['collision_security_bits']} bits")
    print(f"Margin above 128-bit: {margins['collision_margin_bits']} bits")

    # Qubit requirements
    print("\n" + "=" * 50)
    print("Quantum Attack Requirements")
    for bits in [32, 64, 128]:
        reqs = estimate_required_qubits(bits)
        print(f"\nTargeting {bits} bits:")
        print(f"  Logical qubits: {reqs['total_logical_qubits']}")
        print(f"  Physical qubits (w/ error correction): {reqs['total_physical_qubits']}")
        print(f"  Feasible on 128-qubit machine: {reqs['feasible_on_128bit_machine']}")
