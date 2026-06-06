"""Assemble the joint structural-invariant profile of a single handshake.

This is the core artifact of the atlas: for each handshake we compute, in one pass, the
string view (autocorrelation, self-overlap, complexity) and the automaton view (minimal
Moore-machine size = Rubinstein strategy complexity). The evolutionary view is added
separately by :mod:`handshake_atlas.evolution` because it is far more expensive.
"""

from __future__ import annotations

from dataclasses import dataclass

from .handshake import Handshake
from .invariants.autocorrelation import autocorrelation
from .invariants.complexity import complexity_profile
from .invariants.overlap import overlap_profile


@dataclass(frozen=True)
class HandshakeProfile:
    label: str
    length: int
    index: int

    # autocorrelation / shift-mimic resistance
    peak_sidelobe: int
    merit_factor: float
    is_barker: bool

    # self-overlap / bordering
    longest_border: int
    shortest_period: int
    is_unbordered: bool

    # complexity
    lz76: int
    linear_complexity: int
    distinct_factors: int
    bit_entropy: float

    # automaton (Rubinstein complexity)
    min_automaton_states: int

    # raw vectors retained for the explorer / deeper analysis
    sidelobes: tuple[int, ...]
    correlation: tuple[int, ...]
    factor_profile: tuple[int, ...]

    def feature_vector(self) -> list[float]:
        """Length-normalised numeric features used for taxonomy clustering.

        Normalising by length lets handshakes of different lengths share a feature space
        so families are defined by *shape*, not raw size.
        """
        n = self.length
        denom = n if n > 0 else 1
        return [
            self.peak_sidelobe / denom,
            0.0 if self.merit_factor == float("inf") else min(self.merit_factor, 100.0) / 100.0,
            float(self.is_barker),
            self.longest_border / denom,
            self.shortest_period / denom,
            float(self.is_unbordered),
            self.lz76 / denom,
            self.linear_complexity / denom,
            self.distinct_factors / (denom * (denom + 1) / 2),  # vs max distinct factors
            self.bit_entropy,
            self.min_automaton_states / (2 * denom + 2),  # vs un-minimized size
        ]


def profile_handshake(h: Handshake) -> HandshakeProfile:
    ac = autocorrelation(h.signed)
    ov = overlap_profile(h.prefix)
    cx = complexity_profile(h.prefix)
    min_states = h.automaton().minimized().n_states
    return HandshakeProfile(
        label=h.label,
        length=h.length,
        index=h.index,
        peak_sidelobe=ac.peak_sidelobe,
        merit_factor=ac.merit_factor,
        is_barker=ac.is_barker,
        longest_border=ov.longest_border,
        shortest_period=ov.shortest_period,
        is_unbordered=ov.is_unbordered,
        lz76=cx.lz76,
        linear_complexity=cx.linear_complexity,
        distinct_factors=cx.distinct_factors,
        bit_entropy=cx.bit_entropy,
        min_automaton_states=min_states,
        sidelobes=ac.sidelobes,
        correlation=ov.correlation,
        factor_profile=cx.factor_profile,
    )
