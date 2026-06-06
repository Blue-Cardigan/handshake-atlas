"""The minimized Moore machine must reproduce the gated handshake strategy exactly."""

from itertools import product

from handshake_atlas import GOOD, Handshake
from handshake_atlas.handshake import MooreMachine


def gated_reference(h: Handshake, opponent: tuple[int, ...]) -> list[int]:
    """Direct definition of the gated strategy, used as ground truth.

    We emit the prefix for the first k rounds, then -- if the opponent's first k moves
    equalled the prefix -- cooperate forever, else defect forever.
    """
    k = h.length
    p = h.prefix
    out: list[int] = []
    for r in range(len(opponent)):
        if r < k:
            out.append(p[r])
        else:
            matched = tuple(opponent[:k]) == p
            out.append(GOOD if matched else 0)
    return out


def run_machine(m: MooreMachine, opponent: tuple[int, ...]) -> list[int]:
    """Moore semantics: emit current state's output, then consume an opponent move."""
    s = m.start
    out: list[int] = []
    for a in opponent:
        out.append(m.output[s])
        s = m.trans[s][a]
    return out


def test_machine_matches_reference_and_minimization_preserves_behaviour():
    for k in range(1, 6):
        for v in range(1 << k):
            h = Handshake.from_int(v, k)
            raw = h.automaton()
            mini = raw.minimized()
            assert mini.n_states <= raw.reachable().n_states
            # exhaustively check all opponent histories up to length k+3
            for length in range(0, k + 4):
                for opp in product((0, 1), repeat=length):
                    ref = gated_reference(h, opp)
                    assert run_machine(raw, opp) == ref
                    assert run_machine(mini, opp) == ref


def test_minimal_automaton_size_is_a_nontrivial_invariant():
    # The minimized size must actually vary across handshakes of a fixed length --
    # otherwise it would be useless as a classifying invariant.
    sizes = {
        Handshake.from_int(v, 4).automaton().minimized().n_states for v in range(16)
    }
    assert len(sizes) > 1
    assert all(s >= 2 for s in sizes)
