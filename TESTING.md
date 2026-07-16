# Testing log

This repo's skill logic was actually executed, not just written and left unverified. Twenty-six tests, run across sessions between 2026-07-09 and 2026-07-16, documented here as evidence rather than assertion.

**Note on scope:** every test in this log uses fictional company names, even where the underlying test was run against a real job description – the pipeline this repo replaces is the author's real, active job search, and no real employer name or real application detail belongs in a public repo. Where a test needed real-world grounding (a live search actually returning current facts, a scoring run against real market data), the company name and any identifying specifics are fictionalised while the mechanism being tested – live search working, the scoring rubric producing a defensible number – is described honestly.

## Test 1 – Live-search verification agent

Ran a live search for a large, publicly traded enterprise software company ("Halcyon Creative Systems" here – a real, well-known company was used for this test but is not named), following `SKILL.md` Step 3.

**Result:** company headcount and revenue figures were returned from multiple independent sources, in general agreement on order of magnitude, along with confirmation of its public listing. Confirms the mechanism retrieves real, current, externally-sourced facts rather than relying on the model's static training knowledge – which is the entire point of this agent existing.

**Confidence:** confirmed (multiple independent sources agreed on order of magnitude).

## Test 2 – Full scoring pipeline

Scored a Director-level Product Management role at "Halcyon Creative Systems" against the fictional example CV (`examples/CV-example.md` – Jordan Ainsley, Head of Product, ~9 years, UK right-to-work only, comp floor £110k).

**A testing-methodology note, not a product limitation:** several job posting URLs, all appearing in live search results, returned "this position has been filled" or HTTP 410 when fetched minutes later. This happened because *this test* tried to fetch a live JD from a URL, which is not how the tool actually works – in real use, you paste the JD text directly into the conversation, already captured, so it can't go stale between finding it and scoring it. Recorded here because it's a genuine friction worth knowing about if you ever try to test this the same way (by following search-indexed links), not because it limits the shipped product.

