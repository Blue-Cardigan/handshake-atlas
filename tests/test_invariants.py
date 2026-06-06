from handshake_atlas import Handshake
from handshake_atlas.invariants.autocorrelation import autocorrelation
from handshake_atlas.invariants.complexity import (
    bit_entropy,
    factor_complexity,
    linear_complexity,
    lz76,
)
from handshake_atlas.invariants.distance import hamming, min_distance_of_set
from handshake_atlas.invariants.overlap import overlap_profile


def test_barker_codes_recognised():
    # Canonical Barker codes (in Good/Bad with Good=+1): peak sidelobe must be <= 1.
    barker7 = Handshake.from_str("GGGBBGB")  # +++--+-
    barker5 = Handshake.from_str("GGGBG")  # ++++- ... canonical Barker-5 is +++-+
    barker13 = Handshake.from_str("GGGGGBBGGBGBG")  # +++++--++-+-+
    assert autocorrelation(barker7.signed).is_barker
    assert autocorrelation(barker5.signed).is_barker
    assert autocorrelation(barker13.signed).is_barker


def test_constant_prefix_is_worst_autocorrelation():
    const7 = Handshake.from_str("GGGGGGG")
    prof = autocorrelation(const7.signed)
    assert prof.peak_sidelobe == 6  # every shift fully correlates
    assert not prof.is_barker


def test_linear_complexity_known_values():
    assert linear_complexity((0, 0, 0, 0)) == 0
    assert linear_complexity((1, 1, 1, 1)) == 1  # s_i = s_{i-1}
    assert linear_complexity((1, 0, 1, 0, 1, 0)) == 2  # period-2 recurrence
    # An impulse needs an LFSR as long as the sequence.
    assert linear_complexity((0, 0, 0, 1)) == 4


def test_lz76_monotone_intuition():
    constant = lz76((1, 1, 1, 1, 1, 1, 1, 1))
    alternating = lz76((1, 0, 1, 0, 1, 0, 1, 0))
    assert constant < alternating  # repetition compresses, alternation less so


def test_factor_and_entropy():
    fp = factor_complexity((1, 0, 1, 0))  # GBGB
    assert fp[0] == 2  # two distinct length-1 factors: '0','1'
    assert bit_entropy((1, 1, 1, 1)) == 0.0
    assert abs(bit_entropy((1, 0)) - 1.0) < 1e-12


def test_overlap_periods_and_borders():
    gbgb = overlap_profile((1, 0, 1, 0))
    assert gbgb.longest_border == 2
    assert gbgb.shortest_period == 2
    assert gbgb.correlation[2] == 1

    ggb = overlap_profile((1, 1, 0))
    assert ggb.is_unbordered  # 110 has no proper border


def test_distance_helpers():
    assert hamming((1, 0, 1), (1, 1, 1)) == 1
    s = [Handshake.from_str("GGG"), Handshake.from_str("GBB"), Handshake.from_str("BGB")]
    assert min_distance_of_set(s) == 2
