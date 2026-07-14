---
name: job-pipeline
description: Tracks job applications, scores job descriptions for callback likelihood, and maintains a visual pipeline dashboard. Use this skill whenever the user wants to score a job description, log an application, update an application's status or outcome, review their pipeline, or ask for the dashboard to be regenerated. Works entirely on the user's own tracked data – never on data belonging to anyone else.
---

# Job Pipeline Toolkit

An open-source job-application tracker and JD-fit scorer. This skill runs entirely inside your own Claude.ai or Cowork session, using your own account. It never contacts anyone on your behalf, never applies to anything, and never sends your data anywhere.

Read `schema/SCHEMA.md` before doing anything else – it defines the file format everything below assumes.

---

## Security constraints – never violate these

- **No contact with anyone.** This skill researches and scores. It never emails, messages, applies, or otherwise contacts a company, recruiter, or any third party on the user's behalf, under any circumstance, even if asked to draft something "and send it." Drafting is fine; sending is not this skill's job.
- **No data leaves the user's own environment.** Application data, scores, and the dashboard stay inside the user's own Claude Project or local folder. Never suggest uploading tracked data anywhere else.
- **Never operate on someone else's data.** If asked to score or track a role on behalf of anyone other than the user, decline – this skill has no way to verify authorisation and the CV-baseline/comp-floor logic below assumes a single person's own history.
- **Live search is read-only research**, not outreach. It looks things up; it never posts, submits, or replies anywhere.

---

## Platform detection

- **Running in Cowork** (or any environment with local file access): read and write application files directly in the folder the user has pointed you at. Write the regenerated dashboard back to that same folder.
- **Running in a Claude.ai Project**: read application files from the Project's knowledge files. **Project files are read-only from here – there is no way to write or update one directly, for a brand-new application or an edit to an existing one.** Every time you create or update an application file, output it as a downloadable document and **say plainly, every time, not just once**, that the user needs to add/replace it in the Project's files themselves for it to actually persist – otherwise it won't be there next time the pipeline is reviewed, rescored, or the dashboard is regenerated, and any edit you make in this conversation is invisible everywhere else until they do. Regenerate the dashboard as an Artifact when asked – that one's fine as pure output, nothing needs to be re-uploaded for it.

If you're not sure which context you're in, ask once rather than guessing.

---

## Step 1: Find the CV baseline and confirm the compensation floor

Locate the user's current CV/resume among their files (Project knowledge or local folder). Treat it as a single, evolving baseline, not a series of dated snapshots.

- **First time:** if none exists, ask for it – do not score anything without it.
- **More than one candidate file exists:** don't guess from filename or modified date alone – ask which one is current, and suggest the user keep exactly one live CV file going forward (any name) so this never comes up again.
- **Updating it:** when the user provides a new version – a fresh upload, a pasted revision, an edited file – confirm plainly which file you're now treating as the baseline and that it replaces the old one for all scoring from that point forward. Don't silently start using a new file without saying so.
- **Effect on past scores:** a CV update only changes scoring done from that point on. Never re-score an already-scored application against the new baseline unless the user explicitly asks – and never touch a `score.locked: true` application under any circumstance, per Step 4.
- **Role-tailored CVs are a Step 4 concern, not a Step 1 one.** A user may later submit a role-tailored CV for a specific application instead of the baseline as-is. That doesn't change anything here: scoring at this stage always uses the current baseline, full stop – a tailored version doesn't exist yet for a role that hasn't been applied to. See Step 4's `application_materials` handling for what happens once an application actually goes out.

**Compensation floor – ask explicitly, don't infer.** Look for `preferences.md` (see `schema/SCHEMA.md`). If it doesn't exist, ask directly for the user's on-target-earnings floor (base salary plus target bonus/variable comp – explicitly not equity, see `config/weights.json` → `components.comp.equity_handling`) before scoring anything against compensation. **Never read this off the CV**, even if a figure happens to be there – most CVs don't state compensation at all, and a mechanism that only works when the CV happens to include it silently fails for everyone else. Write the answer to `preferences.md` and confirm plainly that this is now the floor used for all compensation scoring.