Scored using real, verified market data (Test 1's company data, and a real comp benchmark for Director-level Product Management at a company of this profile) against a representative Director of Product Management scope for that level, in place of one specific vanished posting's exact text:

| Component | Score | Rationale |
|---|---|---|
| JD fit | 30/45 | Real product-leadership overlap (strategy, cross-functional ownership), but a genuine domain gap – this company's creative/enterprise-platform software vs. the persona's B2B SaaS background. |
| Seniority | 12/15 | Director-level is a one-step-up from the persona's Head of Product baseline – within the "recognisable next step" band, not a severe stretch. |
| Competition | 3/20 | Large, publicly traded, famous employer – correctly scores at the bottom of the band regardless of role specifics, per the rubric's design intent. |
| Comp | 10/10 | The verified market comp range is well above the £110k floor. |
| Blockers | 2/10 | **Real, confirmed blocker**: the persona has UK right-to-work only; this is a San Jose, onsite/hybrid role with no evidenced remote eligibility. |

**Total: 57/100 – Tier 4, Long shot.** The score is correctly dragged down by a real disqualifying constraint, not inflated by the otherwise-strong comp and seniority fit. This is the rubric doing its job: catching a genuine mismatch rather than producing a flattering number.

## Test 3 – Recalibration agent

Ran `SKILL.md` Step 6 against the actual example dataset. The mechanical part of this test (reading outcomes, computing per-component means) is no longer a one-off manual calculation – it's `scripts/verify_recalibration.py`, wired into CI, so it re-runs on every future change to `examples/`. Current output:

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

**Honest output the agent should give:** jd_fit and competition show the strongest association with positive outcomes in the logged data so far; comp and blockers show comparatively weak ones. This is a directional signal, not a validated finding – 5 positive outcomes is a very small sample, and the design's own conservatism rule (see `config/weights.json → recalibration`) means this should be surfaced as "worth watching," not acted on as a confident reweighting.

**A gap this surfaced and fixed:** the dataset originally had zero examples with a real blocker, so `blockers` showed exactly zero variance – the recalibration agent correctly had no signal on that component at all, because the demo data never tested it. Fixed by adding one synthetic application with a genuine confirmed blocker (missing work authorisation), giving the agent real, if still weak, signal on all five components. Left the original zero-variance finding in this log's history (visible in the git diff) rather than quietly editing it away.

## Test 4 – Dashboard prep-priority sort

Added `next_interview_date` to the schema and a default "prep priority" sort to `docs/index.html`: active applications first, soonest known interview date on top, active applications with no known date behind them by most recent activity, rejected/withdrawn always last regardless of date. A sort control also allows switching to a flat score sort (full pipeline, ignoring status) or the old most-recent-activity order.

Ran the rebuilt dashboard locally (`python -m http.server` against `docs/`) and drove it directly – no screenshots this session (the tool wasn't rendering), so verified via raw page text and DOM state instead, which is if anything a stricter check since it can't be fooled by something that merely *looks* right.

**Prep priority (default):** Briarcliff AI (next interview 16 Jun) and Alderwood Data (next interview 19 Jun) sorted to the top, in that order. Every other active application (no known next-interview date) followed, ordered by most recent activity. All rejected/withdrawn applications – regardless of date – sorted after every active one.

**Score sort:** re-sorted the same filtered set purely by `score.value` descending (88, 86, 84, 82, 81, 80, 79...), correctly mixing in closed applications rather than grouping by status – confirms this mode is a genuine flat full-pipeline sort, not prep-priority with a different tiebreaker.

**Most recent activity:** reproduced the dashboard's original (pre-this-change) default ordering exactly, confirming the old behavior is preserved as an explicit option rather than lost.

**Confidence:** confirmed – all three modes read back exactly as designed against the real rebuilt dataset, not asserted from reading the code alone.

## Test 5 – Briefing Pack v2 (standard sections, honest placeholders)

Extended the Briefing pack schema with five new sections (Unique selling points, Interviewer profiles, Prep questions, Questions to ask, Notes) and their parsers in `scripts/build_dashboard.py`. Also found and fixed a real, pre-existing bug during this work: `SCHEMA.md` documented `### Why it progressed / didn't` as the heading, but the parser looked for the exact string `"Why it progressed"` – a file written exactly as documented wouldn't have parsed correctly. Nothing in CI would have caught this (the diff-check only compares build output to committed output, and both were silently wrong together), so `scripts/verify_consistency.py` now round-trips `SCHEMA.md`'s own documented example through the real parser on every push, specifically to close this bug class.

Regenerated all 34 example applications via `scripts/generate_examples.py`. Ran the rebuilt dashboard locally and drove it directly (not just read the code):

- **Full-depth card (Alderwood Data):** all ten Briefing pack sections rendered with real content – 3 USPs, 2 interviewer profiles (one with both "assessing"/"play it" callouts filled in, proving the optional-callout path), 4 Q&A pairs, 3 questions to ask, bullet-format watch-outs, a Notes sub-section. Confirmed a real bug live: USP/watch-out titles rendered with a double period (`"...experience.."`) because the markdown source already includes the period inside the bold text and the renderer added a second one – fixed in `docs/index.html`, re-verified.
- **Placeholder card (Pemberton Health Tech):** deliberately built with an unknown interviewer and unknown Notes, to prove the placeholder path actually works, not just claim it. Confirmed via DOM inspection: exactly one `.unknown`-classed element for the interviewer profile (name renders as "Currently unknown", title as the specific ask), and the Notes prose paragraph also correctly gets the `.unknown` treatment – both written as normal content in their section's own format, no special-case rendering path needed.
- **Briarcliff AI:** interviewer profile with no optional callouts filled in – confirmed the callout lines simply don't render rather than showing empty labels.

## Test 6 – Status vocabulary v2 (pre/post-interview split, recalibration signal)

Extended `status` from six values to eleven (`awaiting_recruiter`, `rejected_after_interview`, `withdrawn_after_interview`, `assumed_rejected`, `role_closed` added), replacing the separate `outcome`/`outcome_date` fields entirely – a second, independently-mutable source of truth for the same fact `status` now expresses more precisely was exactly the kind of thing that caused the Test 5 bug above. Recalibration and score-locking now derive everything from `status` via a new shared module, `scripts/_status.py`, imported by both `build_dashboard.py` and `verify_recalibration.py` so the two can't drift apart the way `outcome` could.

Added two new fully-fleshed examples specifically to prove the pre/post-interview distinction actually changes the recalibration signal, not just the display label – **Fenwick Data Systems** (`rejected_after_interview`, two positive interview stages before losing to an internal candidate) and **Silverlake Systems** (`withdrawn_after_interview`, withdrew after Stage 2 once comp was confirmed below floor).

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

Positive outcomes rose from 5 to 7 – Fenwick and Silverlake now correctly count as positive signal (they validated the scoring rubric's prediction by reaching interview) rather than being indistinguishable from a flat rejection, which is the entire point of this change. Confirmed `score.locked` derives correctly for every status via `scripts/_status.py`'s `should_lock()`: `true` for all six closed statuses and for `offer` (terminal for locking purposes even though it stays in the dashboard's active group for sorting), `false` for `scored`/`applied`/`awaiting_recruiter`/`interviewing`. Also ran `scripts/verify_consistency.py`'s second check – confirmed `docs/index.html`'s JS `STATUS_ORDER` array matches `scripts/_status.py`'s `ALL_STATUSES` exactly, closing the same class of Python/JS drift risk the SCHEMA.md check closes for docs/parser drift.

Confirmed in the live dashboard: `rejected_after_interview` and `withdrawn_after_interview` sort into the closed group (bottom, regardless of date) alongside the other four closed statuses, with distinct badge labels ("Rejected (post-interview)", "Withdrawn (post-interview)") and an expanded stats bar showing the pre/post split explicitly rather than burying it behind filter pills – that split is the actual signal this change exists to surface.

## Test 7 – Status vocabulary simplified to nine values

Real-world review of Test 6's eleven-status design found two problems: `awaiting_recruiter` and `role_closed` were messy to track in practice and added states without adding useful signal, and the model didn't have a clean home for "scored a JD, then deliberately decided not to apply" – that case was left implicitly indistinguishable from "still deciding," sitting at `status: scored` forever either way.

Fixed by removing both unused statuses and adding `didnt_apply` as a genuine sibling to `applied` (both reachable only from `scored`), and folding "withdrew after applying but before interviewing" into plain `rejected` rather than giving it a dedicated status – rare enough, and ambiguous enough for the recalibration signal, that it wasn't earning its own state. The state machine is now fully exhaustive and small:

```
scored       -> applied | didnt_apply
applied      -> rejected | assumed_rejected | interviewing
interviewing -> offer | rejected_after_interview | withdrew_after_interview
```

Also renamed `withdrawn`/`withdrawn_after_interview` to `withdrew`/`withdrew_after_interview` (simple past tense, matching `rejected`), and removed the parenthetical from both post-interview badge labels ("Rejected (post-interview)" → "Rejected post-interview", same for withdrew).

Repurposed the existing Redshank Payments example (previously a pre-interview `withdrawn` case) into a `didnt_apply` case instead – comp confirmed below floor before ever submitting, comp component correctly scored 2/10 to match (it had incorrectly scored 10/10 in the original, a real scoring-logic bug this rewrite also fixed: "confirmed below floor" should never score near-full marks on comp). Removed the two examples that existed solely to demonstrate the now-dropped statuses (Cross Timber Logistics, Pinehollow Systems) rather than force-fitting them elsewhere.

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

## Test 8 – Headline stats and status-flow legend

Split three headline numbers (Total tracked, Interviewed, Rejected) out of the per-status breakdown grid, styled distinctly (32px colored figures vs. 22px neutral tiles) so the one question that actually matters – "is this working" – isn't buried in nine equally-weighted tiles. "Interviewed" and "Rejected" reuse the exact `REACHED_INTERVIEW`/`NO_INTERVIEW_NEGATIVE` sets the recalibration agent already uses (`scripts/_status.py`), so the headline numbers and the recalibration signal can never silently disagree about what counts as which. Extended `scripts/verify_consistency.py` with a third check confirming the JS mirrors of those two sets match Python exactly – same drift protection already in place for `STATUS_ORDER`.

Also added a collapsible status-flow legend to the dashboard (collapsed by default) and a Mermaid flowchart to the README, both showing the exact nine-status state machine. The dashboard legend reuses the existing `.badge` classes rather than introducing new colors, so it can't visually drift from what the actual application cards show.

Ran live:

```
$ python scripts/verify_consistency.py
SCHEMA.md's Briefing pack example round-trips correctly through the parser (10 sections checked).
docs/index.html's STATUS_ORDER matches scripts/_status.py's ALL_STATUSES (9 statuses).
docs/index.html's REACHED_INTERVIEW and NO_INTERVIEW_NEGATIVE match scripts/_status.py.
```

Confirmed in the browser via DOM inspection (screenshots weren't rendering this session): headline stats read Total tracked 32, Interviewed 7, Rejected 17 – the interviewed count matches Test 7's recalibration "positive outcomes" figure exactly, as it should since both derive from the same set. "Total tracked" no longer appears in the per-status grid. Clicked the flow-legend toggle and confirmed all three rows render with the correct transitions and badge colors (scored=purple, applied/interviewing=blue/green, rejected variants=red, didnt_apply/assumed_rejected/withdrew=grey, offer=gold).

**Correction, same session:** the "Rejected" headline label was ambiguous against the granular "Rejected"/"Rejected post-interview" tiles directly below it – a post-interview rejection deliberately counts toward "Interviewed" at the headline level (it validated the scoring prediction) but that's not obvious from the word "Rejected" alone. Considered three options (`Interviewed`/`Not interviewed`, `Reached Interview`/`Didn't Reach Interview`, `Interviewed`/`Rejected before interview`) against length and ambiguity; landed on `Not interviewed`, with the sub-label tightened to "confirmed rejected, interview never reached" to also rule out a "hasn't interviewed yet" misreading against still-active `applied` applications. Rebuilt, re-ran `verify_consistency.py` (unaffected – it checks the underlying status sets, not display text), and re-confirmed in the browser: same counts (32/7/17), new label and CSS class (`not-interviewed`), no console errors.

## Test 9 – Status display order follows the state machine, not active/closed grouping

The prior status-vocabulary work ordered statuses as "active statuses, then closed statuses" (`scored, applied, interviewing, offer, didnt_apply, rejected, ...`), which reads oddly against the actual flow – `offer` sitting in position 4 when it's really the very last thing that can happen, and `assumed_rejected` separated from `rejected` by three unrelated statuses.

Reordered `scripts/_status.py`'s `ALL_STATUSES` to a flow-order read of the state machine instead – each status sits right after wherever it's reached from – with `offer` deliberately pulled to the very end even though structurally it's just one of `interviewing`'s three exits:

```
scored, didnt_apply, applied, rejected, assumed_rejected,
interviewing, rejected_after_interview, withdrew_after_interview, offer
```

`ALL_STATUSES` is no longer derived as `ACTIVE_STATUSES + CLOSED_STATUSES` (that concatenation is exactly what produced the grouped-not-flow order) – it's now the explicit, independent source of truth for display/filter order, while `ACTIVE_STATUSES`/`CLOSED_STATUSES` remain membership-only groups for classification logic where order was never load-bearing.

Propagated to every place order is shown: `docs/index.html`'s `STATUS_ORDER` (drives filter pills), the per-status stats grid array, the status-flow legend's row ordering (Didn't apply before Applied; Offer last in its row), and `SCHEMA.md`'s status table.

Ran live:

```
$ python scripts/verify_consistency.py
SCHEMA.md's Briefing pack example round-trips correctly through the parser (10 sections checked).
docs/index.html's STATUS_ORDER matches scripts/_status.py's ALL_STATUSES (9 statuses).
docs/index.html's REACHED_INTERVIEW and NO_INTERVIEW_NEGATIVE match scripts/_status.py.
```

Confirmed in the browser via DOM inspection: filter pills, the per-status stats grid, and the flow legend all read `Scored → Didn't apply → Applied → Rejected → Assumed rejected → Interviewing → Rejected post-interview → Withdrew post-interview → Offer` – the same order in all three places, no drift between them, `Offer` last everywhere it appears.

## Test 10 – Average score by Interviewed vs. Not interviewed

Requested feature: the legacy hand-maintained tracker this toolkit is replacing showed average score for interviewed vs. not-interviewed applications, and it's genuinely useful – it's the most direct visual answer to "is the scoring rubric actually predicting callbacks." Added to the two relevant headline tiles (`docs/index.html`'s `renderHeadlineStats()`), reusing the exact same `REACHED_INTERVIEW`/`NO_INTERVIEW_NEGATIVE` groupings the counts and the recalibration agent already use – no new classification logic, no new drift risk.

Verified by computing the same average independently in the browser console (not just reading the code) and comparing against what the tile actually rendered:

```
Interviewed tile:      "avg score 79.4"
Not interviewed tile:  "avg score 62.1"
Independent check:     interviewedAvg=79.4, notInterviewedAvg=62.1  – matches exactly
```

The ~17-point gap is directionally consistent with Test 6/7's per-component recalibration means (positive means consistently higher than negative means across jd_fit, seniority, competition) – this is the same underlying signal, just expressed as one overall number instead of five per-component ones. Colored to match each tile (green for Interviewed, red for Not interviewed); confirmed via `getComputedStyle()`, not just visual assumption.

## Test 11 – Regional intelligence: first-class, genuinely optional

Promoted "regional intelligence" (relationship/decision-making style by market) out of the generic Notes catch-all into its own structured section – real table parsing and rendering, not just prose. Unlike the five standard sections, this one is deliberately **not** forced onto every application with a placeholder: it's genuinely absent for single-market roles, present only when the role actually spans multiple markets.

**Found and fixed a real bug during this work, before it shipped:** the first version of `parse_table()` treated every line in the section as a table row – but `SCHEMA.md`'s own documented example (correctly, realistically) has an explanatory note before the table and a caveat paragraph after it, not just the bare table. Tested against the actual documented example directly:

```
Before fix: headers = ["*(Optional – only when the role genuinely spans..."]  – the prose note, not the table header
After fix:  headers = ["Region", "Relationship style", "Decision style", "Key nuances"]  – correct
```

Fixed by filtering to only lines starting with `|` before parsing – prose above and below the table is now correctly ignored. Added "Regional intelligence" to `scripts/verify_consistency.py`'s round-trip check (now 11 sections checked, up from 10) so this exact bug class can't silently return.

Added real example data to Stonebridge Analytics (the one existing example with a plausible multi-market angle – ~300 employees, Series C). Confirmed live in the browser: Stonebridge's briefing pack shows a real two-row table (UK, US) with the caveat "General cultural/business-norm patterns, not verified facts" underneath; Alderwood Data's briefing pack (no regional data) shows no "Regional intelligence" section title at all – confirmed via `.section-title` enumeration, not just visual inspection – proving the optional-not-placeholder design actually holds, not just in theory.

## Test 12 – Average score on the Total tracked headline tile

Added the same average-score treatment already on Interviewed/Not interviewed to Total tracked, plus a clarifying sub-title ("every application, any status") – genuinely informative, not just visual padding, since without it "Total tracked" could be misread as only counting resolved applications the way its two sibling tiles do.

Verified live: Total tracked reads "avg score 66.6" against an independently-computed manual average of the same 32 applications' `score.value` (also 66.6, exact match) – sitting between Interviewed's 79.4 and Not interviewed's 62.1, which is the expected shape (Total is a blend of resolved-positive, resolved-negative, and unresolved applications, so it should land between the two resolved extremes). All three tiles now share the same four-line structure (number, label, sub-title, avg) and each avg is colored to match its tile (blue/green/red).

## Test 13 – Blind test: fresh Claude.ai Project, real (not fictional) data, no prior context

This is the test the previous section flagged as not yet done: a genuinely fresh Claude.ai Project, the skill installed cold via the actual published README instructions, and – going further than "fresh session" alone – real, non-fictional user data (the user's own CV, cover letter, and job description PDFs) instead of the example dataset, so the CV-matching logic had to work without any of the fictional persona's convenient structure.

**Packaging and upload, followed literally from the README:** downloaded the repo as a `.zip` from GitHub, unzipped it, renamed the extracted folder to `job-pipeline`, re-zipped it, and uploaded it via Settings → Customize → Skills → Add → Upload a skill. Verified byte-for-byte before upload that the zip's structure was `job-pipeline/SKILL.md` (not loose at the root, per Anthropic's own skill-packaging requirement). Uploaded successfully; confirmed live in the Skills panel that all 56 files came through intact and `SKILL.md`'s content matched the source exactly.

**Scored a real job description** (a real fintech payments company, referred to here as "Meridian Payments") against a Project containing one general-baseline CV plus several role-tailored CVs, cover letters, and job descriptions – no hints given about which file was which. Result: correctly identified the baseline CV and produced a fully schema-compliant scored application (correct frontmatter, correct component breakdown, correct en-dash tier formatting), live-verified the company's real profile (headcount, public listing, brand) rather than guessing from memory, and proactively noticed the existence of a role-tailored CV/cover letter dated earlier than the baseline – asking whether the application had already gone out. Confirmed and logged as `applied`; the skill correctly recorded which specific tailored documents were used, folded into the Caveats section (the only place available before this test's own fix – see below).

**Three real, previously-undocumented gaps found, all fixed as a direct result:**

1. **Role-tailored CVs weren't a distinct concept anywhere in the design.** The skill handled the case it was tested with with reasonable improvised judgement, but had no structured way to record "the baseline was used" vs. "a specific tailored CV/cover letter/supplementary response was used" – it fell back to unstructured prose in Caveats, which nothing downstream (dashboard, recalibration) can reliably read. Fixed by adding an `application_materials` field to `schema/SCHEMA.md`, set only at the `scored` → `applied` transition (never at scoring time, since a tailored CV for a role nobody's applied to yet doesn't exist), with matching `SKILL.md` guidance in Step 1 and Step 4.
2. **Claude.ai Project files are read-only to Claude – completely undocumented before this test.** Every logged application or status update can only be handed back as a downloadable file; nothing is written to Project knowledge automatically, and the change is invisible everywhere else (including the next dashboard rebuild) until the user manually re-adds the file themselves. The skill actually surfaced this correctly and unprompted in the live test ("your Project files are read-only from my side..."), but it wasn't a documented, guaranteed behavior anywhere – just emergent good judgement in one run. Fixed by making it an explicit, permanent instruction in `SKILL.md`'s Platform detection and Step 4 sections, and by adding it as a named, ongoing cost of the Claude.ai Project path in the README (not just a one-time setup note).
3. **A real, reproducible bug in dashboard-as-Artifact generation: `re.sub` silently corrupting correctly-escaped JSON.** Asked for the dashboard as an Artifact with the (unsaved) Meridian Payments application in context. Result: the artifact rendered its header and footer but the entire pipeline list was blank, with only a browser-console `Uncaught SyntaxError` as evidence – nothing visible to the user pointing at the cause. Asked the skill to diagnose it, and it did, correctly and unprompted, via its own code-execution scripts: it had used `json.dumps` to serialize the data (correct – produces properly-escaped `\n` sequences inside long fields like `jd_summary`/`caveats`), then spliced that JSON string into the HTML template at the `/*__DATA__*/` marker using `re.sub(pattern, json_string, text)` – and `re.sub` reinterprets backslash sequences in a string replacement argument as backreference syntax, silently turning the JSON's valid `\n` escapes into literal raw newlines. Valid JSON going in, invalid JS coming out, entirely inside the splice step. Fixed live by the skill itself, using a replacement *function* instead (`re.sub(pattern, lambda m: json_string, text)`), which doesn't reinterpret backslashes – verified by re-rendering the artifact and confirming the headline stats, per-status grid, and filters all populated correctly (previously nothing rendered at all). This doesn't happen when `build_dashboard.py` generates the file, since it doesn't route the data through `re.sub` this way – it's specific to the Claude.ai Project path, where the skill has to hand-build the substitution itself. Fixed by adding explicit guidance to `SKILL.md` Step 5 naming this exact `re.sub` pitfall and the function-replacement fix.

**Update: all three fixes have now been confirmed live.** The `re.sub` fix was confirmed within the original test conversation, as above. The other two needed a second round: the updated repo was re-packaged into a fresh `job-pipeline.zip` (built via `git archive` directly from the post-fix commit, so it's guaranteed to match exactly – not a manual re-download), and replaced onto the existing skill via Claude.ai's own "Replace" option (Skills → job-pipeline → ⋮ → Replace), which avoids leaving a stale duplicate skill behind.

One real mechanical gotcha along the way, worth recording since it isn't documented anywhere by Anthropic: **replacing a skill's content does not affect chats that started before the replace** – an existing conversation keeps using whatever skill version was loaded when it started, even after the replace completes account-wide. Verified directly: re-asking the same question in the original "Meridian Payments job description scoring" chat after the replace still showed the pre-fix Platform Detection wording; a **brand-new chat** in the same Project picked up the fix immediately. Anyone re-testing a skill update needs to start a fresh chat, not continue an existing one.

That new chat also surfaced an unrelated, real, but out-of-scope finding: Dan's account has another personal skill (`jd-assessor`, pre-existing, unrelated to this repo) whose trigger description overlaps with `job-pipeline`'s ("score a job description..."), and the first prompt in the fresh chat invoked the wrong one. Naming the skill explicitly in the prompt ("using the job-pipeline skill specifically...") resolved it immediately. This is a testing-environment artifact, not a bug in `job-pipeline` – a genuinely new user following the README wouldn't have a second overlapping skill installed – but it's a real thing worth knowing if you maintain multiple JD-scoring skills side by side.

With the wrong-skill issue resolved, a fresh scoring request (a different real company, referred to here as "Cascade Planning", not previously touched) against the updated skill confirmed both remaining fixes working exactly as designed:

- **`application_materials`**: *"CV baseline: [author]'s current CV – this is the only untailored, plainly-named CV in the project files, so I'm treating it as your current single evolving baseline."* Correctly excluded the Meridian Payments and Vantage Consulting role-tailored CVs from baseline consideration without being told to.
- **Read-only-Project reminder**: fired correctly, and generalized properly to the newly-written company-cache file too, not just the application file – *"neither of these files persists on its own – you'll need to add both to the Project's files yourself... or they'll be invisible next time the pipeline is reviewed or the dashboard's regenerated."*

All three Test 13 fixes are now verified live, not just committed.

## Test 14 – Joint model for recalibration (logistic regression, no external dependencies)

The per-component means in Tests 3/6/7 compare each of the five components independently, which can't distinguish "this component is genuinely predictive" from "this component happens to be correlated with a genuinely predictive one." Added a joint model – L2-regularised logistic regression fit via plain gradient descent (no numpy/scikit-learn dependency, consistent with the rest of the repo) over standardised component scores, predicting the positive/negative recalibration signal – to `scripts/verify_recalibration.py`, gated on a separate, higher threshold (`min_logged_outcomes_joint: 25` vs. the simple means' `min_logged_outcomes: 20`) since a 5-feature joint model needs proportionally more data to produce stable coefficients than five independent single-feature comparisons do.

Added three new simple `rejected` examples (Thistlewood Capital, Fenwick Outdoors, Amberline Media) specifically to push the example set's logged-outcome count from 24 to 27 – comfortably past the new joint-model threshold, so this could actually run against real data rather than only being demonstrated in the below-threshold state.

Ran `python scripts/verify_recalibration.py` against the updated 35-application example set:

```
Total applications: 35
Logged outcomes: 27 (threshold: 20)
Positive outcomes: 7 (threshold: 3)
Gate: PASS

jd_fit       positive mean= 38.7  negative mean= 33.7  diff= +5.0
seniority    positive mean= 13.6  negative mean= 11.3  diff= +2.2
competition  positive mean= 14.3  negative mean=  9.5  diff= +4.8
comp         positive mean=  9.1  negative mean=  8.0  diff= +1.1
blockers     positive mean= 10.0  negative mean=  9.7  diff= +0.3

Joint model (logistic regression, L2-regularised) – threshold 25 logged outcomes:
  Standardised coefficients (larger magnitude = stronger association with a positive outcome,
  holding the other four components constant – this is what the per-component means above cannot show):
    seniority    +1.441
    jd_fit       +0.608
    blockers     +0.370
    competition  +0.176
    comp         -0.165
```

**This is a genuinely interesting, real divergence, not a contrived one:** `competition` shows the second-strongest simple mean difference (+4.8) but the second-*weakest* joint coefficient (+0.176) – consistent with its predictive-looking mean difference being substantially explained by correlation with `seniority` and `jd_fit` (more senior, better-fitting roles in this example set also tend to be smaller, lower-competition companies) rather than `competition` doing independent predictive work of its own. `seniority`, by contrast, has a modest simple mean difference (+2.2, the smallest of the five) but by far the largest joint coefficient (+1.441) – the opposite pattern, where its true independent effect is being partly masked in the simple comparison. `comp` flips sign entirely (simple mean +1.1, joint coefficient -0.165), though its magnitude in both is small enough that this is plausibly noise rather than a real effect – exactly the kind of result the "weak signal, not a validated finding" caveat exists for. This is real output from real (synthetic) data, not a designed-to-impress result – it happens to demonstrate the feature's value well because the underlying correlation pattern in the example set is real.

Also ran `python scripts/verify_recalibration.py` with `min_logged_outcomes_joint` temporarily raised in `config/weights.json` (not committed) to confirm the below-threshold path: correctly prints `BELOW THRESHOLD – have 27, need <raised value>` and omits the coefficient table, without affecting the simple per-component means or the overall gate's pass/fail exit code.

## Test 15 – Live-search corroboration requirement

`SKILL.md` Step 3 previously allowed marking a fact `confirmed` off a single search result. Changed to require at least two independent sources agreeing before `confirmed` is used; a single source or disagreeing sources now means `estimated`, stated plainly. `schema/SCHEMA.md`'s `confidence` field description updated to match.

This is an LLM-interpreted instruction change (not a mechanical one `verify_consistency.py` can check), so it can't be proven by a script the way Test 14 was – it's a documentation/behavior change to verify in a live session the same way Tests 1, 2, and 13 were, not yet re-verified against a fresh session as of this commit. Flagged here rather than silently assumed to work.

## Test 16 – Eval harness: five-case golden set, real scoring run

Built a small, repeatable eval (`eval/`) for the one thing Tests 1/2/13 never systematised: whether the scoring rubric produces stable, defensible output across distinct scenarios, checkable again in the future without re-deriving expected behaviour from scratch each time.

Wrote `eval/golden_set.md` – five fictional JDs, each chosen to exercise one distinct scoring scenario rather than five similar "good fit" cases: an ideal fit at a small company, competition drag from a large/famous employer, a severe seniority stretch (the asymmetric rule's one "should score near zero" case), a confirmed comp shortfall, and a confirmed non-immigration blocker (FCA regulatory status, not right-to-work). Expected score bands for every component, plus the reasoning behind each band, were written down in `eval/expected_bands.json` **before** any actual scoring – not derived afterward to fit whatever came out.

Then actually scored all five, mechanically applying `SKILL.md` Step 2's rubric, without revisiting the pre-written bands while scoring. Recorded in `eval/results/2026-07-14.json`. Ran `python scripts/verify_eval_results.py`:

```
Verdant Analytics:            total = 95  (expected 86-100)
Helios Systems Corp:          total = 67  (expected 55-72)
Titan Aerospace Group:        total = 40  (expected 35-55)
Bramston Retail Holdings:     total = 80  (expected 67-83)
Meridian Financial Services:  total = 80  (expected 66-87)

PASS: all 5 golden-set cases fall within their expected bands.
```

All five landed inside their pre-registered bands on the first run, including the two hardest to get right: Titan Aerospace's severe seniority stretch scored `seniority=2/15` (band 0-3, the asymmetric rule doing exactly what it's supposed to), and Bramston Retail's confirmed below-floor comp scored `comp=2/10` (band 0-3) while everything else about the role scored well – the shortfall landed specifically on the comp component, not smeared across others.

**Confirmed the checker actually catches a real failure, not just the happy path:** deliberately corrupted a copy of the results file (zeroed out Verdant Analytics's `comp` score, which should have been a confirmed 10) and re-ran the checker – it correctly reported two violations (`comp` out of band, and the resulting total falling below its band) and exited 1. Deleted the corrupted copy afterward; it was never a real result.

Wired `scripts/verify_eval_results.py` into CI, gated on changes to `eval/expected_bands.json`, `eval/results/**`, or the script itself – CI checks a *committed* results file against the bands, it can't produce a new scoring run itself (no API key, by design – see `eval/README.md`).

## Test 17 – Fresh-agent test: synthesis vs. placeholder behaviour on thin material

Test 13 proved the onboarding flow works end-to-end but never specifically tested the one behaviour `SKILL.md` Step 4 is most exacting about: that a session should attempt real synthesis for Unique selling points / Prep questions / Questions to ask by default, and only fall back to `Currently unknown` in the genuine edge case of having nothing to work with – with two distinct failure modes possible (lazy-defaulting to placeholders where real synthesis was possible; over-confident filling with generic, unevidenced content).

Ran this via a genuinely independent agent with zero context on this repo's build process – given only `SKILL.md`, `SCHEMA.md`, a fictional CV (Jordan-Ainsley-style persona, richer than the example set's version so there was real material to synthesise from), a JD (the golden set's Verdant Analytics case, reused here since its company facts are self-contained), and a realistic thin-material scenario: a first interview had happened with a named interviewer (Priya Okonkwo) but with **zero other detail about her** – deliberately chosen to test the placeholder path on a real interviewer profile, not a contrived empty case.

**Result: no lazy-defaulting, no over-confident filling, on either count.**

- **Unique selling points, Prep questions, Questions to ask** – all real, traceable synthesis. Every USP and every prep-question answer cited a specific fact from the CV (a named prior company, a specific accounts-in-months figure, a specific team-size number, a specific pricing-model specialism) cross-referenced against specific JD language (the "rotating engineering liaison" detail, the "40 accounts to next stage of growth" framing) – not generic interview advice. No section defaulted to a placeholder where real material existed.
- **Interviewer profile (the genuinely thin case)** – the agent actually ran a live search on the named interviewer before concluding there was nothing findable, then used the placeholder convention correctly and transparently: *"No independently verifiable public background found... flagging plainly rather than presenting a thin or absent read as if it were verified."* This is the placeholder mechanism working as designed, not lazy-defaulting – it attempted the research first.
- **Unplanned, useful side-validation of the Step 3 corroboration fix (Test 15):** the agent independently applied the new two-source corroboration rule to the *company* facts too, despite this test not being designed to check that specifically – found no corroborating source for the company itself beyond the job listing, and correctly downgraded `confidence` to `estimated` and skipped writing a `companies/verdant-analytics.json` cache entry rather than treating the listing's self-reported facts as confirmed. Real evidence the Step 3 change is being interpreted correctly by an independent session, not just self-consistently by the session that wrote it.

**One minor, unrelated observation, not a failure of what this test was checking:** the output's frontmatter used `source: null` where the user hadn't stated which channel (LinkedIn, referral, etc.) the application came through. `SCHEMA.md` documents `source` as "optional, free text" without an explicit convention for the not-yet-known case – arguably should have asked, or used an explicit placeholder string consistent with the Briefing pack's own `Currently unknown` convention, rather than silently writing `null`. Noted here for completeness rather than opened as a new backlog item; low-stakes enough to fold into the next unrelated SCHEMA.md pass rather than treated as urgent.

## Test 18 – Score rationale surfaced for every application, not just Briefing Pack cards

Public backlog item: `## Score rationale` exists in every application file per `SCHEMA.md`'s own template, but `scripts/build_dashboard.py` never parsed it into the dashboard's data at all – not even for applications with a full Briefing Pack. It was invisible everywhere, not just for non-interview-stage roles.

Added parsing (`build_dashboard.py`, reusing the existing `parse_plain_bullets()` helper already used for Questions to ask, since Score rationale is structurally the same shape – a bulleted, one-line-per-component list, not prose) and rendering (`docs/index.html`, a new `renderRationale()` following the same pattern as `renderQuestions()`), placed directly under the score bars it explains and above the JD summary – on every card, regardless of status, using the card's existing expand/collapse mechanism rather than a new UI element.

Verified live in the browser (`python -m http.server` against `docs/`, driven via `javascript_tool` DOM inspection since screenshots weren't rendering this session): confirmed the "Score rationale" section appears in the correct position (second, after "Score breakdown") on both a Briefing Pack card (Briarcliff AI) and, more importantly for this backlog item specifically, a plain `scored` card with no Briefing Pack at all (Elmscroft Data) – both showed the correct five-item bulleted list.

**A real, distinct finding along the way, not fixed here:** the example dataset's own `## Score rationale` content is thin – every one of the 37 example applications currently just restates the number (`"JD fit: 41/45"`) rather than the actual one-line reasoning `SKILL.md` Step 2's "Output" instruction asks for. The mechanism now correctly surfaces whatever's there, but "whatever's there" in the demo data isn't a good demonstration of the feature's real value. Rewriting rationale text for 37 examples is a distinct, separate content task from the dashboard mechanism this backlog item was actually about – not done as part of this change, added to `ISSUES.md` as its own item instead of silently expanding scope here.

## Test 19 – Comp scoring redesign, a real score/breakdown bug found and fixed, and full rationale coverage

Started as "write real Score rationale text for all 37 examples" and surfaced two bigger, real problems in the process, both fixed rather than worked around.

**1. `score.value` didn't equal the sum of its own `score.breakdown`, for a large share of the example dataset.** Both numbers were hand-typed independently in `generate_examples.py`, with nothing checking they agreed – e.g. Meridian Cloud Systems was stored as `score: 52` against a breakdown that actually summed to 62; Fernbank Analytics as `81` against a true sum of 89. The number shown prominently at the top of a dashboard card could silently disagree with the five bars directly beneath it. Fixed at the source, not just patched: `generate_examples.py` now computes `score = jd_fit + seniority + competition + comp + blockers` rather than accepting it as a separate hand-typed input, so this specific bug class can't be reintroduced. `scripts/verify_consistency.py` gained a new check (`check_example_score_sums`) enforcing this for every committed example, wired into CI.

**2. The comp component's design itself was flawed, not just its example data.** Raised directly: scoring unknown comp at the maximum (10/10) means a role that simply doesn't state a salary can outscore one with a confirmed, decent-but-imperfect comp band – "not knowing" shouldn't beat "knowing and being good." Also found: several examples had a confirmed-*null* comp band but still scored below 10, directly contradicting the rubric's own stated rule. Redesigned `comp` (`config/weights.json` → `components.comp`, `SKILL.md` Step 2):

- **Explicit collection, not inference.** A new `preferences.md` file (`schema/SCHEMA.md` → "Preferences file"), collected the same way as the CV baseline in Step 1, but asked directly – never read off the CV, since most real CVs don't state compensation at all (unlike the fictional example's, which previously and misleadingly did).
- **Sliding scale, not a step function.** `comp = round(clamp(10 * (1 - shortfall_pct / max_shortfall_pct), 0, 10))`, `max_shortfall_pct` defaulting to 0.5 – a role 10% below floor now scores 8/10, not a flat low number; 0/10 is reserved for ~50%+ below floor.
- **On-target earnings, equity excluded from the number.** Base + bonus/variable only; equity noted separately as a qualitative factor when mentioned, never folded into the score – too unreliable to value consistently.
- **Unstated comp gets a real attempt, not an automatic max score.** Same live-search discipline already applied to `competition` – estimate from role level/seniority/company profile first, mark `estimated`; only fall back to a neutral `unestimable_default` (6/10) when even that isn't reasonably possible.

**3. Full rationale rewrite, reflecting the corrected values.** All 35 examples (28 simple + 7 briefing-pack) got real, specific one-line reasoning for every component – grounded in what was already established for that example (company size/funding/sector, stated or estimated comp figures), not invented backstory. Two entries' comp bands were adjusted for narrative honesty under the new formula: Redshank Payments (the flagship "confirmed below floor, didn't apply" example) needed a genuinely severe shortfall (£65k-75k vs. £110k floor) to still justify that decision under a scale where modest shortfalls are no longer harshly penalised; Silverlake Systems had a `comp_band: null` sitting alongside narrative text that explicitly said comp *was* confirmed below floor after Stage 2 – a real, separate data inconsistency, fixed by giving it an actual confirmed figure instead of leaving the two contradicting each other.

`scripts/verify_consistency.py` gained a second new check (`check_example_rationale_not_thin`) – every example must have exactly five rationale lines, and none may be a bare `"Label: N/45"` restatement with nothing else. **Confirmed both new checks actually catch real failures, not just the happy path:** deliberately broke a copy of one example's score sum (verified the check caught it, exit 1) and deliberately thinned one rationale line back to a bare restatement (verified the check caught that too, exit 1) – both reverted immediately after, neither was ever a real committed state.

**An honest, unforced side-effect worth naming:** with both bugs fixed, almost every example's score moved – mostly upward, since the sum-bug had generally under-counted and the null-comp-band bug had wrongly penalised roughly half the dataset. The corrected dataset now skews toward Tier 1-2 more than the original did; no low-scoring examples were artificially reintroduced to preserve visual tier variety, since doing that would have been the same "shape the data to look right" mistake this whole test exists to move away from. Re-ran `python scripts/verify_recalibration.py` against the corrected data and the recalibration stats shifted accordingly, most notably `comp`: previously a clearly positive component (`diff +0.8` to `+1.1` across earlier tests), now marginally negative (`diff -0.4`, joint coefficient `-0.447`) – a real, direct consequence of several `interviewing`/`offer` briefing-pack examples (Pemberton, Briarcliff, Silverlake) having genuinely below-floor or estimated comp under the new, more honest scoring, while several `rejected` examples now correctly score comp at or near 10. Not adjusted after the fact to look more flattering – this is what the honest numbers produced.

Verified live in the browser (DOM inspection, not just code review) on both the corrected score-sum case (Meridian: `65` shown, matching `30+12+4+9+10`) and the neutral-default comp case (Granite Peak: `comp (6/10)` with the honest "no reliable signal" explanation, not a placeholder and not a max score).

## Test 20 – Duplicate/reposted-role detection

Public backlog item: nothing checked whether a company+role combination had already been scored or tracked before `SKILL.md` Step 2 created a new application file – an accidental re-paste or a genuine repost would silently create a second, disconnected record instead of surfacing the existing one.

Added `scripts/check_duplicate.py`, run by `SKILL.md` Step 2 immediately before file creation. Deliberately narrow matching, not fuzzy/similarity-scored: company names are normalised (lowercased, legal suffixes like Inc/Ltd/LLC/Corp/plc stripped, punctuation and whitespace collapsed) and matched exactly; role titles are compared the same way, exact-after-normalisation only. No partial or substring title matching – that's the fast route to a false positive ("Head of Product" flagging against "Head of Product Strategy", a genuinely different role). Two tiers, both advisory, neither ever blocks:

- **HIGH confidence** – same normalised company, same normalised title: likely an accidental duplicate or an exact repost.
- **LOW confidence** – same normalised company, different title: could be a genuinely distinct role (the real, common "Role 1 / Role 2 at the same company" pattern) or the same role reworded – flagged as worth a quick check, not treated as a problem.

Ran against the real example dataset (`examples/applications/`, 32 files, no two of which currently share a company – confirmed by listing every `company`/`role` pair before testing) to exercise all three outcomes for real, not by inspection:

```
$ python scripts/check_duplicate.py --company "Totally New Company" --role "Head of Product"
No existing tracked application found for 'Totally New Company' / 'Head of Product'.

$ python scripts/check_duplicate.py --company "Northwind Retail Technologies" --role "Head of Product, Platform"
HIGH confidence match - same company and same role title already tracked:
  2026-04-02-northwind-retail-technologies-head-of-product--platform.md  (status: rejected, scored: 2026-04-02)
Likely an accidental duplicate, or this exact listing reposted. Confirm with the user before creating a new file rather than silently doing so.

$ python scripts/check_duplicate.py --company "northwind retail technologies, inc." --role "head of product, platform"
HIGH confidence match - [same result – confirms normalisation survives a legal suffix and case difference, not just an exact string match]

$ python scripts/check_duplicate.py --company "Northwind Retail Technologies" --role "Head of Growth"
LOW confidence match - 'Northwind Retail Technologies' already has 1 other tracked application(s) under a different role title:
  2026-04-02-northwind-retail-technologies-head-of-product--platform.md  -> 'Head of Product, Platform' (status: rejected)
Could be a genuinely distinct role, or the same one under a reworded title. Ask, don't assume either way.
```

All four cases produced the correct, distinct outcome: true negative, exact-match true positive, normalised true positive (proving the suffix/case stripping actually does something rather than just existing in the code), and the low-confidence same-company-different-role case. `SKILL.md` Step 2 gained a new "Before creating the file, check for an existing one" instruction. **A real inconsistency was caught and fixed while planning the next round of testing (before running it, not after):** the instruction originally said Claude.ai Projects have "no code execution," which directly contradicts this repo's own Claude.ai Project setup steps – code execution is a required toggle there, not an optional/absent one. The actual open question, not yet verified either way, is narrower: whether Claude.ai's code-execution sandbox can reach uploaded Project knowledge files at a real filesystem path the way a local Cowork folder can. `SKILL.md` now says to attempt the script first (code execution is available on both platforms) and only fall back to a by-eye scan if the files genuinely aren't reachable that way – phrased as something to actually observe in the next blind test, not asserted as a known fact.

## Test 21 – Blind test: fresh Claude.ai Project, re-verifying the comp redesign and duplicate detection

Re-ran the Test 13 methodology (genuinely fresh Claude.ai Project, skill installed cold, real non-fictional data, no hints) specifically to verify everything shipped since Test 13: the compensation-scoring redesign (Test 19), duplicate detection (Test 20), and the Claude.ai-code-execution correction made while planning this test (see Test 20's note above).

**Setup:** new Project (`job-pipeline-blind-test-2026-07-14`), the account's existing `job-pipeline` skill replaced with a fresh zip built via `git archive` from commit `663b21d` (same reproducible-packaging method as Test 13's re-verification round). Real files uploaded: the author's actual current CV plus a mixed batch of real cover letters and job descriptions. Asked to score one real role – a large, publicly traded global bank, referred to here as "Northgate Financial Group" – with no other hints, in a Project that had never seen this skill before.

**Compensation floor collection – worked exactly as designed.** Before scoring, the skill correctly stopped and asked for an OTE floor, explicitly stating *why*: "The skill explicitly requires me to ask this directly rather than infer it from your CV or any other document, and there's no preferences.md on file yet." No CV inference attempted despite the CV being available. Given a test figure (£120,000), it correctly wrote a downloadable `preferences.md` and flagged, per the Claude.ai read-only-Project reminder, that the user needs to add it to the Project themselves.

**Sliding-scale comp scoring, live-search estimate path – worked as designed.** The JD didn't state a salary. The skill ran two separate live searches (company headcount, then role-specific salary data) before scoring, landed on a defensible estimated OTE range corroborated by two sources, well above the £120k floor, and scored `comp: 10/10, estimated` – correctly using the estimate-first behavior rather than defaulting to the neutral `unestimable_default`.

**Duplicate detection – executed as real code, and resolved the open question from Test 20.** Asked directly afterward whether `check_duplicate.py` had actually run or fallen back to a by-eye scan. The skill reported running `python3 /mnt/skills/user/job-pipeline/scripts/check_duplicate.py --company "..." --role "..." --dir /mnt/project` and confirmed `/mnt/project` is a real, readable path where Claude.ai mounts the Project's uploaded files – closing the question Test 20 had deliberately left open rather than guessed at. **A genuinely useful nuance it caught unprompted:** it flagged that "no duplicate found" in this case reflects an empty tracked-applications set (the Project had source documents but no previously-scored application files yet), not a populated set that was checked and cleared – the kind of distinction that matters for trusting the check's result. `SKILL.md` updated to state the confirmed `/mnt/project` path directly rather than hedging with "if reachable, otherwise fall back."

**Overall scoring output** was well-formed and consistent with the rubric throughout: JD fit correctly penalised for a required (not preferred) heavy technical-certification mismatch against the CV; seniority correctly scored as no stretch; competition correctly scored near-zero for a large public bank, backed by two independently-cited sources; blockers correctly scored clean for a UK-based, on-site role. The resulting score landed solidly in Tier 3 – a defensible, well-reasoned result for a real, previously-unseen role.

No bugs found or fixed in this run – the comp redesign, duplicate detection, and Claude.ai file-reachability behavior all worked exactly as designed on the first real, independent test since they shipped.

**Continuing the same test session, the actual dashboard-as-Artifact step was exercised for the first time – and this is where two real bugs surfaced, both fixed.** Everything above tested scoring mechanics; nothing had yet actually asked the skill to produce the dashboard, which is the repo's actual deliverable. Doing that surfaced the following, in order:

1. **The read-only-Project friction is real, not just documented.** Asking for the dashboard immediately after scoring correctly returned "the Project doesn't have any tracked application files in it right now" – the generated application file, `preferences.md`, and the company cache existed only as that turn's downloadable output, not in `/mnt/project`, until manually downloaded and re-added to the Project. This matches what `SKILL.md` already claimed, now proven end-to-end for the first time rather than assumed. After re-adding the three files, asking again produced a correctly-rendering dashboard Artifact: real data, correct score, correct status/filter UI.

2. **A real, previously-undiscovered `re.sub` corruption bug, still live in `scripts/build_dashboard.py` itself.** A prior session (Test 13) diagnosed this exact bug – `re.sub` reinterpreting `\n` in a plain-string replacement argument as an escape sequence, silently corrupting any JSON string value with an embedded newline into a raw, syntax-breaking newline – and worked around it live, inline, in that session's own reimplementation. That workaround was never actually committed to the repository's own script. It stayed dormant for the public demo purely because none of the 35 example applications' text fields happen to contain a literal embedded newline (confirmed directly: `json.dumps` of the real example dataset currently produces zero escaped-newline sequences) – real user data very plausibly would. Reproduced deliberately with a controlled test case (a value containing an embedded newline) to confirm the corruption is real, not theoretical, then fixed by extracting the splice logic into a shared `inject_data()` function using a replacement *function* instead of a string, and adding a permanent CI regression check (`scripts/verify_consistency.py`) that exercises this exact scenario. Confirmed the check actually catches the bug: deliberately reverted the fix, re-ran the check, watched it fail with the exact expected `json.JSONDecodeError`, then restored the fix and re-confirmed it passes.

3. **The rendered dashboard's banner falsely claimed "Fictional companies and applications... No real job search data.**" This text is correct for the public GitHub Pages demo and was copied verbatim, because the same `docs/index.html` template serves double duty as both the public demo and the file a live session copies to build a real user's own dashboard – nothing previously distinguished the two cases. Fixed structurally, not by adding a reminder sentence to `SKILL.md`: `inject_data()` now takes `subtitle` as a *required* parameter (no default), so any caller – the demo build in `main()`, or a live session building a real dashboard – must explicitly decide what it says, rather than silently inheriting whatever was already in the template. `SKILL.md` now instructs calling `inject_data()` directly (importable from the skill's own mounted `scripts/build_dashboard.py`) rather than reimplementing the injection logic freehand each time, which closes both bugs at once: reusing the real, tested function means neither the corruption bug nor the stale-subtitle bug can recur from a live session re-deriving the logic from memory.

**Why this took three rounds to surface, honestly stated:** each round tested a genuinely different, previously-unexercised path – comp scoring, then duplicate detection, then (in this round) the actual score-to-dashboard loop for a real user – rather than the same thing failing repeatedly. Unit-testing the pieces separately, which is most of what this log verified before this round, structurally cannot catch a bug that only exists in how the pieces combine into the one thing a real user actually sees.

## Test 22 – Reinstalling the updated skill for real ongoing use

Separately from the blind test above, replaced the account's `job-pipeline` skill (previously last updated 7/13, i.e. before the comp redesign and duplicate detection) with the current build, via Settings → Customize → Skills → job-pipeline → ⋮ → Replace, using the same `git archive`-built zip as Test 21. Confirmed via the skill's own file browser, not just the "Replaced" toast: file count went from 56 to 67 (consistent with today's additions – `scripts/check_duplicate.py`, `examples/preferences-example.md`, etc.), `scripts/check_duplicate.py` is present in the file tree, and `ISSUES.md` reads "None currently open." This is the account's now-current skill version for real, ongoing use going forward, separate from the disposable test Project used in Test 21.

**One real automation limitation found and worked around, not a skill bug:** neither the in-app Browser pane (unauthenticated) nor Chrome extension automation (blocked by Chrome's own anti-automation protection on synthetic `<input type=file>` clicks) could complete the actual file-picker step of a skill Replace – this needed a human click on the native OS dialog. Everything else (navigating, opening the Replace menu, verifying the result) was automatable; only the browser-native file selection itself required manual action.

## Test 23 – Dashboard persistence: Chat mode vs Cowork, and a testing-methodology failure corrected

Public backlog / correction: an earlier round of this log's own testing (Test 21) verified that a Chat-mode dashboard Artifact renders correctly, but never checked whether it actually *persists* anywhere findable afterward – the repo's stated purpose is producing a real, ongoing dashboard, not a one-off render, and that gap went unnoticed until directly challenged.

**The failure, stated plainly:** asked to simulate what a brand-new user gets from this skill's own "regenerate the dashboard" step, the first attempt used this session's own code-execution tooling to produce and publish an Artifact – a mechanism only available to sessions with that tooling, not to a real user following the README on Claude.ai or Cowork. This doesn't test what a real user experiences at all, and was a genuine methodology failure, not a technicality: the root cause was that `SKILL.md` had never actually distinguished Cowork's persistence behaviour from Chat mode's, and this had never been tested end-to-end via either real path, only assumed.

**Investigated directly, not asserted:**
- A screenshot of the real Artifacts library (`claude.ai/artifacts`) showed exactly one Code-origin tile from an unrelated project, plus two Cowork-tagged tiles for the user's own real trackers – no Chat-origin dashboard from this skill existed anywhere in the library, confirming the gap was real.
- Anthropic's own published documentation on publishing/sharing Artifacts (a Chat-mode artifact needs an explicit user click on "Publish" to appear in the library at all) and on Cowork's Live Artifacts (a separate, pinnable, auto-updating mechanism) was read directly rather than assumed from either mechanism's general reputation.
- **Live-tested the Chat-mode Publish path end-to-end:** produced a dashboard Artifact in a plain Claude.ai Project chat, published it via the Copy dropdown → "Publish artifact", and confirmed it appeared in the Artifacts library tagged "Chat" with a real public URL. Confirmed directly that it is **not** pinnable and does not auto-update – a static snapshot of that moment, exactly as Anthropic's Cowork documentation implies by contrast, not something asserted from the docs alone. Unpublished it again afterward, since it existed purely to verify the mechanism, not as a real dashboard.

**Fixed, both in behaviour text and in an honest correction of an earlier overstated claim:** `SKILL.md`'s Platform detection section and the README's Claude.ai Project/Cowork sections were rewritten to state plainly, every time a dashboard is produced in Chat mode, that it needs an explicit Publish click to persist at all and remains a static snapshot even then – and that Cowork's Live Artifacts are the only mechanism that's both persistent and always-current. An earlier draft of this same fix overcorrected in the other direction, asserting Cowork was "the only path that produces a real, library-listed, independently-findable dashboard artifact" – flatly wrong, since the Chat-mode Publish path above does exactly that (just not as a *live* one). Corrected once the live test above proved it.

**What's still unverified, honestly flagged rather than assumed:** whether this skill's own `inject_data()` → Artifact flow, run for real inside a genuine Cowork session, actually produces a Live Artifact the way Anthropic's general Cowork documentation describes. Claude Code cannot test this directly – Cowork is desktop-app-only, and computer-use tooling is explicitly and permanently blocked from requesting control of Claude's own application (confirmed via a hard, non-retryable error, not a transient failure). This needs a human-driven session and is tracked in `ISSUES.md` until it's run.

**A small, separate bug found and fixed in the same pass:** the dashboard's browser-tab `<title>` was still hardcoded to the public demo's text ("...example dashboard") even after an earlier fix (Test 21) made the banner subtitle a required, swapped-in argument – the title tag used a different marker and was missed at the time, caught only when pointed out a second time, not proactively. Fixed the same way: `title` is now also a required argument to `inject_data()`, swapped via its own marker pair, with `scripts/verify_consistency.py`'s existing injection check extended to assert both swaps happen and neither stale string survives. Confirmed the check catches a reintroduced regression (deliberately reverted the fix, watched the check fail, restored it).

## Test 24 – Status transitions verified against a live, non-fictional pipeline (Applied → Rejected, Applied → Interviewing)

Continuing the same live Claude.ai Project session used for Test 23 (real CV, real cover letters, real job descriptions – not the example dataset), tested two of the state machine's transitions end-to-end against real scored applications, verifying the actual field values written back, not just the chat's prose summary of what it did.

Scored a real seed-stage B2B sales-tech role, referred to here as "Larkspur Sales Technologies" (~$9M raised, small team, hybrid London): 77/100, Tier 2 (JD fit 32/45, seniority 14/15, competition 14/20 estimated, comp 7/10 estimated against an estimated ~£100k-130k OTE versus the user's £135k floor, blockers 10/10) – the first real exercise of the comp component's sliding scale (Test 19) on a genuinely below-floor case, rather than one at or above it.

**Applied → Rejected**, told the role had come back with a rejection. Verified directly in the file's raw preview, not the chat's summary: `status: rejected`, `status_date` set to the day of the message, `score.locked: true` (the confirmed outcome correctly stops future rescoring), and a new `## Outcome` section added.

Before testing Interviewing, asked for a second role to be scored – a fractional/contract listing, referred to here as "Kestrel Advisory" (Fractional VP of Customer Success, 2 days/week, 3-month minimum). **The skill correctly identified this doesn't fit the scoring model before scoring anything:** the OTE-based comp floor doesn't translate to a day rate, and competition/seniority alignment work differently for interim searches, so it asked whether this was a real fractional-work interest (in which case it would need a day-rate figure to adapt against) or a comparison-only curiosity, rather than force-fitting the OTE floor onto a contract rate. Skipped, by choice, not because it failed – a genuine positive finding: the skill recognised the limits of its own model rather than producing a confidently wrong number.

Scored a second full-time role instead, referred to here as "Haven Wellbeing" (Series C, ~$110-125M raised, ~200 employees, several recognisable enterprise clients): 81/100, Tier 2 (JD fit 38/45, seniority 15/15, competition 10/20 estimated, comp 8/10 estimated against an estimated ~£120k-150k OTE, blockers 10/10).

**Scored → Applied**, told the application had gone in with the baseline CV, no cover letter. Verified: `status: applied`, `date_applied` set correctly, `application_materials` recorded as baseline CV / no cover letter, score locked.

**Applied → Interviewing**, told a first round had been booked. The skill correctly asked for a specific `next_interview_date` rather than inferring or guessing one from "booked" – told none was confirmed yet, it updated `status: interviewing` immediately and left `next_interview_date` for a later message, rather than blocking the status update on a detail that wasn't available. Verified directly: `status: interviewing`, `status_date` set correctly, `date_applied` and every score field preserved unchanged from the Applied step, `locked` still `true`.

Both transitions, and the fractional-role edge case, behaved exactly as `SKILL.md` describes – no bugs found in this round.

## Test 25 – Concurrent Cowork chats silently overwrite each other's edits (user-reported, not independently reproduced)

Distinct from the tests above: this finding came directly from the user's own real, ongoing use of their real Cowork trackers, not from a session run for this log. Running two separate Cowork chats against the same tracked-data folder resulted in an earlier update being silently overwritten – an in-progress edit from one chat was lost when a second, separately-started chat wrote back its own (older) snapshot of the same files.

**Root cause, consistent with Cowork's own documented behaviour rather than a bug specific to this skill:** each Cowork chat works from its own snapshot of the local folder, taken when that chat started, the same way a Claude.ai skill replace doesn't affect an already-open chat (Test 13's skill-replace finding). Two chats open against the same folder have no way to see each other's writes – whichever saves last wins, silently, with no merge and no warning.

**Not independently reproduced by this log, honestly stated:** Claude Code cannot drive a Cowork session itself (see Test 23's tooling-limitation note), so this is recorded as a confirmed real-world report, not a controlled test with before/after evidence the way the rest of this log documents things. Fixed the only way available given that constraint – documentation, not code, since there's no mechanism here that can detect or prevent a second concurrent chat: `README.md`'s Cowork section and `SKILL.md`'s Platform detection section both now state plainly that only one Cowork chat should run against the same data at a time, and `SKILL.md` instructs the skill to mention this risk proactively when a Cowork session starts working with local files.

## Test 26 – Large-file write truncation, and a more important root cause behind it (user-reported, not independently reproduced)

Also from the user's own real, ongoing use of a real Cowork tracker, not a session run for this log, and deliberately described here without any of the real company/personal specifics from that report – this log's standing anonymization rule applies with extra weight to a live, real interview process.

**What happened:** while correcting a couple of company facts and adding new regional-intelligence content, an incremental/patch-based file-editing tool silently truncated the dashboard file right around 155-158KB (reported precisely as a 158,378-byte cap), with no error surfaced – the file simply ended up shorter than intended, cut off mid-content. Rewriting it as a single direct write (164,661 bytes, past the old cap) resolved it immediately.

**The more important finding underneath it:** those corrections were being made by hand-editing the *rendered dashboard HTML directly*, not by updating the underlying source files (`companies/<slug>.json`, the application's own Briefing Pack section) and regenerating. That's a real problem independent of the size bug: the dashboard is a fully regenerated view, so the next real regeneration would read the (still-uncorrected) source files fresh and silently discard every hand-made correction – the whole point of a single source of truth is defeated if the rendered output can be edited directly and treated as if that were the fix. Repeatedly patching a large existing file in place is also exactly the pattern that hit the write-truncation limit; editing small source files and doing one full regenerate avoids both problems at once.

**Directly relevant, not a hypothetical edge case:** this repo's own public demo dashboard, `docs/index.html`, is already 100KB+ with only 35 fictional example applications – a real multi-month pipeline will plausibly cross the reported threshold in normal use.

**Fixed in `SKILL.md`'s Step 5:** added an explicit instruction against hand-editing the rendered HTML for content corrections, pointing to the correct source location instead; completed the dashboard-regeneration code example with the write-back step it was previously missing entirely (it built the new HTML string and just stopped); and added a direct instruction to write the result back in one single call, never through incremental edits.

**Not independently reproduced by this log, honestly stated, same as Test 25:** Claude Code cannot drive a Cowork session, so neither the truncation nor the source-of-truth violation has been triggered and confirmed end-to-end here – only the fixes (state the correct source location, complete the example, write the full file in one call) have been applied, on the reasoning that they're correct and costless regardless of the exact mechanism or threshold involved.

## How to reproduce this

**The mechanical parts (Test 3's statistics, Test 5/6's consistency checks)** are fully reproducible right now: `python scripts/verify_recalibration.py` and `python scripts/verify_consistency.py`. Both re-run in CI on every push that touches `examples/`, `docs/index.html`, `schema/SCHEMA.md`, `scripts/_status.py`, or `config/weights.json`, so none of this is a one-time check.

**The LLM-interpreted parts (Tests 1 and 2 – actual scoring, actual live search; and the "real synthesis, not generic filler" quality bar for Briefing pack v2's USPs/prep Q&A, which no script can verify)** are harder to make deterministic the same way, because they depend on a Claude session interpreting `SKILL.md`, not running fixed code. Test 13 closes most of this gap: a genuinely fresh Claude.ai Project, installed cold from the published README, scoring real (not fictional) data with no hints – and it surfaced two real, previously-undocumented gaps in the process, which is exactly what this kind of test is for. What Test 13 hasn't yet done is re-verify the two fixes it produced (`application_materials`, the read-only-Project reminder) – that needs one more round with the updated skill re-uploaded to the same test Project.

## What this does and doesn't prove

Proves: the scoring rubric, the live-search mechanism, and the recalibration computation all produce sensible, real output when actually run, including correctly surfacing a real disqualifying blocker rather than a flattering score. Proves the recalibration agent's statistical gate is now continuously verified, not a one-off claim, and that it correctly treats a post-interview rejection as positive signal, not a flat negative. Proves the dashboard's sort logic and the eleven-status vocabulary behave exactly as designed against real rebuilt data. Proves the Briefing pack v2 sections – both fully-populated and honestly-placeholdered – render correctly, and found and fixed two real bugs (a docs/parser heading mismatch, a double-period rendering bug) by actually running the thing rather than trusting the code by inspection. Proves, via Test 13, that the published README's onboarding steps work end-to-end for a genuinely new user with a real zip-upload flow, and that the skill copes sensibly with real, non-fictional, ambiguous file sets even where the design had gaps – finding three such gaps for real rather than by inspection, including one reproducible bug in dashboard generation itself, and producing fixes for all three. Proves, via Test 24, that both tested status transitions (Applied → Rejected, Applied → Interviewing) write the correct fields against a real, non-fictional pipeline, and that the skill correctly declines to force-fit a fractional/contract role onto the OTE-based scoring model rather than producing a confidently wrong number. Proves, via Test 23's live Publish test, that a Chat-mode dashboard Artifact really can become a listed, shareable library item – just a static one, not the always-current dashboard the repo's Cowork option promises.

Doesn't prove: that an independent Claude session, with no context from this build process, would interpret `SKILL.md` the same way – including whether it would default to genuine synthesis over `Currently unknown` placeholders as intended, rather than either extreme. Also doesn't prove that this skill's own dashboard-generation flow, run for real inside Cowork, actually produces a Live Artifact – that claim rests on Anthropic's general Cowork documentation, not on this skill's own code path being exercised there, and Claude Code has no way to test it directly (Test 23). Both gaps are tracked in `ISSUES.md` and left un-closed here rather than assumed – see "How to reproduce this" above.
