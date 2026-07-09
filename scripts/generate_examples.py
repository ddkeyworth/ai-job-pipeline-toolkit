#!/usr/bin/env python3
"""
Generates the synthetic example dataset in examples/.
Not required to use the toolkit — this is a one-time authoring aid, kept in
the repo so it's clear exactly how the demo data was produced: entirely
fictional companies, roles, and outcomes, no real job search data of any kind.

Run from the repo root: python scripts/generate_examples.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS_DIR = os.path.join(ROOT, "examples", "applications")
COMPANIES_DIR = os.path.join(ROOT, "examples", "companies")
os.makedirs(APPS_DIR, exist_ok=True)
os.makedirs(COMPANIES_DIR, exist_ok=True)

# (date, company, role, status, outcome, score, tier, jd_fit, seniority, competition, comp, blockers,
#  estimated_fields, comp_band, source, note)
APPLICATIONS = [
    ("2026-05-28", "Meridian Cloud Systems", "Director of Product", "applied", None, 52, "Tier 4 — Long shot",
     30, 12, 4, 6, 10, ["competition"], "£95k-110k base + bonus (unconfirmed split)", "LinkedIn",
     "Large, well-known public cloud platform — huge applicant pool expected."),
    ("2026-06-02", "Fernbank Analytics", "Head of Product", "applied", None, 81, "Tier 2 — Strong callback odds",
     40, 13, 16, 10, 10, [], "£120k-135k OTE", "Referral",
     "Small, private data-analytics startup, narrow role, strong direct fit."),
    ("2026-06-05", "Coastal Ledger", "Senior Director, Product", "applied", None, 68, "Tier 3 — Solid, worth applying",
     35, 12, 11, 10, 10, [], None, "Company site",
     "Mid-size fintech, moderately well-known in its niche."),
    ("2026-06-09", "Union Freight Group", "VP Product", "applied", None, 45, "Tier 4 — Long shot",
     28, 8, 5, 4, 10, ["competition", "comp"], None, "LinkedIn",
     "Large logistics incumbent, broad VP-level role draws a wide pool."),
    ("2026-04-02", "Northwind Retail Technologies", "Head of Product, Platform", "rejected", "rejected", 58, "Tier 3 — Solid, worth applying",
     32, 12, 6, 8, 10, ["competition"], "£110k-125k OTE", "LinkedIn", "Large, recognisable retail-tech brand."),
    ("2026-04-05", "Ashgrove Financial", "Director of Product Strategy", "rejected", "rejected", 61, "Tier 3 — Solid, worth applying",
     33, 11, 9, 8, 10, [], "£100k-115k base", "Company site", "Large regulated financial services firm."),
    ("2026-04-08", "Larkspur Health", "VP Product", "rejected", "rejected", 70, "Tier 3 — Solid, worth applying",
     36, 13, 13, 8, 10, [], None, "Referral", "Mid-size health-tech, moderately known."),
    ("2026-04-11", "Kettlebrook Robotics", "Head of Product", "rejected", "rejected", 74, "Tier 2 — Strong callback odds",
     38, 12, 14, 10, 10, [], "£115k-130k OTE", "LinkedIn",
     "Small robotics startup — good fit on paper, rejected anyway; not every high score converts."),
    ("2026-04-15", "Solari Energy Corp", "Senior Director Product", "rejected", "rejected", 55, "Tier 4 — Long shot",
     31, 10, 6, 8, 10, ["competition"], None, "LinkedIn", "Large, well-funded energy technology company."),
    ("2026-04-18", "Ferrous Metals Digital", "Head of Product", "rejected", "rejected", 66, "Tier 3 — Solid, worth applying",
     34, 12, 12, 8, 10, [], "£105k-120k base", "Company site", "Mid-size industrial-tech firm."),
    ("2026-04-22", "Bramwell Media Group", "VP Product", "rejected", "rejected", 48, "Tier 4 — Long shot",
     29, 9, 4, 6, 10, ["competition", "comp"], None, "LinkedIn", "Large, famous media brand — very high competition."),
    ("2026-04-25", "TidePool Labs", "Head of Product", "rejected", "rejected", 77, "Tier 2 — Strong callback odds",
     39, 13, 15, 10, 10, [], "£118k-132k OTE", "Referral", "Small private labs startup, narrow specialist role."),
    ("2026-04-29", "Granite Peak Software", "Director of Product", "rejected", "rejected", 63, "Tier 3 — Solid, worth applying",
     34, 11, 10, 8, 10, [], None, "LinkedIn", "Mid-size, moderately known enterprise software vendor."),
    ("2026-05-02", "Ovalcrest Insurance", "VP Product Management", "rejected", "rejected", 52, "Tier 4 — Long shot",
     30, 10, 6, 6, 10, ["competition", "comp"], None, "Company site", "Large regulated insurer, broad pool."),
    ("2026-05-06", "Millrace Systems", "Head of Product", "rejected", "rejected", 79, "Tier 2 — Strong callback odds",
     40, 13, 16, 10, 10, [], "£112k-128k OTE", "Referral", "Small private systems company, strong fit."),
    ("2026-05-09", "Copperfield Logistics", "Senior Director Product", "rejected", "rejected", 65, "Tier 3 — Solid, worth applying",
     35, 12, 10, 8, 10, [], None, "LinkedIn", "Mid-size logistics tech firm."),
    ("2026-05-13", "Vantage Point Telecom", "VP Product", "rejected", "rejected", 50, "Tier 4 — Long shot",
     30, 9, 5, 6, 10, ["competition", "comp"], None, "LinkedIn", "Large, recognisable telecom operator."),
    ("2026-05-16", "Hollow Creek Devices", "Head of Product", "rejected", "rejected", 72, "Tier 2 — Strong callback odds",
     37, 12, 13, 10, 10, [], "£108k-122k OTE", "Company site", "Small private hardware/devices startup."),
    ("2026-05-20", "Marlow Continental", "Director of Product", "rejected", "rejected", 59, "Tier 3 — Solid, worth applying",
     33, 11, 7, 8, 10, ["competition"], None, "LinkedIn", "Large multinational, broad applicant pool."),
    ("2026-05-24", "Palisade Robotics", "VP Product", "rejected", "rejected", 42, "Tier 4 — Long shot",
     36, 13, 12, 10, 3, [], "£140k-155k OTE", "LinkedIn",
     "Strong fit on paper, but the role required confirmed US work authorisation the candidate does not hold, and was onsite in Austin with no relocation support — a real, confirmed blocker, not a soft preference."),
    ("2026-05-11", "Redshank Payments", "Director of Product", "withdrawn", "withdrawn", 69, "Tier 3 — Solid, worth applying",
     36, 12, 11, 10, 10, [], "£95k-105k base (below floor once confirmed)", "LinkedIn",
     "Withdrew after confirmed comp band came in below floor."),
]

# Fully fleshed briefing-pack applications (interviewing / offer)
BRIEFING_APPS = [
    dict(date="2026-05-18", company="Alderwood Data", role="Head of Product", status="interviewing", outcome="interview",
         score=84, tier="Tier 1 — Exceptional callback odds", jd_fit=41, seniority=14, competition=17, comp=10, blockers=10,
         estimated_fields=[], comp_band="£125k-140k OTE", source="Referral",
         company_size="~40 employees", funding="Seed/Series A, privately held", competition_tier="low",
         why="Direct fit on a narrow, specialist product mandate; referral likely helped surface the application quickly.",
         watch="Small team — later interview stages likely to probe hands-on delivery experience, not just strategy.",
         stages=["Stage 1 — 2026-05-25 — Recruiter screen — positive, moved forward",
                 "Stage 2 — 2026-06-04 — Hiring manager interview — positive, moved to panel"]),
    dict(date="2026-05-22", company="Pemberton Health Tech", role="VP Product", status="interviewing", outcome="interview",
         score=76, tier="Tier 2 — Strong callback odds", jd_fit=36, seniority=13, competition=11, comp=8, blockers=10,
         estimated_fields=["comp"], comp_band=None, source="LinkedIn",
         company_size="~600 employees", funding="Series C", competition_tier="moderate",
         why="Solid domain adjacency; moderate competition given the company's mid-market profile.",
         watch="Comp band still unconfirmed — worth raising directly before a later stage.",
         stages=["Stage 1 — 2026-05-29 — Recruiter screen — positive, moved forward"]),
    dict(date="2026-05-26", company="Briarcliff AI", role="Head of Product", status="interviewing", outcome="interview",
         score=82, tier="Tier 1 — Exceptional callback odds", jd_fit=40, seniority=14, competition=16, comp=8, blockers=10,
         estimated_fields=["comp"], comp_band=None, source="Company site",
         company_size="~25 employees", funding="Series A", competition_tier="low",
         why="Small, narrow-mandate startup role; strong overlap with prior product-led growth experience.",
         watch="Fast-moving process — later stages may compress quickly; keep availability flexible.",
         stages=["Stage 1 — 2026-06-01 — Founder screen — positive, moved forward",
                 "Stage 2 — 2026-06-08 — Product deep-dive — positive, moved to final round"]),
    dict(date="2026-04-30", company="Wrenfield Software", role="Head of Product", status="offer", outcome="offer",
         score=88, tier="Tier 1 — Exceptional callback odds", jd_fit=42, seniority=15, competition=17, comp=10, blockers=10,
         estimated_fields=[], comp_band="£130k-145k OTE, confirmed above floor", source="Referral",
         company_size="~60 employees", funding="Series B", competition_tier="low",
         why="Very close mandate match plus a warm referral; comp confirmed early and above floor.",
         watch="Decision deadline is tight relative to other processes still in flight.",
         stages=["Stage 1 — 2026-05-06 — Recruiter screen — positive, moved forward",
                 "Stage 2 — 2026-05-14 — Hiring manager interview — positive, moved forward",
                 "Stage 3 — 2026-05-21 — Final panel — positive",
                 "Offer — 2026-05-27 — Extended, under review"]),
    dict(date="2026-05-04", company="Stonebridge Analytics", role="VP Product", status="offer", outcome="offer",
         score=80, tier="Tier 2 — Strong callback odds", jd_fit=38, seniority=13, competition=13, comp=10, blockers=10,
         estimated_fields=[], comp_band="£122k-135k OTE, confirmed above floor", source="LinkedIn",
         company_size="~300 employees", funding="Series C", competition_tier="moderate",
         why="Strong domain fit; moderate competition given company's mid-market scale.",
         watch="Slightly lower comp than Wrenfield — worth comparing full package, not just base, before deciding.",
         stages=["Stage 1 — 2026-05-11 — Recruiter screen — positive, moved forward",
                 "Stage 2 — 2026-05-19 — Hiring manager interview — positive, moved forward",
                 "Stage 3 — 2026-05-28 — Final panel — positive",
                 "Offer — 2026-06-02 — Extended, under review"]),
]


def slugify(name):
    return "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")
    # collapse repeated dashes


def write_simple(app):
    (date, company, role, status, outcome, score, tier, jd_fit, seniority, competition, comp, blockers,
     estimated, comp_band, source, note) = app
    slug = slugify(company)
    fname = f"{date}-{slug}-{slugify(role)}.md"
    est = json.dumps(estimated)
    comp_band_yaml = f'"{comp_band}"' if comp_band else "null"
    fm = f"""---
