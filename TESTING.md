# Testing log

This repo's skill logic was actually executed, not just written and left unverified. Six tests, run across sessions between 2026-07-09 and 2026-07-11, documented here as evidence rather than assertion.

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
Total applications: 29
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

## Test 4 — Dashboard prep-priority sort

Added `next_interview_date` to the schema and a default "prep priority" sort to `docs/index.html`: active applications first, soonest known interview date on top, active applications with no known date behind them by most recent activity, rejected/withdrawn always last regardless of date. A sort control also allows switching to a flat score sort (full pipeline, ignoring status) or the old most-recent-activity order.

Ran the rebuilt dashboard locally (`python -m http.server` against `docs/`) and drove it directly — no screenshots this session (the tool wasn't rendering), so verified via raw page text and DOM state instead, which is if anything a stricter check since it can't be fooled by something that merely *looks* right.

**Prep priority (default):** Briarcliff AI (next interview 16 Jun) and Alderwood Data (next interview 19 Jun) sorted to the top, in that order. Every other active application (no known next-interview date) followed, ordered by most recent activity. All rejected/withdrawn applications — regardless of date — sorted after every active one.

**Score sort:** re-sorted the same filtered set purely by `score.value` descending (88, 86, 84, 82, 81, 80, 79...), correctly mixing in closed applications rather than grouping by status — confirms this mode is a genuine flat full-pipeline sort, not prep-priority with a different tiebreaker.

**Most recent activity:** reproduced the dashboard's original (pre-this-change) default ordering exactly, confirming the old behavior is preserved as an explicit option rather than lost.

**Confidence:** confirmed — all three modes read back exactly as designed against the real rebuilt dataset, not asserted from reading the code alone.

## Test 5 — Briefing Pack v2 (standard sections, honest placeholders)

Extended the Briefing pack schema with five new sections (Unique selling points, Interviewer profiles, Prep questions, Questions to ask, Notes) and their parsers in `scripts/build_dashboard.py`. Also found and fixed a real, pre-existing bug during this work: `SCHEMA.md` documented `### Why it progressed / didn't` as the heading, but the parser looked for the exact string `"Why it progressed"` — a file written exactly as documented wouldn't have parsed correctly. Nothing in CI would have caught this (the diff-check only compares build output to committed output, and both were silently wrong together), so `scripts/verify_consistency.py` now round-trips `SCHEMA.md`'s own documented example through the real parser on every push, specifically to close this bug class.

Regenerated all 34 example applications via `scripts/generate_examples.py`. Ran the rebuilt dashboard locally and drove it directly (not just read the code):

- **Full-depth card (Alderwood Data):** all ten Briefing pack sections rendered with real content — 3 USPs, 2 interviewer profiles (one with both "assessing"/"play it" callouts filled in, proving the optional-callout path), 4 Q&A pairs, 3 questions to ask, bullet-format watch-outs, a Notes sub-section. Confirmed a real bug live: USP/watch-out titles rendered with a double period (`"...experience.."`) because the markdown source already includes the period inside the bold text and the renderer added a second one — fixed in `docs/index.html`, re-verified.
- **Placeholder card (Pemberton Health Tech):** deliberately built with an unknown interviewer and unknown Notes, to prove the placeholder path actually works, not just claim it. Confirmed via DOM inspection: exactly one `.unknown`-classed element for the interviewer profile (name renders as "Currently unknown", title as the specific ask), and the Notes prose paragraph also correctly gets the `.unknown` treatment — both written as normal content in their section's own format, no special-case rendering path needed.
- **Briarcliff AI:** interviewer profile with no optional callouts filled in — confirmed the callout lines simply don't render rather than showing empty labels.

## Test 6 — Status vocabulary v2 (pre/post-interview split, recalibration signal)

Extended `status` from six values to eleven (`awaiting_recruiter`, `rejected_after_interview`, `withdrawn_after_interview`, `assumed_rejected`, `role_closed` added), replacing the separate `outcome`/`outcome_date` fields entirely — a second, independently-mutable source of truth for the same fact `status` now expresses more precisely was exactly the kind of thing that caused the Test 5 bug above. Recalibration and score-locking now derive everything from `status` via a new shared module, `scripts/_status.py`, imported by both `build_dashboard.py` and `verify_recalibration.py` so the two can't drift apart the way `outcome` could.

Added two new fully-fleshed examples specifically to prove the pre/post-interview distinction actually changes the recalibration signal, not just the display label — **Fenwick Data Systems** (`rejected_after_interview`, two positive interview stages before losing to an internal candidate) and **Silverlake Systems** (`withdrawn_after_interview`, withdrew after Stage 2 once comp was confirmed below floor).

Ran `python scripts/verify_recalibration.py` before and after this change against the full 34-application set:

```
Total applications: 34
Logged outcomes: 25 (threshold: 20)  → gate PASSES
Positive outcomes: 7 (threshold: 3)  → gate PASSES

Component     Positive mean   Negative mean   Diff
jd_fit        38.7            34.3            +4.4
seniority     13.6            11.4            +2.1
competition   14.3            9.9             +4.3
comp          9.1             8.4             +0.8
blockers      10.0            9.6             +0.4
```

Positive outcomes rose from 5 to 7 — Fenwick and Silverlake now correctly count as positive signal (they validated the scoring rubric's prediction by reaching interview) rather than being indistinguishable from a flat rejection, which is the entire point of this change. Confirmed `score.locked` derives correctly for every status via `scripts/_status.py`'s `should_lock()`: `true` for all six closed statuses and for `offer` (terminal for locking purposes even though it stays in the dashboard's active group for sorting), `false` for `scored`/`applied`/`awaiting_recruiter`/`interviewing`. Also ran `scripts/verify_consistency.py`'s second check — confirmed `docs/index.html`'s JS `STATUS_ORDER` array matches `scripts/_status.py`'s `ALL_STATUSES` exactly, closing the same class of Python/JS drift risk the SCHEMA.md check closes for docs/parser drift.

Confirmed in the live dashboard: `rejected_after_interview` and `withdrawn_after_interview` sort into the closed group (bottom, regardless of date) alongside the other four closed statuses, with distinct badge labels ("Rejected (post-interview)", "Withdrawn (post-interview)") and an expanded stats bar showing the pre/post split explicitly rather than burying it behind filter pills — that split is the actual signal this change exists to surface.

## How to reproduce this

**The mechanical parts (Test 3's statistics, Test 5/6's consistency checks)** are fully reproducible right now: `python scripts/verify_recalibration.py` and `python scripts/verify_consistency.py`. Both re-run in CI on every push that touches `examples/`, `docs/index.html`, `schema/SCHEMA.md`, `scripts/_status.py`, or `config/weights.json`, so none of this is a one-time check.

**The LLM-interpreted parts (Tests 1 and 2 — actual scoring, actual live search; and the "real synthesis, not generic filler" quality bar for Briefing pack v2's USPs/prep Q&A, which no script can verify)** are harder to make deterministic the same way, because they depend on a Claude session interpreting `SKILL.md`, not running fixed code. The honest limitation: all of it was run once, manually, in the same sessions that wrote the skill. The strongest way to independently verify this — not yet done, a good next step for whoever picks this up — is to open a genuinely fresh Claude.ai or Cowork session with no prior context, install `SKILL.md` cold, and re-score a role and generate a Briefing pack to see whether an independent run produces comparably sound reasoning and genuinely grounded (not generic) content. That's a real test of the skill as *written*, rather than as *remembered by the person who wrote it*.

## What this does and doesn't prove

Proves: the scoring rubric, the live-search mechanism, and the recalibration computation all produce sensible, real output when actually run, including correctly surfacing a real disqualifying blocker rather than a flattering score. Proves the recalibration agent's statistical gate is now continuously verified, not a one-off claim, and that it correctly treats a post-interview rejection as positive signal, not a flat negative. Proves the dashboard's sort logic and the eleven-status vocabulary behave exactly as designed against real rebuilt data. Proves the Briefing pack v2 sections — both fully-populated and honestly-placeholdered — render correctly, and found and fixed two real bugs (a docs/parser heading mismatch, a double-period rendering bug) by actually running the thing rather than trusting the code by inspection.

Doesn't prove: that an independent Claude session, with no context from this build process, would interpret `SKILL.md` the same way — including, now, whether it would default to genuine synthesis over `Currently unknown` placeholders as intended, rather than either extreme. That's the one gap left un-closed here — see "How to reproduce this" above.
