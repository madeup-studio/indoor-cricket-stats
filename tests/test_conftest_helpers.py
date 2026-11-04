import json
from conftest import clone_game, _copy_example, _run_script

def test_clone_and_mirror_reconcile(tmp_path):
    teams = _copy_example(tmp_path)
    clone_game(teams, "2026-10-14")
    p = clone_game(teams, "2026-10-21", mirror=True)
    g = json.loads(p.read_text(encoding="utf-8"))
    assert g["date"] == "2026-10-21" and g["result"]["outcome"] == "win"
    assert (g["team"], g["opponent"], g["innings"][0]["batting_team"]) == ("Our Team", "Opponents", "Our Team")
    assert (g["result"]["team_total"], g["result"]["opponent_total"]) == (80, 51)
    assert g["result"]["player_of_match"] == "Our P7" and g["result"]["player_of_match_team"] == "Our Team"
    assert {r["name"] for r in g["summaries"]["Our Team"]} == {f"Our P{i}" for i in range(1, 9)}
    r = _run_script("build_scorecards.py", env={"TEAMS_DIR": str(teams)})
    assert r.returncode == 0, r.stderr
    r = _run_script("validate_ballbyball.py", env={"TEAMS_DIR": str(teams)})
    assert "ALL RECONCILE" in r.stdout, r.stdout[-1500:]

def test_two_seasons_fixture(tmp_team_two_seasons):
    import os, yaml
    assert os.path.exists(os.path.join(tmp_team_two_seasons, "2027-01-12", "data", "2027-01-14.json"))
    meta = yaml.safe_load(open(os.path.join(tmp_team_two_seasons, "2026-09-01", "season.yaml"), encoding="utf-8"))
    assert meta == {"medal": "silver", "finish": "2nd in Mens E"}
    r = _run_script("validate_ballbyball.py", env={"TEAMS_DIR": os.path.dirname(tmp_team_two_seasons)})
    assert "ALL RECONCILE" in r.stdout
