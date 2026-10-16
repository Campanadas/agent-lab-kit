---
name: compact-docs
description: Use when a current-state document (HANDOFF, ROADMAP, a KNOWLEDGE topic, a status table) is over its budget, has grown by a clause per step, or has to be restructured - and before changing any shared function, file, number or claim that other parts of the project use.
---

# Keep the workspace smaller than a context window

When a project outgrows what an agent can hold, fixes start creating more problems than they solve: the agent changes one thing
without seeing the five places that depend on it. Markdown knowledge outgrows the window just as code does.

## Compacting a document without losing knowledge
1. Copy the committed version aside (or rely on git HEAD).
2. Rewrite as **current state**: what is true now, one line per item, each citing `#N`. History belongs in the ledger.
   Ranges (`#40–#52`) keep the citations of a run of findings in a few characters.
3. `python3 tools/labkit.py cover PATH` (or `--old FILE`, `--rows "| S3 |"` for one table row). It must report
   **dropped 0** findings and **dropped 0** paths; anything dropped must be re-cited or moved to the document that now holds it.
4. `python3 tools/labkit.py budget`: nothing over, nothing stale.

## The status-cell trap
A table cell or status line that gains one clause per step ("...; then X; then Y (#N); then Z (#M)") is a log hiding in a
current-state document. Rewrite it as the current state each time; never extend it.

## Changing something shared
Before changing a shared function, output file, constant or claim:
- find every user: imports, file names, the constant's name, and every `#N` that states it (`labkit grep`);
- prefer an additive change (a new option, a new file) over editing what others read;
- never set another module's globals from outside it;
- update or re-point every user in the same commit.
