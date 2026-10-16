"""labkit: keep a long, agent-run research project small enough to think about.

One ledger (FINDINGS.md) that only grows, read through an index instead of front to back; a few current-state documents that are
rewritten in place within byte budgets; predictions committed before every run. Standard library only.

    labkit init [DIR]                 lay down the templates, the git pre-commit check and the Claude Code hooks / skills
    labkit next                       the next finding number
    labkit add "TITLE" [< body.md]    append one finding (heading + body) to the ledger
    labkit status N                   is #N safe to cite? its tags, what it cites, what cites it
    labkit show N [--max 150]         one finding's text
    labkit grep PATTERN [--max 20]    search the ledger; hits as #N: line
    labkit dead                       every retracted / superseded finding and what killed it
    labkit check FILE                 every #N a document cites, with its status (exit 1 if it cites a dead one)
    labkit append-check [--worktree]  refuse a commit that changes or moves a committed ledger line (the pre-commit hook)
    labkit budget                     entry documents over budget, stale current-state documents, oversized table cells
    labkit cover PATH [--old FILE] [--rows PREFIX]   which #N and paths a rewrite of PATH dropped (exit 1 if any)
    labkit prereg SCRIPT              is SCRIPT's prediction block committed and unchanged? (run it right before the run)
"""
import argparse, datetime, json, os, re, shutil, stat, subprocess, sys

HEAD = re.compile(r'^#{1,4}\s*#(\d+)\s*[—–-]\s*(.*)$')          # '## #12 — title [TAG by #15: why]'
CITE = re.compile(r'#(\d+)\b')
RANGE = re.compile(r'#(\d+)\s*[–-]\s*#?(\d+)\b')
TAG = re.compile(r'\[([A-Z][A-Z -]+?)(?:\s+(?:by|in|see)\s+#(\d+))?(?:[:;][^\]]*)?\]')
DEAD_TAGS = {'RETRACTED', 'SUPERSEDED', 'VOID', 'WITHDRAWN'}
DEADWORD = re.compile(r'\[\s*(\w+)(?:[^\]#]*#(\d+))?[^\]]*\]')                    # [retracted by #9: ...] in any case
LOOKS_LIKE = re.compile(r'^(#{1,4}\s*#?\d+[a-z]?\b|#\d+\s*[—–-])')                   # a finding heading in some other shape
PATHS = re.compile(r'`([\w./-]+\.(?:py|json|md|csv|tsv|txt|ipynb|parquet|npz|npy|log|yaml|yml|toml|sh|r|R|jl))`')
DEFAULTS = {
    'ledger': 'FINDINGS.md',
    'entry_docs': {'CLAUDE.md': {'max_bytes': 6000}, 'HANDOFF.md': {'max_bytes': 8192}, 'ROADMAP.md': {'max_words': 1200},
                   'KNOWLEDGE/README.md': {'max_bytes': 12000}},
    'current_docs': ['HANDOFF.md', 'ROADMAP.md'],
    'stale_lag': 30,
    'table_docs': [], 'max_cell_chars': 1000,
    'knowledge_dir': 'KNOWLEDGE', 'knowledge_max_bytes': 40000,
    'prereg_marker': r'(?i)\b(predictions?|stated before the run|pre-?registered)\b',
}
HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------- repository and configuration
def git(*args, cwd=None):
    r = subprocess.run(('git',) + args, capture_output=True, cwd=cwd)
    return r.stdout.decode('utf-8', 'replace') if r.returncode == 0 else None


def root():
    top = git('rev-parse', '--show-toplevel')
    return top.strip() if top else os.getcwd()


def config(base):
    cfg = dict(DEFAULTS); p = os.path.join(base, 'labkit.json')
    if os.path.exists(p):
        cfg.update(json.load(open(p, encoding='utf-8')))
    return cfg


def read(path):
    return open(path, encoding='utf-8', errors='replace').read()


# ---------------------------------------------------------------- the ledger
def parse(text):
    """{n: dict(title, tags, dead, killer, start, end, body)} from a ledger's text; lines are 1-based."""
    lines = text.split('\n'); heads = []
    for i, line in enumerate(lines):
        m = HEAD.match(line)
        if m: heads.append((i, int(m.group(1)), m.group(2)))
    F = {}
    for k, (i, n, title) in enumerate(heads):
        j = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        tags = [(t.strip(), int(by) if by else None) for t, by in TAG.findall(title)]
        dead = [(t, by) for t, by in tags if t.split()[0] in DEAD_TAGS] or \
               [(w.upper(), int(by) if by else None) for w, by in DEADWORD.findall(title) if w.upper() in DEAD_TAGS]
        F[n] = dict(title=TAG.sub('', title).strip(), tags=tags, dead=bool(dead), dead_tag=dead[0][0] if dead else None, killer=dead[0][1] if dead else None,
                    start=i + 1, end=j, body='\n'.join(lines[i:j]))
    return F


