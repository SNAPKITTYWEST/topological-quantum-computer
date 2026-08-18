# Quick Start Guide: SHA-520 Quantum Cryptanalysis

## Installation

```bash
# Navigate to project directory
cd C:\Users\jessi\Desktop\topological-quantum-computer

# Add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Quick Examples

### SHA-520 Reference Implementation

```python
from python.classical import SHA520

# Create hasher with 80 rounds
hasher = SHA520(rounds=80)

# Hash data
digest = hasher.digest(b"hello world")
print(digest.hex())  # 520-bit (65-byte) hash

# Use reduced rounds for faster testing
hasher_4 = SHA520(rounds=4)
digest_4 = hasher_4.digest(b"test")
```

### Toy SHA-520 (Fast Testing)

```python
from python.classical import ToySHA520

# Create toy hasher: 4 rounds, 32-bit words, 128-bit output
toy = ToySHA520(rounds=4)

# Hash data
digest = toy.digest(b"test")  # 16-byte (128-bit) hash
print(digest.hex())
```

### Classical Attacks

```python
from python.classical import measure_classical_complexity, brute_force_preimage

# Estimate complexity
complexity = measure_classical_complexity(rounds=80, target_bits=64)
print(f"Preimage trials: {complexity['preimage_trials']:.2e}")
print(f"Preimage time: {complexity['preimage_time_years']} years")

# Brute force preimage search
target = SHA520().digest(b"secret")
result, trials, elapsed = brute_force_preimage(target, SHA520().digest, max_trials=10000)
```

### Quantum Circuits

```python
from python.quantum import ReversibleSHA520, GroverSHA520

# Build reversible SHA-520 oracle
rev_sha = ReversibleSHA520(rounds=4, n_qubits_message=32)
oracle = rev_sha.build_oracle(b'\x00' * 64)
print(f"Oracle circuit: {oracle}")
print(f"Resources: {rev_sha.resource_estimate()}")

# Build Grover circuit
grover = GroverSHA520(rounds=4, target_hash=b'\x00' * 64, n_qubits_message=32)
circuit = grover.build_grover_preimage()
resources = grover.estimate_resources()
print(f"Grover iterations: {resources['grover_iterations']}")
print(f"Circuit depth: {resources['total_circuit_depth']}")
```

### Speedup Analysis

```python
from python.quantum import grover_speedup_vs_classical, estimate_resources

# Compare quantum vs classical
speedup = grover_speedup_vs_classical(target_bits=64, rounds=80)
print(f"Speedup: {speedup['speedup_factor']:.2e}x")
print(f"Grover time: {speedup['grover_time_sec']:.2e} sec")
print(f"Classical time: {speedup['classical_time_sec']:.2e} sec")

# Resource requirements
resources = estimate_resources(rounds=80, target_bits=64)
print(f"Logical qubits: {resources['total_logical_qubits']}")
print(f"Physical qubits (with error correction): {resources['total_logical_qubits']}")
```

### Simulators

```python
from python.simulators import TensorNetworkSimulator, estimate_circuit_resources

# Tensor network simulator
sim = TensorNetworkSimulator(n_qubits=8)
print(f"Created {sim.n_qubits}-qubit simulator")

# Qiskit resource estimation
resources = estimate_circuit_resources(rounds=4, target_bits=32)
print(f"Circuit depth: {resources['total_depth']}")
print(f"Gates: {resources['total_gates']}")

# Run with Qiskit (if installed)
try:
    from python.simulators import run_grover_simulation
    result = run_grover_simulation(rounds=4, target_bits=8, shots=1024)
    print(f"Success rate: {result['success_rate']:.2%}")
except ImportError:
    print("Qiskit not available")
```

## Module Organization

```
python/
├── classical/
│   ├── sha520_ref.py           # SHA-520 hash function
│   ├── classical_baselines.py  # Classical attacks & complexity
│   └── toy_permutations.py     # Reduced-round testing
├── quantum/
│   ├── quantum_sha520.py       # Reversible circuits
│   └── grover_sha520.py        # Grover's algorithm
└── simulators/
    ├── tn_simulator.py         # Tensor network MPS
    └── qiskit_simulation.py    # Qiskit wrapper
```

## Key Classes

| Class | Module | Purpose |
|-------|--------|---------|
| `SHA520` | classical.sha520_ref | Full SHA-520 hash (configurable rounds) |
| `ToySHA520` | classical.toy_permutations | Reduced-round toy version (4 rounds, 128-bit) |
| `ReversibleSHA520` | quantum.quantum_sha520 | Reversible quantum oracle |
| `GroverSHA520` | quantum.grover_sha520 | Grover's preimage search |
| `QuantumCircuit` | quantum.quantum_sha520 | Device-independent circuit abstraction |
| `TensorNetworkSimulator` | simulators.tn_simulator | MPS quantum simulator |

## Important Constants

- **SHA-520 digest size**: 65 bytes (520 bits)
- **SHA-520 block size**: 128 bytes (1024 bits)
- **Toy SHA-520 digest size**: 16 bytes (128 bits)
- **Grover optimal iterations**: π/4 × √(search space)

## Performance Notes

- **SHA-520-4** (4 rounds): ~10-100x faster than SHA-520-80
- **Toy SHA-520**: ~100x faster than full SHA-520
- **Quantum advantage**: Appears at ~48-bit search space
- **Resource scaling**: Circuit depth ∝ √(search space) for Grover

## Common Use Cases

### Test Quantum Attack Strategy
```python
# Use toy SHA-520 for fast iteration
toy = ToySHA520(rounds=4)
target = toy.digest(b"test_message")

# Estimate Grover resources
from python.quantum import estimate_resources
resources = estimate_resources(rounds=4, target_bits=16)
print(f"Qubits needed: {resources['total_logical_qubits']}")
```

### Analyze Speedup at Different Scales
```python
from python.quantum import grover_speedup_vs_classical

for bits in [16, 32, 48, 64]:
    speedup = grover_speedup_vs_classical(target_bits=bits)
    print(f"{bits}-bit: {speedup['speedup_factor']:.2e}x")
```

### Profile Classical Attack
```python
from python.classical import timing_benchmark

sha = SHA520(rounds=80)
benchmark = timing_benchmark(sha.digest, message_size=128, iterations=1000)
print(f"Throughput: {benchmark['throughput_mbps']:.1f} MB/s")
```

## Optional Dependencies

```bash
# For Qiskit integration
pip install qiskit qiskit-aer

# For better performance
pip install numpy scipy
```

## Reference Documentation

- SHA-520 spec: 520-bit output, configurable rounds
- Grover complexity: O(√N) queries for N-item search
- Physical qubits: ~1000× logical qubits with surface code error correction
- Gate time assumptions: 100 ns (current NISQ baseline)

## Troubleshooting

**ImportError on quantum module**: Check relative imports in `quantum/grover_sha520.py`

**Qiskit warnings**: These are safe; Qiskit is optional. Resource estimates work without it.

**Memory issues on large simulations**: MPS simulator designed for ≤16 qubits; use resource estimates for larger systems.

**Unrealistic speedups**: Remember speedup scales with qubit count and error rates; current NISQ hardware would not achieve these advantages.
