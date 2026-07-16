# Golden set — scoring eval

Five fictional job descriptions, each scored against `examples/CV-example.md` (Jordan Ainsley), chosen to exercise a distinct failure/success mode in the rubric — not just five similar "good fit" roles. Expected bands are defined here, in writing, **before** any actual scoring run against them — see `eval/results/` for what an actual run produced, and `scripts/verify_eval_results.py` for how the two get compared.

Company facts are given directly in each JD's own text (not left to live search) since these are fictional companies with nothing real to look up — this keeps the eval self-contained and repeatable without depending on search results that could change over time.

Reference persona: Jordan Ainsley — Product leader, ~9 years, Head of Product at a mid-size B2B SaaS company, 0-to-1 product-line experience, led cross-functional teams of 6-12, comp floor £110,000, Head of Product/Director level (occasionally VP at smaller companies), UK right to work, no restrictions.

---

## 1. Verdant Analytics — Head of Product

**JD:** Verdant Analytics is a 35-person, privately-held, seed/Series A data-analytics startup building a usage-based analytics platform for mid-market SaaS companies. We're hiring a Head of Product to own the roadmap end-to-end, lead a small cross-functional team (currently 8 people across product, design, and a rotating engineering liaison), and take the product from early traction (40 paying accounts) to its next stage of growth. You'll report directly to the CEO. We're looking for someone with a proven track record building 0-to-1 product lines in B2B SaaS and leading small, senior teams without a lot of process overhead. Comp: £115,000–£130,000 OTE, negotiable. UK-based, hybrid, no visa sponsorship needed for right-to-work-holders (not applicable here).

**Expected band:** Near-ideal fit on every axis — small unknown company (low competition draw), direct 0-to-1/small-team match, comp above floor, no blockers.
- `jd_fit`: 38–45
- `seniority`: 13–15
- `competition`: 15–20
- `comp`: 10 (confirmed above floor)
- `blockers`: 10
- **Total band: 86–100, Tier 1**

## 2. Helios Systems Corp — Director of Product

**JD:** Helios Systems Corp is a publicly-traded enterprise software company (NYSE-listed, ~11,000 employees globally) serving Fortune 500 clients across ERP, supply chain, and finance software. We're hiring a Director of Product for our Finance Cloud division, owning a mature product line with an established roadmap, managing a team of product managers, and working within our established enterprise governance and release-planning processes. Comp not disclosed in this posting. UK-based (London office), hybrid.

**Expected band:** Strong on-paper fit for a Director-level product leader, but this is a large, publicly-traded, famous employer — the rubric scores competition low for scale/brand regardless of role fit, and the "mature product, established process" framing is a real but softer mismatch against Jordan's 0-to-1 background than a hard disqualifier.
- `jd_fit`: 28–37 (real overlap on Director-level product leadership, but 0-to-1 background against a "mature product, established governance" role is a genuine, non-trivial mismatch — not a severe one)
- `seniority`: 12–15
- `competition`: 0–6 (large, famous, publicly-traded employer)
- `comp`: 10 (unconfirmed, never penalised)
- `blockers`: 10
- **Total band: 55–72, Tier 2–3**

## 3. Titan Aerospace Group — VP of Product Strategy

**JD:** Titan Aerospace Group (NASDAQ-listed, ~40,000 employees) is hiring a VP of Product Strategy to lead product organisations across our Commercial Aviation and Defence Systems business units — 50+ product, engineering, and program-management staff in total — with direct P&L ownership of a $200M+ annual revenue line. You'll report to the Chief Strategy Officer and sit on the divisional leadership team. Requires 10+ years leading product organisations at this scale, demonstrated multi-business-unit P&L ownership, and experience operating within a regulated aerospace/defence environment. Comp: highly competitive, specifics on application. UK or US-based.

**Expected band:** A severe stretch upward against Jordan's evidenced scope (teams of 6-12, no P&L ownership, no multi-BU or regulated-aerospace experience evidenced anywhere) — the asymmetric seniority rule should score this near zero regardless of how well anything else lines up, per `SKILL.md` → Step 2 → Seniority alignment. `jd_fit` should also come in only moderate, since the core responsibilities (P&L ownership, multi-BU scope, regulated-industry experience) aren't things Jordan's CV evidences either — this isn't just a title-level gap, the actual job content doesn't match.
- `jd_fit`: 15–26
- `seniority`: 0–3 (severe stretch upward — the one scenario the rubric says should score near zero regardless of everything else)
- `competition`: 0–8 (large, famous, publicly-traded employer)
- `comp`: 10 (unconfirmed, never penalised)
- `blockers`: 6–10 (no confirmed hard blocker stated, but genuinely unclear without more detail — should not be penalised harshly on a soft inference)
- **Total band: 35–55, Tier 4–5**

## 4. Bramston Retail Holdings — Director of Product

**JD:** Bramston Retail Holdings is a mid-size (~600 employee), privately-held retail-technology company building inventory and merchandising software for independent and small-chain retailers. We're hiring a Director of Product to own a product line, lead a team of 7 product/design staff, and continue a 0-to-1 build-out of a new merchandising module launched 18 months ago. Salary: £95,000–£105,000 base, plus a discretionary bonus (typically 10–15%). UK-based, hybrid.