- **Updating it:** same treatment as the CV – when the user says their floor has changed, confirm plainly, update `preferences.md`, and use the new figure from that point forward. Never re-score a past application against the new floor unless explicitly asked, and never touch a `score.locked: true` application, same rule as CV updates.

## Step 2: Score a job description (100 points)

Load `config/weights.json` for the current component weights – do not hardcode numbers here; the config file is the single source of truth so a user's edits are always respected.

### JD fit
How precisely the CV maps to the stated requirements: seniority, years of experience, specific must-have skills, domain/sector adjacency. Form one overall judgement rather than mechanically averaging sub-parts.

### Seniority alignment
**Asymmetric.** Applying below one's evidenced level should rarely be penalised. A severe stretch upward – a role requiring scope or ownership the CV doesn't evidence – is the one scenario that should score near zero regardless of everything else. Don't split the difference.

### Competition estimate
The component most sensitive to getting company facts right. Base this on company scale and profile (headcount, funding stage, public/private, brand recognition) rather than role seniority – massive or famous employers draw large pools regardless of the specific role. **This is what the live-search verification agent (below) exists to check** – don't estimate company scale from memory when a live lookup is available.

**Never use a platform's own "N people applied" counter as evidence** – it's a snapshot with no reliable relationship to the eventual total.

### Compensation alignment
Score against the user's OTE floor from `preferences.md` (Step 1) – base salary plus target bonus/variable comp. **Equity is never folded into this number** – note it separately in the rationale as a qualitative factor if the JD mentions it, since it's too unreliable to value consistently across companies and stages.

**Sliding scale, not a step function.** At or above floor scores full marks. Below floor, the score slides down linearly rather than dropping to a flat low number – a role 10% under floor should score meaningfully higher than one 45% under. Compute per `config/weights.json` → `components.comp.shortfall_scoring`:

```
shortfall_pct = max(0, (floor - offered) / floor)
comp = round(clamp(10 * (1 - shortfall_pct / max_shortfall_pct), 0, 10))
```

Zero only happens at `max_shortfall_pct` (default 0.5, i.e. 50%+) below floor – genuinely extreme, not just "under."

**If the JD doesn't state a figure:** don't default straight to a placeholder. Attempt a live-search-informed estimate first, the same discipline Step 3 already applies to `competition` – role level, seniority, company size/sector/stage are usually enough to form a defensible band (e.g. "an early-stage, ~25-person startup at this level typically pays below-market cash in favour of equity"). Score that estimate on the same sliding scale and mark it `estimated`. Only fall back to `unestimable_default` (a deliberate middle value, not the max score) when even a reasonable estimate isn't possible – genuinely unknown should score worse than confirmed-good and better than confirmed-below-floor, not tie with the best possible outcome.

### Blockers
Right to work, geography, visa, or other confirmed hard requirements. Test carefully before scoring low here – a soft inconvenience is not a blocker.

### Before creating the file, check for an existing one
Run `python scripts/check_duplicate.py --company "<company>" --role "<role>" --dir <path to the user's applications folder>` – code execution is required for this skill on either platform (see Platform detection above), so this should normally run rather than be skipped. If the application files genuinely aren't reachable as real files at a filesystem path in the current environment, fall back to doing the equivalent by eye: scan existing application files for the same company. A HIGH confidence result (same company, same role title already tracked) means don't silently create a second file – tell the user what already exists and ask whether this is a duplicate/repost or something that should update the existing record instead. A LOW confidence result (same company, different title) just means naming it clearly – e.g. distinguishing "Role 1"/"Role 2" in the filename or a short qualifier – so the two stay easy to tell apart on the dashboard; it's common for one company to have multiple genuinely distinct open roles, so don't treat this as a problem to resolve, just flag it. No match: proceed as normal.

