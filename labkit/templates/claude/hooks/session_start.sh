#!/bin/sh
# SessionStart (startup, resume, clear, compact): where the work stands, in under ~6k characters.
# CLAUDE.md and PROJECT.md load on their own; this adds what changes between sessions.
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
echo "Session start. PROJECT.md outranks everything. HANDOFF.md follows."
echo
head -c 6000 HANDOFF.md 2>/dev/null
echo
echo "Last commits:"
git log --oneline -5 2>/dev/null
n=$(git status --porcelain 2>/dev/null | wc -l)
[ "$n" -gt 0 ] && echo "Uncommitted: $n files."
last=$(python3 tools/labkit.py next 2>/dev/null)
[ -n "$last" ] && echo "Next finding number: #$last"
exit 0
