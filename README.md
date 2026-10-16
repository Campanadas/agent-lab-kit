# Agent Lab Kit

**Run a long research project with Claude Code without the workspace outgrowing the agent.**

Long agent-run projects fail the same way. After a few weeks no session can hold the whole project. Agents re-derive settled
results, cite numbers that were retracted, rebuild things that already exist, and make fixes that break five places they never saw.
Summaries lose facts, status documents grow until nobody reads them, and every test the agent writes seems to pass.

This kit is the system that kept a long, single-researcher, agent-run computational science project coherent. It is a method (`PLAYBOOK.md`), a small tool (`labkit`, Python standard library only), project
templates, and six Claude Code skills that make agents follow the method without being reminded.

## What you get

| part | what it does |
|---|---|
| **An append-only ledger** (`FINDINGS.md`) | Every result is a numbered finding, `## #N — …`. A git pre-commit check refuses any edit to a committed line. Retractions are tags on the original heading, so the record is never rewritten and citations never drift. |
| **A ledger index** (`labkit status / show / grep / dead / check`) | Agents read the ledger through queries instead of front to back. `status N` says whether #N is safe to cite and what cites it. `check FILE` lists every finding a document relies on and flags the dead ones. |
| **Pre-registration** (`labkit prereg SCRIPT` + the `prereg` skill) | Tests, pass floors and predictions are written into the script header and committed before the run; the tool refuses to bless a script whose predictions are uncommitted or changed. |
| **Document budgets** (`labkit budget`) | Entry documents stay within byte and word budgets an agent can read every session. Current-state documents are flagged when they fall behind the record. |
| **Compaction without loss** (`labkit cover`) | When a document is rewritten shorter, `cover` lists every finding number and file path the rewrite dropped. A compaction can no longer silently lose knowledge. |
| **Session memory** (`HANDOFF.md` + a SessionStart hook + the `handoff` skill) | Each session ends by rewriting a fixed-section, ≤ 8 KB handoff. The next session starts from it automatically, so nothing depends on lossy auto-compaction. |
| **Six skills** | `check-the-ledger` (look before you derive), `prereg`, `claim-guard` (can this test fail?), `compact-docs`, `deliver` (build, don't only audit), `handoff`. |
| **Templates** | `CLAUDE.md`, `PROJECT.md` (the owner's own words, which outrank everything), `HANDOFF.md`, `ROADMAP.md`, `FINDINGS.md`, `KNOWLEDGE/`, `labkit.json`. |

## Quick start

Requirements: Python 3.8+, git, Claude Code.

```bash
python3 labkit/cli.py init ~/my-project      # templates, tools/labkit.py, .claude/ hooks and skills, git pre-commit check
cd ~/my-project
$EDITOR PROJECT.md                            # what the project is for, in your own words
git add -A && git commit -m "start"
claude                                        # the session starts from HANDOFF.md
```

`init` never overwrites a file that already exists, so you can add the kit to a project in progress. The project carries its own
copy of the tool at `tools/labkit.py`; nothing is installed system-wide.

## A day with the kit (real output)

```text
$ python3 tools/labkit.py grep "baseline"
#1: ## #1 — The baseline reproduces the published value within 0.002
#1: Script `baseline.py`. Result 0.148 vs 0.148.
#2†: ## #2 — A smaller baseline closes the gap (builds on #1) [RETRACTED by #3: the control could not fail]
#3: ## #3 — The smaller-baseline control could not fail; #2 retracted

$ python3 tools/labkit.py status 2
#2  DEAD (RETRACTED by #3)  FINDINGS.md:16-20
  A smaller baseline closes the gap (builds on #1)
  cites: #1 #3
  cited by: #3

$ python3 tools/labkit.py prereg sweep_y.py
sweep_y.py: pre-registered at a3b10a4 2026-10-15. Cite this commit in the finding.

$ python3 tools/labkit.py add "X survives removing Y only above 0.3 of baseline" < body.md
#4 appended to FINDINGS.md

$ python3 tools/labkit.py budget
ledger: 4 findings, last #4
ok    ENTRY   CLAUDE.md                               3410 / 6000 bytes
ok    ENTRY   HANDOFF.md                               523 / 8192 bytes
ok    ENTRY   ROADMAP.md                               144 / 1200 words
…
summary: 0 over budget, 0 stale

$ git commit -am "fix a number"          # after editing a committed line of FINDINGS.md
FINDINGS.md:13 changed or moved.
  committed: Script `baseline.py`. Result 0.148 vs 0.148.
  now:       Script `baseline.py`. Result 0.150 vs 0.148.
Append new text at the end of the file; change an old finding only by adding a tag to the END of its heading.
```

## Commands

```
labkit init [DIR]                       set up a project (idempotent)
labkit next                             the next finding number
labkit add "TITLE" [< body.md]          append a finding
labkit status N | show N | grep PAT     query the ledger
labkit dead                             retracted and superseded findings, with what killed them
labkit check FILE                       every #N a document cites, with its standing
labkit append-check [--worktree]        the pre-commit check (refuses rewritten ledger lines)
labkit budget [--strict]                document budgets and staleness
labkit cover PATH [--old F] [--rows P]  what a rewrite of PATH dropped
labkit prereg SCRIPT                    is the prediction block committed and unchanged?
```

Configure budgets, documents and the prediction marker in `labkit.json`.

## Not just for science

The ledger works for any long agent project where results accumulate and some get overturned: research, data analysis,
reverse engineering, due diligence, a long refactor with decisions to record. Pre-registration is just "write down what you
expect before you run it", which is useful anywhere an agent runs experiments.

## Want it set up for you?

I set the kit up on existing projects: your notes and results turned into a ledger and knowledge topics, the entry documents
written from a short questionnaire, and custom skills for your workflow. Write to the address on my GitHub profile.

## Licence

Free to use in any of your projects, personal or commercial; see `LICENSE.md`.
