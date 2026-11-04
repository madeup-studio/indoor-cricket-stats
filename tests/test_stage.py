import json, os
from conftest import clone_game, _copy_example, _run_script
import stats_core

def _env(teams): return {"TEAMS_DIR": str(teams)}

def test_stage_round_trips_through_frontmatter(tmp_path):
    teams = _copy_example(tmp_path)
    clone_game(teams, "2026-10-14", stage="final")
    assert _run_script("build_scorecards.py", env=_env(teams)).returncode == 0
    ms = stats_core.load_matches(str(teams / "example-team" / "2026-09-01" / "scorecards"))
    assert [m.get("stage") for m in ms] == [None, "final"]
    text = (teams / "example-team" / "2026-09-01" / "scorecards" / "2026-10-07-our-team-vs-opponents.md").read_text(encoding="utf-8")
    assert "stage:" not in text.split("---")[1]

def test_validator_accepts_each_stage_and_rejects_others(tmp_path):
    teams = _copy_example(tmp_path)
    for i, st in enumerate(("league", "playoff", "semi-final", "final")):
        clone_game(teams, f"2026-11-{10 + i:02d}", stage=st)
    assert "ALL RECONCILE" in _run_script("validate_ballbyball.py", env=_env(teams)).stdout
    clone_game(teams, "2026-11-20", stage="cup")
    r = _run_script("validate_ballbyball.py", env=_env(teams))
    assert r.returncode == 1 and "[M] meta.stage 'cup'" in r.stdout
