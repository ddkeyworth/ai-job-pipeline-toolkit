# Scoring eval harness

A small, repeatable check on whether `SKILL.md`'s scoring rubric (Step 2) produces stable, sensible output over time – across sessions, and across whatever Claude model version is running the skill. This is not a classic ML eval (there are no model weights to fine-tune here, it's a skill interpreted fresh by whatever Claude session reads `SKILL.md`), so it works differently from one:

- **`golden_set.md`** – six fictional job descriptions, each chosen to exercise one distinct scoring scenario (ideal fit, competition drag from a famous employer, a severe seniority stretch, a confirmed comp shortfall, a confirmed non-immigration blocker, and a genuine but non-obviously-titled fit that a plain title-match read would undervalue – added to specifically exercise the competency-cluster derivation in Step 2's JD-fit method), scored against the existing `../examples/CV-example.md` persona. Expected score bands are written down *before* any scoring run, with the reasoning for each band spelled out.
- **`expected_bands.json`** – the same bands in machine-readable form, kept in sync with `golden_set.md`'s prose.
- **`results/<date>.json`** – a dated record of an actual scoring run against the golden set. New runs get a new dated file; old ones stay, so drift over time is visible in git history, not overwritten.
- **`scripts/verify_eval_results.py`** (repo root's `scripts/`) – the mechanical half: reads the most recent `results/*.json` file and checks every component and total against `expected_bands.json`, exits 1 on any violation. Wired into CI so a change to either file gets checked automatically – but CI only checks a *committed* results file against the bands; it cannot produce a new one itself (see below).

## Running a new eval (do this periodically, or after any change to SKILL.md's scoring rubric)

This step needs an actual Claude session interpreting `SKILL.md`, the same way real scoring happens – it can't run unattended in CI without an API key, which this repo deliberately doesn't use.

1. Open a fresh session (ideally one with no prior context on this repo's build, to avoid the session unconsciously scoring toward what it expects rather than what the rubric says).
2. Point it at `SKILL.md` and `../examples/CV-example.md` as the CV baseline.
3. For each of the six cases in `golden_set.md`, ask it to score the JD text exactly as written, following Step 2's rubric.
4. Record the five component scores per case in a new `results/YYYY-MM-DD.json` file, following the same structure as the existing one.
5. Run `python scripts/verify_eval_results.py` from the repo root and check the output.
6. If something falls outside its band: that's either a real rubric-interpretation problem worth investigating (did `SKILL.md` change in a way that shifted behaviour?), or the original band was too narrow and needs revisiting in both `golden_set.md` and `expected_bands.json` – decide which before committing anything. Don't silently widen a band just to make a failing run pass.

## What this does and doesn't prove

Proves: whether the scoring rubric, as written in `SKILL.md`, produces component scores within a defensible, pre-registered range for six distinct, deliberately-varied scenarios – including the two hardest cases to get right (a severe seniority stretch scoring near-zero regardless of other fit; a confirmed sub-floor comp band being penalised specifically on the `comp` component, not spread across others) and the competency-cluster mechanism correctly recognising a non-obvious-fit case a plain title-match read would miss.

Doesn't prove: consistency across *many* runs (six cases is enough to catch a rubric regression, not enough to characterise run-to-run variance statistically), or that live-search-dependent scoring (real companies, not the self-contained fictional ones here) behaves the same way – the golden set deliberately puts company facts directly in the JD text so this harness doesn't depend on live search results that could change over time.
