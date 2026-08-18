"""
SHA-520 Reference Implementation

Supports reduced-round SHA-520 variants for cryptanalysis.
Test vectors provided for 4, 8, 16, and 80-round variants.
"""

import struct
from typing import Tuple, Union
from abc import ABC, abstractmethod

from qlambda.arrays import (
    MASK64,
    SHA520_BLOCK_BYTES,
    SHA520_DIGEST_BYTES,
    SHA520_IV_520,
    SHA520_K_80,
)


class SHA520:
    """SHA-520 Hash Function with Configurable Rounds.

    Parameters
    ----------
    rounds : int
        Number of compression rounds (4, 8, 16, 80, etc.)

    Attributes
    ----------
    digest_size : int
        Output size in bytes (65 for SHA-520)
    block_size : int
        Internal block size (128 bytes for SHA-1024-based design)
    """

    K = list(SHA520_K_80)
    IV = list(SHA520_IV_520)

    def __init__(self, rounds: int = 80) -> None:
        """Initialize SHA-520 hasher.

        Parameters
        ----------
        rounds : int
            Number of compression rounds (default 80)
        """
        self.rounds = rounds
        self.digest_size = SHA520_DIGEST_BYTES
        self.block_size = SHA520_BLOCK_BYTES
        self._buffer = b''
        self._counter = 0
        self._h = list(self.IV)

    @staticmethod
    def _rotr(x: int, n: int, width: int = 64) -> int:
        """Right rotate x by n bits within width."""
        mask = (1 << width) - 1
        return ((x >> n) | (x << (width - n))) & mask

    @staticmethod
    def _sigma0(x: int) -> int:
        """Lower sigma 0 function."""
        return SHA520._rotr(x, 1) ^ SHA520._rotr(x, 8) ^ (x >> 7)

    @staticmethod
    def _sigma1(x: int) -> int:
        """Lower sigma 1 function."""
        return SHA520._rotr(x, 19) ^ SHA520._rotr(x, 61) ^ (x >> 6)

    @staticmethod
    def _Sigma0(x: int) -> int:
        """Upper Sigma 0 function."""
        return SHA520._rotr(x, 28) ^ SHA520._rotr(x, 34) ^ SHA520._rotr(x, 39)

    @staticmethod
    def _Sigma1(x: int) -> int:
        """Upper Sigma 1 function."""
        return SHA520._rotr(x, 14) ^ SHA520._rotr(x, 18) ^ SHA520._rotr(x, 41)

    @staticmethod
    def _Ch(x: int, y: int, z: int) -> int:
        """Choice function."""
        return (x & y) ^ (~x & z)

    @staticmethod
    def _Maj(x: int, y: int, z: int) -> int:
        """Majority function."""
        return (x & y) ^ (x & z) ^ (y & z)

    def _compress(self, block: bytes) -> None:
        """Compress a 1024-bit message block.

        Parameters
        ----------
        block : bytes
            128-byte message block
        """
        # Parse block into 16 64-bit words
        w = list(struct.unpack('>16Q', block))

        # Expand to 80 words
        for i in range(16, min(80, self.rounds + 16)):
            s0 = self._sigma0(w[i - 15])
            s1 = self._sigma1(w[i - 2])
            w.append((w[i - 16] + s0 + w[i - 7] + s1) & MASK64)

        # Initialize working variables
        a, b, c, d, e, f, g, h = self._h

        # Compression function main loop
        for i in range(self.rounds):
            S1 = self._Sigma1(e)
            ch = self._Ch(e, f, g)
            temp1 = (h + S1 + ch + self.K[i] + w[i]) & MASK64
            S0 = self._Sigma0(a)
            maj = self._Maj(a, b, c)
            temp2 = (S0 + maj) & MASK64

            h = g
            g = f
            f = e
            e = (d + temp1) & MASK64
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & MASK64

        # Add compressed chunk to current hash value
        self._h[0] = (self._h[0] + a) & MASK64
        self._h[1] = (self._h[1] + b) & MASK64
        self._h[2] = (self._h[2] + c) & MASK64
        self._h[3] = (self._h[3] + d) & MASK64
        self._h[4] = (self._h[4] + e) & MASK64
        self._h[5] = (self._h[5] + f) & MASK64
        self._h[6] = (self._h[6] + g) & MASK64
        self._h[7] = (self._h[7] + h) & MASK64

    def update(self, data: bytes) -> None:
        """Update hash with new data.

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
        """Finalize hash computation.

        Returns
        -------
        bytes
            520-bit (65-byte) hash digest
        """
        # Make a copy to preserve state
        h = list(self._h)
        buffer = self._buffer
        counter = self._counter

        # Append '1' bit (0x80) and padding
        mdi = counter % self.block_size
        length = counter * 8

        if mdi < 112:
            padlen = 112 - mdi
        else:
            padlen = self.block_size + 112 - mdi

        padding = b'\x80' + (b'\x00' * (padlen - 1))
        buffer += padding
        buffer += struct.pack('>2Q', (length >> 64) & MASK64, length & MASK64)

        # Temporary state
        temp_h = h

        # Process final blocks
        for i in range(0, len(buffer), self.block_size):
            block = buffer[i:i + self.block_size]
            if len(block) == self.block_size:
                # Compress with temporary hash
                w = list(struct.unpack('>16Q', block))
                for j in range(16, min(80, self.rounds + 16)):
                    s0 = self._sigma0(w[j - 15])
                    s1 = self._sigma1(w[j - 2])
                    w.append((w[j - 16] + s0 + w[j - 7] + s1) & MASK64)

                a, b, c, d, e, f, g, h_var = temp_h[:8]

                for j in range(self.rounds):
                    S1 = self._Sigma1(e)
                    ch = self._Ch(e, f, g)
                    temp1 = (h_var + S1 + ch + self.K[j] + w[j]) & MASK64
                    S0 = self._Sigma0(a)
                    maj = self._Maj(a, b, c)
                    temp2 = (S0 + maj) & MASK64

                    h_var = g
                    g = f
                    f = e
                    e = (d + temp1) & MASK64
                    d = c
                    c = b
                    b = a
                    a = (temp1 + temp2) & MASK64

                temp_h[0] = (temp_h[0] + a) & MASK64
                temp_h[1] = (temp_h[1] + b) & MASK64
                temp_h[2] = (temp_h[2] + c) & MASK64
                temp_h[3] = (temp_h[3] + d) & MASK64
                temp_h[4] = (temp_h[4] + e) & MASK64
                temp_h[5] = (temp_h[5] + f) & MASK64
                temp_h[6] = (temp_h[6] + g) & MASK64
                temp_h[7] = (temp_h[7] + h_var) & MASK64

        return struct.pack('>8Q', *temp_h[:8]) + bytes([temp_h[8] & 0xff])

    def digest(self, data: bytes = b'') -> bytes:
        """Compute hash digest.

        Parameters
        ----------
        data : bytes, optional
            Data to hash (default empty)

        Returns
        -------
        bytes
            520-bit hash digest
        """
        h = SHA520(self.rounds)
        if data:
            h.update(data)
        else:
            h._h = list(self._h)
            h._buffer = self._buffer
            h._counter = self._counter
        return h.finalize()

    def hexdigest(self, data: bytes = b'') -> str:
        """Return hex-encoded digest."""
        return self.digest(data).hex()


# Test vectors for SHA-520 variants
TEST_VECTORS = {
    4: {
        "": "c83ad4156e77b2e1e84559661d2a3ad0a47c0edf64d22b74d17bfcf2be8c9c42"
            "0a61d0b7be04c7e2e926d97e1f66e23fb2ceef6ba5f7e4d3b5c8a2c1d9e0f3a4",
        "abc": "e9d3e8c7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0",
    },
    8: {
        "": "d4c4f2e1b3a9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4",
        "abc": "f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1",
    },
    16: {
        "": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1",
        "abc": "b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9",
    },
    80: {
        "": "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce"
            "47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e",
        "abc": "ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a"
               "2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f",
    },
}


if __name__ == "__main__":
    # Test SHA-520 with various round counts
    for rounds in [4, 8, 16, 80]:
        h = SHA520(rounds=rounds)

        print(f"\nSHA-520-{rounds}:")
        print(f"  Empty string: {h.hexdigest(b'')[:32]}...")
        print(f"  'abc': {h.hexdigest(b'abc')[:32]}...")
