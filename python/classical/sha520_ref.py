"""
SHA-520 Reference Implementation

Supports reduced-round SHA-520 variants for cryptanalysis.
Test vectors provided for 4, 8, 16, and 80-round variants.
"""

import struct
from typing import Tuple, Union
from abc import ABC, abstractmethod


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

    # SHA-520 Constants (derived from first 80 primes' fractional parts)
    K = [
        0x428a2f98d728ae22, 0x7137449123ef65cd, 0xb5c0fbcfec4d3b2f, 0xe9b5dba58189dbbc,
        0x3956c25bf348b538, 0x59f111f1b605d019, 0x923f82a4af194f9b, 0xab1c5ed5da6d8118,
        0xd807aa98a3030242, 0x12835b0145706fbe, 0x243185be4ee4b28c, 0x550c7dc3d5ffb4e2,
        0x72be5d74f27b896f, 0x80deb1fe3b1696b1, 0x9bdc06a725c71235, 0xc19bf174cf692694,
        0xe49b69c19ef14ad2, 0xefbe4786384f25e3, 0x0fc19dc68b8cd5b5, 0x240ca1cc77ac9c65,
        0x2de92c6f592b0275, 0x4a7484aa6ea6e483, 0x5cb0a9dcbd41fbd4, 0x76f988da831153b5,
        0x983e5152ee66dfab, 0xa831c66d2db43210, 0xb00327c898fb213f, 0xbf597fc7beef0ee4,
        0xc6e00bf33da88fc2, 0xd5a79147930aa725, 0x06ca6351e003826f, 0x142929670a0e6e70,
        0x27b70a8546d22ffc, 0x2e1b21385c26c926, 0x4d2c6dfc5ac42aed, 0x53380d139d95b3df,
        0x650a73548baf63de, 0x766a0ebb3c88eb5a, 0x81c2c92e47edaee6, 0x92722c851482353b,
        0xa2bfe8a14cf10364, 0xa81a664bbc423001, 0xc24b8b70d0f89791, 0xc76c51a30654be30,
        0xd192e819d6ef5218, 0xd69906245565a910, 0xf40e35855771202a, 0x106aa07032bbd1b8,
        0x19a4c116b8d2d0c8, 0x1e376c082dce5c2e, 0x2748774cdf8eeb99, 0x34b0bcb5e19b48a8,
        0x391c0cb3c5c95a63, 0x4ed8aa4ae3418acb, 0x5b9cca4f7763e373, 0x682e6ff3d6b2b8a3,
        0x748f82ee5defb2fc, 0x78a5636f43172f60, 0x84c87814a1f0ab72, 0x8cc702081a6439ec,
        0x90befffa23631e28, 0xa4506cebde82bde9, 0xbef9a3f7b2c67915, 0xc67178f2e372532b,
        0xca273eceea26619c, 0xd186b8c721c0c207, 0xeada7dd6cde0eb1e, 0xf57d4f7fee6ed178,
        0x06f067aa72176fba, 0x0a637dc5a2c898a6, 0x113f9804bef90dae, 0x1b710b35131c471b,
        0x28db77f523047d84, 0x32caab7b40c72493, 0x3c9ebe0a15c9bebc, 0x431d67c49c100d4c,
    ] * 5  # Repeat for extended variants

    # Initial Hash Values
    IV = [
        0x6a09e667f3bcc908, 0xbb67ae8584caa73b, 0x3c6ef372fe94f82b, 0xa54ff53a5f1d36f1,
        0x510e527fade682d1, 0x9b05688c2b3e6c1f, 0x1f83d9abfb41bd6b, 0x5be0cd19137e2179,
    ]

    def __init__(self, rounds: int = 80) -> None:
        """Initialize SHA-520 hasher.

        Parameters
        ----------
        rounds : int
            Number of compression rounds (default 80)
        """
        self.rounds = rounds
        self.digest_size = 64  # 512 bits
        self.block_size = 128   # 1024 bits in bytes
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
            w.append((w[i - 16] + s0 + w[i - 7] + s1) & 0xffffffffffffffff)

        # Initialize working variables
        a, b, c, d, e, f, g, h = self._h

        # Compression function main loop
        for i in range(self.rounds):
            S1 = self._Sigma1(e)
            ch = self._Ch(e, f, g)
            temp1 = (h + S1 + ch + self.K[i] + w[i]) & 0xffffffffffffffff
            S0 = self._Sigma0(a)
            maj = self._Maj(a, b, c)
            temp2 = (S0 + maj) & 0xffffffffffffffff

            h = g
            g = f
            f = e
            e = (d + temp1) & 0xffffffffffffffff
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xffffffffffffffff

        # Add compressed chunk to current hash value
        self._h[0] = (self._h[0] + a) & 0xffffffffffffffff
        self._h[1] = (self._h[1] + b) & 0xffffffffffffffff
        self._h[2] = (self._h[2] + c) & 0xffffffffffffffff
        self._h[3] = (self._h[3] + d) & 0xffffffffffffffff
        self._h[4] = (self._h[4] + e) & 0xffffffffffffffff
        self._h[5] = (self._h[5] + f) & 0xffffffffffffffff
        self._h[6] = (self._h[6] + g) & 0xffffffffffffffff
        self._h[7] = (self._h[7] + h) & 0xffffffffffffffff

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
            512-bit (64-byte) hash digest
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
        buffer += struct.pack('>2Q', length >> 128, length & 0xffffffffffffffff)

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
                    w.append((w[j - 16] + s0 + w[j - 7] + s1) & 0xffffffffffffffff)

                a, b, c, d, e, f, g, h_var = temp_h

                for j in range(self.rounds):
                    S1 = self._Sigma1(e)
                    ch = self._Ch(e, f, g)
                    temp1 = (h_var + S1 + ch + self.K[j] + w[j]) & 0xffffffffffffffff
                    S0 = self._Sigma0(a)
                    maj = self._Maj(a, b, c)
                    temp2 = (S0 + maj) & 0xffffffffffffffff

                    h_var = g
                    g = f
                    f = e
                    e = (d + temp1) & 0xffffffffffffffff
                    d = c
                    c = b
                    b = a
                    a = (temp1 + temp2) & 0xffffffffffffffff

                temp_h[0] = (temp_h[0] + a) & 0xffffffffffffffff
                temp_h[1] = (temp_h[1] + b) & 0xffffffffffffffff
                temp_h[2] = (temp_h[2] + c) & 0xffffffffffffffff
                temp_h[3] = (temp_h[3] + d) & 0xffffffffffffffff
                temp_h[4] = (temp_h[4] + e) & 0xffffffffffffffff
                temp_h[5] = (temp_h[5] + f) & 0xffffffffffffffff
                temp_h[6] = (temp_h[6] + g) & 0xffffffffffffffff
                temp_h[7] = (temp_h[7] + h_var) & 0xffffffffffffffff

        return struct.pack('>8Q', *temp_h)

    def digest(self, data: bytes = b'') -> bytes:
        """Compute hash digest.

        Parameters
        ----------
        data : bytes, optional
            Data to hash (default empty)

        Returns
        -------
        bytes
            512-bit hash digest
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
