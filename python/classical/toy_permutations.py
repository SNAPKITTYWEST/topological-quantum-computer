"""
Toy SHA-520 Variant for Testing and Development

Reduced-round, reduced-word-size SHA-520 for fast simulation
and verification of cryptanalysis techniques.

Parameters:
- 4 rounds (not 80)
- 32-bit words (not 64-bit)
- 4-word state (not 8)
- Result: 128-bit hashes (not 512-bit)
"""

import struct
from typing import List, Tuple, Dict, Any
import math


class ToySHA520:
    """Toy SHA-520 with reduced parameters for fast simulation.

    Maintains SHA structure but reduces complexity for proof-of-concept
    attacks (Grover, collision search, etc.).

    Parameters
    ----------
    rounds : int
        Number of compression rounds (typically 4)
    word_size : int
        Bits per word (typically 32)
    n_words : int
        Number of state words (typically 4)
    """

    # Toy constants (first 4 round constants, mod 2^32)
    K_toy = [
        0x67452301,
        0xefcdab89,
        0x98badcfe,
        0x10325476,
    ]

    # Toy IV
    IV_toy = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a]

    def __init__(self, rounds: int = 4) -> None:
        """Initialize Toy SHA-520.

        Parameters
        ----------
        rounds : int
            Number of rounds
        """
        self.rounds = rounds
        self.word_size = 32
        self.n_words = 4
        self.digest_size = (self.n_words * self.word_size) // 8  # bytes
        self.block_size = 64  # bytes

        self._h = list(self.IV_toy)
        self._buffer = b''
        self._counter = 0

    @staticmethod
    def _rotr(x: int, n: int) -> int:
        """Right rotate 32-bit word."""
        mask = (1 << 32) - 1
        return ((x >> n) | (x << (32 - n))) & mask

    @staticmethod
    def _sigma0(x: int) -> int:
        """Lower sigma 0 function."""
        return ToySHA520._rotr(x, 1) ^ ToySHA520._rotr(x, 5) ^ (x >> 7)

    @staticmethod
    def _sigma1(x: int) -> int:
        """Lower sigma 1 function."""
        return ToySHA520._rotr(x, 11) ^ ToySHA520._rotr(x, 20) ^ (x >> 14)

    @staticmethod
    def _Sigma0(x: int) -> int:
        """Upper Sigma 0 function."""
        return ToySHA520._rotr(x, 2) ^ ToySHA520._rotr(x, 6) ^ ToySHA520._rotr(x, 15)

    @staticmethod
    def _Sigma1(x: int) -> int:
        """Upper Sigma 1 function."""
        return ToySHA520._rotr(x, 7) ^ ToySHA520._rotr(x, 12) ^ ToySHA520._rotr(x, 22)

    @staticmethod
    def _Ch(x: int, y: int, z: int) -> int:
        """Choice function."""
        return (x & y) ^ (~x & z)

    @staticmethod
    def _Maj(x: int, y: int, z: int) -> int:
        """Majority function."""
        return (x & y) ^ (x & z) ^ (y & z)

    def _compress(self, block: bytes) -> None:
        """Compress a 64-byte block.

        Parameters
        ----------
        block : bytes
            64-byte message block
        """
        # Parse into 16 32-bit words (64 bytes = 16 * 4 bytes)
        w = list(struct.unpack('>16I', block[:64]))

        # Expand to 8 + rounds words
        for i in range(8, min(8 + self.rounds, 16)):
            s0 = self._sigma0(w[i - 7])
            s1 = self._sigma1(w[i - 2])
            w.append((w[i - 8] + s0 + w[i - 5] + s1) & 0xffffffff)

        # Initialize working variables
        a, b, c, d = self._h

        # Compression function
        for i in range(self.rounds):
            K_idx = i % len(self.K_toy)
            w_idx = i % len(w)

            S1 = self._Sigma1(a)
            ch = self._Ch(a, b, c)
            temp1 = (d + S1 + ch + self.K_toy[K_idx] + w[w_idx]) & 0xffffffff

            S0 = self._Sigma0(a)
            maj = self._Maj(a, b, c)
            temp2 = (S0 + maj) & 0xffffffff

            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xffffffff

        # Update hash state
        self._h[0] = (self._h[0] + a) & 0xffffffff
        self._h[1] = (self._h[1] + b) & 0xffffffff
        self._h[2] = (self._h[2] + c) & 0xffffffff
        self._h[3] = (self._h[3] + d) & 0xffffffff

    def update(self, data: bytes) -> None:
        """Update hash with data.

        Parameters
        ----------
        data : bytes
            Data to hash
        """
        if isinstance(data, str):
            data = data.encode()

        self._buffer += data
        self._counter += len(data)

        # Process complete blocks
        while len(self._buffer) >= self.block_size:
            self._compress(self._buffer[:self.block_size])
            self._buffer = self._buffer[self.block_size:]

    def finalize(self) -> bytes:
        """Finalize hash.

        Returns
        -------
        bytes
            16-byte (128-bit) digest
        """
        # Copy state
        h = list(self._h)
        buffer = self._buffer
        counter = self._counter

        # Padding
        mdi = counter % self.block_size
        length = counter * 8

        if mdi < 56:
            padlen = 56 - mdi
        else:
            padlen = self.block_size + 56 - mdi

        padding = b'\x80' + (b'\x00' * (padlen - 1))
        buffer += padding
        buffer += struct.pack('>Q', length)

        # Temporary state
        temp_h = h

        # Process remaining blocks
        for i in range(0, len(buffer), self.block_size):
            block = buffer[i:i + self.block_size]
            if len(block) == self.block_size:
                # Inline compress with temp state
                w = list(struct.unpack('>16I', block[:64]))

                for j in range(8, 8 + self.rounds):
                    s0 = self._sigma0(w[j - 7])
                    s1 = self._sigma1(w[j - 2])
                    w.append((w[j - 8] + s0 + w[j - 5] + s1) & 0xffffffff)

                a, b, c, d = temp_h

                for j in range(self.rounds):
                    K_idx = j % len(self.K_toy)
                    w_idx = j % len(w)

                    S1 = self._Sigma1(a)
                    ch = self._Ch(a, b, c)
                    temp1 = (d + S1 + ch + self.K_toy[K_idx] + w[w_idx]) & 0xffffffff

                    S0 = self._Sigma0(a)
                    maj = self._Maj(a, b, c)
                    temp2 = (S0 + maj) & 0xffffffff

                    d = c
                    c = b
                    b = a
                    a = (temp1 + temp2) & 0xffffffff

                temp_h[0] = (temp_h[0] + a) & 0xffffffff
                temp_h[1] = (temp_h[1] + b) & 0xffffffff
                temp_h[2] = (temp_h[2] + c) & 0xffffffff
                temp_h[3] = (temp_h[3] + d) & 0xffffffff

        return struct.pack('>4I', *temp_h)

    def digest(self, data: bytes = b'') -> bytes:
        """Compute digest.

        Parameters
        ----------
        data : bytes
            Data to hash

        Returns
        -------
        bytes
            128-bit hash
        """
        h = ToySHA520(self.rounds)
        if data:
            h.update(data)
        else:
            h._h = list(self._h)
            h._buffer = self._buffer
            h._counter = self._counter
        return h.finalize()

    def hexdigest(self, data: bytes = b'') -> str:
        """Hex digest."""
        return self.digest(data).hex()