def cites(body, self_n=None):
    s = {int(n) for n in CITE.findall(body)}
    for a, b in RANGE.findall(body):
        a, b = int(a), int(b)
        if a < b <= a + 500: s |= set(range(a, b + 1))
    s.discard(self_n); return s


def ledger(base):
    p = os.path.join(base, config(base)['ledger'])
    return (parse(read(p)) if os.path.exists(p) else {}), p


def standing(F, n):
    if n not in F: return 'UNKNOWN'
    f = F[n]
    if f['dead']: return 'DEAD (%s%s)' % (f['dead_tag'], ' by #%d' % f['killer'] if f['killer'] else '')
    return 'LIVE' + (' (tagged: %s)' % ', '.join(t for t, _ in f['tags']) if f['tags'] else '')


# ---------------------------------------------------------------- commands
def cmd_init(a):
    dest = os.path.abspath(a.dir); os.makedirs(dest, exist_ok=True); tpl = os.path.join(HERE, 'templates'); made, kept = [], []
    for dp, _, files in os.walk(tpl):
        for f in files:
            src = os.path.join(dp, f); rel = os.path.relpath(src, tpl)
            rel = rel.replace('claude' + os.sep, '.claude' + os.sep, 1) if rel.startswith('claude' + os.sep) else rel
            out = os.path.join(dest, rel)
            if os.path.exists(out): kept.append(rel); continue
            os.makedirs(os.path.dirname(out), exist_ok=True); shutil.copyfile(src, out)
            if out.endswith('.sh'): os.chmod(out, os.stat(out).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            made.append(rel)
    tool = os.path.join(dest, 'tools', 'labkit.py')                # the project carries its own copy: no install, no path to break
    if not os.path.exists(tool):
        os.makedirs(os.path.dirname(tool), exist_ok=True); shutil.copyfile(os.path.abspath(__file__), tool); made.append('tools/labkit.py')
    if git('rev-parse', '--git-dir', cwd=dest) is None:
        subprocess.run(['git', 'init', '-q'], cwd=dest)
    hooks = git('rev-parse', '--git-path', 'hooks', cwd=dest).strip(); hooks = os.path.join(dest, hooks) if not os.path.isabs(hooks) else hooks
    os.makedirs(hooks, exist_ok=True); hook = os.path.join(hooks, 'pre-commit')
    line = 'python3 tools/labkit.py append-check || exit 1\n'
    if not os.path.exists(hook):
        open(hook, 'w').write('#!/bin/sh\n# The ledger only grows (labkit).\n' + line)
    elif 'append-check' not in read(hook):
        open(hook, 'a').write(line)
    os.chmod(hook, os.stat(hook).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print('labkit init %s: %d files written, %d already there (left as they are), pre-commit check installed' % (dest, len(made), len(kept)))
    for r in kept: print('  kept', r)
    print('Next: fill in PROJECT.md in your own words, then start a Claude Code session in %s.' % dest)


def cmd_next(a):
    F, _ = ledger(root()); print((max(F) + 1) if F else 1)


def cmd_add(a):
    base = root(); F, p = ledger(base); n = (max(F) + 1) if F else 1
    body = a.body if a.body is not None else ('' if sys.stdin.isatty() else sys.stdin.read())
    head = '## #%d — %s' % (n, a.title.strip())
    block = '\n%s\n\n%s\n' % (head, (body.strip() + '\n') if body.strip() else '_Date: %s._\n' % datetime.date.today().isoformat())
    text = read(p) if os.path.exists(p) else ''
    with open(p, 'a', encoding='utf-8') as fh:
        fh.write(('' if text.endswith('\n') or not text else '\n') + block)
    print('#%d appended to %s' % (n, os.path.relpath(p, base)))


def cmd_status(a):
    F, p = ledger(root()); n = a.n
    if n not in F: print('#%d: not in %s' % (n, os.path.basename(p))); sys.exit(1)
    f = F[n]; by = sorted(m for m, g in F.items() if m != n and n in cites(g['body'], m))
    print('#%d  %s  %s:%d-%d' % (n, standing(F, n), os.path.basename(p), f['start'], f['end']))
    print('  %s' % f['title'][:200])
    out = sorted(cites(f['body'], n)); print('  cites:', ' '.join('#%d%s' % (m, '†' if F.get(m, {}).get('dead') else '') for m in out) or '-')
    print('  cited by:', ' '.join('#%d' % m for m in by) or '-')
    if any(F.get(m, {}).get('dead') for m in out): print('  († = cites a dead finding)')


def cmd_show(a):
    F, _ = ledger(root())
    if a.n not in F: print('#%d not found' % a.n); sys.exit(1)
    L = F[a.n]['body'].split('\n'); print('\n'.join(L[:a.max]))
    if len(L) > a.max: print('... (%d more lines; --max to see them)' % (len(L) - a.max))


def cmd_grep(a):
    F, _ = ledger(root()); rx = re.compile(a.pattern, re.I); hits = 0
    for n in sorted(F):
        for line in F[n]['body'].split('\n'):
            if rx.search(line):
                print('#%d%s: %s' % (n, '†' if F[n]['dead'] else '', line.strip()[:180])); hits += 1
                if hits >= a.max: print('... (stopped at %d hits; --max for more)' % a.max); return
    if not hits: print('no hits')


def cmd_dead(a):
    F, _ = ledger(root()); d = [n for n in sorted(F) if F[n]['dead']]
    for n in d: print('#%d %s — %s' % (n, standing(F, n), F[n]['title'][:120]))
    print('%d dead of %d findings' % (len(d), len(F)))


def cmd_check(a):
    F, _ = ledger(root()); text = read(a.file); refs = sorted(cites(text)); bad = 0
    for n in refs:
        s = standing(F, n); bad += s.startswith('DEAD') or s == 'UNKNOWN'; print('#%d  %s' % (n, s))
    print('%d cited, %d dead or unknown' % (len(refs), bad)); sys.exit(1 if bad else 0)


def cmd_append_check(a):
    base = root(); path = config(base)['ledger']; old = git('show', 'HEAD:' + path, cwd=base)
    if old is None: sys.exit(0)                                     # nothing committed yet: nothing to protect
    new = read(os.path.join(base, path)) if a.worktree else git('show', ':' + path, cwd=base)
    if new is None: print('%s: removed from the index - refused' % path); sys.exit(1)
    o, n = old.split('\n'), new.split('\n')
    if o and o[-1] == '': o = o[:-1]
    if len(n) < len(o): print('%s: %d lines committed, %d now - lines were removed' % (path, len(o), len(n))); sys.exit(1)
    for i, line in enumerate(o):
        if not n[i].startswith(line):
            print('%s:%d changed or moved.\n  committed: %s\n  now:       %s' % (path, i + 1, line[:150], n[i][:150]))
            print('Append new text at the end of the file; change an old finding only by adding a tag to the END of its heading.'); sys.exit(1)
    sys.exit(0)


def size(path, unit):
    t = read(path); return len(t.encode()) if unit == 'bytes' else len(t.split())


def cmd_budget(a):
    base = root(); cfg = config(base); F, _ = ledger(base); last = max(F) if F else 0; over = stale = 0
    print('ledger: %d findings, last #%d' % (len(F), last))
    lp = os.path.join(base, cfg['ledger']); text = read(lp) if os.path.exists(lp) else ''
    nums = [int(m.group(1)) for m in map(HEAD.match, text.split('\n')) if m]; dup = sorted({n for n in nums if nums.count(n) > 1})
    odd = [i + 1 for i, l in enumerate(text.split('\n')) if LOOKS_LIKE.match(l) and not HEAD.match(l)]
    if dup: over += 1; print('WARN  LEDGER  duplicate finding numbers: %s' % ' '.join('#%d' % n for n in dup))
    if odd: over += 1; print('WARN  LEDGER  %d heading-like lines not parsed (not "## #N — title"): lines %s' % (len(odd), ', '.join(map(str, odd[:10]))))
    for p, lim in cfg['entry_docs'].items():
        fp = os.path.join(base, p)
        if not os.path.exists(fp): continue
        unit, v = ('bytes', size(fp, 'bytes')) if 'max_bytes' in lim else ('words', size(fp, 'words')); m = lim.get('max_bytes', lim.get('max_words'))
        bad = v > m; over += bad; print('%s ENTRY   %-36s %7d / %d %s' % ('OVER ' if bad else 'ok   ', p, v, m, unit))
    kd = os.path.join(base, cfg['knowledge_dir'])
    if os.path.isdir(kd):
        for f in sorted(os.listdir(kd)):
            if f.endswith('.md') and f != 'README.md':
                v = size(os.path.join(kd, f), 'bytes'); bad = v > cfg['knowledge_max_bytes']; over += bad
                if bad: print('OVER  KNOWLEDGE %-34s %7d / %d bytes' % (f, v, cfg['knowledge_max_bytes']))
    for p in cfg['table_docs']:
        fp = os.path.join(base, p)
        if not os.path.exists(fp): continue
        rows = [l for l in read(fp).split('\n') if l.startswith('|') and not l.startswith('|-')]
        worst = max([(max(len(c) for c in r.strip().strip('|').split('|')), r[:12]) for r in rows] or [(0, '')])
        bad = worst[0] > cfg['max_cell_chars']; over += bad
        print('%s TABLE   %-36s longest cell %d chars (%s)' % ('OVER ' if bad else 'ok   ', p, worst[0], worst[1].strip()))
    for p in cfg['current_docs']:
        fp = os.path.join(base, p)
        if not os.path.exists(fp) or not last: continue
        refs = [n for n in cites(read(fp)) if n <= last]; newest = max(refs) if refs else 0; lag = last - newest
        bad = lag > cfg['stale_lag']; stale += bad
        print('%s CURRENT %-36s newest #%d cited, %d findings behind' % ('STALE' if bad else 'ok   ', p, newest, lag))
    print('summary: %d over budget, %d stale' % (over, stale)); sys.exit(1 if (over or stale) and a.strict else 0)


def cmd_cover(a):
    base = root(); path = a.path
    old = read(a.old) if a.old else git('show', 'HEAD:' + os.path.relpath(os.path.abspath(path), base), cwd=base)
    if old is None: print('%s is not committed and no --old was given' % path); sys.exit(2)
    new = read(path)
    if a.rows:
        pick = lambda t: '\n'.join(l for l in t.split('\n') if l.startswith(a.rows)); old, new = pick(old), pick(new)
    o_single = {int(n) for n in CITE.findall(old)}; n_cover = cites(new); dropped = sorted(o_single - n_cover)
    lost = sorted(set(PATHS.findall(old)) - set(PATHS.findall(new)))
    print('%s: %d -> %d bytes; findings cited before %d, dropped %d; paths before %d, dropped %d'
          % (path, len(old.encode()), len(new.encode()), len(o_single), len(dropped), len(set(PATHS.findall(old))), len(lost)))
    if dropped: print('dropped #N:', ' '.join('#%d' % n for n in dropped))
    if lost: print('dropped paths:', ' '.join(lost))
    sys.exit(1 if dropped or lost else 0)


def cmd_prereg(a):
    base = root(); cfg = config(base); p = os.path.abspath(a.script); rel = os.path.relpath(p, base); problems = []
    head = '\n'.join(read(p).split('\n')[:a.lines])
    if not re.search(cfg['prereg_marker'], head): problems.append('no prediction block in the first %d lines (looked for %s)' % (a.lines, cfg['prereg_marker']))
    if git('ls-files', '--error-unmatch', rel, cwd=base) is None: problems.append('not committed')
    elif subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--', rel], cwd=base).returncode != 0: problems.append('changed since its last commit')
    if problems:
        print('%s: NOT pre-registered: %s' % (rel, '; '.join(problems)))
        print('Write what you expect (tests, pass floors, predicted outcome) in the header, commit it, then run.'); sys.exit(1)
    h = git('log', '-1', '--format=%h %cs', '--', rel, cwd=base).strip()
    print('%s: pre-registered at %s. Cite this commit in the finding.' % (rel, h))


def main(argv=None):
    ap = argparse.ArgumentParser(prog='labkit', description=__doc__.split('\n')[0]); sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('init'); s.add_argument('dir', nargs='?', default='.'); s.set_defaults(f=cmd_init)
    sub.add_parser('next').set_defaults(f=cmd_next)
    s = sub.add_parser('add'); s.add_argument('title'); s.add_argument('--body'); s.set_defaults(f=cmd_add)
    s = sub.add_parser('status'); s.add_argument('n', type=int); s.set_defaults(f=cmd_status)
    s = sub.add_parser('show'); s.add_argument('n', type=int); s.add_argument('--max', type=int, default=150); s.set_defaults(f=cmd_show)
    s = sub.add_parser('grep'); s.add_argument('pattern'); s.add_argument('--max', type=int, default=20); s.set_defaults(f=cmd_grep)
    sub.add_parser('dead').set_defaults(f=cmd_dead)
    s = sub.add_parser('check'); s.add_argument('file'); s.set_defaults(f=cmd_check)
    s = sub.add_parser('append-check'); s.add_argument('--worktree', action='store_true'); s.set_defaults(f=cmd_append_check)
    s = sub.add_parser('budget'); s.add_argument('--strict', action='store_true', help='exit 1 when anything is over or stale'); s.set_defaults(f=cmd_budget)
    s = sub.add_parser('cover'); s.add_argument('path'); s.add_argument('--old'); s.add_argument('--rows'); s.set_defaults(f=cmd_cover)
    s = sub.add_parser('prereg'); s.add_argument('script'); s.add_argument('--lines', type=int, default=60); s.set_defaults(f=cmd_prereg)
    a = ap.parse_args(argv); a.f(a)


if __name__ == '__main__':
    main()
