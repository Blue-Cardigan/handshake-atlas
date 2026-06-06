"""Self-overlap (bordering) invariants -- the Guibas-Odlyzko correlation.

A handshake is vulnerable to a *mimic* that echoes part of it out of phase. The relevant
structural property is how much the string overlaps shifts of itself:

    overlap[k] = 1  iff  prefix[0 : N-k] == prefix[k : N]   (the length-(N-k) prefix
                        equals the length-(N-k) suffix)  -- i.e. k is a period.

overlap[0] is always 1. A string with no other overlaps is *unbordered* (bifix-free):
maximally resistant to partial self-impersonation and to desynchronisation. This is the
binary correlation of Guibas & Odlyzko (1981).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OverlapProfile:
    correlation: tuple[int, ...]  # overlap[k] for k = 0 .. N-1 (overlap[0] == 1)
    borders: tuple[int, ...]  # lengths of proper borders (prefix==suffix), descending
    longest_border: int  # length of the longest proper border (0 if unbordered)
    shortest_period: int  # smallest period; equals N for an unbordered string
    is_unbordered: bool  # no proper border -> bifix-free


def _prefix_function(s: str) -> list[int]:
    """Standard KMP failure function: pi[i] = length of longest proper border of s[:i+1]."""
    n = len(s)
    pi = [0] * n
    k = 0
    for i in range(1, n):
        while k > 0 and s[i] != s[k]:
            k = pi[k - 1]
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    return pi


def overlap_profile(bits: tuple[int, ...]) -> OverlapProfile:
    s = "".join(str(x) for x in bits)
    n = len(s)
    correlation = [1] + [
        1 if s[: n - k] == s[k:] else 0 for k in range(1, n)
    ]
    # borders via chasing the prefix-function links from the full string
    borders: list[int] = []
    if n > 0:
        pi = _prefix_function(s)
        b = pi[n - 1]
        while b > 0:
            borders.append(b)
            b = pi[b - 1]
    longest_border = borders[0] if borders else 0
    shortest_period = n - longest_border  # classic period = N - longest border
    return OverlapProfile(
        correlation=tuple(correlation),
        borders=tuple(borders),
        longest_border=longest_border,
        shortest_period=shortest_period,
        is_unbordered=(longest_border == 0),
    )