def build_toy_grover_circuit(
    toy: ToySHA520,
    target_hash: bytes,
    iterations: int = 10,
) -> Dict[str, Any]:
    """Build Grover circuit description for Toy SHA-520.

    This is a symbolic representation (not executable circuit code).

    Parameters
    ----------
    toy : ToySHA520
        Toy hash instance
    target_hash : bytes
        Target 16-byte hash
    iterations : int
        Number of Grover iterations

    Returns
    -------
    dict
        Circuit specification with gates and resources
    """
    # For toy with 4 rounds and 32-bit words, hash input can be small

    # Assume 32-bit search space (reasonable for toy)
    n_qubits = 32

    # Oracle requires:
    # - Reversible compression rounds
    # - Comparison with target hash
    # - Phase flip

    # Estimate: 4 rounds * ~50 gates per round + ~100 for comparison
    oracle_gates = 4 * 50 + 100
    oracle_depth = 50

    # Diffusion: ~4*n + 50
    diffusion_gates = 4 * n_qubits + 50
    diffusion_depth = 30

    # Total
    total_gates = iterations * (oracle_gates + diffusion_gates) + n_qubits
    total_depth = iterations * (oracle_depth + diffusion_depth) + n_qubits

    # Circuit description
    circuit_spec = {
        "algorithm": "Grover",
        "hash_variant": "Toy-SHA-520",
        "target_bits": n_qubits,
        "search_space": 2 ** n_qubits,
        "target_hash": target_hash.hex(),
        "grover_iterations": iterations,
        "n_qubits": n_qubits,
        "oracle_gates": oracle_gates,
        "oracle_depth": oracle_depth,
        "diffusion_gates": diffusion_gates,
        "diffusion_depth": diffusion_depth,
        "total_gates": total_gates,
        "total_depth": total_depth,
        "operations": [
            "Initialize superposition (H on all qubits)",
            f"Repeat {iterations} times:",
            "  - Apply SHA-520 oracle (mark target hash)",
            "  - Apply Grover diffusion operator",
            "Measure qubits",
        ],
    }

    return circuit_spec


