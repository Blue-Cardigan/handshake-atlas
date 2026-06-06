"""Evolutionary view: how a handshake fares as an agent in a population.

Everything here is deterministic and analytic -- the strategies are deterministic, so
each pairwise match has a fixed score, and we use the closed-form frequency-dependent
Moran fixation probability (Nowak et al. 2004) rather than stochastic simulation. That
makes every evolutionary invariant exactly reproducible (no RNG).

Two invariants, each tied to a result in the literature:

* ``invade_alld`` -- fixation probability of a single handshake mutant in a population of
  unconditional defectors. This is the invasion-of-defectors test under which Knight et
  al. (2018) saw handshakes emerge. A handshake invades only if the mutual-recognition
  bonus (cooperate forever with a copy) outweighs the *probe cost* of exposing the Good
  bits of its prefix to defectors.

* ``mimic_fixation`` -- fixation probability of a *mimic* mutant (echoes the prefix, then
  defects forever) invading a population of the handshake itself. This operationalises
  Robson's (1990) central tension: a costless recognition signal is invadable by a cheat
  that shows the signal and defects. Magnitude discriminates how badly each handshake
  bleeds to mimics.
"""

from __future__ import annotations

from dataclasses import dataclass

from .handshake import BAD, GOOD, Handshake

# Standard prisoner's dilemma payoffs: T > R > P > S and 2R > T + S.
R, S, T, P = 3.0, 0.0, 5.0, 1.0


def _payoff(me: int, opp: int) -> float:
    if me == GOOD:
        return R if opp == GOOD else S
    return T if opp == GOOD else P


class Player:
    """A deterministic IPD strategy. ``move`` sees the opponent's move history."""

    def move(self, opp_history: list[int]) -> int:  # pragma: no cover - interface
        raise NotImplementedError


# Post-recognition regimes. The classical secret handshake cooperates unconditionally
# once it recognises a copy ("coop"); the vigilant variants instead police the recognised
# partner, which is what lets them punish a mimic that defects after being recognised.
REGIMES = ("coop", "grim", "tft")


class HandshakePlayer(Player):
    """Gated handshake with a configurable post-recognition regime.

    Before/without recognition the behaviour is fixed (play the prefix, then defect
    forever if the opponent did not echo it). After recognition:

    * ``coop`` -- cooperate forever (Robson's costless handshake; mimic-exploitable).
    * ``grim`` -- cooperate until the recognised partner defects once, then defect forever.
    * ``tft``  -- cooperate, then mirror the partner's previous move (forgiving).
    """

    def __init__(self, h: Handshake, regime: str = "coop") -> None:
        self.p = h.prefix
        self.k = h.length
        if regime not in REGIMES:
            raise ValueError(f"unknown regime {regime!r}")
        self.regime = regime

    def move(self, opp_history: list[int]) -> int:
        r = len(opp_history)
        if r < self.k:
            return self.p[r]
        if tuple(opp_history[: self.k]) != self.p:
            return BAD  # not recognised -> defect forever
        post = opp_history[self.k :]  # partner's moves after the recognition window
        if self.regime == "coop":
            return GOOD
        if self.regime == "grim":
            return BAD if any(m == BAD for m in post) else GOOD
        return post[-1] if post else GOOD  # tft


class MimicPlayer(Player):
    """Echoes the handshake's prefix to get recognised, then defects forever."""

    def __init__(self, h: Handshake) -> None:
        self.p = h.prefix
        self.k = h.length

    def move(self, opp_history: list[int]) -> int:
        r = len(opp_history)
        return self.p[r] if r < self.k else BAD


class AllD(Player):
    def move(self, opp_history: list[int]) -> int:
        return BAD


class AllC(Player):
    def move(self, opp_history: list[int]) -> int:
        return GOOD


class TitForTat(Player):
    def move(self, opp_history: list[int]) -> int:
        return GOOD if not opp_history else opp_history[-1]


