"""Command line: build the atlas, or inspect a single handshake."""

from __future__ import annotations

import argparse
import json

from .atlas import build_atlas, write_atlas
from .cluster import classify_family
from .evolution import profile_evolution
from .handshake import Handshake
from .profile import profile_handshake


def _cmd_build(args: argparse.Namespace) -> None:
    atlas = build_atlas(
        struct_max=args.struct_max,
        evo_max=args.evo_max,
        min_length=args.min_length,
        population=args.population,
        rounds=args.rounds,
        selection=args.selection,
        progress=True,
    )
    write_atlas(atlas, args.out)
    meta = atlas["meta"]
    print(f"wrote {meta['n_handshakes']} handshakes -> {args.out}")
    for name, info in meta["families"].items():
        print(f"  {name:13s} {info['count']}")


def _cmd_inspect(args: argparse.Namespace) -> None:
    h = Handshake.from_str(args.handshake)
    prof = profile_handshake(h)
    out = {
        "label": prof.label,
        "length": prof.length,
        "family": classify_family(prof),
        "peak_sidelobe": prof.peak_sidelobe,
        "merit_factor": None if prof.merit_factor == float("inf") else prof.merit_factor,
        "is_barker": prof.is_barker,
        "longest_border": prof.longest_border,
        "shortest_period": prof.shortest_period,
        "is_unbordered": prof.is_unbordered,
        "lz76": prof.lz76,
        "linear_complexity": prof.linear_complexity,
        "distinct_factors": prof.distinct_factors,
        "bit_entropy": round(prof.bit_entropy, 4),
        "min_automaton_states": prof.min_automaton_states,
    }
    if not args.no_evolution:
        ev = profile_evolution(h)
        out["evolution"] = {
            "self_payoff": round(ev.self_payoff, 4),
            "payoff_vs_alld": round(ev.payoff_vs_alld, 4),
            "invade_alld": ev.invade_alld,
            "invade_alld_favoured": ev.invade_alld_favoured,
            "mimic_fixation": ev.mimic_fixation,
            "mimic_resistant": ev.mimic_resistant,
            "mimic_fixation_by_regime": {
                r: round(v, 4) for r, v in ev.mimic_fixation_by_regime.items()
            },
            "mimic_resistant_by_regime": ev.mimic_resistant_by_regime,
            "neutral": ev.neutral,
        }
    print(json.dumps(out, indent=2))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="handshake-atlas")
    sub = parser.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="enumerate, profile, classify, export the atlas")
    b.add_argument("--struct-max", type=int, default=10, dest="struct_max")
    b.add_argument("--evo-max", type=int, default=8, dest="evo_max")
    b.add_argument("--min-length", type=int, default=1, dest="min_length")
    b.add_argument("--population", type=int, default=20)
    b.add_argument("--rounds", type=int, default=200)
    b.add_argument("--selection", type=float, default=0.1)
    b.add_argument("--out", default="web/data/atlas.json")
    b.set_defaults(func=_cmd_build)

    i = sub.add_parser("inspect", help="profile a single handshake (e.g. GGBBGB)")
    i.add_argument("handshake")
    i.add_argument("--no-evolution", action="store_true", dest="no_evolution")
    i.set_defaults(func=_cmd_inspect)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
