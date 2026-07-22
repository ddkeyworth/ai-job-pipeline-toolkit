#!/usr/bin/env python3
"""
Parses examples/applications/*.md and injects them as embedded JSON into
docs/index.html, between the /*__DATA__*/ and /*__END_DATA__*/ markers.

This is the one-time "build" for the example dashboard published via GitHub
Pages. It is NOT required to use the toolkit day-to-day – when the skill
regenerates your own dashboard from your own tracked applications (see
SKILL.md, Step 5), it does the equivalent of this step itself, inline, as
part of answering you in chat. No npm, no bundler, no toolchain either way.

Run from the repo root: python scripts/build_dashboard.py
"""
import json
import os
import pathlib
import re
import sys
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _status import ALL_STATUSES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS_DIR = os.path.join(ROOT, "examples", "applications")
DASHBOARD = os.path.join(ROOT, "docs", "index.html")


def parse_bullet_pairs(text):
    """- **Title.** Body.  ->  [{"title": ..., "body": ...}]"""
    return [
        {"title": m.group(1).strip(), "body": m.group(2).strip()}
        for m in re.finditer(r"^-\s+\*\*(.+?)\*\*\s*(.*)$", text, re.MULTILINE)
    ]


def parse_plain_bullets(text):
    return [line.strip("- ").strip() for line in text.splitlines() if line.strip().startswith("-")]


def parse_qa(text):
    """**Q: ...?**\nA: answer (optionally multi-line) -> [{"q":..., "a":...}]"""
    return [
        {"q": m.group(1).strip(), "a": m.group(2).strip()}
        for m in re.finditer(r"\*\*Q:\s*(.+?)\*\*\s*\n(?:A:\s*)?(.*?)(?=\n\*\*Q:|\Z)", text, re.DOTALL)
    ]


def parse_interviewer_profiles(text):
    profiles = []
    for m in re.finditer(r"####\s+(.+?)\n(.*?)(?=\n####\s|\Z)", text, re.DOTALL):
        header, block = m.group(1).strip(), m.group(2).strip()
        if "–" in header:
            name, title = (p.strip() for p in header.split("–", 1))
        elif "–" in header:  # backward-compat: older files may still use an em-dash
            name, title = (p.strip() for p in header.split("–", 1))
        elif " - " in header:
            name, title = (p.strip() for p in header.split(" - ", 1))
        else:
            name, title = header, ""
        assessing = re.search(r"\*\*What they're assessing:\*\*\s*(.*?)(?=\n\*\*|\Z)", block, re.DOTALL)
        play_it = re.search(r"\*\*How to play it:\*\*\s*(.*?)(?=\n\*\*|\Z)", block, re.DOTALL)
        background = re.split(r"\n\*\*What they're assessing:|\n\*\*How to play it:", block)[0].strip()
        profiles.append({
            "name": name, "title": title, "background": background,
            "assessing": assessing.group(1).strip() if assessing else "",
            "play_it": play_it.group(1).strip() if play_it else "",
        })
    return profiles


def parse_table(text):
    """Generic markdown table parser. Only lines starting with `|` count as
    the table – everything else (an explanatory note above it, a caveat
    paragraph below it, as in SCHEMA.md's own documented example) is
    prose surrounding the table, not part of it. First `|`-line is the
    header, second is the `---` separator (skipped), the rest are data
    rows. Column names aren't hardcoded (Regional intelligence is the
    first user, but this stays generic rather than assuming specific
    columns like Region/Relationship style/Decision style). Returns None
    if there's no table – this section is genuinely optional, unlike the
    five standard ones, so "absent" is a real, expected state, not a gap
    to placeholder-fill."""
    table_lines = [l.strip() for l in text.strip().splitlines() if l.strip().startswith("|")]
    if len(table_lines) < 2:
        return None

    def cells(line):
        return [c.strip() for c in line.strip().strip("|").split("|")]

    headers = cells(table_lines[0])
    rows = [cells(l) for l in table_lines[2:]]  # table_lines[1] is the --- separator
    return {"headers": headers, "rows": rows}


def extract_bp_section(bp_text, heading):
    """Pull one ###-level section's body out of a Briefing pack's raw text.
    Exact heading match – module-level (not nested) so scripts/verify_consistency.py
    can import this same function to round-trip SCHEMA.md's documented headings
    against the real parser, rather than a second, independently-drifting regex."""
    pat = rf"###\s+{re.escape(heading)}\s*\n(.*?)(?=\n###\s|\Z)"
    sm = re.search(pat, bp_text, re.DOTALL)
    return sm.group(1).strip() if sm else ""


