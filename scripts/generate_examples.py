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
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _status import should_lock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS_DIR = os.path.join(ROOT, "examples", "applications")
COMPANIES_DIR = os.path.join(ROOT, "examples", "companies")
os.makedirs(APPS_DIR, exist_ok=True)
os.makedirs(COMPANIES_DIR, exist_ok=True)

# (date, company, role, status, score, tier, jd_fit, seniority, competition, comp, blockers,
#  estimated_fields, comp_band, source, note)
APPLICATIONS = [
    ("2026-05-28", "Meridian Cloud Systems", "Director of Product", "applied", 52, "Tier 4 — Long shot",
     30, 12, 4, 6, 10, ["competition"], "£95k-110k base + bonus (unconfirmed split)", "LinkedIn",
     "Large, well-known public cloud platform — huge applicant pool expected."),
    ("2026-06-02", "Fernbank Analytics", "Head of Product", "applied", 81, "Tier 2 — Strong callback odds",
     40, 13, 16, 10, 10, [], "£120k-135k OTE", "Referral",
     "Small, private data-analytics startup, narrow role, strong direct fit."),
    ("2026-06-05", "Coastal Ledger", "Senior Director, Product", "applied", 68, "Tier 3 — Solid, worth applying",
     35, 12, 11, 10, 10, [], None, "Company site",
     "Mid-size fintech, moderately well-known in its niche."),
    ("2026-06-09", "Union Freight Group", "VP Product", "applied", 45, "Tier 4 — Long shot",
     28, 8, 5, 4, 10, ["competition", "comp"], None, "LinkedIn",
     "Large logistics incumbent, broad VP-level role draws a wide pool."),
    ("2026-06-11", "Harrowgate Systems", "Head of Product", "scored", 73, "Tier 2 — Strong callback odds",
     37, 12, 14, 10, 10, [], "£115k-128k OTE", "LinkedIn",
     "Scored, not yet applied — still deciding whether to prioritise this over other open processes."),
    ("2026-06-13", "Vireo Networks", "Director of Product", "scored", 44, "Tier 4 — Long shot",
     29, 9, 4, 6, 10, ["competition"], None, "LinkedIn",
     "Scored, not applied — large, well-known network infrastructure company; score alone made this a low priority."),
    ("2026-06-14", "Elmscroft Data", "Head of Product", "scored", 86, "Tier 1 — Exceptional callback odds",
     42, 14, 17, 10, 10, [], "£125k-138k OTE", "Referral",
     "Scored today — strong match, referral in hand. Drafting the application next, not yet submitted."),
    ("2026-04-02", "Northwind Retail Technologies", "Head of Product, Platform", "rejected", 58, "Tier 3 — Solid, worth applying",
     32, 12, 6, 8, 10, ["competition"], "£110k-125k OTE", "LinkedIn", "Large, recognisable retail-tech brand."),
    ("2026-04-05", "Ashgrove Financial", "Director of Product Strategy", "rejected", 61, "Tier 3 — Solid, worth applying",
     33, 11, 9, 8, 10, [], "£100k-115k base", "Company site", "Large regulated financial services firm."),
    ("2026-04-08", "Larkspur Health", "VP Product", "rejected", 70, "Tier 3 — Solid, worth applying",
     36, 13, 13, 8, 10, [], None, "Referral", "Mid-size health-tech, moderately known."),
    ("2026-04-11", "Kettlebrook Robotics", "Head of Product", "rejected", 74, "Tier 2 — Strong callback odds",
     38, 12, 14, 10, 10, [], "£115k-130k OTE", "LinkedIn",
     "Small robotics startup — good fit on paper, rejected anyway; not every high score converts."),
    ("2026-04-15", "Solari Energy Corp", "Senior Director Product", "rejected", 55, "Tier 4 — Long shot",
     31, 10, 6, 8, 10, ["competition"], None, "LinkedIn", "Large, well-funded energy technology company."),
    ("2026-04-18", "Ferrous Metals Digital", "Head of Product", "rejected", 66, "Tier 3 — Solid, worth applying",
     34, 12, 12, 8, 10, [], "£105k-120k base", "Company site", "Mid-size industrial-tech firm."),
    ("2026-04-22", "Bramwell Media Group", "VP Product", "rejected", 48, "Tier 4 — Long shot",
     29, 9, 4, 6, 10, ["competition", "comp"], None, "LinkedIn", "Large, famous media brand — very high competition."),
    ("2026-04-25", "TidePool Labs", "Head of Product", "rejected", 77, "Tier 2 — Strong callback odds",
     39, 13, 15, 10, 10, [], "£118k-132k OTE", "Referral", "Small private labs startup, narrow specialist role."),
    ("2026-04-29", "Granite Peak Software", "Director of Product", "rejected", 63, "Tier 3 — Solid, worth applying",
     34, 11, 10, 8, 10, [], None, "LinkedIn", "Mid-size, moderately known enterprise software vendor."),
    ("2026-05-02", "Ovalcrest Insurance", "VP Product Management", "rejected", 52, "Tier 4 — Long shot",
     30, 10, 6, 6, 10, ["competition", "comp"], None, "Company site", "Large regulated insurer, broad pool."),
    ("2026-05-06", "Millrace Systems", "Head of Product", "rejected", 79, "Tier 2 — Strong callback odds",
     40, 13, 16, 10, 10, [], "£112k-128k OTE", "Referral", "Small private systems company, strong fit."),
    ("2026-05-09", "Copperfield Logistics", "Senior Director Product", "rejected", 65, "Tier 3 — Solid, worth applying",
     35, 12, 10, 8, 10, [], None, "LinkedIn", "Mid-size logistics tech firm."),
    ("2026-05-13", "Vantage Point Telecom", "VP Product", "rejected", 50, "Tier 4 — Long shot",
     30, 9, 5, 6, 10, ["competition", "comp"], None, "LinkedIn", "Large, recognisable telecom operator."),
    ("2026-05-16", "Hollow Creek Devices", "Head of Product", "rejected", 72, "Tier 2 — Strong callback odds",
     37, 12, 13, 10, 10, [], "£108k-122k OTE", "Company site", "Small private hardware/devices startup."),
    ("2026-05-20", "Marlow Continental", "Director of Product", "rejected", 59, "Tier 3 — Solid, worth applying",
     33, 11, 7, 8, 10, ["competition"], None, "LinkedIn", "Large multinational, broad applicant pool."),
    ("2026-05-24", "Palisade Robotics", "VP Product", "rejected", 42, "Tier 4 — Long shot",
     36, 13, 12, 10, 3, [], "£140k-155k OTE", "LinkedIn",
     "Strong fit on paper, but the role required confirmed US work authorisation the candidate does not hold, and was onsite in Austin with no relocation support — a real, confirmed blocker, not a soft preference."),
    ("2026-05-11", "Redshank Payments", "Director of Product", "withdrawn", 69, "Tier 3 — Solid, worth applying",
     36, 12, 11, 10, 10, [], "£95k-105k base (below floor once confirmed)", "LinkedIn",
     "Withdrew after confirmed comp band came in below floor."),
    ("2026-05-30", "Oakridge Ventures", "Director of Product", "assumed_rejected", 64, "Tier 3 — Solid, worth applying",
     34, 11, 10, 9, 10, [], "£105k-118k OTE", "LinkedIn",
     "Applied and heard nothing since — no rejection, no further contact. Marked assumed_rejected after the configured silence window (see config/weights.json), not a confirmed rejection."),
    ("2026-06-01", "Pinehollow Systems", "Head of Product", "role_closed", 71, "Tier 2 — Strong callback odds",
     37, 13, 13, 8, 10, [], "£110k-125k OTE", "Company site",
     "Listing disappeared from the careers page three weeks after applying, no response received — the recruiter later confirmed the role was pulled internally, not filled. Not a judgement on the application."),
    ("2026-06-10", "Cross Timber Logistics", "VP Product", "awaiting_recruiter", 67, "Tier 3 — Solid, worth applying",
     35, 12, 10, 10, 10, [], None, "LinkedIn",
     "Applied and had a positive informal chat with the hiring manager, but the process is paused pending a right-to-work eligibility check on the recruiter's side before it can formally proceed."),
]

