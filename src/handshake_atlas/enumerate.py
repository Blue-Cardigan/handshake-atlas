"""Enumeration of the handshake space, stratified by prefix length."""

from __future__ import annotations

from collections.abc import Iterator

from .handshake import Handshake


def enumerate_length(k: int) -> Iterator[Handshake]:
    """Yield all ``2**k`` handshakes of prefix length ``k`` in big-endian order."""
    if k < 1:
        raise ValueError("length must be >= 1")
    for value in range(1 << k):
        yield Handshake.from_int(value, k)


def enumerate_up_to(max_length: int, min_length: int = 1) -> Iterator[Handshake]:
    """Yield all handshakes with length in ``[min_length, max_length]``."""
    for k in range(min_length, max_length + 1):
        yield from enumerate_length(k)


def count_up_to(max_length: int, min_length: int = 1) -> int:
    """Total number of handshakes with length in ``[min_length, max_length]``."""
    return sum(1 << k for k in range(min_length, max_length + 1))
