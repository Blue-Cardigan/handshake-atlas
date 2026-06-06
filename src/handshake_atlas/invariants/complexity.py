"""Per-string complexity invariants: compressibility, predictability, richness.

These are the standard single-sequence complexity measures (LZ76 compressibility,
Berlekamp-Massey linear complexity, factor/subword complexity). They are computed on
the raw 0/1 prefix. We deliberately reuse well-established definitions rather than
inventing new ones -- the novelty of the atlas is the *joint* profile, not the metrics.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import log2


@dataclass(frozen=True)
class ComplexityProfile:
    lz76: int  # Lempel-Ziv 1976 complexity (distinct factors in exhaustive history)
    linear_complexity: int  # length of shortest LFSR generating the bits (over GF(2))
    distinct_factors: int  # total number of distinct non-empty substrings
    factor_profile: tuple[int, ...]  # p(L) for L = 1 .. N
    bit_entropy: float  # Shannon entropy (bits) of the 0/1 frequencies


def lz76(bits: tuple[int, ...]) -> int:
    """Kaspar-Schuster computation of Lempel-Ziv (1976) complexity."""
    n = len(bits)
    if n == 0:
        return 0
    i = 0
    c = 1
    u = 1
    v = 1
    vmax = 1
    while u + v <= n:
        if bits[i + v - 1] == bits[u + v - 1]:
            v += 1
        else:
            vmax = max(v, vmax)
            i += 1
            if i == u:
                c += 1
                u += vmax
                v = 1
                i = 0
                vmax = 1
            else:
                v = 1
    if v != 1:
        c += 1
    return c


def linear_complexity(bits: tuple[int, ...]) -> int:
    """Berlekamp-Massey over GF(2): length of the shortest LFSR generating ``bits``."""
    n = len(bits)
    c = [0] * n
    b = [0] * n
    c[0] = b[0] = 1
    ell = 0
    m = -1
    for i in range(n):
        d = bits[i]
        for j in range(1, ell + 1):
            d ^= c[j] & bits[i - j]
        if d == 1:
            t = c[:]
            shift = i - m
            for j in range(0, n - shift):
                c[j + shift] ^= b[j]
            if 2 * ell <= i:
                ell = i + 1 - ell
                m = i
                b = t
    return ell


def factor_complexity(bits: tuple[int, ...]) -> tuple[int, ...]:
    """p(L) = number of distinct length-L substrings, for L = 1 .. N."""
    s = "".join(str(x) for x in bits)
    n = len(s)
    profile: list[int] = []
    for length in range(1, n + 1):
        factors = {s[i : i + length] for i in range(0, n - length + 1)}
        profile.append(len(factors))
    return tuple(profile)


def bit_entropy(bits: tuple[int, ...]) -> float:
    n = len(bits)
    if n == 0:
        return 0.0
    ones = sum(bits)
    p = ones / n
    if p in (0.0, 1.0):
        return 0.0
    return -(p * log2(p) + (1 - p) * log2(1 - p))


def complexity_profile(bits: tuple[int, ...]) -> ComplexityProfile:
    fp = factor_complexity(bits)
    return ComplexityProfile(
        lz76=lz76(bits),
        linear_complexity=linear_complexity(bits),
        distinct_factors=sum(fp),
        factor_profile=fp,
        bit_entropy=bit_entropy(bits),
    )
