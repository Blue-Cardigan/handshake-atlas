# Methods: definitions and conventions

## Encoding

`bit 1 = Good = Cooperate` (autocorrelation value `+1`); `bit 0 = Bad = Defect`
(value `−1`). A handshake of length `k` is identified by its big-endian integer `index`
within the length-`k` stratum. Labels are written in `G`/`B` (e.g. `GGGBBGB`).

## The gated strategy and its automaton

The handshake plays its prefix `p` for rounds `0..k-1` regardless of the opponent. After
the prefix it inspects the opponent's first `k` moves: if they equal `p`, it cooperates
forever; otherwise it defects forever.

We realise this as a deterministic **Moore machine** over the opponent-move alphabet
`{Good, Bad}`: state output = our move, transitions consume the opponent's move. The
non-minimised machine has `2k + 2` states (a matched/un-matched copy of each prefix
position, plus the COOP and DEF absorbing terminals). We then run **partition-refinement
(Moore/Hopcroft) minimisation**; the resulting state count is the
**minimal-automaton-size** invariant — the Rubinstein (1986) strategy-complexity measure
applied to handshakes. `tests/test_automaton.py` proves the machine (raw and minimised)
reproduces the gated strategy on every opponent history up to length `k+3`.

## String invariants

**Aperiodic autocorrelation.** For the `±1` sequence `a` of length `N`,
`c_v = Σ_{j=0}^{N-1-v} a[j]·a[j+v]` for `v = 1..N-1`.
- *peak sidelobe* = `max_v |c_v|` (0 for `N=1`).
- *merit factor* = `N² / (2·Σ_v c_v²)` (∞ when all sidelobes vanish).
- *Barker* = peak sidelobe ≤ 1 (the optimal low-autocorrelation codes; conjectured to
  stop at length 13). Validated against the canonical Barker-5/7/13 codes.

**Self-overlap (Guibas–Odlyzko correlation).** `overlap[k] = 1` iff the length-`(N−k)`
prefix equals the length-`(N−k)` suffix (i.e. `k` is a period). Borders are computed via
the KMP failure function. *Unbordered* (bifix-free) = no proper border = no partial
self-echo → maximally resistant to desynchronisation / partial impersonation.
*Shortest period* = `N − longest border`.

**Complexity.**
- *LZ76* — Kaspar–Schuster count of distinct factors in the exhaustive history
  (compressibility).
- *Linear complexity* — length of the shortest LFSR generating the bits, via
  Berlekamp–Massey over GF(2) (predictability). Validated on known cases (impulse → `N`,
  constant → 1, period-2 → 2).
- *Factor complexity* — `p(L)` = number of distinct length-`L` substrings; summed to
  *distinct factors* (richness).
- *Bit entropy* — Shannon entropy of the 0/1 frequencies.

## Set invariants

`invariants/distance.py` provides Hamming distance, minimum pairwise distance of a set,
and nearest-neighbour-in-set. **These are deliberately not atlas columns**: within a full
length stratum every string has a single-bit neighbour, so per-string minimum distance is
trivially 1. Distance is meaningful only for *selected* subsets (a discovered family or a
curated code) and is used by the taxonomy/validation layers.

## Evolutionary invariants

Strategies are deterministic, so each pairwise match has a fixed mean per-round payoff; we
therefore use the **closed-form frequency-dependent Moran fixation probability** (Nowak et
al. 2004) instead of stochastic simulation — every value is exactly reproducible.

Payoffs: `R=3, S=0, T=5, P=1` (`T>R>P>S`, `2R>T+S`). Population `N=20`, `rounds=200`,
selection intensity `w=0.1` by default. Fixation of one type-A mutant among `N−1` type-B
with payoffs `a=A|A, b=A|B, c=B|A, d=B|B`:

```
ρ_A = 1 / (1 + Σ_{i=1}^{N-1} Π_{j=1}^{i} f_B(j)/f_A(j)),   f = 1 − w + w·π,
π_A(i) = ((i−1)a + (N−i)b)/(N−1),   π_B(i) = (i·c + (N−i−1)d)/(N−1)
```

Neutral drift = `1/N`.

- **`invade_alld`** — fixation of the handshake invading an all-defector population
  (`A` = handshake, `B` = AllD). It invades only if the mutual-recognition bonus beats the
  *probe cost* of exposing the Good bits of its prefix to defectors. The Knight (2018)
  invasion-of-defectors test.
- **`mimic_fixation`** — fixation of a *mimic* (echoes `p`, then defects forever) invading
  a population of the handshake (`A` = mimic, `B` = handshake). Robson's (1990) tension,
  per handshake. Near-universally above neutral: costless handshakes bleed to mimics.

## Taxonomy

Primary families are assigned by **priority rules** (first match wins), from most to least
structured: Constant → Alternating → Barker → Unbordered → Self-similar → Generic (see
`cluster.py` for the exact predicates). This is reproducible and explainable. As a
cross-check, `emergent_clusters()` runs k-means over the normalised invariant vector; the
emergent clusters substantially recover the rule-based families (Barker, Unbordered,
Constant, Self-similar each fall out as distinct clusters), which is evidence the taxonomy
reflects real geometry rather than arbitrary thresholds.
