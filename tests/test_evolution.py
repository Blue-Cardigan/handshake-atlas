from handshake_atlas import Handshake
from handshake_atlas.evolution import (
    AllD,
    HandshakePlayer,
    MimicPlayer,
    moran_fixation,
    play_match,
    profile_evolution,
)


def test_vigilant_regimes_close_robsons_gap():
    # Unconditional cooperation is exploited by mimics; grim/tft police the recognised
    # partner and punish the post-handshake defection, flipping mimic-resistance.
    for lab in ["GB", "GBG", "GGGBBGB"]:
        h = Handshake.from_str(lab)
        ev = profile_evolution(h)
        fr = ev.mimic_fixation_by_regime
        assert fr["coop"] > ev.neutral  # bled by mimics (Robson's tension)
        assert fr["grim"] < ev.neutral  # vigilance closes the gap
        assert fr["tft"] < ev.neutral
        assert ev.mimic_resistant_by_regime["grim"]
        assert not ev.mimic_resistant_by_regime["coop"]


def test_grim_punishes_post_handshake_defection():
    h = Handshake.from_str("GB")
    grim = HandshakePlayer(h, "grim")
    mimic = MimicPlayer(h)
    g_score, m_score = play_match(grim, mimic, 500)
    # The mimic steals one round then both grind to mutual defection (P=1).
    assert m_score < 1.05  # no sustained exploitation
    assert abs(g_score - m_score) < 0.02  # near-symmetric, unlike the coop regime


def test_self_recognition_reaches_cooperation():
    h = Handshake.from_str("GB")
    s, _ = play_match(HandshakePlayer(h), HandshakePlayer(h), 500)
    # After the 2-round prefix both recognise and cooperate forever -> approaches R=3.
    assert 2.9 < s <= 3.0


def test_mimic_exploits_handshake():
    h = Handshake.from_str("GBG")
    mimic_score, hs_score = play_match(MimicPlayer(h), HandshakePlayer(h), 500)
    # The mimic gets recognised then defects against a cooperator -> strictly exploits.
    assert mimic_score > hs_score
    assert mimic_score > 3.0  # better than mutual cooperation


def test_handshake_defects_against_alld_after_probe():
    h = Handshake.from_str("GGG")
    h_score, _ = play_match(HandshakePlayer(h), AllD(), 500)
    # Three Good probe bits score S=0, then 497 rounds of P=1 -> 497/500, just below P.
    assert 0.98 < h_score < 1.0


def test_moran_neutral_drift():
    # Equal payoffs everywhere -> fixation must equal neutral drift 1/n.
    assert abs(moran_fixation(1, 1, 1, 1, 20, 0.1) - 1 / 20) < 1e-9


def test_evolution_profile_shape():
    prof = profile_evolution(Handshake.from_str("GBB"), population=20, rounds=200)
    assert prof.neutral == 1 / 20
    assert 0.0 <= prof.invade_alld <= 1.0
    assert 0.0 <= prof.mimic_fixation <= 1.0
    # Mimic should be favoured (Robson's tension) for a cooperative-tailed handshake.
    assert not prof.mimic_resistant
