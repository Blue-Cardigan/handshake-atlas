"""Taxonomy: organise handshakes into a "periodic table" of families.

Two complementary layers:

1. A *rule-based* primary family for every handshake (reproducible, explainable, and
   tied directly to the literature's structural classes). This is what the periodic
   table is keyed on.
2. An optional *emergent* clustering (k-means over the normalised invariant vector) used
   in the write-up to check whether the rule-based families actually fall out of the
   joint geometry, or whether the data wants a different cut.
"""

from __future__ import annotations

from .profile import HandshakeProfile

# Primary families in priority order: the first predicate that matches wins. Ordering
# runs from the most specifically-structured to the generic bulk.
FAMILY_ORDER = [
    "Constant",
    "Alternating",
    "Barker",
    "Unbordered",
    "Self-similar",
    "Generic",
]

FAMILY_DESCRIPTIONS = {
    "Constant": "All-Good or all-Bad. Worst possible autocorrelation; trivially "
    "recognised but maximally confusable with any shift of itself.",
    "Alternating": "Strict period-2 (GBGB.../BGBG...). Highly self-overlapping; cheap to "
    "describe, weak as a distinguishing signal.",
    "Barker": "Peak autocorrelation sidelobe <= 1 -- the rare optimal low-autocorrelation "
    "codes. Maximally resistant to out-of-phase mimicry. Conjectured to stop at length 13.",
    "Unbordered": "Bifix-free: no proper prefix equals a suffix. No partial self-echo, so "
    "hard to desynchronise or partially impersonate.",
    "Self-similar": "Low realized complexity -- small minimal automaton and short LFSR "
    "relative to length (constant-free but structurally compressible, Thue-Morse-like).",
    "Generic": "The incompressible bulk: high-complexity prefixes with no special "
    "autocorrelation, bordering, or low-complexity structure.",
}


def classify_family(p: HandshakeProfile) -> str:
    n = p.length
    is_constant = p.bit_entropy == 0.0
    if is_constant:
        return "Constant"
    if n > 2 and p.shortest_period == 2:
        return "Alternating"
    if n >= 2 and p.is_barker:
        return "Barker"
    if p.is_unbordered:
        return "Unbordered"
    # Self-similar: realized complexity well below the generic expectation.
    if n >= 4 and (p.min_automaton_states <= n or p.linear_complexity <= n / 2):
        return "Self-similar"
    return "Generic"


def emergent_clusters(profiles: list[HandshakeProfile], k: int = 6, seed: int = 0):
    """k-means over normalised feature vectors. Returns labels list or None if sklearn
    is unavailable. Used only for the write-up / cross-check, never required at runtime."""
    try:
        import numpy as np
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
    except ImportError:  # pragma: no cover - optional dependency
        return None
    if len(profiles) < k:
        return None
    x = np.array([p.feature_vector() for p in profiles], dtype=float)
    x = StandardScaler().fit_transform(x)
    # Zero-variance columns yield nan/inf after scaling; neutralise them.
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    labels = KMeans(n_clusters=k, random_state=seed, n_init=10).fit_predict(x)
    return labels.tolist()
