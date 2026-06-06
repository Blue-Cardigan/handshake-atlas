# The silent-stages model (`handshake_atlas.courtship`)

A lean sequential-Bayesian model of the "silent stages" of courtship — the noisy, graded,
exploratory signalling that precedes an approach. It is the recognition layer the handshake
atlas deliberately omits: the atlas treats recognition as exact-match and noise-free, whereas
real silent-stage signalling is probabilistic and must be *inferred*.

Run it:

```bash
handshake-atlas courtship          # or: python -m handshake_atlas.courtship
```

## The model

An observer infers a partner's hidden type from a stream of reciprocations. At each step it
issues a probe of intensity `x ∈ [0,1]` (a cheap glance ≈ 0, a costly overt signal ≈ 1),
observes whether it is reciprocated, updates a Bayesian posterior over types, and stops when
the posterior probability the partner is *interested* crosses an upper threshold (**approach**)
or a lower one (**withdraw**); a timeout is a deniable exit.

Three partner types, with reciprocation probability as a function of probe intensity:

| type | cheap probe (x≈0) | costly probe (x≈1) |
|---|---|---|
| `interested` | high | higher (welcomes escalation) |
| `mimic` | high (wants attention) | low (will not pay/commit) |
| `indifferent` | low | low |

Cheap probes separate {interested, mimic} from indifferent; only costly probes separate
interested from mimic. Escalation is therefore required to expose a mimic — the recognition-
layer analogue of the atlas's *vigilance* result.

Decision is a sequential probability ratio test (Wald) / optimal stopping. The probe policy
`info_greedy` with a probe-cost penalty (`cost_weight`) chooses the intensity maximising
information gain minus cost — the epistemic-value term of active inference in reduced form.
With a positive cost it opens cheap and escalates only to resolve the interested-vs-mimic
ambiguity, reproducing the graded, deniable structure of real courtship.

## What it shows (reproducible via the demo)

1. **Discrimination.** Info-greedy escalation approaches interested partners ~0.88, mimics
   ~0.02, indifferent ~0.03.
2. **Noise lengthens probing.** As signal reliability falls (0.95 → 0.65), mean probing time
   rises — the model probes longer before committing under ambiguity.
3. **Exposing a mimic needs both the hypothesis and the escalation.** A *naive* observer that
   never entertains the mimic hypothesis, probing cheaply, is exploited (approaches the mimic
   ~0.89). The full model with only cheap probes is safe but useless (it can never confirm
   interest, approaching no one). Only the full hypothesis set *plus* costly escalation both
   withdraws from the mimic and approaches the genuinely interested partner.

## Relation to the handshake atlas and to active inference

The atlas's lesson — a forgeable recognition signal cannot be fixed by cleverer signal
structure, only by behaviour — reappears here one layer earlier: a mimic in the silent stages
is exposed not by a cleverer opening but by escalation (paying to test sincerity) and by
holding the hypothesis that interest can be performed. This is the reduced, falsifiable core
of active inference (epistemic action under a generative model). The full active-inference
treatment — dyadic theory-of-mind, emergent postural synchrony — is deliberately out of
scope; see the discussion in the project notes.