def parse_notes(text):
    """Light structural split only – no semantic parsing. Returns
    [{"heading": str|None, "body": str}, ...]."""
    if not text.strip():
        return []
    if "#### " not in text:
        return [{"heading": None, "body": text.strip()}]
    return [
        {"heading": m.group(1).strip(), "body": m.group(2).strip()}
        for m in re.finditer(r"####\s+(.+?)\n(.*?)(?=\n####\s|\Z)", text, re.DOTALL)
    ]


def parse_application(path):
    """Returns None for a file with `_duplicate_note` set (see schema/SCHEMA.md) - a
    confirmed-after-the-fact duplicate, kept on disk as an audit trail but never shown
    on the dashboard. Callers must filter out None results (see main() below)."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        raise ValueError(f"No frontmatter found in {path}")
    frontmatter_raw, body = m.group(1), m.group(2)
    fm = yaml.safe_load(frontmatter_raw)

    if fm.get("_duplicate_note"):
        return None

    status = fm["status"]
    if status not in ALL_STATUSES:
        raise ValueError(f"{path}: unknown status {status!r} – must be one of {ALL_STATUSES}")

    def section(heading):
        pat = rf"##\s+{re.escape(heading)}\s*\n(.*?)(?=\n##\s|\Z)"
        sm = re.search(pat, body, re.DOTALL)
        return sm.group(1).strip() if sm else None

    jd_summary = section("JD summary") or ""
    # Structurally a one-line-per-component bulleted list (see SCHEMA.md),
    # not prose - parsed into a list and rendered as bullets (renderQuestions
    # in docs/index.html), same as Questions to ask, rather than squashed
    # into a single <p> the way jd_summary/caveats are.
    score_rationale = parse_plain_bullets(section("Score rationale") or "")
    caveats = section("Caveats") or ""

    app_id = os.path.splitext(os.path.basename(path))[0]

    briefing = None
    if "## Briefing pack" in body:
        bp_match = re.search(r"##\s+Briefing pack\s*\n(.*)$", body, re.DOTALL)
        bp_text = bp_match.group(1) if bp_match else ""

        def bp_section(heading):
            return extract_bp_section(bp_text, heading)

        stage_log_text = bp_section("Interview stage log")
        stages = [line.strip("- ").strip() for line in stage_log_text.splitlines() if line.strip().startswith("-")]

        watch_text = bp_section("Watch-outs")
        watch_bullets = parse_bullet_pairs(watch_text)

        briefing = {
            "company_facts": bp_section("Company facts"),
            "regional_intelligence": parse_table(bp_section("Regional intelligence")),
            "comp": bp_section("Compensation"),
            "why": bp_section("Why it progressed / didn't"),
            "watch": watch_text if not watch_bullets else "",
            "watch_bullets": watch_bullets,
            "usps": parse_bullet_pairs(bp_section("Unique selling points")),
            "interviewer_profiles": parse_interviewer_profiles(bp_section("Interviewer profiles")),
            "prep_qa": parse_qa(bp_section("Prep questions")),
            "questions_to_ask": parse_plain_bullets(bp_section("Questions to ask")),
            "notes": parse_notes(bp_section("Notes")),
            "stages": stages,
        }

    def date_str(v):
        if v is None:
            return None
        return v.isoformat() if hasattr(v, "isoformat") else str(v)

    return {
        "id": app_id,
        "company": fm["company"],
        "role": fm["role"],
        "date_scored": date_str(fm.get("date_scored")),
        "date_applied": date_str(fm.get("date_applied")),
        "status": status,
        "status_date": date_str(fm.get("status_date")),
        "score": fm["score"],
        "at_application_score": fm.get("at_application_score"),
        "next_interview_date": date_str(fm.get("next_interview_date")),
        "comp_band": fm.get("comp_band"),
        "application_materials": fm.get("application_materials"),
        "jd_summary": jd_summary,
        "score_rationale": score_rationale,
        "caveats": caveats,
        "briefing": briefing,
    }


def inject_data(html, apps, subtitle, title, cross_link_path=None, cross_link_label=None):
    """Splice apps (a list of application dicts) into html's /*__DATA__*/.../*__END_DATA__*/
    markers, set the banner subtitle via its own <!--__SUBTITLE__--> marker pair, and set the
    browser-tab title by replacing <title>...</title> directly - not via a marker pair like
    the subtitle, because <title> is an HTML "raw text" element: content inside it is never
    parsed as markup at all, so HTML comment syntax doesn't get hidden the way it does inside
    a normal element like the subtitle's <div>. A <!--__TITLE__--> marker previously used here
    rendered as literal visible text in the browser tab on the live public demo - a real,
    shipped bug, not a hypothetical one. <title> is unique in a valid HTML document, so no
    marker is needed: matching the tag itself is both simpler and actually correct. Shared by
    main() and scripts/verify_consistency.py's regression test, so the exact code path that
    ships is the one that's tested - not a second reimplementation.

    subtitle and title are required arguments, not defaults, on purpose: docs/index.html's
    committed text ("Fictional companies... No real job search data", "...example dashboard")
    is only true for the public GitHub Pages demo built from examples/. When a live
    Claude.ai/Cowork session builds this same template for a real user's own real data, both
    become false - and relying on whoever's generating it to remember to edit text buried in
    a 700-line HTML file is exactly the kind of memory-based fix this repo has moved away
    from elsewhere (see score.value, check_example_score_sums). Making both required
    parameters forces the caller to decide, rather than silently inheriting the demo's text -
    the title tag specifically was missed once already (fixed live only after being pointed
    out, not caught proactively), which is exactly the failure mode requiring it here guards
    against.

    Replacement passed as a function, not a string - re.sub() reinterprets backslash
    sequences (e.g. \\n) in a plain-string replacement as backreferences/escapes, silently
    corrupting any JSON string value that contains an embedded newline into a raw newline
    (which breaks the embedded JSON). A lambda sidesteps that reinterpretation entirely.
    This was previously diagnosed and worked around live in a Claude.ai session (see
    TESTING.md) but never actually fixed here - dormant only because no example field
    happened to contain a literal newline; real user data very plausibly would.

    cross_link_path is optional (unlike subtitle/title) - when a Cowork session maintains
    two local copies of the dashboard with the same content (a durably-pinned Artifact and
    a plain outputs-folder file, confirmed to happen in real use - see TESTING.md), this
    renders the smallest possible link to the other's file path, fixed in the page's
    top-right corner - no explanatory sentence, not even a word by default (just an arrow
    glyph; the full explanation lives in the link's title tooltip, shown on hover). Meant
    to sit below normal reading attention - it's a useful aid, not something that needs
    to be noticed. Takes a plain OS path, not a URL - pathlib builds the file:// URI here
    so the caller never has to hand-construct one (Windows paths need backslash-to-slash
    conversion and a specific number of leading slashes to be valid; getting that wrong by
    hand is exactly the class of bug this repo has moved away from elsewhere). Left empty
    (the default) when there's only one copy - the marker then renders nothing and the
    :empty CSS rule collapses it entirely.
    """
    data_json = json.dumps(apps, ensure_ascii=False, indent=2)
    html = re.sub(
        r"/\*__DATA__\*/.*?/\*__END_DATA__\*/",
        lambda m: f"/*__DATA__*/{data_json}/*__END_DATA__*/",
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"<!--__SUBTITLE__-->.*?<!--__END_SUBTITLE__-->",
        lambda m: f"<!--__SUBTITLE__-->{subtitle}<!--__END_SUBTITLE__-->",
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"<title>.*?</title>",
        lambda m: f"<title>{title}</title>",
        html,
        flags=re.DOTALL,
    )
    if cross_link_path:
        link_href = pathlib.Path(cross_link_path).as_uri()
        link_label = cross_link_label if cross_link_label is not None else "&#8599;"
        cross_link_html = f'<a href="{link_href}" title="Also viewable at another local copy of this dashboard">{link_label}</a>'
    else:
        cross_link_html = ""
    html = re.sub(
        r"<!--__CROSSLINK__-->.*?<!--__END_CROSSLINK__-->",
        lambda m: f"<!--__CROSSLINK__-->{cross_link_html}<!--__END_CROSSLINK__-->",
        html,
        flags=re.DOTALL,
    )
    return html


DEMO_SUBTITLE = (
    'Fictional companies and applications, built to demonstrate the tool. '
    'No real job search data. See <code>README.md</code> to use your own.'
)
DEMO_TITLE = "Job Pipeline Toolkit – example dashboard"


def main():
    apps = []
    for fname in sorted(os.listdir(APPS_DIR)):
        if fname.endswith(".md"):
            app = parse_application(os.path.join(APPS_DIR, fname))
            if app is not None:  # None = a confirmed duplicate, excluded - see parse_application()
                apps.append(app)

    with open(DASHBOARD, "r", encoding="utf-8") as f:
        html = f.read()

    new_html = inject_data(html, apps, DEMO_SUBTITLE, DEMO_TITLE)

    with open(DASHBOARD, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"Injected {len(apps)} applications into {DASHBOARD}")


if __name__ == "__main__":
    main()
