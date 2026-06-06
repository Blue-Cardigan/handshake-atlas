# Paper: *A Periodic Table of Secret Handshakes*

arXiv draft reporting the novel findings from `handshake-atlas`.

## Build

Compiled to `main.pdf` (11 pages) with TinyTeX. Rebuild with:

```bash
pdflatex main && bibtex main && pdflatex main && pdflatex main   # or: latexmk -pdf main.tex
```

Or upload `main.tex`, `sec_*.tex`, and `references.bib` to Overleaf.

Dependencies: `article`, `amsmath/amssymb/amsthm`, `booktabs`, `algorithm`, `algpseudocode`
(algorithmicx), `natbib`, `hyperref`, `cleveref`. Suggested arXiv categories and
classifications are in the `main.tex` header comment (primary `math.CO`; cross-list `cs.GT`,
`nlin.CG`, `q-bio.PE`).

## Files

- `main.tex` — preamble, title, theorem/observation/conjecture environments, `\input`s.
- `sec_intro_background.tex` — abstract, introduction + contributions, preliminaries.
- `sec_method_taxonomy.tex` — the atlas pipeline, the family taxonomy.
- `sec_results.tex` — results, robustness, related work, limitations, conclusion, availability.
- `references.bib` — every entry hand-verified against a real DOI / venue (no LLM-invented
  citations).
- `BRIEF.md` — the drafting brief: the **results ledger** (every admissible number, traced to
  a reproducible computation in the `handshake_atlas` package), the notation contract, the
  closed citation set, and the anti-slop style rules the drafting agents were held to.

## Provenance and rigour

Every quantitative claim in the paper is a number from the ledger in `BRIEF.md`, each
reproducible from the `handshake-atlas` code:

- Barker spectrum, automaton band, unbordered density: `handshake-atlas build --struct-max 13`.
- Invade-AllD and regime/mimic results, plus the 36-cell sensitivity grid: the analysis
  snippets recorded in `docs/LEARNINGS.md` and the `handshake_atlas.evolution` module.

The draft was produced with section-drafting subagents constrained to the ledger and citation
set, then passed through two independent review passes: an adversarial referee (claim-vs-ledger,
overclaim, citation-misuse, notation consistency) and a deslopify copy-edit (LLM-cadence
removal, British English). The applied fixes are recorded in the git history.
