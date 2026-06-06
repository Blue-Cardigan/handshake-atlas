from handshake_atlas import BAD, GOOD, Handshake
from handshake_atlas.enumerate import count_up_to, enumerate_length


def test_from_str_aliases():
    assert Handshake.from_str("GB").prefix == (GOOD, BAD)
    assert Handshake.from_str("CD").prefix == (GOOD, BAD)  # Cooperate/Defect alias
    assert Handshake.from_str("10").prefix == (GOOD, BAD)


def test_from_int_roundtrip():
    for k in range(1, 6):
        for v in range(1 << k):
            h = Handshake.from_int(v, k)
            assert h.index == v
            assert h.length == k


def test_label_and_signed():
    h = Handshake.from_str("GBG")
    assert h.label == "GBG"
    assert h.signed == (1, -1, 1)


def test_empty_prefix_rejected():
    try:
        Handshake(())
    except ValueError:
        return
    raise AssertionError("empty prefix should raise")


def test_enumeration_counts():
    assert count_up_to(3) == 2 + 4 + 8
    labels = [h.label for h in enumerate_length(2)]
    assert labels == ["BB", "BG", "GB", "GG"]