company: "{company}"
role: "{role}"
date_applied: {date}
status: {status}
source: "{source}"

score:
  value: {score}
  tier: "{tier}"
  locked: {"true" if outcome else "false"}
  breakdown:
    jd_fit: {jd_fit}
    seniority: {seniority}
    competition: {competition}
    comp: {comp}
    blockers: {blockers}
  estimated_fields: {est}

outcome: {outcome if outcome else "null"}
outcome_date: {date if outcome else "null"}

comp_band: {comp_band_yaml}
---

## JD summary
{role} at {company}. {note}

## Score rationale
- JD fit: {jd_fit}/45
- Seniority alignment: {seniority}/15
- Competition estimate: {competition}/20
- Comp alignment: {comp}/10
- Blockers: {blockers}/10

## Caveats
{"Competition and/or comp estimated — see estimated_fields above." if estimated else "No estimated fields; all components scored against confirmed information."}
"""
    with open(os.path.join(APPS_DIR, fname), "w", encoding="utf-8") as f:
        f.write(fm)


def write_briefing(app):
    slug = slugify(app["company"])
    fname = f"{app['date']}-{slug}-{slugify(app['role'])}.md"
    est = json.dumps(app["estimated_fields"])
    comp_band_yaml = f'"{app["comp_band"]}"' if app["comp_band"] else "null"
    stages_md = "\n".join(f"- {s}" for s in app["stages"])
    fm = f"""---
