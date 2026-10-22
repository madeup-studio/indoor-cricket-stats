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
