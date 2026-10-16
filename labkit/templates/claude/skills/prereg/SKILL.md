---
name: prereg
description: Use before running any experiment, analysis, sweep or model fit whose result will enter the record - write the tests, their pass floors and the predicted outcome into the script header, commit, verify with labkit prereg, run, then record one finding with the prediction scored.
---

# Pre-register, run, score

A prediction written after the result is a description. A prediction committed before the run is evidence, and it is the only
cheap defence an agent has against fitting its story to whatever came out.

## 1. Before writing the script
- `check-the-ledger` first: has this been asked, built or measured before? Cite what you find in the header.
- Name every number's source: MEASURED / DERIVED / ASSUMED (swept, never tuned) / EMERGENT (a test, never an objective).

## 2. The header (the first ~60 lines of the script)
- **The question**, in one sentence, and the findings it builds on (#N).
- **The arms**: every option being compared. Undecided choices become arms, not silent defaults.
- **The tests**, each with a name (T1, T2, ...), its exact criterion, and its **floor**: what a dead, flat or trivial result
  scores, and the condition that rules that out.
- **Sanity checks** (e.g. "the baseline reproduces #N within 0.002"), so a broken pipeline cannot pass.
- **Predictions stated before the run**: which tests pass, which fail, and the rough numbers you expect.

## 3. Commit, verify, run
```bash
git add SCRIPT && git commit -m "step K SCRIPT: <question>; pre-registered"
python3 tools/labkit.py prereg SCRIPT      # must say "pre-registered at <commit>"
python3 SCRIPT                              # results to a file, with the log beside it
```
A pilot of 1-3 items before a large batch is fine; if you look at pilot results, say so in the header before committing.
A crash fix after the commit is fine if no result was seen; say so in the commit message.

## 4. Record one finding
`python3 tools/labkit.py add "<the result in one sentence>" < body.md`, with: the script and its pre-registration commit; the
results table; every test's verdict; the predictions scored (held / missed); what it says; what status it changes. A test that
passed only vacuously is reported as passed-as-written and **not counted**, and its floor is added from then on.

## 5. Update the current state
Rewrite (never extend) the status lines in ROADMAP / HANDOFF / KNOWLEDGE that this finding changes, citing #N, then
`labkit budget`.
