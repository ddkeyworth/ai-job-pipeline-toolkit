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

4. Every example application's score.value equals the sum of its own
   score.breakdown. These were hand-typed independently of each other once
   and drifted apart on a large fraction of the dataset before this check
   existed (see TESTING.md) - now impossible to reintroduce silently, since
   generate_examples.py itself computes score.value from the breakdown
   rather than accepting it as a separate input.

5. Every example application's Score rationale has exactly five lines (one
   per component) and none of them is a bare restatement of the score
   (e.g. "JD fit: 38/45" with nothing else) - the exact gap that made this
   section invisible-but-also-empty-of-content before it was fixed.

6. build_dashboard.py's inject_data() survives a value with an embedded
   newline without corrupting the surrounding JSON, and correctly swaps both
   the banner subtitle and the page title. The newline bug (re.sub()
   reinterpreting \n in a plain-string replacement as an escape, turning a
   valid JSON string into a raw, syntax-breaking newline) was diagnosed once
   already, live, in a Claude.ai session - but the fix was only ever applied
   in that session's own inline reimplementation, never committed to this
   script. It stayed dormant because no example field happened to contain a
   literal newline; a real user's data plausibly would. The subtitle and
   title are required arguments to inject_data() precisely so a real user's
   dashboard can't silently inherit the demo's "no real job search data"
   disclaimer or "example dashboard" tab title - this check confirms both
   swaps actually happen rather than just asserting the parameters exist.
   The title tag specifically was missed once already even after the
   subtitle fix shipped - caught only when pointed out, not proactively -
   which is exactly why it's a required parameter now rather than a second
   reminder sentence to remember. A second, separate title bug shipped after
   that fix: a <!--__TITLE__--> marker pair, copying the subtitle's pattern,
   rendered as literal visible text in the browser tab on the live public
   demo, because <title> is an HTML raw-text element where comment syntax
   isn't parsed as a comment - unlike the subtitle's <div>, where it works
   correctly. Fixed by matching <title>...</title> directly instead, with no
   marker needed since the tag itself is unique. This check now also asserts
   no "__TITLE__" string ever appears in the output, closing that bug class.

