# Testing log

This repo's skill logic was actually executed, not just written and left unverified. Three tests, run 2026-07-09, documented here as evidence rather than assertion.

**Note on scope:** the two tests below that use a real company ([REDACTED-COMPANY]) are validation exercises only — no application was submitted, no contact was made with anyone, and [REDACTED-COMPANY]'s real data is never written into `examples/`, which stays 100% fictional as documented in the README. This log is the one place in the repo where a real, well-known public company is named, specifically to prove the tool's mechanisms work on real inputs, not just synthetic ones designed to make it look good.

## Test 1 — Live-search verification agent

Ran a live search for [REDACTED-COMPANY] ([REDACTED-TICKER]), following `SKILL.md` Step 3.

**Result:** ~31,000–33,000 employees (sources disagree slightly, expected for headcount data), FY2025 revenue $23.77B, FY2026 target $26.5–26.6B, publicly traded. Confirms the mechanism retrieves real, current, externally-sourced facts rather than relying on the model's static training knowledge — which is the entire point of this agent existing.

**Confidence:** confirmed (multiple independent sources agreed on order of magnitude).

## Test 2 — Full scoring pipeline

Scored a Director-level Product Management role at [REDACTED-COMPANY] against the fictional example CV (`examples/CV-example.md` — Jordan Ainsley, Head of Product, ~9 years, UK right-to-work only, comp floor £110k).

**A genuine limitation surfaced here first:** four separate [REDACTED-COMPANY] job posting URLs, all appearing in live search results, returned "this position has been filled" or HTTP 410 when fetched minutes later. Listings age out of search indexes fast. This doesn't affect the tool's real design — a user pastes JD text directly into the conversation rather than the skill fetching a URL — but it's a genuine finding worth recording rather than hiding: don't rely on a search-indexed job link still being live by the time you follow it.

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

Ran `SKILL.md` Step 6 against the actual 25-application example dataset (computed for real, not hand-written to look plausible):

```
Logged outcomes: 21 (threshold: 20)  → gate PASSES
Positive outcomes: 5 (threshold: 3)  → gate PASSES

Component     Positive mean   Negative mean   Diff
jd_fit        39.4            34.2            +5.2
seniority     13.8            11.4            +2.4
competition   14.8            9.8             +5.0
comp          9.2             8.2             +0.9
blockers      10.0            10.0            +0.0
```

**Honest output the agent should give:** jd_fit and competition show the strongest association with positive outcomes in the logged data so far; comp shows a comparatively weak one. This is a directional signal, not a validated finding — 5 positive outcomes is a very small sample, and the design's own conservatism rule (see `config/weights.json → recalibration`) means this should be surfaced as "worth watching," not acted on as a confident reweighting.

**A genuine limitation this surfaced:** `blockers` shows exactly zero variance, because none of the synthetic example applications include an actual blocker case. The recalibration agent correctly has no signal on that component — not a bug, but worth knowing if you're using the example dataset to sanity-check the agent's behaviour: it will never suggest touching `blockers` weight against this data, and it shouldn't.

## What this does and doesn't prove

Proves: the scoring rubric, the live-search mechanism, and the recalibration computation all produce sensible, real output when actually run, including correctly surfacing a real disqualifying blocker rather than a flattering score.

Doesn't prove: this was run manually, once, by the person who wrote the skill, not by an independent Claude session following `SKILL.md` cold with no other context. It's evidence the logic works, not a substitute for you trying it yourself against your own data.
