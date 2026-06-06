"""A lean sequential-Bayesian model of the silent stages of courtship.

The handshake atlas treats recognition as exact-match and noise-free. The silent stages of
real courtship are the opposite: graded, noisy, and exploratory. An observer issues low-cost
probes (a glance, a held glance), watches whether they are reciprocated, escalates as
evidence accumulates, and either *approaches* (commits) when the posterior that the partner
is genuinely interested crosses an upper threshold, or *withdraws* (a deniable exit) when it
crosses a lower one. That is a sequential probability ratio test / optimal-stopping problem.
The information-greedy probe policy here is the epistemic-value term of active inference in
reduced form: pick the probe that most reduces uncertainty about the partner's type.

Three partner types:
    interested  -- reciprocates readily and welcomes escalation.
    mimic       -- reciprocates cheap probes (wants the attention) but balks at costly ones
                   (will not pay or commit): the recognition-layer analogue of the handshake
                   mimic from :mod:`handshake_atlas.evolution`.
    indifferent -- a low ambient base rate of reciprocation, regardless of the probe.

Low-intensity probes separate {interested, mimic} from indifferent; only high-intensity
(costly) probes separate interested from mimic. So escalation is required to expose a mimic
-- the same lesson as the atlas's vigilance result, now in the recognition layer rather than
the post-recognition strategy.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

TYPES = ("interested", "mimic", "indifferent")


def reciprocation_prob(type_name: str, intensity: float) -> float:
    """P(partner reciprocates | type, probe intensity ``x`` in [0, 1]), noise-free.

    interested rises with intensity; mimic collapses with it; indifferent stays low.
    """
    x = float(intensity)
    if type_name == "interested":
        p = 0.80 + 0.15 * x
    elif type_name == "mimic":
        p = 0.90 - 0.85 * x
    elif type_name == "indifferent":
        p = 0.15 - 0.05 * x
    else:
        raise ValueError(f"unknown type {type_name!r}")
    return float(np.clip(p, 0.01, 0.99))


def observed_prob(type_name: str, intensity: float, reliability: float) -> float:
    """Reciprocation probability after observation noise.

    ``reliability`` in (0.5, 1]: with probability ``reliability`` the true reciprocation is
    observed, otherwise the observation is a coin flip. Lower reliability pulls every signal
    toward 0.5 (less informative) -- the ambient-noise knob.
    """
    p = reciprocation_prob(type_name, intensity)
    return reliability * p + (1.0 - reliability) * 0.5


def _binary_entropy(p: float) -> float:
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return float(-(p * np.log2(p) + (1 - p) * np.log2(1 - p)))


# ---------------------------------------------------------------------------
# Probe (escalation) policies
# ---------------------------------------------------------------------------


def _expected_information_gain(
    posterior: np.ndarray,
    intensity: float,
    reliability: float,
    hypotheses: tuple[str, ...],
) -> float:
    """Mutual information I(type; reciprocation | intensity) under the current posterior."""
    probs = np.array([observed_prob(t, intensity, reliability) for t in hypotheses])
    p_recip = float(np.dot(posterior, probs))  # marginal P(r=1)
    h_marginal = _binary_entropy(p_recip)
    h_conditional = float(np.dot(posterior, [_binary_entropy(p) for p in probs]))
    return h_marginal - h_conditional


@dataclass(frozen=True)
class Policy:
    """How the observer chooses the next probe intensity.

    kind:
        "fixed"       -- always probe at ``level`` (the naive constant approacher).
        "ramp"        -- intensity climbs linearly, reaching 1 after ``ramp_len`` steps.
        "info_greedy" -- choose the intensity (from a grid) with the highest expected
                         information gain about the partner's type (the epistemic policy).
    """

    kind: str = "info_greedy"
    level: float = 0.2
    ramp_len: int = 8
    grid: int = 11
    cost_weight: float = 0.0  # penalty per unit probe intensity for info_greedy

    def probe(
        self,
        step: int,
        posterior: np.ndarray,
        reliability: float,
        hypotheses: tuple[str, ...],
    ) -> float:
        if self.kind == "fixed":
            return float(self.level)
        if self.kind == "ramp":
            return float(min(1.0, step / max(1, self.ramp_len)))
        if self.kind == "info_greedy":
            candidates = np.linspace(0.0, 1.0, self.grid)
            # Net epistemic value: information gain minus the cost of the probe. A positive
            # cost_weight makes the observer prefer cheap, deniable probes and escalate only
            # when ambiguity (interested vs mimic) is worth paying to resolve.
            scores = [
                _expected_information_gain(posterior, x, reliability, hypotheses)
                - self.cost_weight * x
                for x in candidates
            ]
            return float(candidates[int(np.argmax(scores))])
        raise ValueError(f"unknown policy kind {self.kind!r}")


# ---------------------------------------------------------------------------
# Sequential encounter
# ---------------------------------------------------------------------------


@dataclass
class Encounter:
    true_type: str
    decision: str  # "approach", "withdraw", or "timeout_withdraw"
    steps: int
    final_belief: float  # posterior P(interested) at stopping
    intensities: list[float] = field(default_factory=list)
    reciprocations: list[int] = field(default_factory=list)
    beliefs: list[float] = field(default_factory=list)

    @property
    def correct(self) -> bool:
        """Approaching is right only for a genuinely interested partner."""
        if self.true_type == "interested":
            return self.decision == "approach"
        return self.decision != "approach"  # withdrawing from mimic/indifferent is right


def simulate_encounter(
    true_type: str,
    policy: Policy,
    rng: np.random.Generator,
    *,
    theta_lo: float = 0.1,
    theta_hi: float = 0.9,
    max_steps: int = 20,
    reliability: float = 0.85,
    hypotheses: tuple[str, ...] = TYPES,
    prior: np.ndarray | None = None,
) -> Encounter:
    """Run one silent-stage encounter against a partner of ``true_type``.

    The observer entertains the partner types in ``hypotheses`` (a subset of ``TYPES``; an
    observer who omits ``"mimic"`` simply has no hypothesis that someone might fake interest).
    It probes per ``policy``, updates its posterior on each (noisy) reciprocation, and stops
    when P(interested) crosses ``theta_hi`` (approach) or ``theta_lo`` (withdraw), or at
    ``max_steps`` (a deniable timeout-withdraw). The world samples from ``true_type``, which
    need not be in ``hypotheses``.
    """
    if "interested" not in hypotheses:
        raise ValueError("hypotheses must include 'interested'")
    if prior is None:
        logpost = np.log(np.full(len(hypotheses), 1.0 / len(hypotheses)))
    else:
        logpost = np.log(np.asarray(prior, dtype=float))

    enc = Encounter(true_type=true_type, decision="timeout_withdraw", steps=max_steps,
                    final_belief=0.0)
    interested_idx = hypotheses.index("interested")

    for step in range(max_steps):
        posterior = _softmax(logpost)
        x = policy.probe(step, posterior, reliability, hypotheses)
        p_true = observed_prob(true_type, x, reliability)
        r = int(rng.random() < p_true)

        # Bayesian update over the entertained hypotheses.
        for i, t in enumerate(hypotheses):
            pt = observed_prob(t, x, reliability)
            logpost[i] += np.log(pt if r else (1.0 - pt))

        posterior = _softmax(logpost)
        p_interested = float(posterior[interested_idx])
        enc.intensities.append(x)
        enc.reciprocations.append(r)
        enc.beliefs.append(p_interested)

        if p_interested >= theta_hi:
            enc.decision, enc.steps, enc.final_belief = "approach", step + 1, p_interested
            return enc
        if p_interested <= theta_lo:
            enc.decision, enc.steps, enc.final_belief = "withdraw", step + 1, p_interested
            return enc

    enc.final_belief = enc.beliefs[-1] if enc.beliefs else 0.0
    return enc


def _softmax(log_weights: np.ndarray) -> np.ndarray:
    w = log_weights - np.max(log_weights)
    e = np.exp(w)
    return e / e.sum()


# ---------------------------------------------------------------------------
# Batch analysis
# ---------------------------------------------------------------------------


@dataclass
class Outcome:
    approach_rate: float
    withdraw_rate: float
    mean_steps: float
    n: int


def run_batch(
    true_type: str, policy: Policy, n: int, seed: int = 0, **kwargs
) -> Outcome:
    """Aggregate ``n`` encounters against ``true_type`` under ``policy``."""
    rng = np.random.default_rng(seed)
    approaches = withdraws = 0
    steps = 0
    for _ in range(n):
        enc = simulate_encounter(true_type, policy, rng, **kwargs)
        approaches += enc.decision == "approach"
        withdraws += enc.decision != "approach"
        steps += enc.steps
    return Outcome(approaches / n, withdraws / n, steps / n, n)


def demo(n: int = 2000, seed: int = 0) -> None:
    """Print the three falsifiable predictions of the model."""
    info = Policy(kind="info_greedy", cost_weight=0.2)  # cheap first, escalate to confirm
    fixed_low = Policy(kind="fixed", level=0.15)

    print("== 1. Decision quality by partner type (info-greedy escalation, n=%d) ==" % n)
    print(f"{'type':12s} {'approach':>9s} {'withdraw':>9s} {'mean steps':>11s}")
    for t in TYPES:
        o = run_batch(t, info, n, seed=seed)
        print(f"{t:12s} {o.approach_rate:9.3f} {o.withdraw_rate:9.3f} {o.mean_steps:11.2f}")

    print("\n== 2. Ambient noise lengthens probing (interested partner) ==")
    print(f"{'reliability':>11s} {'mean steps':>11s} {'approach rate':>13s}")
    for rel in (0.95, 0.85, 0.75, 0.65):
        o = run_batch("interested", info, n, seed=seed, reliability=rel)
        print(f"{rel:11.2f} {o.mean_steps:11.2f} {o.approach_rate:13.3f}")

    print("\n== 3. Exposing a mimic needs BOTH the hypothesis and the escalation ==")
    naive = ("interested", "indifferent")  # observer with no 'mimic' hypothesis
    full = TYPES
    print(f"{'observer':34s} {'P(approach mimic)':>18s} {'P(approach interested)':>23s}")
    rows = [
        ("naive model + cheap probe", naive, fixed_low),
        ("full model + cheap probe", full, fixed_low),
        ("full model + info-greedy", full, info),
    ]
    for name, hyp, pol in rows:
        m = run_batch("mimic", pol, n, seed=seed, hypotheses=hyp)
        i = run_batch("interested", pol, n, seed=seed, hypotheses=hyp)
        print(f"{name:34s} {m.approach_rate:18.3f} {i.approach_rate:23.3f}")
    print("\nReading: the naive observer (no mimic hypothesis) is exploited -- it approaches")
    print("the mimic. Adding the hypothesis but only cheap probes makes it safe but useless")
    print("(it can never confirm interest, so it approaches no one). Hypothesis + escalation")
    print("both withdraws from the mimic and approaches the genuinely interested partner.")


if __name__ == "__main__":  # pragma: no cover
    demo()
