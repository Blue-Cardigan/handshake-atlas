"""The handshake object: a recognition prefix wrapped in a gated long-run regime.

A *secret handshake* in the iterated prisoner's dilemma is the strategy studied by
Robson (1990) and shown to evolve spontaneously by Knight et al. (2018):

    1. For the first ``k`` rounds, play a fixed recognition prefix ``p in {Good, Bad}^k``,
       regardless of the opponent.
    2. After the prefix, look at the opponent's first ``k`` moves. If they exactly equal
       ``p`` (the opponent "knew the handshake" / looks like a copy of me), cooperate
       forever. Otherwise defect forever.

The prefix fully determines the strategy, so the *space of handshakes* is the space of
binary prefixes. We nonetheless profile each handshake on three levels — as a string,
as a realized finite automaton, and (elsewhere) as an evolutionary agent — because the
interesting structure lives in how those three views diverge.

Encoding convention used throughout the package:

    bit 1 == Good == Cooperate (mapped to autocorrelation value +1)
    bit 0 == Bad  == Defect    (mapped to autocorrelation value -1)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property

GOOD = 1  # Cooperate
BAD = 0  # Defect

_BIT_TO_CHAR = {GOOD: "G", BAD: "B"}
_CHAR_TO_BIT = {"G": GOOD, "B": BAD, "C": GOOD, "D": BAD, "1": GOOD, "0": BAD}


@dataclass(frozen=True)
class Handshake:
    """A secret handshake, identified by its recognition prefix.

    Attributes:
        prefix: tuple of bits (1=Good/Cooperate, 0=Bad/Defect), length >= 1.
    """

    prefix: tuple[int, ...]

    def __post_init__(self) -> None:
        if len(self.prefix) == 0:
            raise ValueError("handshake prefix must be non-empty")
        if any(b not in (GOOD, BAD) for b in self.prefix):
            raise ValueError(f"prefix bits must be 0 or 1, got {self.prefix!r}")

    # -- construction helpers ------------------------------------------------

    @classmethod
    def from_str(cls, s: str) -> "Handshake":
        """Parse from a string of G/B (or C/D, or 1/0). Whitespace is ignored."""
        bits = tuple(_CHAR_TO_BIT[ch] for ch in s.strip() if not ch.isspace())
        return cls(bits)

    @classmethod
    def from_int(cls, value: int, length: int) -> "Handshake":
        """The ``value``-th length-``length`` handshake in big-endian bit order."""
        if value < 0 or value >= (1 << length):
            raise ValueError(f"value {value} out of range for length {length}")
        bits = tuple((value >> (length - 1 - i)) & 1 for i in range(length))
        return cls(bits)

    # -- views ---------------------------------------------------------------

    @property
    def length(self) -> int:
        return len(self.prefix)

    @cached_property
    def label(self) -> str:
        """Canonical G/B label, e.g. ``GB`` for tit-for-tat-flavoured handshake."""
        return "".join(_BIT_TO_CHAR[b] for b in self.prefix)

    @cached_property
    def signed(self) -> tuple[int, ...]:
        """Map to +/-1 for autocorrelation-style invariants (Good=+1, Bad=-1)."""
        return tuple(1 if b == GOOD else -1 for b in self.prefix)

    @cached_property
    def index(self) -> int:
        """Big-endian integer index within its length stratum."""
        v = 0
        for b in self.prefix:
            v = (v << 1) | b
        return v

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return self.label

    def __len__(self) -> int:
        return self.length

    # -- realized automaton --------------------------------------------------

    def automaton(self) -> "MooreMachine":
        """Build the Moore machine that realizes the gated handshake strategy.

        Input alphabet is the opponent's move at each round (Good/Bad). Output of a
        state is *our* move when we are in that state. The minimized size of this
        machine is the Rubinstein (1986) strategy-complexity invariant.
        """
        return build_handshake_automaton(self)


# ---------------------------------------------------------------------------
# Moore machine + minimization
# ---------------------------------------------------------------------------


@dataclass
class MooreMachine:
    """A deterministic Moore machine over the binary opponent-move alphabet.

    states: list of state ids (ints, 0 is the start state).
    output: output[s] is our move (Good/Bad) emitted in state s.
    trans:  trans[s][a] is the next state on reading opponent move a in {0, 1}.
    """

    output: list[int]
    trans: list[list[int]]
    start: int = 0

    @property
    def n_states(self) -> int:
        return len(self.output)

    def reachable(self) -> "MooreMachine":
        """Restrict to states reachable from the start (renumbered from 0)."""
        seen: dict[int, int] = {}
        order: list[int] = []
        stack = [self.start]
        while stack:
            s = stack.pop()
            if s in seen:
                continue
            seen[s] = len(order)
            order.append(s)
            for a in (0, 1):
                nxt = self.trans[s][a]
                if nxt not in seen:
                    stack.append(nxt)
        output = [self.output[s] for s in order]
        trans = [[seen[self.trans[s][a]] for a in (0, 1)] for s in order]
        return MooreMachine(output=output, trans=trans, start=0)

    def minimized(self) -> "MooreMachine":
        """Partition-refinement (Moore/Hopcroft) minimization of a reachable machine.

        Initial partition groups states by output; refine until stable.
        """
        m = self.reachable()
        n = m.n_states
        # block[s] = current block id of state s
        block = list(m.output)  # group by output first
        # normalize block ids to a dense range
        block = _densify(block)
        while True:
            # signature of each state: (current block, block of each successor)
            sig: list[tuple[int, int, int]] = [
                (block[s], block[m.trans[s][0]], block[m.trans[s][1]])
                for s in range(n)
            ]
            new_block = _densify_by_signature(sig)
            if new_block == block:
                break
            block = new_block
        n_blocks = max(block) + 1
        # representative state per block (smallest id) defines output and transitions
        rep: list[int] = [-1] * n_blocks
        for s in range(n):
            if rep[block[s]] == -1:
                rep[block[s]] = s
        output = [m.output[rep[b]] for b in range(n_blocks)]
        trans = [[block[m.trans[rep[b]][a]] for a in (0, 1)] for b in range(n_blocks)]
        return MooreMachine(output=output, trans=trans, start=block[m.start])


def _densify(values: list[int]) -> list[int]:
    """Map arbitrary integer labels to a dense 0..k-1 range, order of first appearance."""
    seen: dict[int, int] = {}
    out: list[int] = []
    for v in values:
        if v not in seen:
            seen[v] = len(seen)
        out.append(seen[v])
    return out


def _densify_by_signature(sigs: list[tuple]) -> list[int]:
    seen: dict[tuple, int] = {}
    out: list[int] = []
    for sig in sigs:
        if sig not in seen:
            seen[sig] = len(seen)
        out.append(seen[sig])
    return out


def build_handshake_automaton(h: Handshake) -> MooreMachine:
    """Construct the (non-minimized) Moore machine for handshake ``h``.

    State space (before minimization):
      - prefix states (i, matched) for i in 0..k-1, matched in {True, False}:
        we are about to play round i; ``matched`` records whether the opponent has
        echoed the prefix exactly so far. Output = p[i].
      - two absorbing terminal states: COOP (output Good) and DEF (output Bad),
        entered after the prefix depending on whether the opponent matched throughout.

    We always emit the prefix during rounds 0..k-1 regardless of the opponent; the
    opponent's moves only steer us between the COOP and DEF terminals afterwards.
    """
    p = h.prefix
    k = h.length

    # Index prefix states: id = 2*i + (0 if matched else 1); terminals appended after.
    def pid(i: int, matched: bool) -> int:
        return 2 * i + (0 if matched else 1)

    coop_state = 2 * k
    def_state = 2 * k + 1
    n = 2 * k + 2

    output = [BAD] * n
    trans = [[0, 0] for _ in range(n)]

    for i in range(k):
        for matched in (True, False):
            s = pid(i, matched)
            output[s] = p[i]
            for a in (BAD, GOOD):  # opponent's move this round
                still_matched = matched and (a == p[i])
                if i + 1 < k:
                    nxt = pid(i + 1, still_matched)
                else:
                    nxt = coop_state if still_matched else def_state
                trans[s][a] = nxt

    output[coop_state] = GOOD
    output[def_state] = BAD
    for a in (BAD, GOOD):
        trans[coop_state][a] = coop_state
        trans[def_state][a] = def_state

    start = pid(0, True)
    machine = MooreMachine(output=output, trans=trans, start=start)
    return machine
