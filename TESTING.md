# Testing log

This repo's skill logic was actually executed, not just written and left unverified. Ten tests, run across sessions between 2026-07-09 and 2026-07-11, documented here as evidence rather than assertion.

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

## Test 7 — Status vocabulary simplified to nine values

Real-world review of Test 6's eleven-status design found two problems: `awaiting_recruiter` and `role_closed` were messy to track in practice and added states without adding useful signal, and the model didn't have a clean home for "scored a JD, then deliberately decided not to apply" — that case was left implicitly indistinguishable from "still deciding," sitting at `status: scored` forever either way.

Fixed by removing both unused statuses and adding `didnt_apply` as a genuine sibling to `applied` (both reachable only from `scored`), and folding "withdrew after applying but before interviewing" into plain `rejected` rather than giving it a dedicated status — rare enough, and ambiguous enough for the recalibration signal, that it wasn't earning its own state. The state machine is now fully exhaustive and small:

```
scored       -> applied | didnt_apply
applied      -> rejected | assumed_rejected | interviewing
interviewing -> offer | rejected_after_interview | withdrew_after_interview
```

Also renamed `withdrawn`/`withdrawn_after_interview` to `withdrew`/`withdrew_after_interview` (simple past tense, matching `rejected`), and removed the parenthetical from both post-interview badge labels ("Rejected (post-interview)" → "Rejected post-interview", same for withdrew).

Repurposed the existing Redshank Payments example (previously a pre-interview `withdrawn` case) into a `didnt_apply` case instead — comp confirmed below floor before ever submitting, comp component correctly scored 2/10 to match (it had incorrectly scored 10/10 in the original, a real scoring-logic bug this rewrite also fixed: "confirmed below floor" should never score near-full marks on comp). Removed the two examples that existed solely to demonstrate the now-dropped statuses (Cross Timber Logistics, Pinehollow Systems) rather than force-fitting them elsewhere.

Ran the full verification suite against the simplified 32-application set (down from 34):

```
$ python scripts/verify_consistency.py
SCHEMA.md's Briefing pack example round-trips correctly through the parser (10 sections checked).
docs/index.html's STATUS_ORDER matches scripts/_status.py's ALL_STATUSES (9 statuses).

$ python scripts/verify_recalibration.py
Total applications: 32
Logged outcomes: 24 (threshold: 20)  → gate PASSES
Positive outcomes: 7 (threshold: 3)  → gate PASSES
```

Confirmed live in the dashboard: Redshank Payments shows `scored 11 May 2026` (not `applied`, since `date_applied` is correctly `null`) with a "Didn't apply" badge; `score.locked` is `true` for it despite never having been applied to, since a deliberate decision is still a closed, final state. All nine statuses are exercised somewhere in the example set. Stats bar shows all nine buckets with bracket-free labels.

## Test 8 — Headline stats and status-flow legend

Split three headline numbers (Total tracked, Interviewed, Rejected) out of the per-status breakdown grid, styled distinctly (32px colored figures vs. 22px neutral tiles) so the one question that actually matters — "is this working" — isn't buried in nine equally-weighted tiles. "Interviewed" and "Rejected" reuse the exact `REACHED_INTERVIEW`/`NO_INTERVIEW_NEGATIVE` sets the recalibration agent already uses (`scripts/_status.py`), so the headline numbers and the recalibration signal can never silently disagree about what counts as which. Extended `scripts/verify_consistency.py` with a third check confirming the JS mirrors of those two sets match Python exactly — same drift protection already in place for `STATUS_ORDER`.

Also added a collapsible status-flow legend to the dashboard (collapsed by default) and a Mermaid flowchart to the README, both showing the exact nine-status state machine. The dashboard legend reuses the existing `.badge` classes rather than introducing new colors, so it can't visually drift from what the actual application cards show.

Ran live:

```
$ python scripts/verify_consistency.py
SCHEMA.md's Briefing pack example round-trips correctly through the parser (10 sections checked).
docs/index.html's STATUS_ORDER matches scripts/_status.py's ALL_STATUSES (9 statuses).
docs/index.html's REACHED_INTERVIEW and NO_INTERVIEW_NEGATIVE match scripts/_status.py.
```

