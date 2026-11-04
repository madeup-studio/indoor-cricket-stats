import json, os

import yaml


def test_jsonable_no_nan():
    from collections import Counter
    import build_site as B
    out = B.jsonable({"a": Counter({5: 2}), "b": (1, "x"), "c": float("nan"), "d": {("p", "q"): 1}})
    assert out == {"a": {"5": 2}, "b": [1, "x"], "c": None, "d": {"('p', 'q')": 1}}
    assert B.jsonable([float("inf"), (2, 1), True, None]) == [None, [2, 1], True, None]


def test_build_example_site(tmp_path):
    import build_site as B
    files = B.build(str(tmp_path))
    assert (tmp_path / "index.html").exists() and (tmp_path / "functions" / "_middleware.js").exists()
    idx = json.load(open(tmp_path / "data" / "index.json", encoding="utf-8"))
    assert idx == [{"slug": "our-team", "name": "Our Team", "badge": "OURS", "colours": {"brand": "#4f46e5", "gold": "#f5b301"}}]
    p = json.load(open(tmp_path / "data" / "our-team.json", encoding="utf-8"))
    assert p["seasons"][0]["label"] == "Spring 2026" and p["seasons"][0]["stats"]["team"]["played"] == 1
    assert p["games"][0]["key"] == "2026-10-07" and p["games"][0]["letter"]["sections"]
    assert p["alltime"]["records"]["team"]["longest_win_streak"]["value"] == 0
    assert p["alltime"]["records"]["individual"]["best_contribution"]["name"] == "Our P2"
    assert os.path.join(str(tmp_path), "data", "our-team.json") in files


def test_payload_shape_and_records():
    import build_site as B
    import paths
    p = B.team_payload(os.path.join(paths.TEAMS_DIR, "example-team"), None)
    t = p["team"]
    assert (t["slug"], t["name"], t["badge"], t["arena"], t["league"], t["gate"]) == (
        "our-team", "Our Team", "OURS", "Example Arena", "Mens E", "pin")
    assert t["coach"] == {"enabled": True, "tone": "banter"} and t["rules"]["wicket_runs"] == -5
    s = p["seasons"][0]
    assert (s["key"], s["games"]) == ("2026-09-01", ["2026-10-07"])
    g = p["games"][0]
    assert (g["season"], g["opp"], g["outcome"], g["total"], g["against"], g["skins"], g["oskins"]) == (
        "2026-09-01", "Opponents", "loss", 51, 80, 1, 3)
    assert g["skin_scores"] == [[28, 15], [6, 21], [6, 15], [11, 29]]
    assert g["pom"] == "Opp P7" and g["pom_ours"] is False and g["top_c"] == ["Our P2", 5]
    assert len(g["summaries"]["ours"]) == 8 and len(g["summaries"]["theirs"]) == 8
    assert {"Our P2", "Our P8"} <= set(p["players"])
    assert p["players"]["Our P2"] == {"slug": "our-p2", "photo": None}
    assert "Opp P7" not in p["players"]
    tr, ir = p["alltime"]["records"]["team"], p["alltime"]["records"]["individual"]
    assert set(tr) == {"high_total", "low_total", "biggest_win", "heaviest_loss", "best_skin",
                       "most_wkts_game", "fewest_extras_game", "longest_win_streak", "longest_loss_streak"}
    assert set(ir) == {"best_contribution", "most_runs_game", "most_wkts_game", "best_econ",
                       "best_partnership", "hattricks", "most_runouts_created"}
    assert tr["high_total"] == {"value": 51, "opp": "Opponents", "date": "2026-10-07", "key": "2026-10-07"}
    assert tr["heaviest_loss"]["value"] == -29 and tr["biggest_win"] is None
    assert tr["best_skin"]["value"] == 15
    assert tr["most_wkts_game"]["value"] == 12 and tr["fewest_extras_game"]["value"] == 17
    assert tr["longest_loss_streak"] == {"value": 1, "from": "2026-10-07", "to": "2026-10-07"}
    assert tr["longest_win_streak"] == {"value": 0, "from": None, "to": None}
    assert ir["best_contribution"]["value"] == 5
    assert (ir["most_runs_game"]["name"], ir["most_runs_game"]["value"]) == ("Our P1", 17)
    assert (ir["most_wkts_game"]["name"], ir["most_wkts_game"]["value"]) == ("Our P3", 4)
    assert (ir["best_econ"]["name"], ir["best_econ"]["value"]) == ("Our P3", -3.0)
    assert ir["best_partnership"]["names"] == ["Our P1", "Our P2"]
    assert ir["best_partnership"]["value"] == 28
    assert ir["hattricks"] == [] and ir["most_runouts_created"]["value"] == 1
    assert p["generated"] == "2026-10-07"