**Expected band:** Strong fit on scope, team size, and 0-to-1 experience — the one real problem is a confirmed salary band that sits below Jordan's £110,000 floor even before considering the bonus, since the rubric scores against base/OTE-equivalent and the base alone is confirmed short.
- `jd_fit`: 35–43
- `seniority`: 12–15
- `competition`: 10–17 (mid-size, privately-held, not a famous brand)
- `comp`: 0–3 (confirmed below floor)
- `blockers`: 10
- **Total band: 67–83, Tier 2–3 (dragged down specifically by the confirmed comp shortfall, not by fit)**

## 5. Meridian Financial Services — Head of Product

**JD:** Meridian Financial Services is a mid-size (~450 employee) regulated financial-services technology provider building compliance and risk-management software for asset managers. We're hiring a Head of Product to own our core platform roadmap, lead a team of 6, and work closely with our regulatory affairs team. **This role requires active FCA-approved Senior Manager Function (SMF) status, or demonstrated near-term eligibility for SMF approval** — this is a hard requirement for this specific role given its regulatory-liaison responsibilities, not a preference. Comp: £120,000–£140,000 OTE. UK-based, hybrid.

**Expected band:** Strong fit on product scope, team size, and comp, but a confirmed hard requirement (FCA SMF status/eligibility) that Jordan's CV doesn't evidence at all — this is a genuine, confirmed blocker distinct from right-to-work, exercising the blockers component on a non-immigration axis.
- `jd_fit`: 34–42
- `seniority`: 12–15
- `competition`: 10–17 (mid-size, not a famous brand)
- `comp`: 10 (confirmed above floor)
- `blockers`: 0–3 (confirmed hard requirement not evidenced in the CV)
- **Total band: 66–87 (regulatory requirement, not aviation-level severity — should still land meaningfully lower than case 1's ideal fit due to the confirmed blocker, but not catastrophically low)**

## 6. Wrenfield Civic Trust — Head of Programme Operations

**JD:** Wrenfield Civic Trust is a growing (~30-person) UK charitable foundation building a new national mentoring programme from the ground up. We're hiring a Head of Programme Operations to own the programme's operating model end-to-end — reporting structures, budget, partner onboarding, impact measurement — and lead a small cross-functional team (7 people across operations, partnerships, and data/impact) as the programme moves from a 3-region pilot (400 participants) toward national rollout. You'll report directly to the Executive Director. We're looking for someone with a proven track record building something from scratch, leading small senior teams without heavy process overhead, and comfortable owning ambiguous, fast-moving scope. Prior nonprofit/charity-sector experience is a plus but not required — we care more about the operating pattern than the sector label. Comp: £85,000–£95,000 base, plus a limited additional pension contribution, negotiable. UK-based, hybrid, no visa sponsorship required for right-to-work holders (not applicable here).

**Why this case exists:** every other case in this set uses a "Product"-titled JD against Jordan's product-titled CV — none of them would catch a regression in the competency-cluster mechanism specifically, since a title-keyword match would already produce the right answer for all five. This case is designed so a naive title/keyword read and the competency-cluster mechanism disagree: "Programme Operations" shares no keyword overlap with "Product," so a title-match read would likely score `jd_fit` in the low-to-mid teens. The JD's actual primary function — own an operating model 0-to-1, lead a similarly-sized cross-functional team, report directly to the top executive, own ambiguous fast-moving scope — is structurally close to Jordan's evidenced pattern (see case 1), and the JD's own text explicitly signals it cares about operating pattern over sector label.

**Expected band:** Meaningfully higher than a title-match read would produce, but genuinely short of an ideal-fit score — there's a real, acknowledged gap: nothing in Jordan's CV evidences nonprofit/charity-sector specifics, only the underlying operating pattern. `jd_fit` should land in a middle band reflecting real credit for the structural match without pretending the sector gap doesn't exist.
- `jd_fit`: 26–35 (real credit for the 0-to-1/cross-functional/direct-to-top-exec operating-pattern match; held back from case 1's range by the complete absence of sector-specific evidence)
- `seniority`: 12–15 (a small-organization exec-adjacent mandate, roughly lateral to Jordan's evidenced level)
- `competition`: 13–20 (small, not a famous brand)
- `comp`: 4–7 (confirmed base range below Jordan's £110,000 floor — sliding-scale shortfall, not extreme)
- `blockers`: 10 (no confirmed hard requirement)
- **Total band: 65–87 (the real test is `jd_fit` specifically — the total band is wide because this case isn't about seniority/competition/comp, which are unaffected by this change)**

---

**Not yet covered by this set:** no case here exercises the recency modifier or the career-break guardrail (`SKILL.md` → Step 2 → JD fit → Recency) — none of the six JDs name a currency-sensitive requirement, and the reference persona has no employment gap. A seventh case pairing a currency-sensitive requirement with a stale-but-reinforced or genuinely-stale piece of evidence, and/or a version of the reference persona with an explained gap, would close that coverage. Flagged, not added yet — see `TESTING.md` Test 27.
