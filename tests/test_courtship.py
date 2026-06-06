import numpy as np

from handshake_atlas.courtship import (
    TYPES,
    Policy,
    observed_prob,
    reciprocation_prob,
    run_batch,
    simulate_encounter,
)

INFO = Policy(kind="info_greedy", cost_weight=0.2)
FIXED_LOW = Policy(kind="fixed", level=0.15)


def test_reciprocation_prob_shape():
    # interested rises with intensity; mimic collapses; indifferent stays low.
    assert reciprocation_prob("interested", 1.0) > reciprocation_prob("interested", 0.0)
    assert reciprocation_prob("mimic", 1.0) < reciprocation_prob("mimic", 0.0)
    assert reciprocation_prob("mimic", 0.0) > 0.8  # mimic mimics interest cheaply
    assert reciprocation_prob("mimic", 1.0) < 0.1  # but balks at cost
    assert reciprocation_prob("indifferent", 0.0) < 0.2


def test_noise_pulls_toward_half():
    p = reciprocation_prob("interested", 0.5)
    noisy = observed_prob("interested", 0.5, reliability=0.6)
    assert abs(noisy - 0.5) < abs(p - 0.5)


def test_info_greedy_discriminates_types():
    i = run_batch("interested", INFO, 1000, seed=0)
    m = run_batch("mimic", INFO, 1000, seed=0)
    d = run_batch("indifferent", INFO, 1000, seed=0)
    assert i.approach_rate > 0.7
    assert m.approach_rate < 0.1
    assert d.approach_rate < 0.1


def test_mimic_needs_hypothesis_and_escalation():
    # The headline: a naive observer (no 'mimic' hypothesis) on cheap probes is exploited;
    # the full model with escalation is not.
    naive = ("interested", "indifferent")
    naive_mimic = run_batch("mimic", FIXED_LOW, 1000, seed=0, hypotheses=naive)
    full_mimic = run_batch("mimic", INFO, 1000, seed=0, hypotheses=TYPES)
    assert naive_mimic.approach_rate > 0.5  # exploited
    assert full_mimic.approach_rate < 0.1  # protected


def test_cheap_only_observer_cannot_confirm_interest():
    # Full model but only cheap probes: interested and mimic stay indistinguishable, so the
    # observer never reaches the approach threshold for anyone.
    i = run_batch("interested", FIXED_LOW, 500, seed=0, hypotheses=TYPES)
    assert i.approach_rate < 0.1


def test_escalation_is_graded():
    # With a probe cost, the observer opens cheap and escalates only to confirm.
    rng = np.random.default_rng(3)
    enc = simulate_encounter("interested", INFO, rng)
    assert enc.intensities[0] < 0.5  # cheap, deniable opener
    assert max(enc.intensities) > 0.5  # escalates to a costly confirming probe


def test_noise_lengthens_probing():
    clear = run_batch("interested", INFO, 1000, seed=0, reliability=0.95)
    noisy = run_batch("interested", INFO, 1000, seed=0, reliability=0.65)
    assert noisy.mean_steps > clear.mean_steps


def test_determinism():
    a = run_batch("interested", INFO, 300, seed=7)
    b = run_batch("interested", INFO, 300, seed=7)
    assert (a.approach_rate, a.mean_steps) == (b.approach_rate, b.mean_steps)


def test_hypotheses_must_include_interested():
    rng = np.random.default_rng(0)
    try:
        simulate_encounter("mimic", INFO, rng, hypotheses=("mimic", "indifferent"))
    except ValueError:
        return
    raise AssertionError("should require 'interested' in hypotheses")