def estimate_toy_grover_speedup(target_bits: int = 32) -> Dict[str, Any]:
    """Estimate speedup of Grover over classical for toy SHA-520.

    Parameters
    ----------
    target_bits : int
        Bits in search space

    Returns
    -------
    dict
        Speedup metrics
    """
    search_space = 2 ** target_bits

    # Classical: 2^n evaluations
    classical_evals = search_space
    classical_time_sec = classical_evals * 1e-6  # 1 μs per eval

    # Grover iterations
    grover_iters = int((math.pi / 4.0) * math.sqrt(search_space))

    # Circuit execution (gate time ~100 ns)
    gates_per_iter = 400  # Rough estimate
    gate_time_sec = 100e-9
    grover_time_sec = grover_iters * gates_per_iter * gate_time_sec

    speedup = classical_time_sec / max(grover_time_sec, 1e-9)

    return {
        "target_bits": target_bits,
        "search_space": search_space,
        "classical_evaluations": classical_evals,
        "classical_time_sec": classical_time_sec,
        "grover_iterations": grover_iters,
        "gates_per_iteration": gates_per_iter,
        "gate_time_sec": gate_time_sec,
        "grover_time_sec": grover_time_sec,
        "speedup_factor": speedup,
    }


if __name__ == "__main__":
    print("Toy SHA-520 for Cryptanalysis Testing")
    print("=" * 60)

    # Test Toy SHA-520
    toy = ToySHA520(rounds=4)
    print(f"Toy SHA-520-{toy.rounds}")
    print(f"  Word size: {toy.word_size} bits")
    print(f"  State words: {toy.n_words}")
    print(f"  Digest size: {toy.digest_size} bytes ({toy.digest_size * 8} bits)")

    # Test vectors
    print("\nTest vectors:")
    test_cases = [b'', b'abc', b'hello world', b'a' * 100]

    for msg in test_cases:
        digest = toy.digest(msg)
        msg_display = msg.decode() if len(msg) < 20 else f"{msg[:20].decode()}..."
        print(f"  {msg_display:30s} -> {digest.hex()}")

    # Grover circuit
    print("\n" + "=" * 60)
    print("Grover Circuit for Toy SHA-520")

    target = b'\x00' * 16
    circuit_spec = build_toy_grover_circuit(toy, target, iterations=10)

    print(f"\nCircuit specification:")
    for key, value in circuit_spec.items():
        if key != "operations":
            print(f"  {key}: {value}")

    print(f"\nOperations:")
    for op in circuit_spec["operations"]:
        print(f"  {op}")

    # Speedup analysis
    print("\n" + "=" * 60)
    print("Grover vs Classical Speedup")

    for bits in [16, 24, 32]:
        speedup = estimate_toy_grover_speedup(bits)
        print(
            f"\n{bits}-bit search:"
            f"\n  Classical time: {speedup['classical_time_sec']:.2e} sec"
            f"\n  Grover time: {speedup['grover_time_sec']:.2e} sec"
            f"\n  Speedup: {speedup['speedup_factor']:.2e}x"
        )
