---
name: handoff
description: End a task cleanly - rewrite HANDOFF.md in place (fixed sections, at most 8 KB), check the document budgets, commit, then stop. Use at the end of every roadmap task, before a long break, or when the context is getting full; prefer it to compaction, which summarises lossily.
---

# Handoff: write the memory, then stop

A compaction summarises lossily. A handoff you write yourself, from what you know is true, does not. The session-start hook prints
`HANDOFF.md` into the next session's context, so it is what the next session starts from.

1. **Rewrite `HANDOFF.md` in place.** Do not append a dated block: git keeps the history. Keep these sections exactly:
   - `## Goal`: one or two lines. It points to `PROJECT.md`; it never paraphrases the owner.
   - `## Confirmed`: every line cites `#N`. If a line has been disproved, rewrite or remove it; never add a correction beneath it.
   - `## Current`: what is half-done, with its commit hashes.
   - `## Failed (do not retry)`: every line cites `#N` or a commit.
   - `## Next`: the next roadmap task first, named as it appears in `ROADMAP.md`.
2. **Rewrite, don't extend.** A status line says what is true now. If a line has grown by one clause per step, rewrite it as the
   current state; the steps are in the ledger.
3. **Check:** `python3 tools/labkit.py budget` (HANDOFF at most 8192 bytes; nothing over budget or stale). Cut before you add.
   If you compacted a document, `python3 tools/labkit.py cover PATH` must report nothing dropped.
4. **Record any decision the owner made this session** in `PROJECT.md` (quoted, dated; ask before editing) or in the roadmap.
5. **Commit:** `git add HANDOFF.md` plus whatever the task changed, then `git commit`. The pre-commit check refuses a rewritten
   ledger line: fix the cause, never bypass the check.
6. **Stop.** Tell the owner in one or two lines what was committed and what comes next.
