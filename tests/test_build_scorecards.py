import json


def test_card_footnote_shows_game_wicket_value(tmp_team, run_script):
    gpath = tmp_team / "example-team" / "2026-09-01" / "data" / "2026-10-07.json"
    game = json.loads(gpath.read_text(encoding="utf-8"))
    game["meta"]["rules"] = {"wicket_runs": -3}
    gpath.write_text(json.dumps(game, indent=1), encoding="utf-8")
    r = run_script("build_scorecards.py", env={"TEAMS_DIR": str(tmp_team)})
    assert r.returncode == 0, r.stderr
    card = next((tmp_team / "example-team" / "2026-09-01" / "scorecards").glob("*.md"))
    text = card.read_text(encoding="utf-8")
    assert "= dismissal (-3)" in text and "Dismissals worth −3" in text
    assert "(-5)" not in text and "−5" not in text
