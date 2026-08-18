"""Explicit arrays for the SHA-520-r and Q-Lambda layers.

The earlier repository buried these constants inside classes. This module makes
the arrays importable, auditable, and reusable by the classical implementation,
DSL compiler tests, and topological resource estimators.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

MASK64 = 0xFFFFFFFFFFFFFFFF
SHA520_DIGEST_BITS = 520
SHA520_DIGEST_BYTES = 65
SHA520_BLOCK_BITS = 1024
SHA520_BLOCK_BYTES = 128
SHA520_WORD_BITS = 64
SHA520_STATE_WORDS = 9
SHA520_ROUNDS: Tuple[int, ...] = (4, 8, 12, 16, 20, 24, 28, 32, 40, 48, 56, 64, 72, 80)

# First 8 values are the SHA-512 IV. The ninth value is the extended SHA-520
# word from the operator packet; only its low byte is emitted in the digest.
SHA520_IV_520: Tuple[int, ...] = (
    0x6A09E667F3BCC908,
    0xBB67AE8584CAA73B,
    0x3C6EF372FE94F82B,
    0xA54FF53A5F1D36F1,
    0x510E527FADE682D1,
    0x9B05688C2B3E6C1F,
    0x1F83D9ABFB41BD6B,
    0x5BE0CD19137E2179,
    0x6F98F4C3E7A2B5D4,
)

SHA520_K_80: Tuple[int, ...] = (
    0x428A2F98D728AE22,
    0x7137449123EF65CD,
    0xB5C0FBCFEC4D3B2F,
    0xE9B5DBA58189DBBC,
    0x3956C25BF348B538,
    0x59F111F1B605D019,
    0x923F82A4AF194F9B,
    0xAB1C5ED5DA6D8118,
    0xD807AA98A3030242,
    0x12835B0145706FBE,
    0x243185BE4EE4B28C,
    0x550C7DC3D5FFB4E2,
    0x72BE5D74F27B896F,
    0x80DEB1FE3B1696B1,
    0x9BDC06A725C71235,
    0xC19BF174CF692694,
    0xE49B69C19EF14AD2,
    0xEFBE4786384F25E3,
    0x0FC19DC68B8CD5B5,
    0x240CA1CC77AC9C65,
    0x2DE92C6F592B0275,
    0x4A7484AA6EA6E483,
    0x5CB0A9DCBD41FBD4,
    0x76F988DA831153B5,
    0x983E5152EE66DFAB,
    0xA831C66D2DB43210,
    0xB00327C898FB213F,
    0xBF597FC7BEEF0EE4,
    0xC6E00BF33DA88FC2,
    0xD5A79147930AA725,
    0x06CA6351E003826F,
    0x142929670A0E6E70,
    0x27B70A8546D22FFC,
    0x2E1B21385C26C926,
    0x4D2C6DFC5AC42AED,
    0x53380D139D95B3DF,
    0x650A73548BAF63DE,
    0x766A0ABB3C77B2A8,
    0x81C2C92E47EDAEE6,
    0x92722C851482353B,
    0xA2BFE8A14CF10364,
    0xA81A664BBC423001,
    0xC24B8B70D0F89791,
    0xC76C51A30654BE30,
    0xD192E819D6EF5218,
    0xD69906245565A910,
    0xF40E35855771202A,
    0x106AA07032BBD1B8,
    0x19A4C116B8D2D0C8,
    0x1E376C085141AB53,
    0x2748774CDF8EEB99,
    0x34B0BCB5E19B48A8,
    0x391C0CB3C5C95A63,
    0x4ED8AA4AE3418ACB,
    0x5B9CCA4F7763E373,
    0x682E6FF3D6B2B8A3,
    0x748F82EE5DEFB2FC,
    0x78A5636F43172F60,
    0x84C87814A1F0AB72,
    0x8CC702081A6439EC,
    0x90BEFFFA23631E28,
    0xA4506CEBDE82BDE9,
    0xBEF9A3F7B2C67915,
    0xC67178F2E372532B,
    0xCA273ECEEA26619C,
    0xD186B8C721C0C207,
    0xEADA7DD6CDE0EB1E,
    0xF57D4F7FEE6ED178,
    0x06F067AA72176FBA,
    0x0A637DC5A2C898A6,
    0x113F9804BEF90DAE,
    0x1B710B35131C471B,
    0x28DB77F523047D84,
    0x32CAAB7B40C72493,
    0x3C9EBE0A15C9BEBC,
    0x431D67C49C100D4C,
    0x4CC5D4BECB3E42B6,
    0x597F299CFC657E2A,
    0x5FCB6FAB3AD6FAEC,
    0x6C44198C4A475817,
)

FALSIFICATION_CRITERIA: Dict[str, str] = {
    "braid_overhead_excessive": "Solovay-Kitaev factor > 10000 for epsilon=1e-10",
    "oracle_dominates": "Oracle T-count > 90% of total circuit",
    "fusion_qft_exponential": "QFT on fusion space requires more than 2^n braids",
    "topological_no_advantage": "Logical error rate exceeds surface code at same overhead",
    "adiabatic_too_slow": "Braid time > 1 microsecond",
    "measurement_fidelity_low": "Interferometric visibility < 80%",
    "thermal_noise_high": "Thermal anyon rate > 1e-3 per braid",
    "scaling_breakdown": "Resources grow super-polynomially with rounds",
}

Q_LAMBDA_PRIMITIVE_ARRAYS: Dict[str, Tuple[str, ...]] = {
    "sigma0": ("ROTR 28", "ROTR 34", "ROTR 39", "XOR", "XOR"),
    "sigma1": ("ROTR 14", "ROTR 18", "ROTR 41", "XOR", "XOR"),
    "lower_sigma0": ("ROTR 1", "ROTR 8", "SHR 7", "XOR", "XOR"),
    "lower_sigma1": ("ROTR 19", "ROTR 61", "SHR 6", "XOR", "XOR"),
    "choice": ("AND x y", "NOT x", "AND not_x z", "XOR"),
    "majority": ("AND x y", "AND x z", "AND y z", "XOR", "XOR"),
    "add64": ("MAJ forward", "SUM", "UMA reverse"),
}


@dataclass(frozen=True)
class ArrayManifest:
    name: str
    length: int
    word_bits: int
    digest_bits: int


def sha520_array_manifest() -> Dict[str, ArrayManifest]:
    return {
        "SHA520_IV_520": ArrayManifest("SHA520_IV_520", len(SHA520_IV_520), 64, 520),
        "SHA520_K_80": ArrayManifest("SHA520_K_80", len(SHA520_K_80), 64, 520),
        "SHA520_ROUNDS": ArrayManifest("SHA520_ROUNDS", len(SHA520_ROUNDS), 16, 520),
    }


def words_to_bits(words: Tuple[int, ...], bit_limit: int | None = None) -> List[int]:
    bits: List[int] = []
    for word in words:
        for offset in range(63, -1, -1):
            bits.append((word >> offset) & 1)
    return bits if bit_limit is None else bits[:bit_limit]