Confirmed in the browser via DOM inspection (screenshots weren't rendering this session): headline stats read Total tracked 32, Interviewed 7, Rejected 17 — the interviewed count matches Test 7's recalibration "positive outcomes" figure exactly, as it should since both derive from the same set. "Total tracked" no longer appears in the per-status grid. Clicked the flow-legend toggle and confirmed all three rows render with the correct transitions and badge colors (scored=purple, applied/interviewing=blue/green, rejected variants=red, didnt_apply/assumed_rejected/withdrew=grey, offer=gold).

**Correction, same session:** the "Rejected" headline label was ambiguous against the granular "Rejected"/"Rejected post-interview" tiles directly below it — a post-interview rejection deliberately counts toward "Interviewed" at the headline level (it validated the scoring prediction) but that's not obvious from the word "Rejected" alone. Considered three options (`Interviewed`/`Not interviewed`, `Reached Interview`/`Didn't Reach Interview`, `Interviewed`/`Rejected before interview`) against length and ambiguity; landed on `Not interviewed`, with the sub-label tightened to "confirmed rejected, interview never reached" to also rule out a "hasn't interviewed yet" misreading against still-active `applied` applications. Rebuilt, re-ran `verify_consistency.py` (unaffected — it checks the underlying status sets, not display text), and re-confirmed in the browser: same counts (32/7/17), new label and CSS class (`not-interviewed`), no console errors.

## Test 9 — Status display order follows the state machine, not active/closed grouping

The prior status-vocabulary work ordered statuses as "active statuses, then closed statuses" (`scored, applied, interviewing, offer, didnt_apply, rejected, ...`), which reads oddly against the actual flow — `offer` sitting in position 4 when it's really the very last thing that can happen, and `assumed_rejected` separated from `rejected` by three unrelated statuses.

Reordered `scripts/_status.py`'s `ALL_STATUSES` to a flow-order read of the state machine instead — each status sits right after wherever it's reached from — with `offer` deliberately pulled to the very end even though structurally it's just one of `interviewing`'s three exits:

```
scored, didnt_apply, applied, rejected, assumed_rejected,
interviewing, rejected_after_interview, withdrew_after_interview, offer
```

`ALL_STATUSES` is no longer derived as `ACTIVE_STATUSES + CLOSED_STATUSES` (that concatenation is exactly what produced the grouped-not-flow order) — it's now the explicit, independent source of truth for display/filter order, while `ACTIVE_STATUSES`/`CLOSED_STATUSES` remain membership-only groups for classification logic where order was never load-bearing.

Propagated to every place order is shown: `docs/index.html`'s `STATUS_ORDER` (drives filter pills), the per-status stats grid array, the status-flow legend's row ordering (Didn't apply before Applied; Offer last in its row), and `SCHEMA.md`'s status table.

Ran live:

```
$ python scripts/verify_consistency.py
SCHEMA.md's Briefing pack example round-trips correctly through the parser (10 sections checked).
docs/index.html's STATUS_ORDER matches scripts/_status.py's ALL_STATUSES (9 statuses).
docs/index.html's REACHED_INTERVIEW and NO_INTERVIEW_NEGATIVE match scripts/_status.py.
```

Confirmed in the browser via DOM inspection: filter pills, the per-status stats grid, and the flow legend all read `Scored → Didn't apply → Applied → Rejected → Assumed rejected → Interviewing → Rejected post-interview → Withdrew post-interview → Offer` — the same order in all three places, no drift between them, `Offer` last everywhere it appears.

## Test 10 — Average score by Interviewed vs. Not interviewed

Requested feature: the legacy hand-maintained tracker this toolkit is replacing showed average score for interviewed vs. not-interviewed applications, and it's genuinely useful — it's the most direct visual answer to "is the scoring rubric actually predicting callbacks." Added to the two relevant headline tiles (`docs/index.html`'s `renderHeadlineStats()`), reusing the exact same `REACHED_INTERVIEW`/`NO_INTERVIEW_NEGATIVE` groupings the counts and the recalibration agent already use — no new classification logic, no new drift risk.

Verified by computing the same average independently in the browser console (not just reading the code) and comparing against what the tile actually rendered:

```
Interviewed tile:      "avg score 79.4"
Not interviewed tile:  "avg score 62.1"
Independent check:     interviewedAvg=79.4, notInterviewedAvg=62.1  — matches exactly
```

The ~17-point gap is directionally consistent with Test 6/7's per-component recalibration means (positive means consistently higher than negative means across jd_fit, seniority, competition) — this is the same underlying signal, just expressed as one overall number instead of five per-component ones. Colored to match each tile (green for Interviewed, red for Not interviewed); confirmed via `getComputedStyle()`, not just visual assumption.

## How to reproduce this

**The mechanical parts (Test 3's statistics, Test 5/6's consistency checks)** are fully reproducible right now: `python scripts/verify_recalibration.py` and `python scripts/verify_consistency.py`. Both re-run in CI on every push that touches `examples/`, `docs/index.html`, `schema/SCHEMA.md`, `scripts/_status.py`, or `config/weights.json`, so none of this is a one-time check.

**The LLM-interpreted parts (Tests 1 and 2 — actual scoring, actual live search; and the "real synthesis, not generic filler" quality bar for Briefing pack v2's USPs/prep Q&A, which no script can verify)** are harder to make deterministic the same way, because they depend on a Claude session interpreting `SKILL.md`, not running fixed code. The honest limitation: all of it was run once, manually, in the same sessions that wrote the skill. The strongest way to independently verify this — not yet done, a good next step for whoever picks this up — is to open a genuinely fresh Claude.ai or Cowork session with no prior context, install `SKILL.md` cold, and re-score a role and generate a Briefing pack to see whether an independent run produces comparably sound reasoning and genuinely grounded (not generic) content. That's a real test of the skill as *written*, rather than as *remembered by the person who wrote it*.

## What this does and doesn't prove

Proves: the scoring rubric, the live-search mechanism, and the recalibration computation all produce sensible, real output when actually run, including correctly surfacing a real disqualifying blocker rather than a flattering score. Proves the recalibration agent's statistical gate is now continuously verified, not a one-off claim, and that it correctly treats a post-interview rejection as positive signal, not a flat negative. Proves the dashboard's sort logic and the eleven-status vocabulary behave exactly as designed against real rebuilt data. Proves the Briefing pack v2 sections — both fully-populated and honestly-placeholdered — render correctly, and found and fixed two real bugs (a docs/parser heading mismatch, a double-period rendering bug) by actually running the thing rather than trusting the code by inspection.

Doesn't prove: that an independent Claude session, with no context from this build process, would interpret `SKILL.md` the same way — including, now, whether it would default to genuine synthesis over `Currently unknown` placeholders as intended, rather than either extreme. That's the one gap left un-closed here — see "How to reproduce this" above.
