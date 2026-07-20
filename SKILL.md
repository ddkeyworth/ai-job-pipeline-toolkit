---
name: job-pipeline
description: Tracks job applications, scores job descriptions for callback likelihood, and maintains a visual pipeline dashboard. Use this skill whenever the user wants to score a job description, log an application, update an application's status or outcome, review their pipeline, or produce/update/add to their dashboard, however they phrase it. Works entirely on the user's own tracked data – never on data belonging to anyone else.
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

- **Running in Cowork with a local folder connected**: read and write application files directly in that folder. Write the regenerated dashboard back to it, then **offer to pin it to the user's Artifacts library as a standard part of this step, every time it's the first dashboard produced in a chat – don't wait to be asked separately.** Confirmed live: without this offer, a real user has no way to know the extra step exists, and the dashboard stays a local file only. This offer has also been confirmed, three separate times, not to reliably happen on its own even with this instruction present – so if the user's own first message already asks for the pinned Artifact explicitly (the README's recommended pattern), treat that as the actual instruction and prioritise it, rather than silently working toward the offer-it-yourself version instead.
- **Running in Cowork with only a Project's files connected, no local folder**: this only gives read access – confirmed directly, live, from Cowork's own explanation: there is no tool available to write into a Claude.ai Project's knowledge from Cowork, a hard platform limit, not a missing instruction. Use it freely to read source material (CV, JDs, cover letters), but never claim or imply that anything written this way (a scored application, a company cache, a dashboard) has persisted anywhere the user can rely on finding it again – it has only gone to a working location this specific session can reach, not a durable one. Say so plainly, and recommend connecting a local folder for anything meant to last.
- **Cowork's dashboards are local files, pinned in a local Artifacts panel – not cloud-hosted, and not self-refreshing "Live Artifacts" in the connector sense.** Confirmed directly, from Cowork's own explanation: this kind of Artifact has no web URL at all – it's a file on the machine running Cowork (Windows: `C:\Users\<user>\Claude\Artifacts\<name>\index.html`), opened via the desktop app's own Artifacts panel or directly from disk, not reachable from `claude.ai` in a browser or from any other device. Never say it's "saved to claude.ai," "shareable via link," or "accessible from a browser" – all wrong for this kind of Artifact, correct only for a Chat-mode Published one (see below). Separately: genuine auto-refresh only happens when an Artifact calls a connector tool (Slack, Gmail, a calendar, etc.) live from the browser – this skill's data is local markdown files with no connector behind it, so a job-pipeline dashboard **cannot** auto-refresh that way either, on top of not being web-hosted at all. Real, correctly-described benefits over Chat mode: it persists on disk independent of the chat that created it, doesn't need a manual Publish click, and updating it never needs a download/re-upload round-trip. Never describe it as "auto-updating," "always-current," or "live" in the sense of updating itself unprompted – say "pinned and persisted locally, updated whenever the dashboard is regenerated" instead. Push updates to the *same* pinned Artifact on every subsequent regeneration, not a new one each time. **Never confirm to the user that something is pinned unless you have actual confirmation it happened** – confirmed directly that a session can narrate this as done when it wasn't; if there's any doubt, tell the user to check Cowork's own Artifacts panel themselves rather than asserting success.
- **Running in a Claude.ai Project (Chat mode, no Cowork)**: read application files from the Project's knowledge files. **Project files are read-only from here – there is no way to write or update one directly, for a brand-new application or an edit to an existing one.** Every time you create or update an application file, output it as a downloadable document and **say plainly, every time, not just once**, that the user needs to add/replace it in the Project's files themselves for it to actually persist – otherwise it won't be there next time the pipeline is reviewed, rescored, or the dashboard is regenerated, and any edit you make in this conversation is invisible everywhere else until they do.
- **The dashboard Artifact in Chat mode is real but static, and needs an explicit action to persist at all.** Regenerating the dashboard as an Artifact in a Claude.ai Project produces a correctly-rendered Artifact, but it does **not** appear in the user's Artifacts library automatically – it only exists inside that one chat thread until the user opens it and clicks **Publish** themselves (Claude never does this on the user's behalf – see "Explicit permission required" territory). Once published, it does become a real, independently-findable item in the Artifacts library and gets a shareable URL – but it is a **static snapshot, not a Live Artifact**: it does not auto-update as new applications are scored or logged, isn't pinnable, and has to be manually republished (a new Publish, not an edit) to reflect anything that's changed since. **Say plainly, every time a dashboard Artifact is produced in Chat mode**, that it needs to be published to persist at all, and that even published it's a snapshot, not a live view – then mention Cowork's Live Artifacts as the option that behaves like an actual ongoing dashboard, without overstating Chat mode as unusable.

