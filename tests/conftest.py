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
    """Copy the example team, cut back to its original single game (2026-10-07): the
    public example has since grown, and the fixtures below build their own extras."""
    import shutil
    teams = tmp_path / "Teams"
    shutil.copytree(os.path.join(REPO, "Teams", "example-team"), teams / "example-team",
                    ignore=shutil.ignore_patterns(".build", "*.pdf", "2026-10-14*",
                                                  "2026-10-21*", "2027-01-1*", "season.yaml"))
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


def clone_game(teams_dir, date, *, season_folder="2026-09-01", season_label=None,
               mirror=False, stage=None):
    """Clone the example game into `<season_folder>/data/<date>.json` under the tmp
    copy at `teams_dir`; returns the written path. `mirror=True` swaps the two sides
    so Our Team wins 80-51. Does not run build_scorecards.py."""
    import json, re
    team_dir = teams_dir / "example-team"
    src = team_dir / "2026-09-01" / "data" / "2026-10-07.json"
    text = src.read_text(encoding="utf-8")
    if mirror:
        text = (text.replace("Our Team", "@@T@@").replace("Opponents", "Our Team")
                .replace("@@T@@", "Opponents"))
        text = re.sub(r"Our P(\d)", r"@@P\1@@", text)
        text = re.sub(r"Opp P(\d)", r"Our P\1", text)
        text = re.sub(r"@@P(\d)@@", r"Opp P\1", text)
    g = json.loads(text)
    g["date"] = date
    if mirror:
        g["team"], g["opponent"] = "Our Team", "Opponents"
        res = g["result"]
        for a, b in (("team_total", "opponent_total"), ("team_skins", "opponent_skins"),
                     ("team_skins_won", "opponent_skins_won")):
            res[a], res[b] = res[b], res[a]
        res["outcome"] = "win"
    if season_label is not None:
        g["meta"]["season"] = season_label
    if stage is not None:
        g["meta"]["stage"] = stage
    season = team_dir / season_folder
    (season / "data").mkdir(parents=True, exist_ok=True)
    (season / "scorecards").mkdir(parents=True, exist_ok=True)
    out = season / "data" / f"{date}.json"
    out.write_text(json.dumps(g, indent=1), encoding="utf-8")
    return out


@pytest.fixture
def tmp_team_three_games(tmp_path):
    """Example game + a straight clone (2026-10-14) + a mirrored win (2026-10-21), built;
    returns the team dir."""
    teams = _copy_example(tmp_path)
    clone_game(teams, "2026-10-14")
    clone_game(teams, "2026-10-21", mirror=True)
    r = _run_script("build_scorecards.py", env={"TEAMS_DIR": str(teams)})
    assert r.returncode == 0, r.stderr
    return str(teams / "example-team")


@pytest.fixture
def tmp_team_two_seasons(tmp_path):
    """The three games plus season.yaml on the first season and a second season
    (Summer 2027) with one game, built; returns the team dir."""
    teams = _copy_example(tmp_path)
    clone_game(teams, "2026-10-14")
    clone_game(teams, "2026-10-21", mirror=True)
    (teams / "example-team" / "2026-09-01" / "season.yaml").write_text(
        'medal: silver\nfinish: "2nd in Mens E"\n', encoding="utf-8")
    clone_game(teams, "2027-01-14", season_folder="2027-01-12", season_label="Summer 2027")
    r = _run_script("build_scorecards.py", env={"TEAMS_DIR": str(teams)})
    assert r.returncode == 0, r.stderr
    return str(teams / "example-team")
