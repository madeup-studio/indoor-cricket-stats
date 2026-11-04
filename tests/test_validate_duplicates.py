import json
from conftest import clone_game, _copy_example, _run_script

def test_same_date_and_opponent_twice_fails(tmp_path):
    teams = _copy_example(tmp_path)
    p = clone_game(teams, "2026-10-07")                # writes 2026-10-07.json over the original
    g = json.loads(p.read_text(encoding="utf-8"))
    (p.parent / "2026-10-07-again.json").write_text(json.dumps(g), encoding="utf-8")
    r = _run_script("validate_ballbyball.py", env={"TEAMS_DIR": str(teams)})
    assert r.returncode == 1
    assert "duplicate game: 2026-10-07-again.json and 2026-10-07.json both record 2026-10-07 vs Opponents" in r.stdout

def test_double_header_is_not_a_duplicate(tmp_team_two_games_same_day):
    import os
    r = _run_script("validate_ballbyball.py", env={"TEAMS_DIR": os.path.dirname(tmp_team_two_games_same_day)})
    assert "ALL RECONCILE" in r.stdout and "duplicate" not in r.stdout