def test_games_payload_double_header(tmp_team_two_games_same_day):
    # fixture: example team + a copy of the game dated the same day vs "Other Side"
    import build_site as B
    p = B.team_payload(tmp_team_two_games_same_day, None)
    assert sorted(g["key"] for g in p["games"]) == ["2026-10-07-opponents", "2026-10-07-other-side"]
    assert p["seasons"][0]["games"] == [g["key"] for g in p["games"]]


def test_build_site_summaries_only(tmp_team_summaries_only):
    # fixture: example game with ball_by_ball status != verified
    import build_site as B
    p = B.team_payload(tmp_team_summaries_only, None)
    assert p["alltime"]["records"]["individual"]["best_partnership"] is None
    assert p["seasons"][0]["stats"]["partnerships"] == []
    assert p["alltime"]["records"]["team"]["fewest_extras_game"] is None
    assert p["alltime"]["records"]["individual"]["most_runouts_created"] is None
    assert "NaN" not in json.dumps(p)


def test_cli_builds_several_teams_without_TEAM(tmp_team, tmp_path, run_script):
    import shutil
    shutil.copytree(tmp_team / "example-team", tmp_team / "second")
    cfg_path = tmp_team / "second" / "team.yaml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    cfg["name"], cfg["badge"] = "Second Side", "SEC"
    cfg_path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    out = tmp_path / "site"
    r = run_script("build_site.py", "--out", out, env={"TEAM": "", "TEAMS_DIR": str(tmp_team)})
    assert r.returncode == 0, r.stdout + r.stderr
    idx = json.loads((out / "data" / "index.json").read_text(encoding="utf-8"))
    assert [t["slug"] for t in idx] == ["our-team", "second-side"]
    assert (out / "data" / "second-side.json").exists()


def test_cli_builds_empty_repo(tmp_path, run_script):
    (tmp_path / "Teams").mkdir()
    out = tmp_path / "site"
    r = run_script("build_site.py", "--out", out, env={"TEAM": "", "TEAMS_DIR": str(tmp_path / "Teams")})
    assert r.returncode == 0, r.stdout + r.stderr
    assert json.loads((out / "data" / "index.json").read_text(encoding="utf-8")) == []
    assert (out / "index.html").exists()


def test_viewer_tests_not_copied(tmp_path):
    import build_site as B
    B.build(str(tmp_path))
    assert not list(tmp_path.rglob("*.test.js")) and not (tmp_path / "tests").exists()
    assert not (tmp_path / "package.json").exists()      # dev-only (node --test)


def test_payload_show_defaults_and_override(tmp_team):
    import build_site as B, team_settings as TS, yaml
    team_dir = tmp_team / "example-team"
    assert B.team_payload(str(team_dir), None)["team"]["show"] == TS.SHOW_DEFAULTS
    cfg = yaml.safe_load((team_dir / "team.yaml").read_text(encoding="utf-8"))
    cfg["show"] = {"awards": True, "records": {"low_total": False}}
    (team_dir / "team.yaml").write_text(yaml.safe_dump(cfg), encoding="utf-8")
    show = B.team_payload(str(team_dir), None)["team"]["show"]
    assert show["awards"] is True and show["records"]["low_total"] is False and show["streaks"] is True


def test_payload_seasons_medal_finished_awards(tmp_team_two_seasons):
    import build_site as B
    p = B.team_payload(tmp_team_two_seasons, None)
    s0, s1 = p["seasons"]
    assert (s0["key"], s0["medal"], s0["finish"], s0["finished"]) == ("2026-09-01", "silver", "2nd in Mens E", True)
    assert (s1["key"], s1["label"], s1["medal"], s1["finished"], s1["awards"]) == ("2027-01-12", "Summer 2027", None, False, None)
    assert set(s0["awards"]) == {"batter", "bowler", "player"} and s0["awards"]["player"]["name"].startswith("Our P")
    winners = {a["name"] for a in s0["awards"].values()}
    for n in winners:
        assert sum(p["players"][n]["awards"].values()) >= 1
    assert all("awards" not in v for k, v in p["players"].items() if k not in winners)


def test_payload_current_season_without_medal_is_not_finished(tmp_team_three_games):
    import build_site as B
    s = B.team_payload(tmp_team_three_games, None)["seasons"][0]
    assert s["finished"] is False and s["awards"] is None and s["medal"] is None


def test_payload_game_stage(tmp_path):
    import build_site as B
    from conftest import clone_game, _copy_example, _run_script
    teams = _copy_example(tmp_path)
    clone_game(teams, "2026-10-14", stage="final")
    assert _run_script("build_scorecards.py", env={"TEAMS_DIR": str(teams)}).returncode == 0
    p = B.team_payload(str(teams / "example-team"), None)
    assert [g["stage"] for g in p["games"]] == [None, "final"]


def test_bad_medal_fails_the_build(tmp_team):
    import build_site as B, pytest
    (tmp_team / "example-team" / "2026-09-01" / "season.yaml").write_text("medal: Silver\n", encoding="utf-8")
    with pytest.raises(ValueError, match="season.yaml"):
        B.team_payload(str(tmp_team / "example-team"), None)
