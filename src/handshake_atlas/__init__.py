"""handshake-atlas: enumerate, profile, and classify iterated-prisoner's-dilemma
secret handshakes.

A *secret handshake* is a recognition-prefix strategy: play a fixed prefix, then
cooperate forever with anyone who echoed it and defect forever against everyone else.
This package enumerates the prefix space, computes a joint structural-invariant profile
for each handshake (autocorrelation, self-overlap, complexity, minimal-automaton size,
and -- optionally -- evolutionary robustness), and organises the results into a
"periodic table" of handshake families.
"""

from __future__ import annotations

from .enumerate import count_up_to, enumerate_length, enumerate_up_to
from .handshake import BAD, GOOD, Handshake, MooreMachine
from .profile import HandshakeProfile, profile_handshake

__version__ = "0.1.0"

__all__ = [
    "Handshake",
    "MooreMachine",
    "GOOD",
    "BAD",
    "enumerate_length",
    "enumerate_up_to",
    "count_up_to",
    "HandshakeProfile",
    "profile_handshake",
    "__version__",
]