### Output
State the score, tier, a one-line rationale per component, and explicitly flag any component that's an estimate rather than a confirmed fact (e.g. an anonymised listing with unverifiable company details). Create the application file per `schema/SCHEMA.md` with `status: scored` and `date_applied: null` – scoring a JD doesn't mean it's been applied to. Not every scored JD gets a follow-up application, and the pipeline should show that honestly rather than only tracking JDs after the fact.

## Step 3: Live-search verification agent

Triggered automatically as part of scoring (Step 2), not a separate user request – but see the caching rule below, which is what keeps this cheap.

1. Check `examples/companies/<company-slug>.json` (or the user's own `companies/` folder) for an existing entry less than 90 days old. If found, use it – **do not re-search**.
2. If missing or stale, run live search to confirm: company size/headcount, funding stage or public status, sector, and anything relevant to the specific role. Also do a brief legitimacy sanity-check for anonymised or low-signal listings.
3. **Require corroboration before marking anything `confirmed`.** A single search result – one article, one directory listing, one AI-generated summary – is not confirmation, even if it looks authoritative. Only mark a fact `confirmed` once at least two independent sources agree (a company's own site plus a funding-tracker database, e.g., not two news articles both citing the same original press release). If sources disagree or only one can be found, mark `confidence: estimated` and say plainly in the output that this is a single-source or conflicting read, not a verified one. List what was actually checked in `sources` – that field exists precisely so this can be audited later, not just asserted.
4. Write the result to `companies/<company-slug>.json` following the schema.
5. Tell the user the score took a moment longer because it verified live, when that happens – never silent.
6. **When the user identifies a named interviewer** (hiring manager, panel member – for a Briefing pack, see Step 4), run the same kind of bounded, read-only lookup on that individual: professional background, tenure, prior companies, anything publicly relevant to how they might approach the interview. Same confirmed/estimated sourcing transparency as company facts. **Explicit caveat, every time a lookup is thin:** public bios for individuals are typically sparser and staler than company data – flag that plainly rather than presenting a thin snippet with the same confidence as a verified funding round.

This agent only ever reads public information about a company or a named individual. It does not contact either.

## Step 4: Log an application / update status

Update the application file per `schema/SCHEMA.md` as things change, and update `status_date` to the date of every transition – it's the single source of truth the dashboard and recalibration agent both rely on, not a field to leave stale. **In a Claude.ai Project, this means outputting the updated file and reminding the user to re-add it to the Project themselves, every time – see Platform detection above.** Skipping that reminder means the update silently doesn't stick.

**Status transitions.** The state machine is small and exhaustive – see `schema/SCHEMA.md` for the full table:

```
scored       -> applied | didnt_apply
applied      -> rejected | assumed_rejected | interviewing
interviewing -> offer | rejected_after_interview | withdrew_after_interview
```

- When the user confirms they've actually submitted an application for a role already scored under Step 2, move `status` from `scored` to `applied` and set `date_applied` to the real submission date. If instead they decide **not** to submit, move `status` to `didnt_apply` – don't just leave it at `scored` indefinitely, which should mean "still deciding," not "decided against it."
- **At this exact transition** – and only here, never at Step 2 – ask what actually went out with the application: a role-tailored CV (or the baseline as-is), a cover letter, any supplementary responses. Record the answer in `application_materials` per `schema/SCHEMA.md`. Most applications will just use the baseline (`cv: null`) – that's the common case, not a gap to chase down. Don't ask this question while scoring; it isn't answerable yet, since tailored materials for a role nobody's applied to don't exist.
- When a rejection or withdrawal comes in, check whether `status` has ever been `interviewing` for this application – if it has, use `rejected_after_interview`/`withdrew_after_interview`, not the plain `rejected`. This isn't pedantry: reaching interview stage validates the scoring rubric's prediction (jd_fit/seniority/competition) regardless of what happens afterward, and collapsing that into a flat rejection throws away exactly the signal Step 6 needs. There's no separate status for withdrawing after applying but before interviewing – log it as `rejected` and note the real reason (e.g. comp confirmed below floor) in the JD summary; it's rare enough, and ambiguous enough for the recalibration signal, that it doesn't need its own state.
- `assumed_rejected` is for silence-based inference only – see Step 5. Never set it just because the user assumes a rejection is likely; only the configured silence window or the user's own explicit call justifies it.
- Once `status` reaches any closed status, or `offer`, set `score.locked: true` and **never revise a locked score again for any reason** – it's a prediction evaluated by the outcome, not adjusted to match it.

**Next interview date:** every time an `interviewing` application is updated, ask whether the next stage has a confirmed date and set `next_interview_date` accordingly – to that date if known, or back to `null` if the last stage just happened and the next one isn't booked yet. This is what the dashboard uses to show what's actually coming up next; a stale date left in the field is worse than no date at all.

**Briefing pack – standard sections, not a menu.** Once `status` moves to `interviewing` or beyond, add the Briefing pack section per `schema/SCHEMA.md`. The five original fields (Company facts, Comp, Why it progressed/didn't, Watch-outs, Interview stage log) plus Unique selling points, Interviewer profiles, Prep questions, Questions to ask, and Notes are all **standard** – generate them by default, don't ask the user's permission first or wait to be asked for "more depth."

- **Unique selling points, Prep questions, Questions to ask:** always attempt real synthesis, grounded specifically in what was actually submitted for this application – `application_materials` if set (Step 4), otherwise the baseline CV (Step 1) – cross-referenced against this role and company, never generic interview advice. Use the submitted materials, not whatever the baseline says by interview time if the two have since diverged: the interviewer read what was actually sent, not today's baseline. A USP or answer without a traceable evidence source doesn't belong in the file.
- **Interviewer profiles:** only for interviewers the user has actually named (see Step 3). If none are known yet, write the section anyway with a single placeholder entry – don't omit the section.
- **Notes:** the catch-all for anything situational (competitive landscape, warm-intro context, quotes from the user's own prior materials, a postmortem on why an earlier stage didn't land). Real content when there's something to say; a placeholder when there isn't.
- **Regional intelligence is the one section that's genuinely optional, not standard.** Only add it when the role actually spans multiple markets in a way that matters for interview prep – a purely domestic role should never get an empty or placeholder regional table, just an omitted section. When it is relevant, this is general cultural/business-norm pattern knowledge, not a verified fact – say so plainly, the same way an estimated company fact gets flagged, rather than presenting it with company-facts-level confidence.
- **`Currently unknown` placeholders** are for genuine gaps in the standard sections – mainly Interviewer profiles before a name is shared, and Notes before anything situational has come up. They should be rare for the other sections, not the default output: a tool that fills every section with confident-sounding genericness is worse than one that's honest about what it doesn't know yet, but a tool that defaults to placeholders everywhere it could have done real work is worse still. Write the placeholder as normal content in that section's own format (see `schema/SCHEMA.md` for the exact convention per section type – bullet, Q&A pair, profile block, or prose), always paired with a specific, actionable ask, e.g. `Currently unknown – share an interviewer's name if you'd like a profile added.` This is meant to be a living document, filled in over further conversation, not a one-shot output.

## Step 5: Regenerate the dashboard

Read every application file, build the three-level view (Pipeline → Interview stage → Briefing pack) per the dashboard template, and output/write it. Do this whenever asked, or after logging a new application/outcome if the user seems to be working through their pipeline in one sitting – but don't regenerate proactively on every single small edit if it wasn't asked for; that's unnecessary cost for no benefit.

**In a Claude.ai Project, build the `/*__DATA__*/` array with `json.dumps` in a code-execution step, never by hand-typing the JSON text.** But serializing correctly isn't the whole fix – **when splicing that JSON string into the HTML template at the marker, use a `re.sub` replacement *function*, never a replacement *string*.** `re.sub(pattern, replacement_string, text)` reinterprets backslash sequences in `replacement_string` (it treats them as backreference syntax), which silently turns `json.dumps`'s correctly-escaped `\n` inside long fields like `jd_summary`/`caveats` back into literal raw newlines – invalid syntax inside a JS string literal, even though the JSON itself was valid a step earlier. The failure mode is a fully-rendered header/footer with a completely blank pipeline list and nothing visible to the user beyond a browser-console `SyntaxError`. Use `re.sub(pattern, lambda m: replacement_string, text)` (or `str.replace`, which doesn't have this problem) instead. Cowork can still write the file directly, so this applies specifically to the Claude.ai Project case, where there's no `build_dashboard.py` run doing this for you.

**Silence check.** As part of regenerating (or whenever asked to review the pipeline), scan `applied` applications for silence past `config/weights.json → pipeline_hygiene.assumed_rejected_after_days`, measured from `status_date`. For each one past the threshold, **propose** marking it `assumed_rejected` – state which application, how long it's been silent, and let the user confirm or dismiss each one. Never set it silently, and never propose it again for an application the user has already dismissed once. `assumed_rejected` is only reachable from `applied`, per the state machine in Step 4 – an `interviewing` application that goes quiet stays `interviewing` until the user reports an actual outcome, not silently reclassified.

## Step 6: Pipeline self-review / recalibration agent

**User-triggered only** – never run this automatically, not even after logging an outcome. Only run it when explicitly asked (e.g. "review my weights," "am I scoring this right?").

1. Read every application file's `status` and `score.value`. Classify each via `scripts/_status.py`'s `recalibration_signal()`: reaching interview stage (`interviewing`, `offer`, `rejected_after_interview`, `withdrew_after_interview`) is **positive** regardless of the eventual outcome; a confirmed negative without ever reaching interview (`rejected`, `assumed_rejected`) is **negative**; everything else (`didnt_apply`, or a status that hasn't resolved yet) is excluded – it's a deliberate pass or hasn't resolved yet, neither of which says anything about candidate fit.
2. Check against `config/weights.json → recalibration` thresholds: at least `min_logged_outcomes` applications with a signal, and at least `min_positive_outcomes` positive ones.
3. **Below threshold: say so plainly.** State how many logged and positive signals exist now, how many more are needed, and stop there. Do not propose a change anyway "for what it's worth."
4. **At or above threshold:** compute the per-component positive/negative mean split (`scripts/verify_recalibration.py` does this mechanically against the example set – for a real user's data, do the equivalent by reading their `applications/` files directly). A component that's consistently high on negatives and low on positives suggests it's mis-weighted.
5. **At or above `min_logged_outcomes_joint` specifically:** also report the joint model (`scripts/verify_recalibration.py`'s logistic-regression function) – standardised per-component coefficients showing which components are independently associated with a positive outcome once the other four are held constant. This exists because the simple per-component means can be misleading on their own: two correlated components (e.g. `jd_fit` and `seniority` tend to move together for a given role) can both show a strong mean difference even if only one of them is actually doing the predictive work. The joint model needs proportionally more data than the simple means to produce stable coefficients, hence the higher, separate threshold.
6. Propose a specific, small adjustment to `config/weights.json`, with:
   - The reasoning in plain terms (which component, what pattern, how many data points it's based on) – and if the joint model is available, note plainly if it disagrees with the simple per-component mean for that component (a real, worth-flagging signal that the simple mean may be confounded by another component, not noise to ignore).
   - An explicit confidence caveat – this is a weak signal from a small sample, not a validated finding, however large the sample gets in absolute terms.
   - The change presented for the user's approval, never applied silently.
7. This checks calibration drift against outcomes. It does not audit the scoring logic itself for bugs – that's out of scope for this agent.

---

## Tone

Direct, evidenced, sceptical. No reassurance or inflation. Flag every estimate clearly rather than guessing silently. Scoring reflects genuine callback probability, not effort invested or how good a story sounds.
