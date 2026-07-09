# Testing log

This repo's skill logic was actually executed, not just written and left unverified. Three tests, run 2026-07-09, documented here as evidence rather than assertion.

**Note on scope:** the two tests below that use a real company ([REDACTED-COMPANY]) are validation exercises only — no application was submitted, no contact was made with anyone, and [REDACTED-COMPANY]'s real data is never written into `examples/`, which stays 100% fictional as documented in the README. This log is the one place in the repo where a real, well-known public company is named, specifically to prove the tool's mechanisms work on real inputs, not just synthetic ones designed to make it look good.

## Test 1 — Live-search verification agent

Ran a live search for [REDACTED-COMPANY] ([REDACTED-TICKER]), following `SKILL.md` Step 3.

**Result:** ~31,000–33,000 employees (sources disagree slightly, expected for headcount data), FY2025 revenue $23.77B, FY2026 target $26.5–26.6B, publicly traded. Confirms the mechanism retrieves real, current, externally-sourced facts rather than relying on the model's static training knowledge — which is the entire point of this agent existing.

**Confidence:** confirmed (multiple independent sources agreed on order of magnitude).

## Test 2 — Full scoring pipeline

Scored a Director-level Product Management role at [REDACTED-COMPANY] against the fictional example CV (`examples/CV-example.md` — Jordan Ainsley, Head of Product, ~9 years, UK right-to-work only, comp floor £110k).

**A testing-methodology note, not a product limitation:** four separate [REDACTED-COMPANY] job posting URLs, all appearing in live search results, returned "this position has been filled" or HTTP 410 when fetched minutes later. This happened because *this test* tried to fetch a live JD from a URL, which is not how the tool actually works — in real use, you paste the JD text directly into the conversation, already captured, so it can't go stale between finding it and scoring it. Recorded here because it's a genuine friction worth knowing about if you ever try to test this the same way (by following search-indexed links), not because it limits the shipped product.

Scored using real, verified facts (Test 1's company data, and a real Glassdoor-sourced comp benchmark of $351K–$532K total comp for Director-level Product Management at [REDACTED-COMPANY]) against a representative Director of Product Management scope for that level, in place of one specific vanished posting's exact text:

| Component | Score | Rationale |
|---|---|---|
| JD fit | 30/45 | Real product-leadership overlap (strategy, cross-functional ownership), but a genuine domain gap — [REDACTED-COMPANY]'s creative/enterprise-platform software vs. the persona's B2B SaaS background. |
| Seniority | 12/15 | Director-level is a one-step-up from the persona's Head of Product baseline — within the "recognisable next step" band, not a severe stretch. |
| Competition | 3/20 | Large, publicly traded, famous employer — correctly scores at the bottom of the band regardless of role specifics, per the rubric's design intent. |
| Comp | 10/10 | $351K–$532K is well above the £110k floor. |
| Blockers | 2/10 | **Real, confirmed blocker**: the persona has UK right-to-work only; this is a San Jose, onsite/hybrid role with no evidenced remote eligibility. |

**Total: 57/100 — Tier 4, Long shot.** The score is correctly dragged down by a real disqualifying constraint, not inflated by the otherwise-strong comp and seniority fit. This is the rubric doing its job: catching a genuine mismatch rather than producing a flattering number.

## Test 3 — Recalibration agent

Ran `SKILL.md` Step 6 against the actual example dataset. The mechanical part of this test (reading outcomes, computing per-component means) is no longer a one-off manual calculation — it's `scripts/verify_recalibration.py`, wired into CI, so it re-runs on every future change to `examples/`. Current output:

```
Total applications: 26
Logged outcomes: 22 (threshold: 20)  → gate PASSES
Positive outcomes: 5 (threshold: 3)  → gate PASSES

Component     Positive mean   Negative mean   Diff
jd_fit        39.4            34.3            +5.1
seniority     13.8            11.5            +2.3
competition   14.8            9.9             +4.9
comp          9.2             8.4             +0.8
blockers      10.0            9.6             +0.4
```

**Honest output the agent should give:** jd_fit and competition show the strongest association with positive outcomes in the logged data so far; comp and blockers show comparatively weak ones. This is a directional signal, not a validated finding — 5 positive outcomes is a very small sample, and the design's own conservatism rule (see `config/weights.json → recalibration`) means this should be surfaced as "worth watching," not acted on as a confident reweighting.

**A gap this surfaced and fixed:** the dataset originally had zero examples with a real blocker, so `blockers` showed exactly zero variance — the recalibration agent correctly had no signal on that component at all, because the demo data never tested it. Fixed by adding one synthetic application with a genuine confirmed blocker (missing work authorisation), giving the agent real, if still weak, signal on all five components. Left the original zero-variance finding in this log's history (visible in the git diff) rather than quietly editing it away.

## How to reproduce this

**The mechanical part (Test 3's statistics)** is fully reproducible right now: `python scripts/verify_recalibration.py`. It re-runs in CI on every push that touches `examples/` or `config/weights.json`, so it isn't just a one-time check.

**The LLM-interpreted parts (Tests 1 and 2 — actual scoring, actual live search)** are harder to make deterministic the same way, because they depend on a Claude session interpreting `SKILL.md`, not running fixed code. The honest limitation: both were run once, manually, in the same session that wrote the skill. The strongest way to independently verify these — not yet done, a good next step for whoever picks this up — is to open a genuinely fresh Claude.ai or Cowork session with no prior context, install `SKILL.md` cold, and re-score the same role (or a new one) to see whether an independent run produces comparably sound reasoning. That's a real test of the skill as *written*, rather than as *remembered by the person who wrote it*.

## What this does and doesn't prove

Proves: the scoring rubric, the live-search mechanism, and the recalibration computation all produce sensible, real output when actually run, including correctly surfacing a real disqualifying blocker rather than a flattering score. Proves the recalibration agent's statistical gate is now continuously verified, not a one-off claim.

Doesn't prove: that an independent Claude session, with no context from this build process, would interpret `SKILL.md` the same way. That's the one gap left un-closed here — see "How to reproduce this" above.
