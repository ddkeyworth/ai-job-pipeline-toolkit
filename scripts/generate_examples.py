#!/usr/bin/env python3
"""
Generates the synthetic example dataset in examples/.
Not required to use the toolkit – this is a one-time authoring aid, kept in
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

# score is deliberately NOT a field here - it's computed as the sum of the
# breakdown in write_simple()/write_briefing(), so it can never drift from
# its own breakdown the way a hand-typed number could (and, in the dataset
# this replaced, did - see TESTING.md).
#
# (date, company, role, status, tier, jd_fit, seniority, competition, comp,
#  blockers, estimated_fields, comp_band, source, note, rationale)
# rationale = (jd_fit_reason, seniority_reason, competition_reason,
#              comp_reason, blockers_reason) - real one-line reasoning per
# component, not a restatement of the number (see SCHEMA.md -> Score rationale).
APPLICATIONS = [
    ("2026-05-28", "Meridian Cloud Systems", "Director of Product", "applied", "Tier 3 – Solid, worth applying",
     30, 12, 4, 9, 10, ["competition", "comp"], "£95k-110k base + bonus (unconfirmed split)", "LinkedIn",
     "Large, well-known public cloud platform – huge applicant pool expected.",
     ("Director-level product leadership overlaps well, but limited evidence of experience operating at true public-cloud-platform scale.",
      "Director level matches the candidate's demonstrated range without a stretch.",
      "Large, well-known public cloud platform – draws a very large applicant pool regardless of role specifics.",
      "£95k-110k base + bonus stated, but the base/bonus split is unconfirmed – estimated modestly below floor pending clarity.",
      "No blocker identified.")),
    ("2026-06-02", "Fernbank Analytics", "Head of Product", "applied", "Tier 1 – Exceptional callback odds",
     40, 13, 16, 10, 10, [], "£120k-135k OTE", "Referral",
     "Small, private data-analytics startup, narrow role, strong direct fit.",
     ("Narrow, specialist mandate maps closely onto direct prior experience.",
      "Head of Product matches the candidate's evidenced level well.",
      "Small, private startup with a narrow role – a limited applicant pool expected.",
      "£120k-135k OTE confirmed comfortably above floor.",
      "No blocker identified.")),
    ("2026-06-05", "Coastal Ledger", "Senior Director, Product", "applied", "Tier 2 – Strong callback odds",
     35, 12, 11, 10, 10, ["comp"], "£115k-130k OTE (estimated)", "Company site",
     "Mid-size fintech, moderately well-known in its niche.",
     ("Reasonable domain fit, with some gaps against a fintech-specific product mandate.",
      "Senior Director level within the candidate's evidenced range.",
      "Mid-size company, moderately well-known in its niche – a moderate applicant pool.",
      "Not stated in the JD; estimated at £115k-130k OTE for a Senior Director role at a mid-size fintech, comfortably above floor.",
      "No blocker identified.")),
    ("2026-06-09", "Union Freight Group", "VP Product", "applied", "Tier 3 – Solid, worth applying",
     28, 8, 5, 10, 10, ["competition", "comp"], "£115k-135k OTE (estimated)", "LinkedIn",
     "Large logistics incumbent, broad VP-level role draws a wide pool.",
     ("Real gaps against a broad, incumbent-scale VP mandate versus the candidate's more focused prior scope.",
      "A genuine stretch upward against the candidate's demonstrated team-leadership scale.",
      "Large logistics incumbent with a broad VP-level role – a wide applicant pool expected.",
      "Not stated in the JD; estimated at £115k-135k OTE for a VP role at a large incumbent, above floor.",
      "No blocker identified.")),
    ("2026-06-11", "Harrowgate Systems", "Head of Product", "scored", "Tier 2 – Strong callback odds",
     37, 12, 14, 10, 10, [], "£115k-128k OTE", "LinkedIn",
     "Scored, not yet applied – still deciding whether to prioritise this over other open processes.",
     ("Strong overlap on core Head of Product responsibilities.",
      "Matches the candidate's evidenced level without a stretch.",
      "Mid-size, not a widely recognised brand – a moderate-to-favourable applicant pool.",
      "£115k-128k OTE confirmed above floor.",
      "No blocker identified.")),
    ("2026-06-13", "Vireo Networks", "Director of Product", "scored", "Tier 3 – Solid, worth applying",
     29, 9, 4, 10, 10, ["competition", "comp"], "£110k-125k OTE (estimated)", "LinkedIn",
     "Scored, not applied – large, well-known network infrastructure company; score alone made this a low priority.",
     ("Moderate overlap; network-infrastructure domain depth is a real, if not disqualifying, gap.",
      "Director title matches on paper, but infrastructure product organisations at this scale often expect broader cross-product ownership than evidenced.",
      "Large, well-known network infrastructure company – a large applicant pool expected.",
      "Not stated in the JD; estimated at £110k-125k OTE for this level at a large infrastructure company, above floor.",
      "No blocker identified.")),
    ("2026-06-14", "Elmscroft Data", "Head of Product", "scored", "Tier 1 – Exceptional callback odds",
     42, 14, 17, 10, 10, [], "£125k-138k OTE", "Referral",
     "Scored today – strong match, referral in hand. Drafting the application next, not yet submitted.",
     ("Very close match to the candidate's demonstrated product mandate.",
      "Head of Product matches the candidate's evidenced level closely.",
      "Small, less widely known company with a referral already in hand – a limited applicant pool expected.",
      "£125k-138k OTE confirmed above floor.",
      "No blocker identified.")),
    ("2026-04-02", "Northwind Retail Technologies", "Head of Product, Platform", "rejected", "Tier 2 – Strong callback odds",
     32, 12, 6, 10, 10, ["competition"], "£110k-125k OTE", "LinkedIn",
     "Large, recognisable retail-tech brand.",
     ("Reasonable platform-product overlap, with a real gap against retail-specific domain depth.",
      "Matches the candidate's evidenced level.",
      "Large, recognisable retail-tech brand – a large applicant pool expected.",
      "£110k-125k OTE confirmed at and above floor.",
      "No blocker identified.")),
    ("2026-04-05", "Ashgrove Financial", "Director of Product Strategy", "rejected", "Tier 2 – Strong callback odds",
     33, 11, 9, 10, 10, [], "£100k-115k base", "Company site",
     "Large regulated financial services firm.",
     ("Reasonable strategic-product overlap, with a real gap against regulated financial-services domain depth.",
      "Director level within range, modestly below the role's strategy-level framing.",
      "Large, regulated financial services firm – a sizeable applicant pool expected.",
      "£100k-115k base, just within range of floor.",
      "No blocker identified.")),
    ("2026-04-08", "Larkspur Health", "VP Product", "rejected", "Tier 2 – Strong callback odds",
     36, 13, 13, 9, 10, ["comp"], "£95k-110k OTE (estimated)", "Referral",
     "Mid-size health-tech, moderately known.",
     ("Strong general product-leadership overlap, with a partial health-tech domain gap.",
      "VP level matches the candidate's evidenced range well.",
      "Mid-size, moderately known health-tech company – a moderate applicant pool.",
      "Not stated in the JD; estimated at £95k-110k OTE for this level at a mid-size health-tech company, modestly below floor.",
      "No blocker identified.")),
    ("2026-04-11", "Kettlebrook Robotics", "Head of Product", "rejected", "Tier 2 – Strong callback odds",
     38, 12, 14, 10, 10, [], "£115k-130k OTE", "LinkedIn",
     "Small robotics startup – good fit on paper, rejected anyway; not every high score converts.",
     ("Strong fit on paper for a small, specialist robotics product mandate.",
      "Matches the candidate's evidenced level well.",
      "Small robotics startup – a limited applicant pool expected.",
      "£115k-130k OTE confirmed above floor.",
      "No blocker identified.")),
    ("2026-04-15", "Solari Energy Corp", "Senior Director Product", "rejected", "Tier 3 – Solid, worth applying",
     31, 10, 6, 10, 10, ["competition", "comp"], "£115k-130k OTE (estimated)", "LinkedIn",
     "Large, well-funded energy technology company.",
     ("Moderate overlap; energy-sector domain depth is a real gap against the stated mandate.",
      "Senior Director level modestly below the candidate's typical scope for a company this size.",
      "Large, well-funded energy technology company – a large applicant pool expected.",
      "Not stated in the JD; estimated at £115k-130k OTE for this level at a large, well-funded company, above floor.",
      "No blocker identified.")),
    ("2026-04-18", "Ferrous Metals Digital", "Head of Product", "rejected", "Tier 2 – Strong callback odds",
     34, 12, 12, 10, 10, [], "£105k-120k base", "Company site",
     "Mid-size industrial-tech firm.",
     ("Reasonable digital-product overlap, with a moderate gap against industrial-sector domain depth.",
      "Matches the candidate's evidenced level.",
      "Mid-size, moderately known industrial-tech firm – a moderate applicant pool.",
      "£105k-120k base, just at and above floor.",
      "No blocker identified.")),
    ("2026-04-22", "Bramwell Media Group", "VP Product", "rejected", "Tier 3 – Solid, worth applying",
     29, 9, 4, 8, 10, ["competition", "comp"], "£90k-105k OTE (estimated)", "LinkedIn",
     "Large, famous media brand – very high competition.",
     ("Real gaps against a broad, brand-scale VP mandate versus the candidate's more focused prior scope.",
      "A meaningful stretch upward against the candidate's demonstrated team-leadership scale.",
      "Large, famous media brand – a very high applicant pool expected.",
      "Not stated in the JD; large media brands often run modest cash comp for VP roles relative to tech – estimated at £90k-105k OTE, below floor.",
      "No blocker identified.")),
    ("2026-04-25", "TidePool Labs", "Head of Product", "rejected", "Tier 1 – Exceptional callback odds",
     39, 13, 15, 10, 10, [], "£118k-132k OTE", "Referral",
     "Small private labs startup, narrow specialist role.",
     ("Strong fit for a narrow, specialist product mandate.",
      "Matches the candidate's evidenced level closely.",
      "Small private labs startup with a narrow specialist role – a limited applicant pool expected.",
      "£118k-132k OTE confirmed above floor.",
      "No blocker identified.")),
    ("2026-04-29", "Granite Peak Software", "Director of Product", "rejected", "Tier 2 – Strong callback odds",
     34, 11, 10, 6, 10, ["comp"], None, "LinkedIn",
     "Mid-size, moderately known enterprise software vendor.",
     ("Reasonable general product-leadership overlap for an enterprise software mandate.",
      "Director level within the candidate's evidenced range.",
      "Mid-size, moderately known enterprise software vendor – a moderate applicant pool.",
      "Not stated in the JD, and no reliable signal (company size, sector norms) to form a defensible estimate – scored at the neutral default rather than assumed favourable.",
      "No blocker identified.")),
    ("2026-05-02", "Ovalcrest Insurance", "VP Product Management", "rejected", "Tier 3 – Solid, worth applying",
     30, 10, 6, 10, 10, ["competition", "comp"], "£100k-115k OTE (estimated)", "Company site",
     "Large regulated insurer, broad pool.",
     ("Real gaps against a broad, regulated-insurer VP mandate versus the candidate's more focused prior scope.",
      "A meaningful stretch upward against the candidate's demonstrated team-leadership scale.",
      "Large, regulated insurer – a large, broad applicant pool expected.",
      "Not stated in the JD; estimated at £100k-115k OTE for this level at a large regulated insurer, around floor.",
      "No blocker identified.")),
    ("2026-05-06", "Millrace Systems", "Head of Product", "rejected", "Tier 1 – Exceptional callback odds",
     40, 13, 16, 10, 10, [], "£112k-128k OTE", "Referral",
     "Small private systems company, strong fit.",
     ("Strong direct fit for the stated product mandate.",
      "Matches the candidate's evidenced level well.",
      "Small private systems company – a limited applicant pool expected.",
      "£112k-128k OTE confirmed above floor.",
      "No blocker identified.")),
    ("2026-05-09", "Copperfield Logistics", "Senior Director Product", "rejected", "Tier 2 – Strong callback odds",
     35, 12, 10, 6, 10, ["comp"], None, "LinkedIn",
     "Mid-size logistics tech firm.",
     ("Reasonable product-leadership overlap for a mid-size logistics-tech mandate.",
      "Senior Director level within the candidate's evidenced range.",
      "Mid-size logistics tech firm – a moderate applicant pool.",
      "Not stated in the JD, and no reliable signal to form a defensible estimate – scored at the neutral default rather than assumed favourable.",
      "No blocker identified.")),
    ("2026-05-13", "Vantage Point Telecom", "VP Product", "rejected", "Tier 3 – Solid, worth applying",
     30, 9, 5, 9, 10, ["competition", "comp"], "£95k-110k OTE (estimated)", "LinkedIn",
     "Large, recognisable telecom operator.",
     ("Real gaps against a broad, incumbent-scale VP mandate versus the candidate's more focused prior scope.",
      "A meaningful stretch upward against the candidate's demonstrated team-leadership scale.",
      "Large, recognisable telecom operator – a large applicant pool expected.",
      "Not stated in the JD; estimated at £95k-110k OTE for this level at a large telecom incumbent, modestly below floor.",
      "No blocker identified.")),
    ("2026-05-16", "Hollow Creek Devices", "Head of Product", "rejected", "Tier 2 – Strong callback odds",
     37, 12, 13, 10, 10, [], "£108k-122k OTE", "Company site",
     "Small private hardware/devices startup.",
     ("Strong fit for a small, specialist hardware/devices product mandate.",
      "Matches the candidate's evidenced level well.",
      "Small private hardware/devices startup – a limited applicant pool expected.",
      "£108k-122k OTE confirmed at and above floor.",
      "No blocker identified.")),
    ("2026-05-20", "Marlow Continental", "Director of Product", "rejected", "Tier 2 – Strong callback odds",
     33, 11, 7, 10, 10, ["competition", "comp"], "£105k-120k OTE (estimated)", "LinkedIn",
     "Large multinational, broad applicant pool.",
     ("Reasonable overlap for a large-multinational product-leadership mandate.",
      "Director level within the candidate's evidenced range.",
      "Large multinational – a broad applicant pool expected.",
      "Not stated in the JD; estimated at £105k-120k OTE for this level at a large multinational, at and above floor.",
      "No blocker identified.")),
    ("2026-05-24", "Palisade Robotics", "VP Product", "rejected", "Tier 2 – Strong callback odds",
     36, 13, 12, 10, 3, [], "£140k-155k OTE", "LinkedIn",
     "Strong fit on paper, but the role required confirmed US work authorisation the candidate does not hold, and was onsite in Austin with no relocation support – a real, confirmed blocker, not a soft preference.",
     ("Strong fit for the stated robotics product mandate.",
      "VP level matches the candidate's evidenced range well.",
      "Small robotics startup – a limited applicant pool expected.",
      "£140k-155k OTE confirmed well above floor.",
      "Confirmed hard blocker: the role required US work authorisation the candidate does not hold, onsite in Austin with no relocation support – not a soft preference.")),
    ("2026-05-11", "Redshank Payments", "Director of Product", "didnt_apply", "Tier 2 – Strong callback odds",
     36, 12, 11, 3, 10, [], "£65k-75k base, confirmed well below floor (early-stage, equity-heavy package)", "LinkedIn",
     "Scored well on fit, but the comp band came back confirmed well below floor before applying – decided not to submit rather than pursue a role that couldn't clear the floor regardless of interview performance.",
     ("Strong overlap on the core product mandate.",
      "Director level matches the candidate's evidenced range.",
      "Mid-size fintech, moderate applicant pool expected.",
      "£65k-75k base confirmed well below floor even before applying – an early-stage, equity-heavy package that couldn't clear the floor regardless of interview performance.",
      "No blocker identified.")),
    ("2026-05-30", "Oakridge Ventures", "Director of Product", "assumed_rejected", "Tier 2 – Strong callback odds",
     34, 11, 10, 10, 10, [], "£105k-118k OTE", "LinkedIn",
     "Applied and heard nothing since – no rejection, no further contact. Marked assumed_rejected after the configured silence window (see config/weights.json), not a confirmed rejection.",
     ("Reasonable overlap for the stated product mandate.",
      "Director level within the candidate's evidenced range.",
      "Mid-size company – a moderate applicant pool.",
      "£105k-118k OTE confirmed at and above floor.",
      "No blocker identified.")),
    ("2026-06-16", "Thistlewood Capital", "Director of Product", "rejected", "Tier 3 – Solid, worth applying",
     31, 11, 8, 9, 10, [], "£100k-112k base", "LinkedIn",
     "Mid-size asset manager, moderate applicant pool – added to give the recalibration agent's joint model enough data points to clear its higher threshold.",
     ("Reasonable overlap for a mid-size asset manager's product mandate.",
      "Director level within the candidate's evidenced range.",
      "Mid-size asset manager – a moderate applicant pool.",
      "£100k-112k base, modestly below floor.",
      "No blocker identified.")),
    ("2026-06-18", "Fenwick Outdoors", "Head of Product", "rejected", "Tier 3 – Solid, worth applying",
     29, 10, 5, 6, 10, ["competition", "comp"], None, "LinkedIn",
     "Large, well-known consumer outdoor brand – broad applicant pool.",
     ("Moderate overlap; consumer-outdoor domain depth is a real gap against the candidate's B2B SaaS background.",
      "Head of Product level within range, modestly below the role's apparent scope.",
      "Large, well-known consumer outdoor brand – a broad applicant pool expected.",
      "Not stated in the JD, and no reliable signal to form a defensible estimate – scored at the neutral default rather than assumed favourable.",
      "No blocker identified.")),
    ("2026-06-20", "Amberline Media", "VP Product", "rejected", "Tier 2 – Strong callback odds",
     33, 12, 9, 10, 10, [], "£108k-120k OTE", "Company site",
     "Mid-size media company, moderately competitive.",
     ("Reasonable overlap for a mid-size media company's product mandate.",
      "VP level matches the candidate's evidenced range.",
      "Mid-size media company, moderately competitive.",
      "£108k-120k OTE confirmed at and above floor.",
      "No blocker identified.")),
]

# Fully fleshed briefing-pack applications – interviewing / offer / and the
# two "reached interview, then didn't convert" statuses this needs a real
# example of (rejected_after_interview, withdrew_after_interview).
#
# Alderwood, Wrenfield get full depth throughout. Pemberton deliberately
# keeps some sections as genuine "Currently unknown" placeholders – the
# skill should default to real synthesis, not placeholders, but this repo's
# examples should prove the placeholder path actually works too, not just
# claim it does. Briarcliff exercises an interviewer profile with no
# optional callouts filled in.
BRIEFING_APPS = [
    dict(
        date="2026-05-18", status_date="2026-06-04",
        company="Alderwood Data", role="Head of Product", status="interviewing",
        tier="Tier 1 – Exceptional callback odds", jd_fit=41, seniority=14, competition=17, comp=10, blockers=10,
        estimated_fields=[], comp_band="£125k-140k OTE", source="Referral",
        company_size="~40 employees", funding="Seed/Series A, privately held", competition_tier="low",
        rationale=dict(
            jd_fit="Very close fit for a narrow, specialist product mandate – direct 0-to-1 experience at a similarly-staged company.",
            seniority="Head of Product matches the candidate's evidenced level closely.",
            competition="~40-person, privately-held seed/Series A company – a limited applicant pool expected.",
            comp="£125k-140k OTE confirmed above floor.",
            blockers="No blocker identified.",
        ),
        why="Direct fit on a narrow, specialist product mandate; referral likely helped surface the application quickly.",
        usps=[
            {"title": "Direct data-platform PM experience",
             "body": "Owned the roadmap for a usage-based analytics product at a prior 60-person startup, taking it from 12 to 40 paying accounts in nine months – close to Alderwood's own stage and product shape."},
            {"title": "Comfortable operating without a large team",
             "body": "Ran product, a chunk of go-to-market, and customer research solo for five months before a second PM was hired – the kind of stretch this role is asking for."},
            {"title": "Track record shipping to specialist buyers",
             "body": "Built onboarding flows for data engineers, not consumer users – Alderwood's buyer persona (data/analytics leads) is a similarly technical, low-tolerance-for-fluff audience."},
        ],
        profiles=[
            {"name": "Priya Nandan", "title": "Head of Product",
             "background": "Joined Alderwood roughly 18 months ago from a mid-size data-infrastructure company; previously an IC engineer before moving into product. [estimated – public bio is thin]",
             "assessing": "Whether the candidate can operate with real autonomy on a small team, not just describe a strategy.",
             "play_it": "Lead with specific examples of decisions made without a large team backing you up, not frameworks."},
            {"name": "Marcus Webb", "title": "Co-founder & CEO",
             "background": "Second-time founder; previously built and sold a smaller developer-tools company. [estimated]",
             "assessing": "Product instinct, and whether the candidate will push back on him rather than just agree.",
             "play_it": "Bring one genuine, prepared disagreement or pushback on the product direction – he reportedly values candidates who challenge him respectfully."},
        ],
        prep_qa=[
            {"q": "Walk me through a product decision you made that you'd now do differently.",
             "a": "The analytics onboarding flow at [prior company] launched with too many configuration steps up front – usage data showed a third of new accounts stalled before their first real report. Simplified to a single default view with configuration deferred until after first value, which measurably improved week-one activation."},
            {"q": "How would you prioritise between a feature a big prospect is asking for and your own roadmap conviction?",
             "a": "Ask whether the request generalises – if three or more other accounts would plausibly want it too, it's probably signal, not a one-off. If it's genuinely bespoke to one prospect, the answer is usually 'not on the roadmap, happy to discuss as a paid customisation' rather than letting one deal reshape the product."},
            {"q": "You'd be one of two PMs here. How do you divide scope with a peer without stepping on each other?",
             "a": "Split by customer segment or product surface, not by task type – task-based splits create constant hand-offs and ambiguity about who owns a decision. A clear owner per surface, with a standing weekly sync to flag anything that crosses the boundary."},
            {"q": "What's a metric you'd push back on if leadership over-indexed on it?",
             "a": "Raw signup count without an activation gate – easy to inflate with top-of-funnel spend and tells you almost nothing about whether the product is actually landing. Would push for a paired activation-rate metric alongside any growth target."},
        ],
        questions_to_ask=[
            "How is the roadmap actually prioritised day to day – a formal process, or Priya and Marcus's judgement call?",
            "What's the biggest thing that's broken as you've scaled from roughly 12 to 40 employees?",
            "What would make the next six months a clear success for this hire specifically?",
        ],
        watch_bullets=[
            {"title": "Small team", "body": "Later interview stages likely to probe hands-on delivery experience, not just strategy."},
            {"title": "Founder-level scrutiny", "body": "Marcus reportedly likes being pushed back on – over-agreeing may read as weak rather than diplomatic."},
        ],
        notes=[{"heading": "Logistics", "body": "Role is London-hybrid, two days/week in office – confirm this is workable before the panel round, not after an offer."}],
        next_interview_date="2026-06-19",
        stages=["Stage 1 – 2026-05-25 – Recruiter screen – positive, moved forward",
                "Stage 2 – 2026-06-04 – Hiring manager interview – positive, moved to panel"],
    ),
    dict(
        date="2026-05-22", status_date="2026-05-29",
        company="Pemberton Health Tech", role="VP Product", status="interviewing",
        tier="Tier 2 – Strong callback odds", jd_fit=36, seniority=13, competition=11, comp=9, blockers=10,
        estimated_fields=["comp"], comp_band="£100k-112k OTE (estimated)", source="LinkedIn",
        company_size="~600 employees", funding="Series C", competition_tier="moderate",
        rationale=dict(
            jd_fit="Solid domain adjacency to prior regulated-sector product experience.",
            seniority="VP level matches the candidate's evidenced range, with team-management scope already demonstrated.",
            competition="~600-employee, Series C company – a moderate applicant pool given its mid-market profile.",
            comp="Not stated in the JD; estimated at £100k-112k OTE for a VP role at a Series C health-tech company, modestly below floor.",
            blockers="No blocker identified.",
        ),
        why="Solid domain adjacency; moderate competition given the company's mid-market profile.",
        usps=[
            {"title": "Regulated-sector product experience",
             "body": "Shipped features inside a healthcare-adjacent compliance framework at a prior role – Pemberton's health-tech context carries similar constraints."},
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
             "a": "Treat compliance requirements as a fixed floor, not a competing priority – they get built regardless of ROI debate, and the actual prioritisation conversation happens on everything above that floor."},
            {"q": "What's your experience managing a small product team, not just being an IC?",
             "a": "Managed two PMs at [prior company] – the main shift was moving from owning decisions to owning the quality of other people's decisions, which meant more time in 1:1 review of their rationale and less time writing specs myself."},
            {"q": "Health-tech buyers are often risk-averse. How does that change how you'd position a new feature?",
             "a": "Lead with what doesn't change (existing workflows, compliance posture) before what does – risk-averse buyers respond to evidence that the new thing doesn't destabilise what already works, not just to the upside case."},
        ],
        questions_to_ask=[
            "What does the compliance/product relationship actually look like day to day – a blocking gate, or an embedded partner?",
            "What's driving the VP Product hire specifically now, versus six months ago?",
        ],
        watch="Comp is an estimate, not yet confirmed by the company – worth raising directly before a later stage.",
        notes="Currently unknown – nothing situational to flag yet; will add if something comes up in later stages.",
        next_interview_date=None,
        stages=["Stage 1 – 2026-05-29 – Recruiter screen – positive, moved forward"],
    ),
    dict(
        date="2026-05-26", status_date="2026-06-08",
        company="Briarcliff AI", role="Head of Product", status="interviewing",
        tier="Tier 1 – Exceptional callback odds", jd_fit=40, seniority=14, competition=16, comp=7, blockers=10,
        estimated_fields=["comp"], comp_band="£85k-100k OTE (estimated, cash-only; equity offered separately)", source="Company site",
        company_size="~25 employees", funding="Series A", competition_tier="low",
        rationale=dict(
            jd_fit="Strong product-led-growth track record maps closely onto the stated self-serve motion.",
            seniority="Head of Product matches the candidate's evidenced level.",
            competition="~25-person, Series A startup – a limited applicant pool expected.",
            comp="Not stated in the JD; ~25-person Series A startups typically pay below-market cash in favour of equity – estimated at £85k-100k OTE cash, below floor. Equity mentioned separately by the founder but not counted in this score – too unreliable to value consistently at this stage.",
            blockers="No blocker identified.",
        ),
        why="Small, narrow-mandate startup role; strong overlap with prior product-led growth experience.",
        usps=[
            {"title": "Product-led growth track record",
             "body": "Drove self-serve activation improvements that reduced time-to-first-value from 9 minutes to under 2 at a prior PLG product – directly relevant to Briarcliff's stated self-serve motion."},
            {"title": "Comfortable in a genuinely early-stage environment",
             "body": "Joined a 15-person company as first PM hire previously – knows what building process from nothing actually requires, not just how to operate inside an existing one."},
        ],
        profiles=[
            {"name": "Elena Torres", "title": "Founder",
             "background": "Ran the founder screen. Previously a senior engineer at a larger AI infrastructure company before starting Briarcliff. [estimated – limited public information available]",
             "assessing": "", "play_it": ""},
        ],
        prep_qa=[
            {"q": "What would you do in the first 30 days here?",
             "a": "Spend the first two weeks almost entirely in user conversations and usage data before proposing any roadmap change – at 25 people, the risk isn't lack of ideas, it's building the wrong thing fast."},
            {"q": "How do you think about product-market fit signal at this stage versus a later one?",
             "a": "Retention curves that flatten, not vanity signups – at this stage, a small number of users who won't stop using it is a stronger signal than a larger number who tried it once."},
            {"q": "The process has moved quickly. What questions haven't you had a chance to ask yet that you'd want answered before a final round?",
             "a": "What's the realistic runway, and is this hire funded by the current round or contingent on the next one – directly affects how much risk this role represents."},
        ],
        questions_to_ask=[
            "What's the split today between self-serve and any assisted/sales-led motion, and is that expected to shift?",
            "What does Elena see as the single biggest product risk over the next two quarters?",
        ],
        watch="Fast-moving process – later stages may compress quickly; keep availability flexible.",
        notes=[{"heading": None, "body": "Process has moved unusually fast – screen to panel in one week. Worth asking directly whether that pace reflects urgency to fill the role or just a lean, fast-moving team; the answer changes how much leverage exists in later comp conversations."}],
        next_interview_date="2026-06-16",
        stages=["Stage 1 – 2026-06-01 – Founder screen – positive, moved forward",
                "Stage 2 – 2026-06-08 – Product deep-dive – positive, moved to final round"],
    ),
    dict(
        date="2026-04-30", status_date="2026-05-27",
        company="Wrenfield Software", role="Head of Product", status="offer",
        tier="Tier 1 – Exceptional callback odds", jd_fit=42, seniority=15, competition=17, comp=10, blockers=10,
        estimated_fields=[], comp_band="£130k-145k OTE, confirmed above floor", source="Referral",
        company_size="~60 employees", funding="Series B", competition_tier="low",
        rationale=dict(
            jd_fit="Very close mandate match – not an adjacent-domain stretch.",
            seniority="Head of Product matches the candidate's evidenced level exactly.",
            competition="~60-person, Series B company – a limited applicant pool expected.",
            comp="£130k-145k OTE confirmed above floor.",
            blockers="No blocker identified.",
        ),
        why="Very close mandate match plus a warm referral; comp confirmed early and above floor.",
        usps=[
            {"title": "Direct mandate match",
             "body": "Role scope mirrors a product owned end-to-end at a similarly-staged prior company – not an adjacent-domain stretch."},
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
             "a": "A comp band confirmed below floor, or a mandate that turns out narrower in practice than described in the process – neither applies here, comp is confirmed above floor."},
            {"q": "How do you evaluate a smaller company's risk profile before accepting?",
             "a": "Runway relative to current burn, and whether the role is backed by the current funding round or contingent on the next one – worth confirming explicitly during the offer conversation, not assuming."},
        ],
        questions_to_ask=[
            "Is there flexibility on the start date given other processes still in flight?",
            "What does the first-90-days success definition look like from Dev's side specifically?",
        ],
        watch_bullets=[
            {"title": "Decision deadline is tight", "body": "Relative to other processes still in flight – worth being direct about needing a short extension if one is required."},
        ],
        notes=[{"heading": "Negotiation notes", "body": "Comp already confirmed above floor, so negotiation leverage is mainly about start date and any signing considerations, not base/OTE. Worth comparing total package (not just base) against Stonebridge before deciding between the two."}],
        next_interview_date=None,
        stages=["Stage 1 – 2026-05-06 – Recruiter screen – positive, moved forward",
                "Stage 2 – 2026-05-14 – Hiring manager interview – positive, moved forward",
                "Stage 3 – 2026-05-21 – Final panel – positive",
                "Offer – 2026-05-27 – Extended, under review"],
    ),
    dict(
        date="2026-05-04", status_date="2026-06-02",
        company="Stonebridge Analytics", role="VP Product", status="offer",
        tier="Tier 2 – Strong callback odds", jd_fit=38, seniority=13, competition=13, comp=10, blockers=10,
        estimated_fields=[], comp_band="£122k-135k OTE, confirmed above floor", source="LinkedIn",
        company_size="~300 employees", funding="Series C", competition_tier="moderate",
        rationale=dict(
            jd_fit="Strong domain fit for the stated product mandate.",
            seniority="VP level matches the candidate's evidenced range.",
            competition="~300-employee, Series C company – a moderate applicant pool given its mid-market scale.",
            comp="£122k-135k OTE confirmed above floor.",
            blockers="No blocker identified.",
        ),
        why="Strong domain fit; moderate competition given company's mid-market scale.",
        regional_intelligence=[
            {"region": "UK", "relationship_style": "Direct, commercial", "decision_style": "Moderate speed",
             "nuances": "Existing customer base concentrated here – role likely leans on this market's playbook as the template for expansion elsewhere."},
            {"region": "US", "relationship_style": "Results-first", "decision_style": "Fast at SME, slower at enterprise",
             "nuances": "Stated growth target for the year – worth asking directly how much of the VP mandate is US-expansion-specific versus global product ownership."},
        ],
        usps=[
            {"title": "Mid-market SaaS scaling experience",
             "body": "Operated at a similar company scale (a few hundred employees) previously – familiar with the specific coordination overhead at this size, distinct from either startup or enterprise."},
        ],
        profiles=[
            {"name": "Farah Idris", "title": "Chief Product Officer",
             "background": "Final-round interviewer; previously VP Product at a larger analytics company before joining Stonebridge as CPO. [estimated]",
             "assessing": "Strategic thinking at VP level, and cross-functional credibility with Sales and Engineering leadership.",
             "play_it": "Bring examples of cross-functional alignment, not just product execution."},
        ],
        prep_qa=[
            {"q": "How would you balance Wrenfield-style ownership versus a larger organisation's coordination overhead?",
             "a": "Larger orgs need more explicit alignment mechanisms (documented decisions, wider stakeholder review) – the skill is knowing when to invoke that process versus when it's genuinely a unilateral call."},
        ],
        questions_to_ask=[
            "What's the biggest source of friction between Product and Sales today?",
        ],
        watch="Slightly lower comp than Wrenfield – worth comparing full package, not just base, before deciding.",
        notes=[{"heading": None, "body": "Second live offer alongside Wrenfield – decision should weigh total package and role scope, not just base comp, before the Wrenfield deadline forces the choice."}],
        next_interview_date=None,
        stages=["Stage 1 – 2026-05-11 – Recruiter screen – positive, moved forward",
                "Stage 2 – 2026-05-19 – Hiring manager interview – positive, moved forward",
                "Stage 3 – 2026-05-28 – Final panel – positive",
                "Offer – 2026-06-02 – Extended, under review"],
    ),
    dict(
        date="2026-05-15", status_date="2026-06-12",
        company="Fenwick Data Systems", role="Head of Product", status="rejected_after_interview",
        tier="Tier 2 – Strong callback odds", jd_fit=38, seniority=13, competition=14, comp=10, blockers=10,
        estimated_fields=[], comp_band="£118k-130k OTE", source="LinkedIn",
        company_size="~120 employees", funding="Series B", competition_tier="moderate",
        rationale=dict(
            jd_fit="Direct domain overlap with an almost identical prior product category.",
            seniority="Head of Product matches the candidate's evidenced level.",
            competition="~120-employee, Series B company – a moderate applicant pool.",
            comp="£118k-130k OTE confirmed above floor.",
            blockers="No blocker identified.",
        ),
        why="Progressed through two positive interview stages; ultimately lost out to an internal candidate at the final round – the scoring rubric correctly predicted engagement (jd_fit, seniority, competition all landed within range) even though the outcome wasn't a hire. A useful real example of why rejected_after_interview is tracked separately from a flat rejection.",
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
             "a": "Separate the technical disagreement from the relationship – push on the technical point with evidence, but explicitly signal that disagreement on scope isn't a verdict on the working relationship."},
            {"q": "What would you want to know in the first week here that you wouldn't get from the JD?",
             "a": "Whatever's currently the biggest unresolved internal debate about product direction – that's usually the real job, not what's written in the posting."},
        ],
        questions_to_ask=[
            "Is there an internal candidate also being considered for this role?",
            "What does success in the first quarter look like specifically?",
        ],
        watch_bullets=[
            {"title": "Internal-candidate risk wasn't asked about directly", "body": "Worth asking early and directly in future processes whether an internal candidate exists – a structural disadvantage no interview performance overcomes, and better to know going in."},
        ],
        notes=[{"heading": "Why it didn't progress", "body": "Recruiter confirmed after the final round that an internal candidate with existing platform context was preferred. Not a reflection of interview performance – both prior stages were explicitly described as positive. The scoring rubric's prediction (this would land an interview) was validated; the eventual outcome was decided by a factor the scoring model doesn't and can't account for."}],
        next_interview_date=None,
        stages=["Stage 1 – 2026-05-22 – Recruiter screen – positive, moved forward",
                "Stage 2 – 2026-06-02 – Engineering collaboration interview – positive, moved to final round",
                "Stage 3 – 2026-06-12 – Final round – rejected, internal candidate preferred"],
    ),
    dict(
        date="2026-05-19", status_date="2026-06-10",
        company="Silverlake Systems", role="VP Product", status="withdrew_after_interview",
        tier="Tier 2 – Strong callback odds", jd_fit=36, seniority=13, competition=12, comp=5, blockers=10,
        estimated_fields=[], comp_band="£75k-85k base, confirmed ~27% below floor after Stage 2", source="Referral",
        company_size="~180 employees", funding="Series B", competition_tier="moderate",
        rationale=dict(
            jd_fit="Solid overlap for the stated VP product mandate.",
            seniority="VP level matches the candidate's evidenced range.",
            competition="~180-employee, Series B company – a moderate applicant pool.",
            comp="£75k-85k base confirmed after Stage 2, meaningfully below floor – the recruiter's earlier verbal indication ('should be competitive') didn't hold up once pressed for specifics.",
            blockers="No blocker identified.",
        ),
        why="Withdrew after Stage 2 once the comp band was finally confirmed – meaningfully below floor, despite an earlier verbal indication from the recruiter that it would be competitive.",
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
             "a": "Raise it directly and immediately rather than continuing through further stages on the assumption it might improve – continuing signals the floor is negotiable when it isn't, and wastes both sides' time."},
        ],
        questions_to_ask=[
            "What's the actual confirmed comp band, in writing, before the next stage?",
        ],
        watch="Get the comp band confirmed in writing before Stage 1, not verbally after Stage 2 – this is the second process this floor issue has surfaced late in.",
        notes=[{"heading": "Why withdrew", "body": "The recruiter's Stage 1 verbal indication ('should be competitive') didn't match the actual confirmed band once pressed for specifics after Stage 2 – roughly 27% below floor. Withdrew rather than continue a process that couldn't clear the floor regardless of interview performance."}],
        next_interview_date=None,
        stages=["Stage 1 – 2026-05-26 – Recruiter screen – positive, moved forward",
                "Stage 2 – 2026-06-10 – Hiring manager interview – positive, but comp band confirmed below floor immediately after; withdrew same week"],
    ),
]


def slugify(name):
    return "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")
    # collapse repeated dashes


def write_simple(app):
    (date, company, role, status, tier, jd_fit, seniority, competition, comp, blockers,
     estimated, comp_band, source, note, rationale) = app
    score = jd_fit + seniority + competition + comp + blockers
    slug = slugify(company)
    fname = f"{date}-{slug}-{slugify(role)}.md"
    est = json.dumps(estimated)
    comp_band_yaml = f'"{comp_band}"' if comp_band else "null"
    date_applied = "null" if status in ("scored", "didnt_apply") else date
    locked = "true" if should_lock(status) else "false"
    r_jd_fit, r_seniority, r_competition, r_comp, r_blockers = rationale
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
- JD fit ({jd_fit}/45): {r_jd_fit}
- Seniority alignment ({seniority}/15): {r_seniority}
- Competition estimate ({competition}/20): {r_competition}
- Compensation alignment ({comp}/10): {r_comp}
- Blockers ({blockers}/10): {r_blockers}

## Caveats
{"Competition and/or comp estimated – see estimated_fields above." if estimated else "No estimated fields; all components scored against confirmed information."}
"""
    with open(os.path.join(APPS_DIR, fname), "w", encoding="utf-8") as f:
        f.write(fm)


