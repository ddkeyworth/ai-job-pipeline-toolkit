# Data Schema

This is the shared contract between every part of this toolkit — the skill, the dashboard, and both front ends (a Claude.ai Project's files, or a local folder used with Cowork). Nothing here is platform-specific. If you follow this format, it doesn't matter which of the two ways you run the tool.

There is no database and no server. Every tracked application is one plain-text file. Your data lives wherever you put it — never inside a clone of this repo (see `README.md` → Security).

## 1. Application file

One file per tracked application. Markdown with YAML frontmatter. Suggested filename: `YYYY-MM-DD-company-role-slug.md`, but the filename itself is never parsed — only the frontmatter and body matter.

```yaml
---
company: "Acme Corp"
role: "VP, Customer Success"
date_scored: 2026-02-26      # always set — the date the JD was scored
date_applied: 2026-03-01     # null until status is applied or later — see status note below
status: applied            # scored | applied | interviewing | rejected | withdrawn | offer
source: "LinkedIn"         # optional, free text

score:
  value: 78
  tier: "Tier 2 — Strong callback odds"
  locked: false            # true once an outcome is known — locked scores are never revised
  breakdown:
    jd_fit: 38             # /45
    seniority: 12          # /15
    competition: 12        # /20
    comp: 10               # /10
    blockers: 10           # /10
  estimated_fields: ["competition"]   # sub-scores flagged as estimates, not certainties

outcome: null               # null | interview | offer | rejected | withdrawn
outcome_date: null

comp_band: "£140k-160k OTE"  # or null if unknown — absence is never penalised, see SKILL.md
---

## JD summary
Short paraphrase of the role, not a copy-paste of the listing.

## Score rationale
One line per component, matching the breakdown above.

## Caveats
Anything estimated rather than confirmed (anonymised listing, unclear comp split, etc.)
```

**`status: scored`** is the state every application starts in — a JD has been scored, nothing has been submitted yet. This is deliberately a first-class status, not an afterthought: scoring happens *before* the decision to apply, and a real pipeline includes JDs that were scored and never applied to, not just ones that made the cut. `date_applied` stays `null` for as long as `status` is `scored`. When the user actually submits, update `status` to `applied` and set `date_applied` to the real submission date — `date_scored` never changes.

If `status` is `interviewing` or later, add a **Briefing pack** section to the body:

```markdown
## Briefing pack

### Company facts
Pulled from the live-search verification agent — size, funding stage, sector, anything relevant to the role. See `companies/<company-slug>.json` for the cached source.

### Comp
What's known, what's still open.

### Why it progressed / didn't
Honest read of what worked or didn't at each stage.

### Watch-outs
Anything to be careful of going into the next stage.

### Interview stage log
- Stage 1 — [date] — [what happened, outcome]
- Stage 2 — [date] — [what happened, outcome]
```

## 2. Company-fact cache

One file per company, only created once the live-search verification agent has actually looked a company up. Reused across every application to that company — this is what keeps live-search costs down (see `SKILL.md` → Live-search verification agent).

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

`confidence` is either `confirmed` or `estimated` — the latter for anonymised or unverifiable listings. Never presented as certain when it isn't (see `SKILL.md` → transparency rule).

Cache entries are considered fresh for 90 days. Past that, the next application to the same company triggers a fresh lookup rather than reusing stale data.

## 3. Weights config

`config/weights.json` — the only file a user needs to touch to change scoring behaviour. Documented fully in that file's own comments-equivalent (`_notes` field) rather than here, so the numbers and their explanation never drift apart.

## 4. Outcome log (implicit)

There is no separate outcomes file. The recalibration agent (see `SKILL.md`) derives outcome history by reading every application file's `status`, `outcome`, and `score.value` fields directly — this is why consistent status/outcome values matter more than anything else in this schema. Get this part wrong and the recalibration agent has nothing reliable to work from.
