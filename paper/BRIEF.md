# Drafting brief — handshake-atlas paper

You are drafting part of a short arXiv paper. Follow this brief EXACTLY. Output LaTeX
fragments only (no preamble, no `\documentclass`, no `\begin{document}`). British English
spelling throughout (behaviour, neighbour, generalise, characterise, analyse, modelling).

## Hard rules (non-negotiable)

1. **Citations:** use ONLY the BibTeX keys listed in "Allowed references" below. NEVER
   invent a citation, DOI, author, or year. If you want to cite something not in the list,
   instead write the claim without a citation or omit it. Cite with `\citep{key}` /
   `\citet{key}`.
2. **Every quantitative claim must use a number from the LEDGER below** — do not invent
   numbers, do not round differently, do not extrapolate beyond stated scope.
3. **Claim vocabulary:** `\begin{theorem}` only for proven statements; `\begin{observation}`
   for results computationally established over the enumerated set (state the scope, e.g.
   "for all $k\le 11$"); `\begin{conjecture}` for extrapolation beyond what was enumerated.
4. **Anti-slop (enforced in a later pass, write clean now):** banlist — delve, showcase,
   underscore, leverage, harness, intricate, crucial, pivotal, robust (as filler), realm,
   tapestry, interplay, seamless, nuanced, multifaceted, holistic, paramount, "it is worth
   noting", "it is important to note", notably, importantly, "not only...but also". Near-zero
   paragraph-initial connectives (Furthermore/Moreover/Additionally). Em-dashes sparing.
   No bold in body prose. No "In conclusion". Prefer a number or a precise term to any
   adjective. No "opens new avenues".
5. Tables use `booktabs` (`\toprule`/`\midrule`/`\bottomrule`), captions above tables.
   Reference every float in the prose with `\cref{}`.

## Notation contract (use these symbols consistently)

- Actions: $C$ (cooperate) and $D$ (defect). (The software calls these Good/Bad; the paper
  uses $C$/$D$.)
- A **handshake** is a recognition prefix $p \in \{C,D\}^k$ of length $k\ge 1$.
- The **gated strategy** $H_p$ with post-recognition regime $\rho$: play $p$ for the first
  $k$ rounds; if the opponent's first $k$ actions equal $p$, enter regime $\rho$, else
  defect forever. Regimes: $\rho \in \{\textsc{coop}, \textsc{grim}, \textsc{tft}\}$.
  \textsc{coop} = cooperate forever (the classical secret handshake); \textsc{grim} =
  cooperate until the recognised partner defects once, then defect forever; \textsc{tft} =
  cooperate then mirror.
- A **mimic** of $p$ plays $p$ then defects forever (the cheat that forges the signal).
- Payoffs: $R=3, S=0, T=5, P=1$ (so $T>R>P>S$ and $2R>T+S$). Per-round mean payoff over
  $n$ rounds ($n=200$ default).
- $m(p)$ = number of states of the minimal Moore machine realising $H_p$ (the
  Rubinstein/Myhill--Nerode strategy-complexity measure), computed by partition refinement.
- Aperiodic autocorrelation of the $\pm1$ image of $p$: sidelobes $c_v=\sum_{j} a_j a_{j+v}$;
  peak sidelobe $\max_v |c_v|$; merit factor $N^2/(2\sum_v c_v^2)$; Barker iff peak $\le 1$.
- Self-overlap / Guibas--Odlyzko correlation; $p$ is **unbordered** (bifix-free) iff it has
  no proper border (no proper prefix equal to a suffix).
- Complexity: LZ76 (Lempel--Ziv 1976), linear complexity (Berlekamp--Massey), factor
  complexity.
- Moran process: population $N$, selection intensity $w$, fixation probability of a single
  mutant by the closed-form constant-selection formula; neutral drift baseline $1/N$.
  Default $N=20$, $w=0.1$.

## LEDGER (the only admissible numbers)

**Enumeration scale.** Structural invariants computed for all handshakes with $k\le 13$
(16{,}382 handshakes); evolutionary invariants for $k\le 8$ (510 handshakes). Enumeration is
exhaustive and deterministic (big-endian order within each length). Strategy fully
deterministic; fixation probabilities computed in closed form (no RNG, exactly reproducible).

**Barker validation.** Built to $k\le 13$, handshakes whose peak autocorrelation sidelobe
$\le 1$ occur at exactly $k = 2,3,4,5,7,11,13$ and at NO other length $\le 13$ (absent at
$6,8,9,10,12$). Per-length counts: $k{=}2{:}4$, $3{:}4$, $4{:}8$, $5{:}4$, $7{:}4$,
$11{:}4$, $13{:}4$. This recovers the complete known Barker spectrum
\citep{barker1953,turyn1961}; the spectrum is not encoded anywhere in the tool. The
$k=13$ set includes $CCCCCDDCCDCDC$.

