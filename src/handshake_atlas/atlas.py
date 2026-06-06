"""Build the atlas: enumerate -> profile -> evolve -> classify -> export.

The atlas is the central reusable artifact. Structural invariants are cheap and computed
for every handshake up to ``struct_max``; the evolutionary invariants are far more
expensive, so they are computed only up to ``evo_max`` (and that cap is reported in the
metadata, never silently applied).
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from typing import Any

from .cluster import FAMILY_DESCRIPTIONS, classify_family
from .enumerate import count_up_to, enumerate_up_to
from .evolution import profile_evolution
from .profile import HandshakeProfile, profile_handshake
from .handshake import Handshake


def _jsonable(value: float) -> Any:
    if isinstance(value, float) and math.isinf(value):
        return None
    return value


@dataclass
class AtlasRecord:
    label: str
    length: int
    index: int
    family: str
    # structural invariants
    peak_sidelobe: int
    merit_factor: float | None
    is_barker: bool
    longest_border: int
    shortest_period: int
    is_unbordered: bool
    lz76: int
    linear_complexity: int
    distinct_factors: int
    bit_entropy: float
    min_automaton_states: int
    raw_automaton_states: int
    # evolutionary invariants (None beyond evo_max)
    self_payoff: float | None
    payoff_vs_alld: float | None
    invade_alld: float | None
    invade_alld_favoured: bool | None
    mimic_fixation: float | None
    mimic_resistant: bool | None
    # mimic-resistance under vigilant post-recognition regimes
    mimic_fixation_grim: float | None
    mimic_fixation_tft: float | None
    mimic_resistant_grim: bool | None
    mimic_resistant_tft: bool | None
    # retained vectors for the explorer
    sidelobes: list[int]
    correlation: list[int]


def build_record(
    h: Handshake, prof: HandshakeProfile, with_evolution: bool, **evo_kwargs
) -> AtlasRecord:
    family = classify_family(prof)
    raw_states = h.automaton().reachable().n_states
    rec = AtlasRecord(
        label=prof.label,
        length=prof.length,
        index=prof.index,
        family=family,
        peak_sidelobe=prof.peak_sidelobe,
        merit_factor=_jsonable(prof.merit_factor),
        is_barker=prof.is_barker,
        longest_border=prof.longest_border,
        shortest_period=prof.shortest_period,
        is_unbordered=prof.is_unbordered,
        lz76=prof.lz76,
        linear_complexity=prof.linear_complexity,
        distinct_factors=prof.distinct_factors,
        bit_entropy=round(prof.bit_entropy, 6),
        min_automaton_states=prof.min_automaton_states,
        raw_automaton_states=raw_states,
        self_payoff=None,
        payoff_vs_alld=None,
        invade_alld=None,
        invade_alld_favoured=None,
        mimic_fixation=None,
        mimic_resistant=None,
        mimic_fixation_grim=None,
        mimic_fixation_tft=None,
        mimic_resistant_grim=None,
        mimic_resistant_tft=None,
        sidelobes=list(prof.sidelobes),
        correlation=list(prof.correlation),
    )
    if with_evolution:
        ev = profile_evolution(h, **evo_kwargs)
        rec.self_payoff = round(ev.self_payoff, 6)
        rec.payoff_vs_alld = round(ev.payoff_vs_alld, 6)
        rec.invade_alld = ev.invade_alld
        rec.invade_alld_favoured = ev.invade_alld_favoured
        rec.mimic_fixation = ev.mimic_fixation
        rec.mimic_resistant = ev.mimic_resistant
        rec.mimic_fixation_grim = ev.mimic_fixation_by_regime["grim"]
        rec.mimic_fixation_tft = ev.mimic_fixation_by_regime["tft"]
        rec.mimic_resistant_grim = ev.mimic_resistant_by_regime["grim"]
        rec.mimic_resistant_tft = ev.mimic_resistant_by_regime["tft"]
    return rec


def build_atlas(
    struct_max: int,
    evo_max: int = 0,
    min_length: int = 1,
    population: int = 20,
    rounds: int = 200,
    selection: float = 0.1,
    progress: bool = False,
) -> dict[str, Any]:
    """Build the full atlas dictionary, ready for JSON export."""
    if evo_max > struct_max:
        raise ValueError("evo_max cannot exceed struct_max")
    records: list[AtlasRecord] = []
    total = count_up_to(struct_max, min_length)
    done = 0
    for h in enumerate_up_to(struct_max, min_length):
        prof = profile_handshake(h)
        rec = build_record(
            h,
            prof,
            with_evolution=(h.length <= evo_max),
            population=population,
            rounds=rounds,
            selection=selection,
        )
        records.append(rec)
        done += 1
        if progress and done % 2000 == 0:
            print(f"  profiled {done}/{total}")

    family_counts: dict[str, int] = {}
    for rec in records:
        family_counts[rec.family] = family_counts.get(rec.family, 0) + 1

    return {
        "meta": {
            "version": "0.1.0",
            "struct_max": struct_max,
            "evo_max": evo_max,
            "min_length": min_length,
            "n_handshakes": len(records),
            "evolution": {
                "population": population,
                "rounds": rounds,
                "selection": selection,
                "payoffs": {"R": 3, "S": 0, "T": 5, "P": 1},
                "note": (
                    f"Evolutionary invariants computed for lengths <= {evo_max}; "
                    f"structural invariants for all lengths <= {struct_max}."
                ),
            },
            "families": {
                name: {"count": family_counts.get(name, 0), "description": desc}
                for name, desc in FAMILY_DESCRIPTIONS.items()
            },
        },
        "handshakes": [asdict(rec) for rec in records],
    }


def write_atlas(atlas: dict[str, Any], path: str) -> None:
    with open(path, "w") as fh:
        json.dump(atlas, fh, separators=(",", ":"))
