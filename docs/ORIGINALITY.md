# Originality & prior art

This note records the literature scan done before building, so the contribution is
defensible and so we never re-claim something already done. Conclusion up front:

> **The *concept* of a handshake and the *individual* invariants are not novel. The novel
> artifact is the synthesis:** an enumerated atlas of IPD recognition handshakes, each
> profiled by a *joint* structural–evolutionary invariant vector, organised into a *named
> family taxonomy* ("periodic table"). That exact bundle returned zero direct hits.

## What is already established (do not re-claim)

**Handshakes as a concept.**
- Robson, A.J. (1990). "Efficiency in evolutionary games: Darwin, Nash and the secret
  handshake." *J. Theoretical Biology* 144(3): 379–396. — A costless recognition signal
  invades any Pareto-inferior ESS, but only *transiently*: a mimic that shows the signal
  and defects beats it. This mimic tension is intrinsic and is exactly what our
  `mimic_fixation` invariant measures.
- Knight, V. et al. (2018). "Evolution reinforces cooperation with the emergence of
  self-recognition mechanisms." *PLOS ONE* 13(10): e0204981. — Handshakes (CD, CCD)
  *emerge* in evolved finite-state machines, and handshake machines are the strongest
  invasion-resistors. Observed, never enumerated. Our `invade_alld` mirrors their test.

**Tag / green-beard recognition.** Hamilton (1964); Dawkins (1976); Riolo, Cohen &
Axelrod (2001, *Nature*); Traulsen & Nowak (2007, *PLOS ONE*). The static-tag analogue of
a behavioural handshake; same mimic failure mode.

**Strategy complexity.** Rubinstein (1986, *JET*); Abreu & Rubinstein (1988,
*Econometrica*). Strategy = finite automaton; complexity = state count; studies the
complexity↔payoff tradeoff at equilibrium. We *reuse* the automaton-size measure but apply
it to recognition prefixes, which they never did. Gaffney, Harper & Knight (2019,
arXiv:1912.04493) compute FSM memory depth — one invariant, not a prefix space.

**Low-complexity strategy structure.** Press & Dyson (2012, *PNAS*) zero-determinant
strategies; Hilbe, Chatterjee & Nowak (2018, *Nat. Hum. Behav.*) partner/rival taxonomy of
memory-one strategies. A taxonomy exists — but keyed on *steady-state payoff geometry*,
not recognition-prefix structure.

**The invariants themselves** (all standard, all from separate fields):
- Aperiodic autocorrelation, Barker codes, merit factor — radar/sequence design.
- Prefix-freeness / Kraft, minimum Hamming distance / Singleton & Hamming bounds — coding
  theory.
- Factor complexity, Sturmian/Thue–Morse, automatic sequences — combinatorics on words.
- LZ76 complexity, linear complexity / Berlekamp–Massey — compression & cryptography.
- Guibas & Odlyzko (1981) string correlation / bordering — the self-overlap measure.

**Enumerate-and-profile binary strings.** arXiv:1611.00607 ("Three Perspectives on
Complexity") enumerates all binary strings ≤ len ~11 with multiple complexity measures;
the Coding-Theorem-Method tables (Soler-Toscano/Zenil) give algorithmic complexity of
short strings. Generic strings, no IPD framing, no taxonomy step.

**Classify strategies.** Ashlock & Kim (2008, IEEE TEVC) fingerprinting →
cluster → name, *for IPD strategies* — but signatures are *behavioural* and the space is
*sampled/evolved* agents, not an enumerated bit-sequence atlas.

## The unoccupied intersection

No prior artifact does all three at once:
1. exhaustively **enumerate** short binary sequences **as IPD recognition handshakes**;
2. compute a **joint** vector — autocorrelation/mimic-resistance + self-overlap +
   compressibility + linear complexity + **minimal-automaton size** + **evolutionary
   robustness** — together, per handshake;
3. organise them into a **named family taxonomy** rendered as a periodic table.

The two nearest misses each own only one axis (Ashlock: classify behavioural; 1611.00607:
enumerate+profile generic) and neither carries the IPD-handshake framing or the
structural+evolutionary join.

## Honest caveats (things NOT to overclaim)

- Handshakes are a known idea — novelty is the *artifact*, not the concept.
- Computing complexity invariants of short binary strings is done — we reuse definitions.
- Minimum Hamming distance over a *full* length stratum is trivially 1 for every string;
  it is only meaningful for selected subsets (families/codes), and is exposed as a utility,
  not as a per-handshake atlas column. This honesty is encoded in `invariants/distance.py`.