7. Every example past "scored"/"didnt_apply" (see _status.py's HAS_APPLIED)
   has at_application_score set - SCHEMA.md requires it never be left blank
   once an application actually went out, so the dashboard's at-application
   sort has no gaps. And for every example with at_application_score,
   competition/comp/blockers exactly match score.breakdown - they're carried
   over unchanged by design (only jd_fit/seniority are ever recomputed), so a
   mismatch here would mean either a scoring bug or a value that quietly
   drifted from its source, the same class of bug check 4 above guards
   against for score.value/score.breakdown.

Run from the repo root: python scripts/verify_consistency.py
Exits 1 on any mismatch.
"""
import json
import os
import pathlib
import re
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _status import ALL_STATUSES, REACHED_INTERVIEW, NO_INTERVIEW_NEGATIVE, HAS_APPLIED
from build_dashboard import (
    extract_bp_section,
    inject_data,
    parse_application,
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
APPS_DIR = os.path.join(ROOT, "examples", "applications")
COMPONENTS = ["jd_fit", "seniority", "competition", "comp", "blockers"]
# A rationale line that's just "Label (N/45):" or "Label: N/45" with nothing
# after the score - i.e. it tells the reader nothing the breakdown numbers
# above it don't already show.
THIN_RATIONALE_RE = re.compile(r"^-\s+.+?\(?\d+\s*/\s*\d+\)?:?\s*$", re.MULTILINE)

# heading -> a function that should return truthy content for SCHEMA.md's example
CHECKS = {
    "Company facts": lambda bp: extract_bp_section(bp, "Company facts"),
    "Regional intelligence": lambda bp: parse_table(extract_bp_section(bp, "Regional intelligence")),
    "Compensation": lambda bp: extract_bp_section(bp, "Compensation"),
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


def load_example_applications():
    apps = []
    for fname in sorted(os.listdir(APPS_DIR)):
        if not fname.endswith(".md"):
            continue
        text = open(os.path.join(APPS_DIR, fname), encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
        fm = yaml.safe_load(m.group(1))
        apps.append((fname, fm, m.group(2)))
    return apps


def check_example_score_sums():
    apps = load_example_applications()
    ok = True
    for fname, fm, body in apps:
        breakdown = fm["score"]["breakdown"]
        total = sum(breakdown[c] for c in COMPONENTS)
        if total != fm["score"]["value"]:
            print(f"FAIL: {fname} - score.value ({fm['score']['value']}) doesn't equal the sum of its own breakdown ({total}).")
            ok = False
    if ok:
        print(f"All {len(apps)} example applications' score.value matches the sum of their own breakdown.")
    return ok


def check_example_rationale_not_thin():
    apps = load_example_applications()
    ok = True
    for fname, fm, body in apps:
        m = re.search(r"##\s+Score rationale\s*\n(.*?)(?=\n##\s|\Z)", body, re.DOTALL)
        rationale_text = m.group(1) if m else ""
        lines = [l for l in rationale_text.splitlines() if l.strip().startswith("-")]
        if len(lines) != len(COMPONENTS):
            print(f"FAIL: {fname} - Score rationale should have exactly {len(COMPONENTS)} lines (one per component), found {len(lines)}.")
            ok = False
        if THIN_RATIONALE_RE.search(rationale_text):
            print(f"FAIL: {fname} - Score rationale has a line that only restates the score, no real reasoning.")
            ok = False
    if ok:
        print(f"All {len(apps)} example applications' Score rationale has {len(COMPONENTS)} real, non-thin lines.")
    return ok


def check_at_application_score():
    apps = load_example_applications()
    ok = True
    for fname, fm, body in apps:
        status = fm["status"]
        at_score = fm.get("at_application_score")
        if status in HAS_APPLIED and at_score is None:
            print(f"FAIL: {fname} - status {status!r} means an application went out, but at_application_score is unset.")
            ok = False
            continue
        if at_score is None:
            continue
        breakdown = at_score["breakdown"]
        total = sum(breakdown[c] for c in COMPONENTS)
        if total != at_score["value"]:
            print(f"FAIL: {fname} - at_application_score.value ({at_score['value']}) doesn't equal the sum of its own breakdown ({total}).")
            ok = False
        score_breakdown = fm["score"]["breakdown"]
        for c in ("competition", "comp", "blockers"):
            if breakdown[c] != score_breakdown[c]:
                print(f"FAIL: {fname} - at_application_score.breakdown.{c} ({breakdown[c]}) should be carried over unchanged from score.breakdown.{c} ({score_breakdown[c]}).")
                ok = False
    if ok:
        print(f"All {len(apps)} example applications' at_application_score is present wherever required and internally consistent.")
    return ok


def check_duplicate_note_excluded():
    """A file with `_duplicate_note` set (see schema/SCHEMA.md) must be excluded from
    the dashboard build - parse_application() returns None for it, main() filters
    those out. Written to a temp file outside APPS_DIR so it can't be picked up by
    the other checks above, which scan APPS_DIR directly."""
    import tempfile
    content = (
        "---\n"
        'company: "Acme Corp"\n'
        'role: "VP, Customer Success"\n'
        "date_scored: 2026-01-01\n"
        "date_applied: null\n"
        "status: scored\n"
        "status_date: 2026-01-01\n"
        'source: "LinkedIn"\n'
        '_duplicate_note: "Duplicate of some-other-file.md"\n'
        "\n"
        "score:\n"
        "  value: 50\n"
        '  tier: "Tier 3 – Solid, worth applying"\n'
        "  locked: false\n"
        "  breakdown:\n"
        "    jd_fit: 20\n"
        "    seniority: 10\n"
        "    competition: 10\n"
        "    comp: 5\n"
        "    blockers: 5\n"
        "  estimated_fields: []\n"
        "\n"
        "next_interview_date: null\n"
        "comp_band: null\n"
        "---\n"
        "\n"
        "## JD summary\nTest.\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(content)
        temp_path = f.name
    try:
        result = parse_application(temp_path)
    finally:
        os.remove(temp_path)

    if result is not None:
        print(f"FAIL: parse_application() returned a value for a file with _duplicate_note set - should return None so it's excluded from the dashboard. Got: {result!r}")
        return False

    print("parse_application() correctly excludes a file with _duplicate_note set (returns None).")
    return True


def check_dashboard_injection_survives_embedded_newline():
    html = (
        "PREFIX /*__DATA__*/OLD/*__END_DATA__*/ "
        "<!--__SUBTITLE__-->OLD SUBTITLE<!--__END_SUBTITLE__--> "
        "<!--__CROSSLINK__--><!--__END_CROSSLINK__--> "
        "<title>OLD TITLE</title> SUFFIX"
    )
    apps = [{"id": "test", "notes": "Line one.\nLine two."}]
    new_html = inject_data(html, apps, "Your real tracked applications.", "Your Job Pipeline")

    m = re.search(r"/\*__DATA__\*/(.*?)/\*__END_DATA__\*/", new_html, re.DOTALL)
    try:
        parsed = json.loads(m.group(1))
    except Exception as e:
        print(f"FAIL: inject_data() corrupted a value containing an embedded newline - {e}")
        return False
    if parsed != apps:
        print(f"FAIL: inject_data() round-tripped the data incorrectly - got {parsed!r}, expected {apps!r}")
        return False

    if "Your real tracked applications." not in new_html or "OLD SUBTITLE" in new_html:
        print("FAIL: inject_data() did not correctly swap the banner subtitle.")
        return False

    if "<title>Your Job Pipeline</title>" not in new_html or "OLD TITLE" in new_html:
        print("FAIL: inject_data() did not correctly swap the page title.")
        return False

    if "__TITLE__" in new_html:
        print("FAIL: a <!--__TITLE__--> marker leaked into the output - this renders as literal visible "
              "text in a browser tab, since <title> is a raw-text element where comment syntax isn't "
              "parsed as a comment. This exact bug shipped once already (see TESTING.md).")
        return False

    if "<a href=" in new_html:
        print("FAIL: inject_data() rendered a cross-link with no cross_link_path given - should be empty.")
        return False

    # Absolute path valid on whatever OS is actually running this (Windows locally, Ubuntu in CI) -
    # this exists specifically so the test doesn't assume one platform's path conventions.
    test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "other-copy", "index.html")
    expected_href = pathlib.Path(test_path).as_uri()
    linked_html = inject_data(
        html, apps, "Your real tracked applications.", "Your Job Pipeline",
        cross_link_path=test_path, cross_link_label="Other copy",
    )
    if f'href="{expected_href}"' not in linked_html:
        print("FAIL: inject_data() did not build a correct file:// URI from cross_link_path.")
        return False
    if "Other copy" not in linked_html:
        print("FAIL: inject_data() did not use the given cross_link_label.")
        return False

    print("build_dashboard.py's inject_data() survives an embedded newline, swaps the subtitle and title correctly, and builds a correct cross-link when given a path.")
    return True


def main():
    ok = (
        check_schema_docs()
        and check_status_order()
        and check_recalibration_sets()
        and check_example_score_sums()
        and check_example_rationale_not_thin()
        and check_at_application_score()
        and check_duplicate_note_excluded()
        and check_dashboard_injection_survives_embedded_newline()
    )
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
