#!/usr/bin/env python3
"""
Parses examples/applications/*.md and injects them as embedded JSON into
docs/index.html, between the /*__DATA__*/ and /*__END_DATA__*/ markers.

This is the one-time "build" for the example dashboard published via GitHub
Pages. It is NOT required to use the toolkit day-to-day — when the skill
regenerates your own dashboard from your own tracked applications (see
SKILL.md, Step 5), it does the equivalent of this step itself, inline, as
part of answering you in chat. No npm, no bundler, no toolchain either way.

Run from the repo root: python scripts/build_dashboard.py
"""
import json
import os
import re
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS_DIR = os.path.join(ROOT, "examples", "applications")
DASHBOARD = os.path.join(ROOT, "docs", "index.html")


def parse_application(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        raise ValueError(f"No frontmatter found in {path}")
    frontmatter_raw, body = m.group(1), m.group(2)
    fm = yaml.safe_load(frontmatter_raw)

    def section(heading):
        pat = rf"##\s+{re.escape(heading)}\s*\n(.*?)(?=\n##\s|\Z)"
        sm = re.search(pat, body, re.DOTALL)
        return sm.group(1).strip() if sm else None

    jd_summary = section("JD summary") or ""
    caveats = section("Caveats") or ""

    app_id = os.path.splitext(os.path.basename(path))[0]

    briefing = None
    if "## Briefing pack" in body:
        bp_match = re.search(r"##\s+Briefing pack\s*\n(.*)$", body, re.DOTALL)
        bp_text = bp_match.group(1) if bp_match else ""

        def bp_section(heading):
            pat = rf"###\s+{re.escape(heading)}\s*\n(.*?)(?=\n###\s|\Z)"
            sm = re.search(pat, bp_text, re.DOTALL)
            return sm.group(1).strip() if sm else ""

        stage_log_text = bp_section("Interview stage log")
        stages = [line.strip("- ").strip() for line in stage_log_text.splitlines() if line.strip().startswith("-")]

        briefing = {
            "company_facts": bp_section("Company facts"),
            "comp": bp_section("Comp"),
            "why": bp_section("Why it progressed"),
            "watch": bp_section("Watch-outs"),
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
        "status": fm["status"],
        "score": fm["score"],
        "outcome": fm.get("outcome"),
        "comp_band": fm.get("comp_band"),
        "jd_summary": jd_summary,
        "caveats": caveats,
        "briefing": briefing,
    }


def main():
    apps = []
    for fname in sorted(os.listdir(APPS_DIR)):
        if fname.endswith(".md"):
            apps.append(parse_application(os.path.join(APPS_DIR, fname)))

    data_json = json.dumps(apps, ensure_ascii=False, indent=2)

    with open(DASHBOARD, "r", encoding="utf-8") as f:
        html = f.read()

    new_html = re.sub(
        r"/\*__DATA__\*/.*?/\*__END_DATA__\*/",
        f"/*__DATA__*/{data_json}/*__END_DATA__*/",
        html,
        flags=re.DOTALL,
    )

    with open(DASHBOARD, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"Injected {len(apps)} applications into {DASHBOARD}")


if __name__ == "__main__":
    main()
