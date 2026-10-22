"""The ai-coach skill's stats snippet must run as written, including in a repo
with several teams (where every per-team command needs TEAM=<folder>)."""
import os, re, shutil, subprocess, sys

from conftest import REPO


def snippet():
    text = open(os.path.join(REPO, ".claude", "skills", "ai-coach", "SKILL.md"), encoding="utf-8").read()
    code = re.search(r"```python\n(.*?)```", text, re.S).group(1)
    return "\n".join(line[3:] if line.startswith("   ") else line for line in code.splitlines())


def test_ai_coach_snippet_runs_with_two_teams(tmp_team):
    shutil.copytree(tmp_team / "example-team", tmp_team / "second")
    code = (snippet().replace("<KEY>", "2026-10-07").replace("<TEAM>", "example-team")
            + "\nprint(d['team']['games'][-1]['total'], a['team']['played'])\n")
    env = {k: v for k, v in os.environ.items() if k != "TEAM"}
    env.update(TEAMS_DIR=str(tmp_team), PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, "-c", code], cwd=REPO, env=env,
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.split() == ["51", "1"]
