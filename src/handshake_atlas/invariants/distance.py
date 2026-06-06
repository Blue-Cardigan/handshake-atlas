"""Set-level Hamming-distance utilities.

Important honesty note: within a *full* length-k stratum every string has a
single-bit neighbour, so the minimum Hamming distance to the rest of the stratum is
trivially 1 for every handshake. Distance only becomes informative for a *selected*
subset -- a curated code, or a discovered family. These helpers are therefore used by
the taxonomy and validation layers (e.g. "how separated is the Barker family?"), not as
a per-handshake atlas column over the full enumeration.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..handshake import Handshake


def hamming(a: tuple[int, ...], b: tuple[int, ...]) -> int:
    if len(a) != len(b):
        raise ValueError("Hamming distance requires equal-length sequences")
    return sum(x != y for x, y in zip(a, b))


def min_distance_of_set(handshakes: Sequence[Handshake]) -> int:
    """Minimum pairwise Hamming distance within a set of equal-length handshakes."""
    items = list(handshakes)
    if len(items) < 2:
        raise ValueError("need at least two handshakes")
    length = items[0].length
    if any(h.length != length for h in items):
        raise ValueError("all handshakes must share a length")
    best = length
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            d = hamming(items[i].prefix, items[j].prefix)
            if d < best:
                best = d
                if best == 1:
                    return 1
    return best


def nearest_in_set(
    target: Handshake, pool: Sequence[Handshake]
) -> tuple[Handshake | None, int]:
    """Nearest handshake to ``target`` within ``pool`` (excluding itself)."""
    best_h: Handshake | None = None
    best_d = target.length + 1
    for h in pool:
        if h.prefix == target.prefix:
            continue
        d = hamming(target.prefix, h.prefix)
        if d < best_d:
            best_d, best_h = d, h
    return best_h, (best_d if best_h is not None else 0)
