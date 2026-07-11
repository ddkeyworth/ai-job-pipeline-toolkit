#!/usr/bin/env python3
"""
Consistency checks that nothing else in CI catches:

1. SCHEMA.md's own documented Briefing pack example is round-tripped through
   the real parser (scripts/build_dashboard.py's extract_bp_section() and
   friends) – every heading the docs claim is supported must actually parse
   to non-empty content. This exists because that exact class of bug shipped
   once already this session: SCHEMA.md documented "### Why it progressed /
   didn't" while the parser looked for the exact string "Why it progressed",
   and nothing caught the mismatch until it was found by hand.

2. docs/index.html's JS STATUS_ORDER array is regex-extracted and compared
   against scripts/_status.py's ALL_STATUSES – the Python and JS sides of the
   status vocabulary have no shared import (one's a script, one's browser
   JS), so nothing else would catch them drifting apart.

3. docs/index.html's JS REACHED_INTERVIEW / NO_INTERVIEW_NEGATIVE arrays
   (used by the dashboard's headline "Interviewed"/"Rejected" counts) are
   compared against scripts/_status.py's sets of the same name – same drift
   risk as (2), for the headline stats added alongside the status vocabulary
   simplification.

Run from the repo root: python scripts/verify_consistency.py
Exits 1 on any mismatch.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _status import ALL_STATUSES, REACHED_INTERVIEW, NO_INTERVIEW_NEGATIVE
from build_dashboard import (
    extract_bp_section,
    parse_bullet_pairs,
    parse_interviewer_profiles,
    parse_notes,
    parse_plain_bullets,
    parse_qa,
    parse_table,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(ROOT, "schema", "SCHEMA.md")
DASHBOARD_PATH = os.path.join(ROOT, "docs", "index.html")

# heading -> a function that should return truthy content for SCHEMA.md's example
CHECKS = {
    "Company facts": lambda bp: extract_bp_section(bp, "Company facts"),
    "Regional intelligence": lambda bp: parse_table(extract_bp_section(bp, "Regional intelligence")),
    "Comp": lambda bp: extract_bp_section(bp, "Comp"),
    "Why it progressed / didn't": lambda bp: extract_bp_section(bp, "Why it progressed / didn't"),
    "Unique selling points": lambda bp: parse_bullet_pairs(extract_bp_section(bp, "Unique selling points")),
    "Interviewer profiles": lambda bp: parse_interviewer_profiles(extract_bp_section(bp, "Interviewer profiles")),
    "Prep questions": lambda bp: parse_qa(extract_bp_section(bp, "Prep questions")),
    "Questions to ask": lambda bp: parse_plain_bullets(extract_bp_section(bp, "Questions to ask")),
    "Watch-outs": lambda bp: extract_bp_section(bp, "Watch-outs"),
    "Notes": lambda bp: parse_notes(extract_bp_section(bp, "Notes")),
    "Interview stage log": lambda bp: extract_bp_section(bp, "Interview stage log"),
}


def check_schema_docs():
    schema_text = open(SCHEMA_PATH, encoding="utf-8").read()
    m = re.search(r"```markdown\n(## Briefing pack\n.*?)\n```", schema_text, re.DOTALL)
    if not m:
        print("FAIL: could not find the fenced Briefing pack example in SCHEMA.md.")
        return False

    bp_full = m.group(1)
    bp_match = re.search(r"##\s+Briefing pack\s*\n(.*)$", bp_full, re.DOTALL)
    bp_text = bp_match.group(1) if bp_match else ""

    failures = []
    for heading, check in CHECKS.items():
        result = check(bp_text)
        if not result:
            failures.append(heading)

    if failures:
        print(f"FAIL: SCHEMA.md documents these headings but the real parser returns nothing for them: {failures}")
        return False

    print(f"SCHEMA.md's Briefing pack example round-trips correctly through the parser ({len(CHECKS)} sections checked).")
    return True


def check_status_order():
    html = open(DASHBOARD_PATH, encoding="utf-8").read()
    m = re.search(r"const STATUS_ORDER\s*=\s*\[(.*?)\];", html, re.DOTALL)
    if not m:
        print("FAIL: could not find STATUS_ORDER in docs/index.html.")
        return False

    js_statuses = re.findall(r'"([a-z_]+)"', m.group(1))

    if js_statuses != ALL_STATUSES:
        print("FAIL: docs/index.html's STATUS_ORDER doesn't match scripts/_status.py's ALL_STATUSES.")
        print(f"  docs/index.html: {js_statuses}")
        print(f"  _status.py:      {ALL_STATUSES}")
        return False

    print(f"docs/index.html's STATUS_ORDER matches scripts/_status.py's ALL_STATUSES ({len(ALL_STATUSES)} statuses).")
    return True


def check_recalibration_sets():
    html = open(DASHBOARD_PATH, encoding="utf-8").read()
    ok = True
    for js_name, py_set in (("REACHED_INTERVIEW", REACHED_INTERVIEW), ("NO_INTERVIEW_NEGATIVE", NO_INTERVIEW_NEGATIVE)):
        m = re.search(rf"const {js_name}\s*=\s*\[(.*?)\];", html, re.DOTALL)
        if not m:
            print(f"FAIL: could not find {js_name} in docs/index.html.")
            ok = False
            continue
        js_set = set(re.findall(r'"([a-z_]+)"', m.group(1)))
        if js_set != py_set:
            print(f"FAIL: docs/index.html's {js_name} doesn't match scripts/_status.py's {js_name}.")
            print(f"  docs/index.html: {sorted(js_set)}")
            print(f"  _status.py:      {sorted(py_set)}")
            ok = False

    if ok:
        print("docs/index.html's REACHED_INTERVIEW and NO_INTERVIEW_NEGATIVE match scripts/_status.py.")
    return ok


def main():
    ok = check_schema_docs() and check_status_order() and check_recalibration_sets()
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
