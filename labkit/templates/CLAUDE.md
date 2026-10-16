# Read this before doing anything

@PROJECT.md

1. **`PROJECT.md`** (imported above) is the owner's definition of the project in their own words. It outranks every other
   document, plan, finding, skill and memory. Where they disagree, `PROJECT.md` wins. Change it only in the owner's words.
2. **`HANDOFF.md`** says where the work stands. **`ROADMAP.md`** is the one live roadmap and says what is next.
3. **`KNOWLEDGE/`** holds one current document per topic (index: `KNOWLEDGE/README.md`). Read the topic's document before opening
   old files; it cites `#N` for everything it states.
4. **`FINDINGS.md` is the append-only record.** Never read it front to back. Cite findings by `#N`, never by line.
   - `python3 tools/labkit.py status N` (safe to cite?) · `show N` · `grep PATTERN` · `dead` · `check FILE`.
   - Append with `python3 tools/labkit.py add "TITLE" < body.md`. The pre-commit check refuses any committed line that moved or changed.
   - Retract or qualify in place: add a tag to the END of the original heading (`[RETRACTED by #N: why]`, `[REFINED by #N]`),
     then append the new finding that explains it.

**The test for any work:** does it move the project toward the goal in `PROJECT.md`? Rank work by what it changes in the result,
not by how tidy it makes the record.

## Rules of evidence
- **Look before you derive.** Before any step, `labkit grep` the ledger for the quantity, the method and the source's first author.
  Re-deriving a settled result costs a session and produces nothing.
- **Pre-register every run.** Write the tests, their pass floors and your predicted outcome in the script's header, commit it,
  run `python3 tools/labkit.py prereg SCRIPT`, and only then run it. One finding per step, with the prediction scored.
- **No vacuous passes.** Ask what a dead or flat result scores on each test, and add the floor (survival, amplitude, effect size)
  that rules it out before you commit.
- **Say where every number comes from:** MEASURED (from data), DERIVED (computed from measured numbers), ASSUMED (stated, to be
  swept, never tuned), EMERGENT (an output; a test, never an objective).
- **A control must be able to fail.** Delete the mechanism and re-run; a test that still passes was not testing it.

## Rules for the workspace (it must stay smaller than an agent's context)
- **Every document has one role.** The ledger is read through the index. Current-state documents (HANDOFF, ROADMAP, KNOWLEDGE)
  are rewritten in place within their budgets, never grown a clause per step.
- **One fact, one home:** a result lives in its finding; current-state documents give its status in a line and cite `#N`.
- **Before changing a shared function, file, number or claim, find every user of it** and update all of them. Prefer additive changes.
- After restructuring docs run `python3 tools/labkit.py budget`; before committing a compaction run `labkit cover PATH`.
- **Nothing is deleted.** Move it to an archive folder with a note of why.

## The owner
- The owner's decisions are not made for them. Undecided questions become options that are built and compared; answered
  questions stay answered (record the answer in `PROJECT.md`, quoted and dated).
- Ask before anything outward-facing: sending, publishing, pushing, buying, or deleting.

## At the end of a task
Run the `handoff` skill: it rewrites `HANDOFF.md` in place (at most 8 KB), commits, and stops.