- **Before scoring or tracking anything in Chat mode (no local file access), confirm this is actually what the user wants.** State plainly: this path doesn't produce an ongoing tracker – every update needs a manual re-upload, and the dashboard is a one-off snapshot even if published – then ask directly whether this is deliberate one-off/occasional use, or whether they're starting a real job search Cowork would serve better. Wait for an actual answer before proceeding; don't assume a Claude.ai Project was a deliberate choice, since most users won't know the distinction exists until it's pointed out. Ask once per chat, not on every message – once answered, respect it and get on with the work.

- **Only one Cowork chat should be active against the same data at a time.** Each Cowork chat works from its own snapshot of the folder taken when that chat started – it has no visibility into edits a separate, concurrently-open Cowork chat makes to the same files. If two chats are both pointed at the same folder (or an old one is left open while a new one starts), whichever writes last silently overwrites the other's changes, with no merge and no warning – the same failure mode as the skill-snapshot behaviour above, just for the tracked data rather than the skill definition itself. Since there's no way to detect this from inside a single chat, mention it once when starting work in a Cowork session against local files, and recommend the user close any other Cowork chat pointed at the same folder first.

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
Before scoring, read the CV and derive 3-6 core competency clusters from its actual substantive content – the underlying capability patterns the CV concentrates around, not job titles. Never hardcode a specific profession into this instruction; the derivation runs fresh off whatever CV is loaded, so it produces a different set of clusters for a different person without any rewording here. This is a fast, implicit read for the common case, not a heavyweight ritual – most JDs will map obviously onto the candidate's most recent role, and deriving clusters just makes that mapping explicit rather than skipping straight to a title-match.

Then: identify the JD's primary required function from its own stated responsibilities, not its title. Match that function against the derived clusters – best match, secondary match, or **no good match**. A genuine mismatch should still score low; that's the model working correctly, not a flaw this step is meant to soften. Form one overall judgement of fit within the matched cluster(s), weighing seniority, years of experience, and specific must-have skills together – never mechanically score each named requirement separately and average them; that produces a worse, more brittle read than one holistic judgement grounded in real evidence. This is what catches a genuine but non-obvious fit – a role whose title doesn't resemble the candidate's most recent one, but whose actual day-to-day responsibilities draw on the same underlying capability – that a plain title-match read would otherwise structurally undervalue.

**Recency.** Not all evidence ages the same way. Durable capability – programme delivery, budget stewardship, executive stakeholder management, cross-functional leadership – doesn't meaningfully decay; sustained tenure in that mode is a strength, not something to discount for age. Currency-sensitive specifics – a named tool, a market's current competitive dynamics, a platform's present feature set – genuinely can go stale. This is a **discount only, never a bonus**: form the fit judgement above first, then apply a small deduction (range in `config/weights.json` → `components.jd_fit.recency_modifier`, default 0 to -3) only when **both** are true: the JD names something explicitly currency-sensitive, and the candidate's best evidence for it is old and unreinforced by anything recent. Fresh, current evidence simply isn't discounted – it was never a reason to add points beyond what the fit judgement already reflects. Never apply it to leadership/institutional-scale credentials, and never as a blanket discount across the whole score.

**Career-break guardrail.** A planned, explained gap in paid work is not itself evidence of decaying capability and should never trigger the recency modifier on its own – score it as a bounded pause, not staleness. Self-directed work done during the gap (a side project, published writing, self-directed study) counts as genuinely recent evidence wherever a JD's requirement touches on it – this rewards someone who kept building during a break rather than penalising the gap itself.

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

