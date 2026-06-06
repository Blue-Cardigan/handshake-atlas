"""Aperiodic autocorrelation invariants.

For a handshake mapped to a +/-1 sequence ``a`` of length ``N`` (Good=+1, Bad=-1),
the aperiodic autocorrelation at shift ``v`` (1 <= v < N) is

    c_v = sum_{j=0}^{N-1-v} a[j] * a[j+v].

Small off-peak sidelobes mean the prefix does not resemble shifted copies of itself,
i.e. it is hard for a mimic to partially echo it out of phase. Barker codes are the
optimum (|c_v| <= 1 for all v); the continuous quality measure when no perfect code
exists is the *merit factor* F = N^2 / (2 * sum_v c_v^2).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import inf


@dataclass(frozen=True)
class AutocorrelationProfile:
    sidelobes: tuple[int, ...]  # c_v for v = 1 .. N-1
    peak_sidelobe: int  # max |c_v|, 0 for length-1
    merit_factor: float  # N^2 / (2 * sum c_v^2); inf when all sidelobes vanish
    is_barker: bool  # peak_sidelobe <= 1


def autocorrelation(signed: tuple[int, ...]) -> AutocorrelationProfile:
    n = len(signed)
    sidelobes: list[int] = []
    for v in range(1, n):
        c = sum(signed[j] * signed[j + v] for j in range(n - v))
        sidelobes.append(c)
    peak = max((abs(c) for c in sidelobes), default=0)
    ss = sum(c * c for c in sidelobes)
    merit = (n * n) / (2 * ss) if ss > 0 else inf
    return AutocorrelationProfile(
        sidelobes=tuple(sidelobes),
        peak_sidelobe=peak,
        merit_factor=merit,
        is_barker=peak <= 1,
    )
