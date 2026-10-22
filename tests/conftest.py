"""Shared test setup: point every script at the example team and make scripts/
importable. The env var must be set before any scripts module is imported."""
import os, subprocess, sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO, "scripts")

os.environ["TEAM"] = "example-team"
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)


def _run_script(name, *args, env=None):
    """Run `python scripts/<name> args...` from the repo root with TEAM=example-team
    (plus any `env` overrides); returns the CompletedProcess with text output."""
    full_env = dict(os.environ, TEAM="example-team", PYTHONIOENCODING="utf-8")
    full_env.update(env or {})
    return subprocess.run([sys.executable, os.path.join(SCRIPTS, name), *map(str, args)],
                          cwd=REPO, env=full_env, capture_output=True, text=True,
                          encoding="utf-8")


@pytest.fixture
def run_script():
    return _run_script


def _copy_example(tmp_path):
    import shutil
    teams = tmp_path / "Teams"
    shutil.copytree(os.path.join(REPO, "Teams", "example-team"), teams / "example-team",
                    ignore=shutil.ignore_patterns(".build", "*.pdf"))
    return teams


@pytest.fixture
def tmp_team(tmp_path):
    """A copy of Teams/example-team under tmp_path/Teams; returns that Teams dir."""
    return _copy_example(tmp_path)


@pytest.fixture
def tmp_team_two_games_same_day(tmp_path):
    """Example team + a copy of its game on the same day vs "Other Side"; returns the team dir."""
    import json
    teams = _copy_example(tmp_path)
    data = teams / "example-team" / "2026-09-01" / "data"
    g = json.loads((data / "2026-10-07.json").read_text(encoding="utf-8"))
    old, new = g["opponent"], "Other Side"
    g["opponent"] = new
    g["summaries"] = {(new if k == old else k): v for k, v in g["summaries"].items()}
    for inn in g["innings"]:
        if inn["batting_team"] == old:
            inn["batting_team"] = new
    if g["result"]["player_of_match_team"] == old:
        g["result"]["player_of_match_team"] = new
    (data / "2026-10-07-other-side.json").write_text(json.dumps(g, indent=1), encoding="utf-8")
    r = _run_script("build_scorecards.py", env={"TEAMS_DIR": str(teams)})
    assert r.returncode == 0, r.stderr
    return str(teams / "example-team")


@pytest.fixture
def tmp_team_summaries_only(tmp_path):
    """Example team whose only game has summaries but no verified ball-by-ball."""
    teams = _copy_example(tmp_path)
    cards = teams / "example-team" / "2026-09-01" / "scorecards"
    for card in cards.glob("*.md"):
        text = card.read_text(encoding="utf-8")
        card.write_text(text.replace("  status: verified", "  status: summaries-only"),
                        encoding="utf-8")
    return str(teams / "example-team")
