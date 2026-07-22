# Data Schema

This is the shared contract between every part of this toolkit – the skill, the dashboard, and both front ends (a Claude.ai Project's files, or a local folder used with Cowork). Nothing here is platform-specific. If you follow this format, it doesn't matter which of the two ways you run the tool.

There is no database and no server. Every tracked application is one plain-text file. Your data lives wherever you put it – never inside a clone of this repo (see `README.md` → Security).

## 1. Preferences file

One file, `preferences.md`, holding the user's own stable settings – right now just their compensation floor, structured to grow later without a redesign. Collected explicitly (see `SKILL.md` Step 1), never inferred from a CV – most CVs don't state compensation at all, and guessing from one that happens to would silently fail for everyone else.

```markdown
# Preferences

## Compensation floor
On-target earnings (base salary + target bonus/variable comp; equity explicitly excluded – see `config/weights.json` → `components.comp.equity_handling`): £110,000

Confirmed: 2026-07-14
```

Treated exactly like the CV baseline (`SKILL.md` Step 1): a single evolving value, not re-asked every session, updated only when the user explicitly says it's changed, with the update confirmed plainly rather than applied silently. `Confirmed: <date>` is the same "when was this last set" convention `status_date` uses elsewhere in this schema – it's what tells you whether a floor might be stale, not a field anything parses programmatically.

## 2. Application file

One file per tracked application. Markdown with YAML frontmatter. Suggested filename: `YYYY-MM-DD-company-role-slug.md`, but the filename itself is never parsed – only the frontmatter and body matter.

```yaml
---
company: "Acme Corp"
role: "VP, Customer Success"
date_scored: 2026-02-26      # always set – the date the JD was scored
date_applied: 2026-03-01     # null until status is applied or later – see status note below
status: applied            # see status table below
status_date: 2026-03-01    # the date the CURRENT status was last set – updated on every transition
source: "LinkedIn"         # optional, free text

score:
  value: 78
  tier: "Tier 2 – Strong callback odds"
  locked: false            # true once status reaches a closed status – locked scores are never revised
  breakdown:
    jd_fit: 38             # /45
    seniority: 12          # /15
    competition: 12        # /20
    comp: 10               # /10
    blockers: 10           # /10
  estimated_fields: ["competition"]   # sub-scores flagged as estimates, not certainties

next_interview_date: null   # null, or the next confirmed interview date (YYYY-MM-DD)

comp_band: "£140k-160k OTE"  # stated or estimated on-target earnings (base + bonus, equity excluded); null if not stated and not reasonably estimable – see SKILL.md and config/weights.json -> components.comp

application_materials:       # null while status is "scored" – set once when status moves to "applied", never guessed
  cv: null                   # null = the baseline CV was used as-is; otherwise the filename/description of a role-tailored CV
  cover_letter: null         # null, or the filename/description of the cover letter actually submitted
  supplementary: []          # any other submitted documents (supplementary responses, portfolio, etc.) – empty list if none

at_application_score:        # null while status is "scored"/"didnt_apply" – set once, alongside application_materials, when status moves to "applied". Same shape as score, minus locked - see note below.
  value: 82
  tier: "Tier 1 – Exceptional callback odds"
  breakdown:
    jd_fit: 41
    seniority: 13
    competition: 12          # carried over unchanged from score.breakdown
    comp: 10                 # carried over unchanged from score.breakdown
    blockers: 10             # carried over unchanged from score.breakdown
---

## JD summary
Short paraphrase of the role, not a copy-paste of the listing.

## Score rationale
One line per component, matching the breakdown above – real reasoning, not a restatement of the number:

```markdown
- JD fit (38/45): Strong overlap on core CS-leadership responsibilities; no direct experience in the stated regulatory domain.
- Seniority alignment (12/15): Director level matches the candidate's evidenced range.
- Competition estimate (12/20, estimated): Mid-size, not a widely recognised brand.
- Compensation alignment (10/10): £140k-160k OTE, confirmed above the £110k floor.
- Blockers (10/10): No blocker identified.
```

A line that just repeats the score (`"JD fit: 38/45"`, nothing else) isn't a rationale – it tells the reader nothing the breakdown numbers above it don't already show.

## Caveats
Anything estimated rather than confirmed (anonymised listing, unclear comp split, etc.)
```

### Status values

The state machine is small and exhaustive – every status is reached from exactly one place:

```
scored       -> applied | didnt_apply
applied      -> rejected | assumed_rejected | interviewing
interviewing -> offer | rejected_after_interview | withdrew_after_interview
```

Listed in flow order below – each status sits right after wherever it's reached from, not grouped by active/closed:

| Status | Meaning | Active / closed |
|---|---|---|
| `scored` | JD scored, decision pending | active |
| `didnt_apply` | Scored, then a deliberate decision **not** to submit – distinct from `scored`, which means the decision is still pending | closed |
| `applied` | Submitted, no response yet | active |
| `rejected` | Rejected **before** ever reaching interview stage | closed |
| `assumed_rejected` | No response past a configurable silence window (`config/weights.json → pipeline_hygiene`) – inferred, never confirmed | closed |
| `interviewing` | In an active interview process | active |
| `rejected_after_interview` | Rejected **after** reaching interview stage | closed |
| `withdrew_after_interview` | Withdrew **after** reaching interview stage | closed |
| `offer` | Offer extended | active |

Two earlier candidates for this list – a recruiter-gating status and an externally-closed-role status – were tried and dropped: too messy to track in practice, and not enough signal to justify the extra states. Removed rather than left in unused.

The pre/post-interview split on rejection and withdrawal is deliberate, not pedantic: reaching interview stage is itself a validated positive signal for the scoring rubric (jd_fit/seniority/competition correctly predicted a callback), regardless of what happens afterward. Collapsing `rejected_after_interview` into plain `rejected` would throw away exactly the signal the recalibration agent needs – see `SKILL.md` → Step 6.

**`status: scored`** is the state every application starts in. This is deliberately first-class, not an afterthought: scoring happens *before* the decision to apply, and a real pipeline includes JDs that were scored and never applied to, not just ones that made the cut. `date_applied` stays `null` for as long as `status` is `scored`. Once a deliberate decision is made not to apply, move to `didnt_apply` rather than leaving it at `scored` indefinitely – `scored` should mean "still deciding," not "decided against it."

There is deliberately no status for withdrawing after applying but before interviewing – in practice that's rare enough, and ambiguous enough for the recalibration signal, that it's folded into `rejected` (see `SKILL.md` → Step 4 for how to log it honestly in the JD summary even though the status itself doesn't distinguish it).

**`status_date`** updates every time `status` changes – it's what the dashboard's sort falls back to for closed applications, and what silence-based `assumed_rejected` detection compares against (see `SKILL.md` → Step 5). There is no separate `outcome`/`outcome_date` field – `status` plus `status_date` is the single source of truth for where an application stands; a second, independently-mutable field for the same fact is exactly the kind of thing that drifts out of sync over time.

**`score.locked`** becomes `true` once `status` reaches any closed status, or `offer` – the score is a prediction, evaluated by the outcome, never adjusted to match it. `offer` isn't in the closed-status list (it stays in the active group for sorting – still exciting, not buried with rejections) but is effectively terminal for locking purposes: this schema doesn't track what happens after an offer (accepted/declined/negotiated is out of scope), so nothing further would ever unlock it anyway. See `scripts/_status.py`'s `should_lock()`.

**`next_interview_date`** only matters once `status` is `interviewing` – it's what lets the dashboard surface "what's coming up" instead of just a flat list. Set it to the next confirmed date whenever one is booked. Once that interview happens, set it back to `null` immediately if the next stage isn't scheduled yet – don't leave a past date sitting in the field. That's what makes a card fall to the back of the active group until a new date is actually known, rather than staying stuck at the top on a stale date.

**`application_materials`** exists because the CV baseline isn't the whole story: some applications go out with a role-tailored CV, cover letter, or supplementary responses instead of (or alongside) the baseline, and some don't. This is deliberately **not** asked at scoring time (`status: scored`) – a JD gets scored against the current baseline, full stop, since tailored materials for a role you haven't even applied to yet don't exist. The question belongs at the `scored` → `applied` transition instead: what actually went out the door for this specific application? A `cv` of `null` means the baseline was used unmodified – that's the common case and not something to flag as missing. Once set, this is what interview-prep content (see Briefing pack below) should be grounded in, not necessarily whatever the baseline CV says by the time an interview happens – the interviewer read what was actually submitted, not today's baseline.

**`score` is a frozen prediction – never edited to reflect `at_application_score`, never edited at all outside Step 2, regardless of what's learned later.** It's the "pre-application" read: how well the role fit the baseline CV at the moment the JD was scored, before any tailored materials existed. This is what `score.locked` and Step 6's recalibration agent both depend on – recalibration only means something if it's checking the rubric's original prediction against the real outcome, not a version quietly touched up with hindsight.

**`at_application_score`** is a separate "at-application" read, populated once, alongside `application_materials`, at the `scored` → `applied` transition – deliberately **always** set at that point, not only when materials happen to differ from the baseline, so it's never blank for an applied application and the dashboard can sort on it cleanly. Same shape as `score` – `value`, `tier`, `breakdown` – but no `locked` flag, since it isn't part of the recalibration signal and there's no later checkpoint that revises it further. `jd_fit` and `seniority` are recomputed against what was actually submitted (they measure the candidate's evidence against the role, so they should reflect what went out the door); `competition`, `comp`, and `blockers` are carried over from `score.breakdown` unchanged, since they're properties of the role, the company, and fixed candidate circumstances that don't depend on which CV version was sent. When `application_materials` matches the baseline exactly, this recompute reproduces the same `jd_fit`/`seniority` already in `score` – `at_application_score` ends up an exact duplicate of `score`, which is correct, not redundant: it keeps every applied application sortable on this field with nothing missing. **Step 6 recalibration always reads `score`, never `at_application_score`** – see Step 6 in `SKILL.md`.

### Briefing pack

If `status` is `interviewing` or later, add a **Briefing pack** section to the body – it must be the last `##`-level section in the file:

```markdown
## Briefing pack

### Company facts
Pulled from the live-search verification agent – size, funding stage, sector, anything relevant to the role. See `companies/<company-slug>.json` for the cached source.

### Regional intelligence
*(Optional – only when the role genuinely spans multiple markets in a way that matters for interview prep. Omit entirely for single-market roles; don't force an empty table onto every application the way the standard sections below get a placeholder. Columns aren't fixed – use whatever's actually relevant.)*

A markdown table, one row per region:

| Region | Relationship style | Decision style | Key nuances |
|---|---|---|---|
| UK | Direct, commercial | Moderate speed | Post-Brexit cross-border complexity is a live concern – worth leading with. |
| US | Results-first | Fast at SME, slower at enterprise | Largest market, most competitive. |

Cultural/business-norm content like this is general pattern knowledge, not a verified fact the way company size or funding stage is – say so plainly rather than presenting it with the same confidence as a live-search result.

### Compensation
What's known, what's still open. `Currently unknown – not disclosed in the listing; worth asking early.` is valid content, not a gap to hide.

### Why it progressed / didn't
Honest read of what worked or didn't at each stage.

### Unique selling points
A bullet list, one evidenced argument per bullet, bold lead-in:
- **Direct P&L ownership.** Led a $40M product line through two quarters of contraction into growth – see CV, Acme Corp.
- **Cross-functional fluency.** Partnered with eng/design leads across three orgs at ScaleCo.

### Interviewer profiles
Repeatable `#### Name – Title` blocks, only for interviewers the user has actually named:

#### Jane Doe – VP Engineering
Ex-Google, 12 years in infra. [confirmed/estimated per live-search agent]

**What they're assessing:** Whether the candidate can hold their own in a technical review.
**How to play it:** Lead with concrete system-level examples, not roadmap stories.

### Prep questions
`**Q: ...?**` / `A:` pairs, typically 6–12, grounded in the candidate's real CV/cover-letter content:
**Q: Tell me about a time you had to trade off speed against quality?**
A: At Acme Corp, shipped the v1 checkout redesign in 3 weeks by...

### Questions to ask
A plain bullet list:
- How is the product org structured relative to engineering?
- What does success look like in the first 90 days?

### Watch-outs
Either prose, or a bullet list with the same bold-lead-in format as Unique selling points:
- **Small team.** Later stages likely to probe hands-on delivery, not just strategy.

### Notes
A freeform catch-all for anything situational – competitive landscape, warm-intro context, quotes from the candidate's own prior application materials, a postmortem on why an earlier stage didn't land. Free text, optionally using `####` sub-headings for organisation. Not deeply parsed – this is where one-off content goes instead of forcing a new rigid field every time something new comes up.

### Interview stage log
- Stage 1 – [date] – [what happened, outcome]
- Stage 2 – [date] – [what happened, outcome]
```

**Unique selling points, Interviewer profiles, Prep questions, Questions to ask, and Notes are all standard** – generated by default once `status` reaches `interviewing`, not conditional on being asked for. **Regional intelligence is the one exception** – genuinely optional, included only when the role spans multiple markets in a way that matters, omitted entirely otherwise (see above). Where a standard section's information genuinely isn't known yet, the skill says so plainly, **written as normal content in that section's own format**, not specially marked or omitted:

- Prose sections: `Currently unknown – [specific ask]`.
- Interviewer profiles: `#### Currently unknown – share an interviewer's name if you'd like a profile added` as the sole entry.
- Bullet sections (USPs, Watch-outs): `- **Currently unknown.** Share more about what makes you a strong fit for this specific role and I'll turn it into tailored selling points.`
- Prep questions: `**Q: Currently unknown**` / `A: Share more about the role or interview format and I can draft targeted prep questions.`

This should be the exception, not the default output – see `SKILL.md` → Step 4 for when a placeholder is appropriate versus when the skill should actually be doing the research or synthesis. An application with only the original three prose fields (Company facts, Compensation, Why it progressed/didn't) plus Watch-outs and the stage log is still a complete, valid briefing pack if that's genuinely all there is – the standard sections exist to be filled in over time, through conversation, not generated once and left static.

## 3. Company-fact cache

One file per company, only created once the live-search verification agent has actually looked a company up. Reused across every application to that company – this is what keeps live-search costs down (see `SKILL.md` → Live-search verification agent).

`companies/<company-slug>.json`:

```json
{
  "company": "Acme Corp",
  "verified_at": "2026-03-01",
  "size_estimate": "~2,000 employees",
  "funding_stage": "Series D, publicly traded",
  "profile": "Large, well-known SaaS company",
  "competition_tier": "high",
  "confidence": "confirmed",
  "sources": ["company careers page", "recent press coverage"]
}
```

`confidence` is either `confirmed` or `estimated`. `confirmed` requires at least two independent sources to agree (see `SKILL.md` → Step 3) – a single source, however authoritative it looks, is `estimated`. Anonymised or unverifiable listings are always `estimated`. Never presented as certain when it isn't (see `SKILL.md` → transparency rule). The same confirmed/estimated convention applies to interviewer research within a Briefing pack (see `SKILL.md` → Step 3) – individual public bios are typically sparser and staler than company data, and that should be flagged plainly, not smoothed over.

Cache entries are considered fresh for 90 days. Past that, the next application to the same company triggers a fresh lookup rather than reusing stale data.

## 4. Weights config

`config/weights.json` – the only file a user needs to touch to change scoring behaviour, plus the `pipeline_hygiene` block controlling silence-based `assumed_rejected` detection. Documented fully in that file's own comments-equivalent (`_notes` fields) rather than here, so the numbers and their explanation never drift apart.

## 5. Outcome signal (derived, not stored)

There is no separate outcomes file, and no separate `outcome` field. The recalibration agent (see `SKILL.md` → Step 6) derives its positive/negative comparison directly from each application's `status` and `score.value`, via `scripts/_status.py`'s `recalibration_signal()` – reaching interview stage (`interviewing`, `offer`, `rejected_after_interview`, `withdrew_after_interview`) is treated as positive; a confirmed negative without ever reaching interview (`rejected`, `assumed_rejected`) is negative; everything else (`scored`, `applied`, `didnt_apply` – a deliberate pass, or a status that hasn't resolved yet) is excluded from the comparison entirely. This is why consistent `status` values matter more than anything else in this schema – get this part wrong and the recalibration agent has nothing reliable to work from.