def play_match(a: Player, b: Player, rounds: int) -> tuple[float, float]:
    """Return mean per-round payoff to ``a`` and ``b`` over ``rounds`` rounds."""
    hist_a: list[int] = []
    hist_b: list[int] = []
    score_a = 0.0
    score_b = 0.0
    for _ in range(rounds):
        ma = a.move(hist_b)
        mb = b.move(hist_a)
        score_a += _payoff(ma, mb)
        score_b += _payoff(mb, ma)
        hist_a.append(ma)
        hist_b.append(mb)
    return score_a / rounds, score_b / rounds


def moran_fixation(a: float, b: float, c: float, d: float, n: int, w: float) -> float:
    """Closed-form fixation probability of one type-A mutant among ``n``-1 type-B.

    Payoffs: a = A-vs-A, b = A-vs-B, c = B-vs-A, d = B-vs-B. ``w`` is selection
    intensity. Neutral drift gives 1/n.
    """
    prod = 1.0
    total = 0.0
    for i in range(1, n):
        pi_a = ((i - 1) * a + (n - i) * b) / (n - 1)
        pi_b = (i * c + (n - i - 1) * d) / (n - 1)
        f_a = 1 - w + w * pi_a
        f_b = 1 - w + w * pi_b
        prod *= f_b / f_a
        total += prod
    return 1.0 / (1.0 + total)


def mimic_fixation(
    h: Handshake, regime: str, population: int, rounds: int, selection: float
) -> float:
    """Fixation probability of a mimic (echo prefix, then defect) invading a population
    of the handshake running ``regime`` after recognition."""

    def hp() -> HandshakePlayer:
        return HandshakePlayer(h, regime)

    m_self, _ = play_match(MimicPlayer(h), MimicPlayer(h), rounds)
    m_vs_h, h_vs_m = play_match(MimicPlayer(h), hp(), rounds)
    self_pay, _ = play_match(hp(), hp(), rounds)
    return moran_fixation(m_self, m_vs_h, h_vs_m, self_pay, population, selection)


@dataclass(frozen=True)
class EvolutionProfile:
    self_payoff: float  # per-round payoff of the handshake against a copy of itself
    payoff_vs_alld: float  # per-round payoff against unconditional defectors (probe cost)
    invade_alld: float  # fixation prob of the handshake invading an AllD population
    invade_alld_favoured: bool  # invade_alld > neutral (1/n)
    mimic_fixation: float  # fixation prob of a mimic vs the unconditional (coop) handshake
    mimic_resistant: bool  # mimic_fixation < neutral (rare -- Robson's tension)
    # mimic-resistance under vigilant post-recognition regimes:
    mimic_fixation_by_regime: dict[str, float]
    mimic_resistant_by_regime: dict[str, bool]
    neutral: float  # 1/n, the drift baseline


def profile_evolution(
    h: Handshake, population: int = 20, rounds: int = 200, selection: float = 0.1
) -> EvolutionProfile:
    n = population
    neutral = 1.0 / n

    hp = HandshakePlayer(h)
    self_payoff, _ = play_match(hp, HandshakePlayer(h), rounds)
    d_alld, _ = play_match(AllD(), AllD(), rounds)
    h_vs_d, d_vs_h = play_match(HandshakePlayer(h), AllD(), rounds)

    # Handshake (A) invading AllD (B).
    invade_alld = moran_fixation(self_payoff, h_vs_d, d_vs_h, d_alld, n, selection)

    # Mimic resistance under each post-recognition regime.
    fix_by_regime = {
        regime: mimic_fixation(h, regime, n, rounds, selection) for regime in REGIMES
    }
    res_by_regime = {regime: fix < neutral for regime, fix in fix_by_regime.items()}

    return EvolutionProfile(
        self_payoff=self_payoff,
        payoff_vs_alld=h_vs_d,
        invade_alld=invade_alld,
        invade_alld_favoured=invade_alld > neutral,
        mimic_fixation=fix_by_regime["coop"],
        mimic_resistant=res_by_regime["coop"],
        mimic_fixation_by_regime=fix_by_regime,
        mimic_resistant_by_regime=res_by_regime,
        neutral=neutral,
    )
