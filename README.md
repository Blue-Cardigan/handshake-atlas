# handshake-atlas

An enumerated **periodic table of secret handshakes** for the iterated prisoner's
dilemma.

A *secret handshake* is a recognition-prefix strategy (Robson 1990; Knight et al. 2018):

> play a fixed prefix `p ∈ {Good, Bad}^k`; afterwards, **cooperate forever with any
> opponent who echoed the prefix exactly, and defect forever against everyone else.**

The prefix is the whole strategy, so the space of handshakes *is* the space of binary
prefixes. This project enumerates that space and gives each handshake a **joint
structural–evolutionary invariant profile**, then organises the results into named
families and renders them as an interactive periodic table.

## Why this is original

The handshake *concept* is old and the individual invariants are textbook. What did not
exist before (see [`docs/ORIGINALITY.md`](docs/ORIGINALITY.md) for the literature scan) is
the **fusion**: enumerate short binary sequences *framed as IPD handshakes*, compute a
*joint* invariant battery per handshake, and classify them into a *named taxonomy*.

| Axis | Closest prior work | What it lacked |
|---|---|---|
| Handshake existence | Robson 1990; Knight et al. 2018 | no enumeration — emergence observed, not catalogued |
| Strategy complexity | Rubinstein 1986; Abreu–Rubinstein 1988 | never applied to recognition prefixes |
| Enumerate + profile strings | arXiv:1611.00607; CTM tables | generic strings, no IPD framing, no taxonomy |
| Classify strategies | Ashlock fingerprinting | behavioural signatures on *sampled* agents, not enumerated bit-sequences |

## The invariant battery

Three views of each handshake:

* **String** — aperiodic autocorrelation (peak sidelobe, merit factor, Barker test →
  resistance to out-of-phase mimicry); self-overlap / bordering (Guibas–Odlyzko
  correlation → bifix-free = no partial self-impersonation); complexity (LZ76, linear
  complexity via Berlekamp–Massey, factor complexity, bit entropy).
* **Automaton** — minimal Moore-machine size realising the gated strategy (the Rubinstein
  strategy-complexity measure, applied to handshakes for the first time).
* **Evolutionary** — exact analytic Moran fixation: `invade_alld` (can it invade
  defectors? the Knight 2018 test) and `mimic_fixation` (how badly a cheat that echoes the
  prefix then defects invades it — Robson's tension, quantified per handshake). Mimic
  fixation is reported under three post-recognition regimes (unconditional cooperate, grim,
  tit-for-tat) to isolate *what* closes Robson's gap — the answer is vigilance, not the
  prefix (see `docs/LEARNINGS.md`).

## Quick start

```bash
pip install -e ".[all]"          # numpy required; sklearn/pandas optional
pytest                            # 21 tests: automaton equivalence, Barker codes, Moran

# inspect a single handshake
handshake-atlas inspect GGGBBGB   # the length-7 Barker code

# (re)build the atlas the web explorer reads (k<=11 keeps it light & shows Barker revival)
handshake-atlas build --struct-max 11 --evo-max 8 --out web/data/atlas.json
# go to k<=13 to reproduce the full Barker spectrum (heavier: ~10MB, 16382 handshakes)
handshake-atlas build --struct-max 13 --evo-max 8 --out web/data/atlas.full.json
```

## The explorer

```bash
cd web && python3 -m http.server 8765   # then open http://localhost:8765
```

A periodic table: rows are prefix length `k`, every cell is a handshake, coloured by
family or by any invariant. Click a cell for its full profile and autocorrelation
sidelobe sparkline. It is a static site — deployable on Vercel by pointing the project
root at `web/` (no build step). See [`docs/METHODS.md`](docs/METHODS.md) for definitions
and [`docs/LEARNINGS.md`](docs/LEARNINGS.md) for what the atlas reveals.

## Scale honesty

Cheap structural invariants are computed for **every** handshake up to `struct_max`
(`k ≤ 10` → 2046 handshakes by default). The expensive evolutionary invariants are
computed only up to `evo_max` (`k ≤ 8`); beyond that they are reported as "not computed",
never silently dropped. Both caps are recorded in the atlas metadata.
