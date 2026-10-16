"""End-to-end tests: init a throwaway project, then exercise every command the way an agent would.
    python3 -m unittest discover -s tests -v"""
import os, subprocess, sys, tempfile, unittest

KIT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'labkit', 'cli.py')


def run(args, cwd, stdin=None):
    r = subprocess.run([sys.executable] + args, cwd=cwd, input=stdin, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def write(path, text, mode='w'):
    with open(path, mode) as fh: fh.write(text)


def readf(path):
    with open(path) as fh: return fh.read()


def sh(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)


class LabkitTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.d = os.path.join(self.tmp.name, 'proj')
        rc, out = run([KIT, 'init', self.d], self.tmp.name); self.assertEqual(rc, 0, out)
        sh('git config user.email t@t && git config user.name t && git add -A && git commit -qm init', self.d)
        self.L = lambda *a, stdin=None: run(['tools/labkit.py'] + list(a), self.d, stdin)

    def tearDown(self):
        self.tmp.cleanup()

    def test_init_lays_down_everything(self):
        for p in ('CLAUDE.md', 'PROJECT.md', 'HANDOFF.md', 'ROADMAP.md', 'FINDINGS.md', 'KNOWLEDGE/README.md', 'labkit.json',
                  'tools/labkit.py', '.claude/settings.json', '.claude/hooks/session_start.sh',
                  '.claude/skills/handoff/SKILL.md', '.claude/skills/prereg/SKILL.md'):
            self.assertTrue(os.path.exists(os.path.join(self.d, p)), p)
        self.assertIn('append-check', readf(os.path.join(self.d, '.git', 'hooks', 'pre-commit')))
        rc, out = run([KIT, 'init', self.d], self.tmp.name)                    # idempotent: nothing overwritten
        self.assertEqual(rc, 0); self.assertIn('0 files written', out)

    def test_add_status_and_dead(self):
        self.assertEqual(self.L('next')[1].strip(), '1')
        self.L('add', 'The baseline reproduces the published value', stdin='Result: 0.148 vs 0.148.\n')
        self.L('add', 'A sweep moves it toward the target (builds on #1)', stdin='See #1. Gap closed 11%.\n')
        rc, out = self.L('status', '1'); self.assertIn('LIVE', out); self.assertIn('cited by: #2', out)
        sh('git add -A && git commit -qm f', self.d)
        p = os.path.join(self.d, 'FINDINGS.md'); t = readf(p)
        t = t.replace('## #1 — The baseline reproduces the published value', '## #1 — The baseline reproduces the published value [RETRACTED by #3: wrong file]')
        write(p, t); self.L('add', 'The baseline used the wrong file; #1 retracted', stdin='Retracts #1.\n')
        self.assertEqual(sh('git add -A && git commit -qm retract', self.d).returncode, 0)   # a heading-end tag is allowed
        rc, out = self.L('status', '1'); self.assertIn('DEAD (RETRACTED by #3)', out)
        rc, out = self.L('status', '2'); self.assertIn('#1†', out)
        rc, out = self.L('dead'); self.assertIn('1 dead of 3', out)
        doc = os.path.join(self.d, 'note.md'); write(doc, 'As shown in #1 and #2.')
        rc, out = self.L('check', 'note.md'); self.assertEqual(rc, 1); self.assertIn('#1  DEAD', out)
        rc, out = self.L('grep', 'gap closed'); self.assertIn('#2:', out)
        t = readf(p).replace('## #2 — A sweep moves it toward the target (builds on #1)', '## #2 — A sweep moves it toward the target (builds on #1) [superseded by #3]')
        write(p, t); rc, out = self.L('status', '2'); self.assertIn('DEAD (SUPERSEDED by #3)', out)      # lowercase tags count too

    def test_append_only_refuses_rewrites(self):
        self.L('add', 'First result', stdin='Body line one.\n'); sh('git add -A && git commit -qm f', self.d)
        p = os.path.join(self.d, 'FINDINGS.md'); write(p, readf(p).replace('Body line one.', 'Body line ONE.'))
        r = sh('git add -A && git commit -qm edit', self.d)
        self.assertNotEqual(r.returncode, 0); self.assertIn('changed or moved', r.stdout + r.stderr)
        rc, out = self.L('append-check', '--worktree'); self.assertEqual(rc, 1)

    def test_budget_and_cover(self):
        p = os.path.join(self.d, 'HANDOFF.md'); write(p, '# HANDOFF\n- result (#1)\n- range (#2–#5)\n- file `run.py`\n')
        sh('git add -A && git commit -qm h', self.d)
        write(p, '# HANDOFF\n- results (#1–#4)\n')                 # drops #5 and run.py
        rc, out = self.L('cover', 'HANDOFF.md'); self.assertEqual(rc, 1); self.assertIn('#5', out); self.assertIn('run.py', out)
        write(p, 'x' * 9000)
        rc, out = self.L('budget'); self.assertIn('OVER  ENTRY   HANDOFF.md', out)
        rc, out = self.L('budget', '--strict'); self.assertEqual(rc, 1)
        f = os.path.join(self.d, 'FINDINGS.md'); write(f, '\n# #7. odd shape\n\n## #8 — fine\n\n## #8 — duplicate\n', 'a')
        rc, out = self.L('budget'); self.assertIn('duplicate finding numbers: #8', out); self.assertIn('1 heading-like lines not parsed', out)

    def test_prereg(self):
        s = os.path.join(self.d, 'step1.py'); write(s, '"""Question.\nPredictions stated before the run: T1 passes."""\nprint(1)\n')
        rc, out = self.L('prereg', 'step1.py'); self.assertEqual(rc, 1); self.assertIn('not committed', out)
        sh('git add step1.py && git commit -qm prereg', self.d)
        rc, out = self.L('prereg', 'step1.py'); self.assertEqual(rc, 0, out); self.assertIn('pre-registered at', out)
        write(s, 'print(2)\n', 'a')
        rc, out = self.L('prereg', 'step1.py'); self.assertEqual(rc, 1); self.assertIn('changed since', out)
        n = os.path.join(self.d, 'nopred.py'); write(n, 'print(1)\n'); sh('git add nopred.py && git commit -qm x', self.d)
        rc, out = self.L('prereg', 'nopred.py'); self.assertEqual(rc, 1); self.assertIn('no prediction block', out)


if __name__ == '__main__':
    unittest.main()