# Fully fleshed briefing-pack applications — interviewing / offer / and the
# two "reached interview, then didn't convert" statuses this needs a real
# example of (rejected_after_interview, withdrawn_after_interview).
#
# Alderwood, Wrenfield get full depth throughout. Pemberton deliberately
# keeps some sections as genuine "Currently unknown" placeholders — the
# skill should default to real synthesis, not placeholders, but this repo's
# examples should prove the placeholder path actually works too, not just
# claim it does. Briarcliff exercises an interviewer profile with no
# optional callouts filled in.
BRIEFING_APPS = [
    dict(
        date="2026-05-18", status_date="2026-06-04",
        company="Alderwood Data", role="Head of Product", status="interviewing",
        score=84, tier="Tier 1 — Exceptional callback odds", jd_fit=41, seniority=14, competition=17, comp=10, blockers=10,
        estimated_fields=[], comp_band="£125k-140k OTE", source="Referral",
        company_size="~40 employees", funding="Seed/Series A, privately held", competition_tier="low",
        why="Direct fit on a narrow, specialist product mandate; referral likely helped surface the application quickly.",
        usps=[
            {"title": "Direct data-platform PM experience",
             "body": "Owned the roadmap for a usage-based analytics product at a prior 60-person startup, taking it from 12 to 40 paying accounts in nine months — close to Alderwood's own stage and product shape."},
            {"title": "Comfortable operating without a large team",
             "body": "Ran product, a chunk of go-to-market, and customer research solo for five months before a second PM was hired — the kind of stretch this role is asking for."},
            {"title": "Track record shipping to specialist buyers",
             "body": "Built onboarding flows for data engineers, not consumer users — Alderwood's buyer persona (data/analytics leads) is a similarly technical, low-tolerance-for-fluff audience."},
        ],
        profiles=[
            {"name": "Priya Nandan", "title": "Head of Product",
             "background": "Joined Alderwood roughly 18 months ago from a mid-size data-infrastructure company; previously an IC engineer before moving into product. [estimated — public bio is thin]",
             "assessing": "Whether the candidate can operate with real autonomy on a small team, not just describe a strategy.",
             "play_it": "Lead with specific examples of decisions made without a large team backing you up, not frameworks."},
            {"name": "Marcus Webb", "title": "Co-founder & CEO",
             "background": "Second-time founder; previously built and sold a smaller developer-tools company. [estimated]",
             "assessing": "Product instinct, and whether the candidate will push back on him rather than just agree.",
             "play_it": "Bring one genuine, prepared disagreement or pushback on the product direction — he reportedly values candidates who challenge him respectfully."},
        ],
        prep_qa=[
            {"q": "Walk me through a product decision you made that you'd now do differently.",
             "a": "The analytics onboarding flow at [prior company] launched with too many configuration steps up front — usage data showed a third of new accounts stalled before their first real report. Simplified to a single default view with configuration deferred until after first value, which measurably improved week-one activation."},
            {"q": "How would you prioritise between a feature a big prospect is asking for and your own roadmap conviction?",
             "a": "Ask whether the request generalises — if three or more other accounts would plausibly want it too, it's probably signal, not a one-off. If it's genuinely bespoke to one prospect, the answer is usually 'not on the roadmap, happy to discuss as a paid customisation' rather than letting one deal reshape the product."},
            {"q": "You'd be one of two PMs here. How do you divide scope with a peer without stepping on each other?",
             "a": "Split by customer segment or product surface, not by task type — task-based splits create constant hand-offs and ambiguity about who owns a decision. A clear owner per surface, with a standing weekly sync to flag anything that crosses the boundary."},
            {"q": "What's a metric you'd push back on if leadership over-indexed on it?",
             "a": "Raw signup count without an activation gate — easy to inflate with top-of-funnel spend and tells you almost nothing about whether the product is actually landing. Would push for a paired activation-rate metric alongside any growth target."},
        ],
        questions_to_ask=[
            "How is the roadmap actually prioritised day to day — a formal process, or Priya and Marcus's judgement call?",
            "What's the biggest thing that's broken as you've scaled from roughly 12 to 40 employees?",
            "What would make the next six months a clear success for this hire specifically?",
        ],
        watch_bullets=[
            {"title": "Small team", "body": "Later interview stages likely to probe hands-on delivery experience, not just strategy."},
            {"title": "Founder-level scrutiny", "body": "Marcus reportedly likes being pushed back on — over-agreeing may read as weak rather than diplomatic."},
        ],
        notes=[{"heading": "Logistics", "body": "Role is London-hybrid, two days/week in office — confirm this is workable before the panel round, not after an offer."}],
        next_interview_date="2026-06-19",
        stages=["Stage 1 — 2026-05-25 — Recruiter screen — positive, moved forward",
                "Stage 2 — 2026-06-04 — Hiring manager interview — positive, moved to panel"],
    ),
    dict(
        date="2026-05-22", status_date="2026-05-29",
        company="Pemberton Health Tech", role="VP Product", status="interviewing",
        score=76, tier="Tier 2 — Strong callback odds", jd_fit=36, seniority=13, competition=11, comp=8, blockers=10,
        estimated_fields=["comp"], comp_band=None, source="LinkedIn",
        company_size="~600 employees", funding="Series C", competition_tier="moderate",
        why="Solid domain adjacency; moderate competition given the company's mid-market profile.",
        usps=[
            {"title": "Regulated-sector product experience",
             "body": "Shipped features inside a healthcare-adjacent compliance framework at a prior role — Pemberton's health-tech context carries similar constraints."},
            {"title": "VP-level scope already evidenced",
             "body": "Managed a small product team, not just an individual-contributor role, at the current seniority level."},
        ],
        profiles=[
            {"name": "Currently unknown", "title": "share an interviewer's name if you'd like a profile added",
             "background": "No interviewer named yet beyond the Stage 1 recruiter screen.",
             "assessing": "", "play_it": ""},
        ],
        prep_qa=[
            {"q": "How would you approach roadmap prioritisation inside a compliance-heavy product?",
             "a": "Treat compliance requirements as a fixed floor, not a competing priority — they get built regardless of ROI debate, and the actual prioritisation conversation happens on everything above that floor."},
            {"q": "What's your experience managing a small product team, not just being an IC?",
             "a": "Managed two PMs at [prior company] — the main shift was moving from owning decisions to owning the quality of other people's decisions, which meant more time in 1:1 review of their rationale and less time writing specs myself."},
            {"q": "Health-tech buyers are often risk-averse. How does that change how you'd position a new feature?",
             "a": "Lead with what doesn't change (existing workflows, compliance posture) before what does — risk-averse buyers respond to evidence that the new thing doesn't destabilise what already works, not just to the upside case."},
        ],
        questions_to_ask=[
            "What does the compliance/product relationship actually look like day to day — a blocking gate, or an embedded partner?",
            "What's driving the VP Product hire specifically now, versus six months ago?",
        ],
        watch="Comp band still unconfirmed — worth raising directly before a later stage.",
        notes="Currently unknown — nothing situational to flag yet; will add if something comes up in later stages.",
        next_interview_date=None,
        stages=["Stage 1 — 2026-05-29 — Recruiter screen — positive, moved forward"],
    ),
    dict(
        date="2026-05-26", status_date="2026-06-08",
        company="Briarcliff AI", role="Head of Product", status="interviewing",
        score=82, tier="Tier 1 — Exceptional callback odds", jd_fit=40, seniority=14, competition=16, comp=8, blockers=10,
        estimated_fields=["comp"], comp_band=None, source="Company site",
        company_size="~25 employees", funding="Series A", competition_tier="low",
        why="Small, narrow-mandate startup role; strong overlap with prior product-led growth experience.",
        usps=[
            {"title": "Product-led growth track record",
             "body": "Drove self-serve activation improvements that reduced time-to-first-value from 9 minutes to under 2 at a prior PLG product — directly relevant to Briarcliff's stated self-serve motion."},
            {"title": "Comfortable in a genuinely early-stage environment",
             "body": "Joined a 15-person company as first PM hire previously — knows what building process from nothing actually requires, not just how to operate inside an existing one."},
        ],
        profiles=[
            {"name": "Elena Torres", "title": "Founder",
             "background": "Ran the founder screen. Previously a senior engineer at a larger AI infrastructure company before starting Briarcliff. [estimated — limited public information available]",
             "assessing": "", "play_it": ""},
        ],
        prep_qa=[
            {"q": "What would you do in the first 30 days here?",
             "a": "Spend the first two weeks almost entirely in user conversations and usage data before proposing any roadmap change — at 25 people, the risk isn't lack of ideas, it's building the wrong thing fast."},
            {"q": "How do you think about product-market fit signal at this stage versus a later one?",
             "a": "Retention curves that flatten, not vanity signups — at this stage, a small number of users who won't stop using it is a stronger signal than a larger number who tried it once."},
            {"q": "The process has moved quickly. What questions haven't you had a chance to ask yet that you'd want answered before a final round?",
             "a": "What's the realistic runway, and is this hire funded by the current round or contingent on the next one — directly affects how much risk this role represents."},
        ],
        questions_to_ask=[
            "What's the split today between self-serve and any assisted/sales-led motion, and is that expected to shift?",
            "What does Elena see as the single biggest product risk over the next two quarters?",
        ],
        watch="Fast-moving process — later stages may compress quickly; keep availability flexible.",
        notes=[{"heading": None, "body": "Process has moved unusually fast — screen to panel in one week. Worth asking directly whether that pace reflects urgency to fill the role or just a lean, fast-moving team; the answer changes how much leverage exists in later comp conversations."}],
        next_interview_date="2026-06-16",
        stages=["Stage 1 — 2026-06-01 — Founder screen — positive, moved forward",
                "Stage 2 — 2026-06-08 — Product deep-dive — positive, moved to final round"],
    ),
    dict(
        date="2026-04-30", status_date="2026-05-27",
        company="Wrenfield Software", role="Head of Product", status="offer",
        score=88, tier="Tier 1 — Exceptional callback odds", jd_fit=42, seniority=15, competition=17, comp=10, blockers=10,
        estimated_fields=[], comp_band="£130k-145k OTE, confirmed above floor", source="Referral",
        company_size="~60 employees", funding="Series B", competition_tier="low",
        why="Very close mandate match plus a warm referral; comp confirmed early and above floor.",
        usps=[
            {"title": "Direct mandate match",
             "body": "Role scope mirrors a product owned end-to-end at a similarly-staged prior company — not an adjacent-domain stretch."},
            {"title": "Warm referral already vouching for delivery track record",
             "body": "Referral came from a former colleague now at Wrenfield who worked directly with the candidate on a prior shipped product."},
        ],
        profiles=[
            {"name": "Dev Ahluwalia", "title": "VP Product (line manager)",
             "background": "Ran the Stage 2 and Stage 3 rounds; joined Wrenfield at Series A after a scaling-stage role at a larger SaaS company. [estimated]",
             "assessing": "Whether the candidate can own the full roadmap independently at this stage, not just execute a handed-down plan.",
             "play_it": "Frame answers around ownership and judgement calls made solo, not process followed."},
        ],
        prep_qa=[
            {"q": "What would make you turn down an otherwise-solid offer?",
             "a": "A comp band confirmed below floor, or a mandate that turns out narrower in practice than described in the process — neither applies here, comp is confirmed above floor."},
            {"q": "How do you evaluate a smaller company's risk profile before accepting?",
             "a": "Runway relative to current burn, and whether the role is backed by the current funding round or contingent on the next one — worth confirming explicitly during the offer conversation, not assuming."},
        ],
        questions_to_ask=[
            "Is there flexibility on the start date given other processes still in flight?",
            "What does the first-90-days success definition look like from Dev's side specifically?",
        ],
        watch_bullets=[
            {"title": "Decision deadline is tight", "body": "Relative to other processes still in flight — worth being direct about needing a short extension if one is required."},
        ],
        notes=[{"heading": "Negotiation notes", "body": "Comp already confirmed above floor, so negotiation leverage is mainly about start date and any signing considerations, not base/OTE. Worth comparing total package (not just base) against Stonebridge before deciding between the two."}],
        next_interview_date=None,
        stages=["Stage 1 — 2026-05-06 — Recruiter screen — positive, moved forward",
                "Stage 2 — 2026-05-14 — Hiring manager interview — positive, moved forward",
                "Stage 3 — 2026-05-21 — Final panel — positive",
                "Offer — 2026-05-27 — Extended, under review"],
    ),
    dict(
        date="2026-05-04", status_date="2026-06-02",
        company="Stonebridge Analytics", role="VP Product", status="offer",
        score=80, tier="Tier 2 — Strong callback odds", jd_fit=38, seniority=13, competition=13, comp=10, blockers=10,
        estimated_fields=[], comp_band="£122k-135k OTE, confirmed above floor", source="LinkedIn",
        company_size="~300 employees", funding="Series C", competition_tier="moderate",
        why="Strong domain fit; moderate competition given company's mid-market scale.",
        usps=[
            {"title": "Mid-market SaaS scaling experience",
             "body": "Operated at a similar company scale (a few hundred employees) previously — familiar with the specific coordination overhead at this size, distinct from either startup or enterprise."},
        ],
        profiles=[
            {"name": "Farah Idris", "title": "Chief Product Officer",
             "background": "Final-round interviewer; previously VP Product at a larger analytics company before joining Stonebridge as CPO. [estimated]",
             "assessing": "Strategic thinking at VP level, and cross-functional credibility with Sales and Engineering leadership.",
             "play_it": "Bring examples of cross-functional alignment, not just product execution."},
        ],
        prep_qa=[
            {"q": "How would you balance Wrenfield-style ownership versus a larger organisation's coordination overhead?",
             "a": "Larger orgs need more explicit alignment mechanisms (documented decisions, wider stakeholder review) — the skill is knowing when to invoke that process versus when it's genuinely a unilateral call."},
        ],
        questions_to_ask=[
            "What's the biggest source of friction between Product and Sales today?",
        ],
        watch="Slightly lower comp than Wrenfield — worth comparing full package, not just base, before deciding.",
        notes=[{"heading": None, "body": "Second live offer alongside Wrenfield — decision should weigh total package and role scope, not just base comp, before the Wrenfield deadline forces the choice."}],
        next_interview_date=None,
        stages=["Stage 1 — 2026-05-11 — Recruiter screen — positive, moved forward",
                "Stage 2 — 2026-05-19 — Hiring manager interview — positive, moved forward",
                "Stage 3 — 2026-05-28 — Final panel — positive",
                "Offer — 2026-06-02 — Extended, under review"],
    ),
    dict(
        date="2026-05-15", status_date="2026-06-12",
        company="Fenwick Data Systems", role="Head of Product", status="rejected_after_interview",
        score=75, tier="Tier 2 — Strong callback odds", jd_fit=38, seniority=13, competition=14, comp=10, blockers=10,
        estimated_fields=[], comp_band="£118k-130k OTE", source="LinkedIn",
        company_size="~120 employees", funding="Series B", competition_tier="moderate",
        why="Progressed through two positive interview stages; ultimately lost out to an internal candidate at the final round — the scoring rubric correctly predicted engagement (jd_fit, seniority, competition all landed within range) even though the outcome wasn't a hire. A useful real example of why rejected_after_interview is tracked separately from a flat rejection.",
        usps=[
            {"title": "Direct domain overlap", "body": "Prior role covered an almost identical product category, which is likely why the process moved quickly through the first two stages."},
            {"title": "Demonstrated delivery under ambiguity", "body": "Shipped a v1 product with an incomplete spec at a prior company, which came up directly in the Stage 2 conversation."},
        ],
        profiles=[
            {"name": "Owen Bright", "title": "Head of Engineering",
             "background": "Ran the Stage 2 technical/collaboration interview. [estimated]",
             "assessing": "Whether the candidate would be an easy, low-friction partner for engineering leadership day to day.",
             "play_it": ""},
        ],
        prep_qa=[
            {"q": "How do you handle disagreement with an engineering lead over scope?",
             "a": "Separate the technical disagreement from the relationship — push on the technical point with evidence, but explicitly signal that disagreement on scope isn't a verdict on the working relationship."},
            {"q": "What would you want to know in the first week here that you wouldn't get from the JD?",
             "a": "Whatever's currently the biggest unresolved internal debate about product direction — that's usually the real job, not what's written in the posting."},
        ],
        questions_to_ask=[
            "Is there an internal candidate also being considered for this role?",
            "What does success in the first quarter look like specifically?",
        ],
        watch_bullets=[
            {"title": "Internal-candidate risk wasn't asked about directly", "body": "Worth asking early and directly in future processes whether an internal candidate exists — a structural disadvantage no interview performance overcomes, and better to know going in."},
        ],
        notes=[{"heading": "Why it didn't progress", "body": "Recruiter confirmed after the final round that an internal candidate with existing platform context was preferred. Not a reflection of interview performance — both prior stages were explicitly described as positive. The scoring rubric's prediction (this would land an interview) was validated; the eventual outcome was decided by a factor the scoring model doesn't and can't account for."}],
        next_interview_date=None,
        stages=["Stage 1 — 2026-05-22 — Recruiter screen — positive, moved forward",
                "Stage 2 — 2026-06-02 — Engineering collaboration interview — positive, moved to final round",
                "Stage 3 — 2026-06-12 — Final round — rejected, internal candidate preferred"],
    ),
    dict(
        date="2026-05-19", status_date="2026-06-10",
        company="Silverlake Systems", role="VP Product", status="withdrawn_after_interview",
        score=71, tier="Tier 3 — Solid, worth applying", jd_fit=36, seniority=13, competition=12, comp=8, blockers=10,
        estimated_fields=["comp"], comp_band=None, source="Referral",
        company_size="~180 employees", funding="Series B", competition_tier="moderate",
        why="Withdrew after Stage 2 once the comp band was finally confirmed — well below floor, despite an earlier verbal indication from the recruiter that it would be competitive.",
        usps=[
            {"title": "Referral-backed credibility", "body": "Referral from a current Silverlake employee helped the process move quickly through Stage 1."},
        ],
        profiles=[
            {"name": "Currently unknown", "title": "no further interviewer met before withdrawing",
             "background": "Stage 2 was with the hiring manager, but no name or background was captured before the process ended.",
             "assessing": "", "play_it": ""},
        ],
        prep_qa=[
            {"q": "How would you handle a comp mismatch discovered mid-process?",
             "a": "Raise it directly and immediately rather than continuing through further stages on the assumption it might improve — continuing signals the floor is negotiable when it isn't, and wastes both sides' time."},
        ],
        questions_to_ask=[
            "What's the actual confirmed comp band, in writing, before the next stage?",
        ],
        watch="Get the comp band confirmed in writing before Stage 1, not verbally after Stage 2 — this is the second process this floor issue has surfaced late in.",
        notes=[{"heading": "Why withdrew", "body": "The recruiter's Stage 1 verbal indication ('should be competitive') didn't match the actual confirmed band once pressed for specifics after Stage 2 — around 15% below floor. Withdrew rather than continue a process that couldn't clear the floor regardless of interview performance."}],
        next_interview_date=None,
        stages=["Stage 1 — 2026-05-26 — Recruiter screen — positive, moved forward",
                "Stage 2 — 2026-06-10 — Hiring manager interview — positive, but comp band confirmed below floor immediately after; withdrew same week"],
    ),
]