**Minimal-automaton band.** For every $k$ with $1\le k\le 11$, $m(p)$ takes every value and
exactly the range $[\,k+2,\ 2k+1\,]$ against an unminimised construction of $2k+2$ states.
Minimum $k+2$ is attained by $D$-tailed prefixes (e.g. $DDDDDD$, $CDDDDD$); maximum $2k+1$ by
$C$-heavy prefixes (e.g. $CCCCCC$, $CCCDDC$). (Asymmetry arises because the COOP terminal
emits $C$ and the DEF terminal emits $D$.)

**Unbordered density.** Fraction of unbordered prefixes by length:
$k$: 1,2,3,4,5,6,7,8,9,10,11,12,13 -> 1.0000, 0.5000, 0.5000, 0.3750, 0.3750, 0.3125,
0.3125, 0.2891, 0.2891, 0.2773, 0.2773, 0.2725, 0.2725. Decreasing, equal in consecutive
pairs, converging from above toward the known bifix-free density $\approx 0.2678$
\citep{oeisA003000}.

**Invade-AllD (probe cost).** Neutral $=1/20=0.05$. Mean fixation probability of $H_p$
(\textsc{coop}) invading an all-defector population, by number of $C$ bits in $p$:
- $k=6$: 0 C-bits -> 0.0096; $\ge 1$ C-bit -> 0.0750--0.0770 (monotone slight decline).
- Same pattern at $k=4$ (0 -> 0.0095; 1 -> 0.0773) and $k=8$ (0 -> 0.0098; 1 -> 0.0768).
The all-defect prefix ($0$ $C$-bits) sits BELOW neutral: defectors echo the all-$D$ prefix,
so $H_p$ mis-recognises them as kin and is exploited (payoff vs.\ AllD $=0.020$ for $DDDD$
vs.\ $0.995$ for $CDDD$/$DDDC$). One $C$ bit makes the prefix unforgeable by pure defectors
and flips $H_p$ to invasion-favoured.

**Mimic-resistance and the regime fix.** Under \textsc{coop}, a mimic invades: fixation
$\approx 0.15 > 0.05$ for every handshake tested. Under \textsc{grim} and \textsc{tft},
fixation $\approx 0.015 < 0.05$ (mimic-resistant) for every handshake. Mechanism: the mimic
steals exactly one round, then the vigilant handshake collapses the interaction to mutual
defection ($P$ each), so the cheat gains nothing sustained.

**Sensitivity (robustness of the regime result).** Over the full grid
$N\in\{10,20,50,100\}$, $w\in\{0.01,0.1,0.5\}$, $n\in\{50,200,1000\}$ (36 cells), the
qualitative result holds in ALL 36 cells: \textsc{coop} mimic-fixation $>$ neutral, while
\textsc{grim} and \textsc{tft} $<$ neutral. The margin scales with selection: at
$(N{=}10,w{=}0.01,n{=}50)$ it is small (\textsc{coop} 0.109 vs.\ \textsc{grim} 0.095,
neutral 0.100); at $(N{=}100,w{=}0.5,n{=}1000)$ it is large (\textsc{coop} 0.339 vs.\
\textsc{grim} 0.000).

**Taxonomy.** Six rule-based families (Constant, Alternating, Barker, Unbordered,
Self-similar, Generic) assigned by priority predicates over the invariants. Cross-check:
$k$-means over the standardised invariant vectors (for $k\le 8$) recovers the rule families
as distinct clusters — one cluster is 100% Constant, one 85% Barker, two are 88--100%
Unbordered, one 76% Self-similar — evidence the taxonomy reflects the joint geometry rather
than arbitrary thresholds. Structured families do not scale with the space: Constant is
always 2 and Alternating always 2 (for $k\ge3$), while the total doubles each step, so the
special families' share tends to zero — a thin structured shell inside an exponentially
growing incompressible bulk.

## Allowed references (BibTeX keys; use no others)

robson1990 (secret handshake origin); knight2018 (handshakes emerge in evolved FSMs in the
Moran process; invasion-of-defectors test); rubinstein1986, abreu1988 (automaton strategy
complexity); press2012, hilbe2018 (low-complexity strategy structure); nowak2004 (finite-
population fixation formula); moran1958 (Moran process); axelrod1984 (IPD/tournaments);
knight2016 (Axelrod-Python library); barker1953, turyn1961 (Barker codes / spectrum bound);
guibas1981 (string overlaps/bordering); lempel1976 (LZ complexity); massey1969 (Berlekamp--
Massey linear complexity); hopcroft1971, nerode1958 (DFA minimisation / Myhill--Nerode);
oeisA003000 (bifix-free word counts).

## Title (fixed)

"A Periodic Table of Secret Handshakes: Enumerating and Profiling Recognition-Prefix
Strategies for the Iterated Prisoner's Dilemma"