**A candidate's own voluntary statement of comp flexibility is never equivalent to a confirmed sub-floor band.** If the user mentions telling a recruiter they're open to less than their stated floor, that's the candidate's negotiating position, not a fact about what the role pays – score against what the company/role has actually disclosed (or the live-search estimate above), never against the candidate's own stated openness.

### Blockers
Right to work, geography, visa, or other confirmed hard requirements. Test carefully before scoring low here – a soft inconvenience is not a blocker.

### Before creating the file, check for an existing one
Run `python scripts/check_duplicate.py --company "<company>" --role "<role>" --dir <path to the user's applications folder>` – on Cowork, `--dir` is the user's real local applications folder; on Claude.ai, it's `/mnt/project` (confirmed working: Project files are mounted there and readable by code execution, even though they're read-only to write – see Platform detection above). A HIGH confidence result (same company, same role title already tracked) means don't silently create a second file – tell the user what already exists and ask whether this is a duplicate/repost or something that should update the existing record instead. A LOW confidence result (same company, different title) just means naming it clearly – e.g. distinguishing "Role 1"/"Role 2" in the filename or a short qualifier – so the two stay easy to tell apart on the dashboard; it's common for one company to have multiple genuinely distinct open roles, so don't treat this as a problem to resolve, just flag it. No match: proceed as normal – but note that "no match" only means no schema-formatted application file matched, not that none was checked; if this is the first time the skill is tracking applications in this location, say so rather than implying a populated set was searched and cleared.

### Output
State the score, tier, a one-line rationale per component, and explicitly flag any component that's an estimate rather than a confirmed fact (e.g. an anonymised listing with unverifiable company details). The `jd_fit` rationale line should name which competency cluster the role's primary function matched against – or state plainly that none matched – not just restate the score. Create the application file per `schema/SCHEMA.md` with `status: scored` and `date_applied: null` – scoring a JD doesn't mean it's been applied to. Not every scored JD gets a follow-up application, and the pipeline should show that honestly rather than only tracking JDs after the fact.

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

**In Cowork, "regenerate the dashboard" means two actions, not one: build the file, and pin/update the Artifact. Neither is optional, and the second is not implied by the first.** If this task is being tracked as a checklist or plan of any kind, put both on it now, at the start – not just "write the dashboard file," which is the incomplete version of this task that has already shipped once. A dashboard that exists only as a local file is not a completed regeneration in Cowork.

Read every application file, build the three-level view (Pipeline → Interview stage → Briefing pack) per the dashboard template, and output/write it. Do this whenever asked, or after logging a new application/outcome if the user seems to be working through their pipeline in one sitting – but don't regenerate proactively on every single small edit if it wasn't asked for; that's unnecessary cost for no benefit. **In a Claude.ai Project (Chat mode, no Cowork), producing the dashboard this way also means telling the user plainly, in the same turn the Artifact is shown, every time, not just once, that it needs an explicit Publish click (by them, not by Claude) to appear in their Artifacts library at all, and that even published it's a static snapshot, pushed forward again only by a fresh manual Publish – see Platform detection above for exactly how this compares to Cowork's pinned-but-also-not-self-refreshing dashboards, and don't describe either one as "auto-updating." Skipping the Chat-mode disclosure leaves the user believing they have a saved, current dashboard when they don't.**

**Call `inject_data()` from `scripts/build_dashboard.py` directly – never hand-splice the `/*__DATA__*/` marker or reimplement the injection logic freehand.** The skill's own scripts are reachable via code execution on both platforms (Cowork has direct local access; on Claude.ai the skill's files are mounted at `/mnt/skills/user/job-pipeline/`, confirmed working – see `scripts/check_duplicate.py`'s usage above). Import it and call it:

```python
import sys, json
sys.path.insert(0, "/mnt/skills/user/job-pipeline/scripts")  # local path for Cowork instead
from build_dashboard import inject_data

with open("/mnt/skills/user/job-pipeline/docs/index.html") as f:  # local path for Cowork instead
    html = f.read()
new_html = inject_data(
    html, apps,
    subtitle="Your tracked applications – N scored so far.",
    title="Your Job Pipeline",
)
with open("/mnt/skills/user/job-pipeline/docs/index.html", "w") as f:  # local path for Cowork instead
    f.write(new_html)
```

**Never hand-edit the rendered dashboard HTML directly for a content correction – a wrong company fact, a misspelled name, a missing regional row, anything the dashboard displays.** The dashboard is a fully regenerated view, not an independent record: the next full regeneration reads the application files and `companies/<slug>.json` fresh and rebuilds the HTML from scratch, silently discarding anything patched directly into the HTML that was never written back to its actual source. Fix the source instead – `companies/<slug>.json` for a company fact (it's reused across every application to that company, so a stale one there stays wrong everywhere), the application's own Briefing Pack section for anything specific to that application (Regional intelligence, interviewer profiles, etc.) – then regenerate via `inject_data()` as above. Patching the rendered HTML in place is also what tends to trigger the write-truncation risk below, since it means repeatedly editing a large existing file instead of rebuilding it in one shot from small source files.

**Write the result back this way – one direct, complete write – never through an incremental/patch-based file-editing tool.** A real dashboard is not small: this repo's own 35-example demo is already 100KB+, and a genuine multi-month pipeline will grow well past that. A concrete report from real use: an incremental file-editing tool silently truncated a dashboard file right around 155-158KB, with no error surfaced – the file just ended up shorter than intended, mid-content, until rewritten as a single direct write. Read the whole file, build the whole new string, write the whole thing back in one call, exactly as above.

**Immediately after that write, in Cowork: pin it or push to it. Do not respond to the user describing the dashboard as done until this has happened.**
1. First dashboard in this chat → ask directly whether to pin it to the Artifacts library, stating plainly in the same message that this makes it a persisted snapshot, not a self-refreshing one (see Platform detection above for why).
2. A pinned Artifact from this chat already exists → push the update to that same Artifact directly. Don't ask again.

This was skipped once already in real use, with the file written correctly and the turn simply ending there – confirm in your own response that you actually did this, not just that the file was written.

**If a separate local outputs-folder copy and a pinned Artifact both end up existing with the same content, cross-link them – confirmed working, and it directly resolves the "which one am I actually looking at" confusion that caused real, repeated confirmation problems in testing.** Call `inject_data()` twice, once per file, each time passing `cross_link_path` as the *other* file's real path (plain OS path, not a URL – `inject_data()` builds the `file://` URI itself via `pathlib`, so don't hand-construct one). This renders a small banner naming the other copy; leave `cross_link_path` unset (the default) when there's only one copy, and the banner disappears entirely rather than showing empty. One asymmetry, confirmed live: the outputs-copy → pinned-Artifact link works reliably when opened in a real browser, but the reverse direction may not open from inside the pinned Artifact's own sandboxed view, which blocks most outbound navigation – if so, the path is still there as visible text to copy manually, so don't treat that as a failure to fix.

Reusing the real, tested function (rather than reimplementing it inline each time) is what actually prevents three real bugs that have all shipped before:

- **A `re.sub` corruption bug.** A plain-string replacement to `re.sub` reinterprets backslash sequences (it treats them as backreference syntax), silently turning `json.dumps`'s correctly-escaped `\n` inside long fields like `jd_summary`/`caveats` back into literal raw newlines – invalid syntax inside a JS string literal. The failure mode is a fully-rendered header/footer with a completely blank pipeline list and nothing visible to the user beyond a browser-console `SyntaxError`. `inject_data()` already handles this correctly internally – that's exactly why it should be called, not re-derived from memory.
- **A stale "fictional data" disclaimer.** The template's banner subtitle says "Fictional companies... No real job search data" – true only for the public demo. `inject_data()` requires a `subtitle` argument for this reason: write something accurate for the user's own real data (e.g. `"Your tracked applications – N scored so far."`), never leave or copy the demo's disclaimer text into a real user's dashboard.
- **A stale "example dashboard" browser-tab title.** Same root cause as the subtitle, one level less visible – easy to miss even right after fixing the subtitle, which is exactly what happened once already. `title` is required for the same reason: write something accurate (e.g. `"Your Job Pipeline"`), never leave the demo's title in a real user's dashboard.

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