def slugify(name):
    return "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")
    # collapse repeated dashes


def write_simple(app):
    (date, company, role, status, score, tier, jd_fit, seniority, competition, comp, blockers,
     estimated, comp_band, source, note) = app
    slug = slugify(company)
    fname = f"{date}-{slug}-{slugify(role)}.md"
    est = json.dumps(estimated)
    comp_band_yaml = f'"{comp_band}"' if comp_band else "null"
    date_applied = "null" if status == "scored" else date
    locked = "true" if should_lock(status) else "false"
    fm = f"""---
company: "{company}"
role: "{role}"
date_scored: {date}
date_applied: {date_applied}
status: {status}
status_date: {date}
source: "{source}"

score:
  value: {score}
  tier: "{tier}"
  locked: {locked}
  breakdown:
    jd_fit: {jd_fit}
    seniority: {seniority}
    competition: {competition}
    comp: {comp}
    blockers: {blockers}
  estimated_fields: {est}

next_interview_date: null

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


def usps_md(items):
    return "\n".join(f"- **{i['title']}.** {i['body']}" for i in items)


def profiles_md(profiles):
    blocks = []
    for p in profiles:
        title_part = f" — {p['title']}" if p.get("title") else ""
        lines = [f"#### {p['name']}{title_part}", "", p.get("background", "").strip()]
        callouts = []
        if p.get("assessing"):
            callouts.append(f"**What they're assessing:** {p['assessing']}")
        if p.get("play_it"):
            callouts.append(f"**How to play it:** {p['play_it']}")
        if callouts:
            lines.append("")
            lines.extend(callouts)
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def qa_md(pairs):
    return "\n\n".join(f"**Q: {p['q']}**\nA: {p['a']}" for p in pairs)


def questions_md(items):
    return "\n".join(f"- {q}" for q in items)


def notes_md(notes):
    if isinstance(notes, str):
        return notes
    parts = []
    for b in notes:
        if b.get("heading"):
            parts.append(f"#### {b['heading']}\n\n{b['body']}")
        else:
            parts.append(b["body"])
    return "\n\n".join(parts)


def write_briefing(app):
    slug = slugify(app["company"])
    fname = f"{app['date']}-{slug}-{slugify(app['role'])}.md"
    est = json.dumps(app["estimated_fields"])
    comp_band_yaml = f'"{app["comp_band"]}"' if app["comp_band"] else "null"
    next_interview_yaml = app["next_interview_date"] if app["next_interview_date"] else "null"
    stages_md = "\n".join(f"- {s}" for s in app["stages"])
    locked = "true" if should_lock(app["status"]) else "false"

    watch_section = (
        usps_md(app["watch_bullets"]) if app.get("watch_bullets") else app.get("watch", "")
    )

    fm = f"""---
company: "{app['company']}"
role: "{app['role']}"
date_scored: {app['date']}
date_applied: {app['date']}
status: {app['status']}
status_date: {app['status_date']}
source: "{app['source']}"

score:
  value: {app['score']}
  tier: "{app['tier']}"
  locked: {locked}
  breakdown:
    jd_fit: {app['jd_fit']}
    seniority: {app['seniority']}
    competition: {app['competition']}
    comp: {app['comp']}
    blockers: {app['blockers']}
  estimated_fields: {est}

next_interview_date: {next_interview_yaml}

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

### Why it progressed / didn't
{app['why']}

### Unique selling points
{usps_md(app['usps'])}

### Interviewer profiles
{profiles_md(app['profiles'])}

### Prep questions
{qa_md(app['prep_qa'])}

### Questions to ask
{questions_md(app['questions_to_ask'])}

### Watch-outs
{watch_section}

### Notes
{notes_md(app['notes'])}

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