company: "{app['company']}"
role: "{app['role']}"
date_applied: {app['date']}
status: {app['status']}
source: "{app['source']}"

score:
  value: {app['score']}
  tier: "{app['tier']}"
  locked: true
  breakdown:
    jd_fit: {app['jd_fit']}
    seniority: {app['seniority']}
    competition: {app['competition']}
    comp: {app['comp']}
    blockers: {app['blockers']}
  estimated_fields: {est}

outcome: {app['outcome']}
outcome_date: {app['date']}

comp_band: {comp_band_yaml}
---

## JD summary
{app['role']} at {app['company']}.

## Score rationale
- JD fit: {app['jd_fit']}/45
- Seniority alignment: {app['seniority']}/15
- Competition estimate: {app['competition']}/20
- Comp alignment: {app['comp']}/10
- Blockers: {app['blockers']}/10

## Caveats
{"Comp estimated pending confirmation." if "comp" in app["estimated_fields"] else "No estimated fields."}

## Briefing pack

### Company facts
{app['company']} — {app['company_size']}, {app['funding']}. See `examples/companies/{slug}.json` for the cached source.

### Comp
{app['comp_band'] if app['comp_band'] else "Not yet confirmed."}

### Why it progressed
{app['why']}

### Watch-outs
{app['watch']}

### Interview stage log
{stages_md}
"""
    with open(os.path.join(APPS_DIR, fname), "w", encoding="utf-8") as f:
        f.write(fm)

    company_json = {
        "company": app["company"],
        "verified_at": app["date"],
        "size_estimate": app["company_size"],
        "funding_stage": app["funding"],
        "profile": f"{app['funding']}, {app['competition_tier']} competition profile",
        "competition_tier": app["competition_tier"],
        "confidence": "confirmed",
        "sources": ["company careers page", "public funding announcement"]
    }
    with open(os.path.join(COMPANIES_DIR, f"{slug}.json"), "w", encoding="utf-8") as f:
        json.dump(company_json, f, indent=2)


for app in APPLICATIONS:
    write_simple(app)

for app in BRIEFING_APPS:
    write_briefing(app)

print(f"Wrote {len(APPLICATIONS)} simple applications and {len(BRIEFING_APPS)} briefing-pack applications.")
print(f"Total: {len(APPLICATIONS) + len(BRIEFING_APPS)} applications.")
