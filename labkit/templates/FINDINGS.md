# FINDINGS — the append-only record

Each finding starts with a heading `## #N — one-sentence result`, numbered in order, and is never edited after it is committed.
Add findings with `python3 tools/labkit.py add "TITLE" < body.md`. To retract or qualify a finding, add a tag to the END of its
heading line, e.g. `[RETRACTED by #N: the control could not fail]` or `[REFINED by #N]`, and append the finding that explains it.
Dead tags: RETRACTED, SUPERSEDED, VOID, WITHDRAWN. Read this file through `labkit status / show / grep`, never front to back.

A finding body usually has: what was asked and why (citing earlier #N); the script and its pre-registration commit; the result,
with numbers and their sources; the prediction scored; what it says; the status it changes.
