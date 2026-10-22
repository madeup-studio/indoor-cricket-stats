def test_example_game_reconciles(run_script):
    r = run_script("validate_ballbyball.py")
    assert r.returncode == 0 and "ALL RECONCILE" in r.stdout


def test_example_team_stats():
    import report_data as RD
    seasons, allm, R = RD.load_all()
    d = RD.build(allm, R)
    t = d["team"]
    assert (t["played"], t["won"], t["lost"]) == (1, 0, 1)
    assert (t["runs_for"], t["runs_against"]) == (51, 80)
    assert (t["skins_for"], t["skins_against"]) == (1, 3)