def usps_md(items):
    return "\n".join(f"- **{i['title']}.** {i['body']}" for i in items)


def region_table_md(regions):
    if not regions:
        return ""
    header = "| Region | Relationship style | Decision style | Key nuances |"
    sep = "|---|---|---|---|"
    rows = "\n".join(
        f"| {r['region']} | {r['relationship_style']} | {r['decision_style']} | {r['nuances']} |"
        for r in regions
    )
    return f"{header}\n{sep}\n{rows}"


def profiles_md(profiles):
    blocks = []
    for p in profiles:
        title_part = f" – {p['title']}" if p.get("title") else ""
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
    score = app["jd_fit"] + app["seniority"] + app["competition"] + app["comp"] + app["blockers"]
    r = app["rationale"]

    watch_section = (
        usps_md(app["watch_bullets"]) if app.get("watch_bullets") else app.get("watch", "")
    )
    region_table = region_table_md(app.get("regional_intelligence"))
    region_section = f"\n### Regional intelligence\n{region_table}\n" if region_table else ""

    fm = f"""---
company: "{app['company']}"
role: "{app['role']}"
date_scored: {app['date']}
date_applied: {app['date']}
status: {app['status']}
status_date: {app['status_date']}
source: "{app['source']}"

score:
  value: {score}
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
- JD fit ({app['jd_fit']}/45): {r['jd_fit']}
- Seniority alignment ({app['seniority']}/15): {r['seniority']}
- Competition estimate ({app['competition']}/20): {r['competition']}
- Compensation alignment ({app['comp']}/10): {r['comp']}
- Blockers ({app['blockers']}/10): {r['blockers']}

## Caveats
{"Comp estimated pending confirmation." if "comp" in app["estimated_fields"] else "No estimated fields."}

## Briefing pack

### Company facts
{app['company']} – {app['company_size']}, {app['funding']}. See `examples/companies/{slug}.json` for the cached source.
{region_section}
### Compensation
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
