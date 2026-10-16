# The Playbook: running a long project with AI agents

This is the method behind the kit. The tools enforce parts of it; the skills remind agents of the rest. Read it once; the
templates and skills carry it from then on.

## 1. The problem: the project outgrows the agent

An agent sees only what fits in its context. A project that runs for weeks accumulates far more than that: hundreds of results,
dozens of scripts, notes that contradict older notes. Past a certain size, every session works on a partial picture, and the
failures look like this:

- **Walking in circles.** A session re-derives a result that was settled a month ago, or rebuilds a mechanism that already
  exists, because nothing told it to look.
- **Citing the dead.** A number that was retracted keeps being quoted, because the retraction lives somewhere the session never read.
- **Fixes that make more problems.** A shared function or constant is changed to fix one thing, and five dependants the session
  never opened break silently.
- **Documents that grow until nobody reads them.** Status pages gain a clause per step until they are logs nobody can hold.
- **Lossy memory.** Automatic summaries of a long session keep the gist and drop exactly the caveat that mattered.
- **Tests that cannot fail.** Under pressure to make progress, an agent writes checks that a dead or trivial result would pass.

None of these is a lapse of a particular agent. They are what happens when the record outgrows the reader. The fix is
structural: shape the workspace so that what an agent must read is always small, and what it may skip is always indexed.

## 2. The architecture: four layers

| layer | files | rule |
|---|---|---|
| **The owner's words** | `PROJECT.md` | What the project is for, quoted and dated. Outranks every other document. Agents paraphrase; this file quotes. |
| **Entry documents** | `CLAUDE.md`, `HANDOFF.md`, `ROADMAP.md`, `KNOWLEDGE/README.md` | Read at every session start, so each has a budget (bytes or words). Rewritten in place, never appended to. |
| **Current knowledge** | `KNOWLEDGE/<topic>.md` | One document per topic saying what is true now, every statement citing a finding. Rewritten when the truth changes. |
| **The ledger** | `FINDINGS.md` | Every result, numbered, append-only. Never read whole; queried through `labkit`. |

The ledger can grow without limit because nobody reads it whole. Everything that is read whole has a budget.

## 3. The rules

**1. The owner's words outrank everything.** `PROJECT.md` holds the owner's definitions and decisions as quotations with dates.
When an agent's plan, a skill, or an old note disagrees with it, `PROJECT.md` wins. Agents never paraphrase the owner into it.

**2. The record only grows.** Results are appended as `## #N — one-sentence result`. A pre-commit check refuses any commit
that changes or moves a committed line. To retract or qualify an old finding, add a tag to the end of its heading
(`[RETRACTED by #N: why]`) and append the finding that explains it. Citations by number never drift, and the history of what was
believed when is never lost.

**3. Read the ledger through an index, never front to back.** `labkit grep` to find, `labkit status N` before citing,
`labkit check FILE` before anything leaves the project.

**4. Look before you derive.** Before any step, search the ledger for the quantity, the method, the build and the source's
author. Before asking a human for a paper or dataset, search for it on disk. This one habit saves more sessions than any other.

**5. Current-state documents are rewritten, never extended.** A status line says what is true now and cites `#N`. The trap is
the line that grows by one clause per step ("…; then X; then Y (#N)"): that is a log hiding in a status page. Rewrite it.

**6. One fact, one home.** A result lives in its finding. Other documents state its status in a line and cite the number, so a
correction touches one place.

**7. Pre-register every run.** Before running anything whose result enters the record, write in the script's header: the
question, the arms, each test with its exact criterion, the sanity checks, and the predicted outcome. Commit it. Then run. The
finding scores the prediction (held / missed). One finding per step.

**8. Put a floor under every test.** For each test ask what a dead, flat or trivial result scores. If it would pass, add the
floor that excludes it (a survival condition, a minimum amplitude, a minimum effect) before the run. A test that passes vacuously
is reported as "passed as written, not counted", and its floor is added from then on.

**9. Type every number.** MEASURED (from data), DERIVED (computed from measured values), ASSUMED (stated and swept, never tuned
to make a test pass), EMERGENT (an output: a test, never an objective). Most self-deception in modelling is an emergent quantity
quietly used as a fitting target.

**10. Open questions become arms.** When a choice is undecided, the agent builds the options and compares them on the same
tests. It does not pick silently. Questions the owner has answered stay answered.

**11. Find every user before changing anything shared.** Before changing a shared function, output file, constant or claim,
find everything that uses it (imports, file names, finding numbers), prefer an additive change, and update every user in the same
commit. Never set another module's globals from outside it.

**12. Hand off; don't rely on compaction.** At the end of a task the agent rewrites `HANDOFF.md` (fixed sections, at most 8 KB),
checks budgets, commits, and stops. The next session starts from it via a SessionStart hook.

**13. Nothing is deleted.** Superseded files are archived with a note of why. Deleting is the one irreversible step, and
the one an agent is most tempted to take when tidying.

**14. Build, don't only audit.** Checking and tidying always succeed, so long-running agents drift toward them. At the end of a
turn, name the capability that exists now and did not before. If the last three steps were audits, the next one is a build.

## 4. The daily loop

1. Session starts; the hook prints `HANDOFF.md`, the last commits, and the next finding number.
2. Pick the next item from `ROADMAP.md`.
3. `labkit grep` for what is already known (quantity, method, build, author).
4. Write the script with its pre-registration header; commit; `labkit prereg`.
5. Run; save results and the log.
6. `labkit add` one finding with the prediction scored.
7. Rewrite the status lines it changes (ROADMAP, KNOWLEDGE, HANDOFF); `labkit budget`; `labkit cover` if you compacted.
8. Commit. Next item, or `handoff` and stop.

## 5. Failures this method was built from

Each rule above exists because its absence cost real sessions in the project the kit came from:

- **A parser that saw one shape.** A checker that recognised only one heading format reported 25 existing findings as
  "never written". Since then the tools report what they cannot parse instead of assuming absence, and the ledger has one heading format.
- **A transcription error that lived for nearly forty findings.** A model constant was copied wrong from a published paper and every
  later result inherited it. It was found by reading the authors' code. The fix was to tag the affected headings in place and append
  the correction, not to rewrite history. Every downstream claim stayed traceable.
- **The rebuilt loop.** A mechanism was built and tested for a day before anyone noticed an equivalent build weeks earlier in the
  ledger. Rule 4 now includes builds, not just numbers.
- **The paper that was already on disk.** An agent asked the owner to fetch a paper that the owner had supplied a week before.
  Rule 4 now includes "search the papers folder before asking".
- **The test a dead system passed.** A pre-registered "it oscillates" test passed on swings of 1% of the range. It is reported as
  passed-as-written and not counted, and every oscillation test now carries an amplitude floor (rule 8).
- **Status pages that became logs.** Roadmap cells grew by a clause per step until the roadmap ran to tens of thousands of words.
  Budgets and the status-cell rule (rule 5) brought it back under 1,200 words without losing a citation (`labkit cover`).

## 6. Adopting it in a project already under way

1. `labkit init` in the project (nothing existing is overwritten).
2. Write `PROJECT.md` in your own words.
3. Start the ledger now: number new results from #1. Do not try to convert old notes; cite them by path from new findings when needed.
4. Move the current state into `HANDOFF.md` and `ROADMAP.md`, within budget.
5. From the next experiment on, pre-register.
