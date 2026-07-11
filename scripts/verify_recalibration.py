#!/usr/bin/env python3
"""
Reproducible check for the recalibration agent's underlying computation
(SKILL.md, Step 6) against whatever is currently in examples/applications/.

This is the mechanical, non-LLM part of the recalibration agent — reading
logged outcomes and computing per-component positive/negative score means.
Making this a real script (not a one-off calculation in TESTING.md) means
it's re-verified on every push via CI, not just checked once by hand.

The LLM-interpreted parts of SKILL.md (actual scoring, live-search
verification) aren't reproducible this way — they need an independent
Claude session run, not a script. See TESTING.md for what this does and
doesn't prove.

Run from the repo root: python scripts/verify_recalibration.py
Exits 1 if the gate no longer passes against the current example data, so a
future edit to examples/ that breaks the demo's own premise gets caught.
"""
import json
import os
import re
import statistics
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _status import recalibration_signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS_DIR = os.path.join(ROOT, "examples", "applications")
WEIGHTS_PATH = os.path.join(ROOT, "config", "weights.json")

COMPONENTS = ["jd_fit", "seniority", "competition", "comp", "blockers"]


def load_applications():
    apps = []
    for fname in sorted(os.listdir(APPS_DIR)):
        if not fname.endswith(".md"):
            continue
        text = open(os.path.join(APPS_DIR, fname), encoding="utf-8").read()
        fm = yaml.safe_load(re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL).group(1))
        apps.append(fm)
    return apps


def main():
    weights = json.load(open(WEIGHTS_PATH, encoding="utf-8"))
    min_logged = weights["recalibration"]["min_logged_outcomes"]
    min_positive = weights["recalibration"]["min_positive_outcomes"]

    apps = load_applications()
    signals = [(a, recalibration_signal(a["status"])) for a in apps]
    logged = [a for a, sig in signals if sig is not None]
    positive = [a for a, sig in signals if sig == "positive"]
    negative = [a for a, sig in signals if sig == "negative"]

    gate_passes = len(logged) >= min_logged and len(positive) >= min_positive

    print(f"Total applications: {len(apps)}")
    print(f"Logged outcomes: {len(logged)} (threshold: {min_logged})")
    print(f"Positive outcomes: {len(positive)} (threshold: {min_positive})")
    print(f"Gate: {'PASS' if gate_passes else 'BELOW THRESHOLD'}")
    print()

    no_variance = []
    for c in COMPONENTS:
        pos_vals = [a["score"]["breakdown"][c] for a in positive]
        neg_vals = [a["score"]["breakdown"][c] for a in negative]
        all_vals = pos_vals + neg_vals
        pos_mean = statistics.mean(pos_vals) if pos_vals else float("nan")
        neg_mean = statistics.mean(neg_vals) if neg_vals else float("nan")
        variance_flag = " (NO VARIANCE — agent has zero signal here)" if len(set(all_vals)) <= 1 else ""
        if variance_flag:
            no_variance.append(c)
        print(f"{c:12s} positive mean={pos_mean:5.1f}  negative mean={neg_mean:5.1f}  diff={pos_mean - neg_mean:+5.1f}{variance_flag}")

    print()
    if no_variance:
        print(f"Components with no variance in example data: {', '.join(no_variance)}")
    else:
        print("All five components have variance across the example data — the recalibration agent has some signal on every component.")

    if not gate_passes:
        print("\nFAIL: example dataset no longer crosses the recalibration gate threshold.")
        sys.exit(1)


if __name__ == "__main__":
    main()
