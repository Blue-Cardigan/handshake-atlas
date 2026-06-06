# What the atlas reveals

Findings from the enumerated atlas (`struct_max=10`, `evo_max=8`), framed as answers to
the questions that motivated the project. All numbers are reproducible from
`handshake-atlas build` + the snippets in this repo.

## 1. Is there structure, or just "every sequence with linearly decreasing frequency"?

**There is strong structure, and the linear-decrease intuition is wrong.** Two regimes
coexist:

| k | #handshakes | Barker | unbordered % | min-automaton range |
|--:|--:|--:|--:|--:|
| 2 | 4 | 4 | 50% | 4–5 |
| 3 | 8 | 4 | 50% | 5–7 |
| 4 | 16 | 8 | 38% | 6–9 |
| 5 | 32 | 4 | 38% | 7–11 |
| 6 | 64 | **0** | 31% | 8–13 |
| 7 | 128 | 4 | 31% | 9–15 |
| 8 | 256 | **0** | 29% | 10–17 |
| 9 | 512 | **0** | 29% | 11–19 |
| 10 | 1024 | **0** | 28% | 12–21 |

- **Structured families do not scale with the space.** `Constant` is always exactly 2;
  `Alternating` is always exactly 2 (for k≥3); `Barker` is sporadic and dies. Meanwhile
  the total count doubles each step. So the *fraction* of special handshakes collapses
  toward zero — the interesting ones live on a **thin shell inside an exponentially growing
  incompressible bulk**, not a linearly-thinning list.
- **The frequency distribution you'd actually observe is driven by your sampling prior**,
  not the strings: there are `2^k` handshakes of length `k`, so any "decreasing with
  length" curve comes from how the generator picks length, not from the handshakes.

## 2. The atlas independently rediscovers known mathematics

- **Barker codes vanish — and revive — exactly where theory says.** Built to
  `struct_max=13`, the atlas finds Barker handshakes at **k = 2, 3, 4, 5, 7, 11, 13** and
  **none at k = 6, 8, 9, 10, 12** — the complete, famous Barker spectrum, reproduced from
  first principles with no special-casing. The length-13 set includes the canonical
  `GGGGGBBGGBGBG`. Barker codes are conjectured to exist at no length beyond 13.

  | k | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
  |--|--|--|--|--|--|--|--|--|--|--|--|--|
  | Barker handshakes | 4 | 4 | 8 | 4 | 0 | 4 | 0 | 0 | 0 | 4 | 0 | 4 |
- **The unbordered fraction converges to its known constant.** The share of bifix-free
  prefixes settles around 0.28 as k grows — approaching the known limiting density of
  unbordered binary words (≈ 0.2677).
- **Minimal-automaton size is a real, linearly-bounded invariant.** It spans
  `[k+2, 2k+1]` against a raw `2k+2`: the *simplest* handshakes (constant/alternating)
  collapse to ≈ `k+2` states; the *hardest* barely compress (`2k+1`). So "maximum
  complexity" is **unbounded and grows linearly with length** — there is no ceiling, and
  the most complex handshakes resist minimisation almost completely.

## 3. The structural → evolutionary bridge (the genuinely new part)

Joining the string view to the Moran view surfaces effects neither sees alone:

- **One Good bit is the difference between invading defectors and being suckered by
  them.** Mean fixation against an AllD population (neutral drift = 0.05):

  | Good bits in prefix | mean invade-AllD fixation |
  |--:|--:|
  | 0 | **0.010** (cannot invade) |
  | ≥1 | ~0.077 (invasion-favoured) |

  The all-Bad handshake fails catastrophically: a population of defectors *accidentally
  echoes* the all-Defect prefix, so the handshake mis-recognises defectors as kin and
  cooperates into exploitation. Adding a single cooperative probe bit makes the prefix
  un-echoable by pure defectors, and the handshake flips to invasion-favoured. This is a
  crisp, quantified statement of *why a recognition signal must contain a cooperative
  commitment*.

- **Mimic-resistance is structure-independent — Robson's tension is universal.** Across
  every family, the mimic (echo the prefix, then defect) fixates at ≈ 0.15, far above the
  0.05 drift baseline. No prefix structure — not Barker, not unbordered, nothing — buys
  resistance to a cheat that shows the signal and defects. The atlas makes Robson's 1990
  result tangible: **structural cleverness improves recognition but cannot fix the
  costless-signal vulnerability.**

- **What *does* close the gap: vigilance, not the prefix.** Replacing the
  cooperate-forever regime with a *vigilant* post-recognition rule that polices the
  recognised partner flips mimic-resistance decisively, identically for every prefix:

  | post-recognition regime | mimic fixation | verdict (neutral = 0.05) |
  |---|--:|---|
  | Unconditional cooperate (classical) | 0.15 | **bled** (mimic invades) |
  | Grim (defect forever after any defection) | 0.015 | **resists** |
  | Tit-for-tat | 0.015 | **resists** |

  The mimic steals exactly one round, then the vigilant handshake collapses the
  interaction to mutual defection, so the cheat gains nothing sustained. This localises
  Robson's fix precisely: the recognition *signal* is irreparably forgeable; the
  *post-recognition strategy* is where defection against cheats must live.

## 4. Can we generate endless handshakes and explore patterns? Yes.

The enumeration is exhaustive and the invariants are cheap, so the atlas extends to any
length compute allows (structural invariants for k≤10 take ~0.4 s). Open threads the
current tool sets up but does not yet chase:

- Push `struct_max` to 14–16 to test the unbordered-density limit (≈ 0.2677) to more digits
  and confirm no Barker codes appear beyond 13.
- Sweep population size `N`, selection intensity `w`, and round count to confirm the regime
  result (vigilance closes Robson's gap) is robust, not an artefact of the default
  parameters.
- Treat discovered families as codes and compute their set-level minimum Hamming distance
  (the `distance.py` utilities are ready) — i.e. how confusable whole families are under
  noise.
