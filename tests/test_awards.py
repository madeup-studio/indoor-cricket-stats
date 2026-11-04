import os, report_data as RD, roster, stats_core as S

def _season(team_dir, folder):
    R = roster.load(os.path.join(team_dir, "players.yaml"))
    return RD.build(S.load_matches(os.path.join(team_dir, folder, "scorecards")), R)

def test_awards_follow_the_rankings(tmp_team_three_games):
    d = _season(tmp_team_three_games, "2026-09-01")
    a = RD.season_awards(d)
    first = lambda k: next(x for x in d[k] if x["ranked"])
    assert a["batter"] == {"name": first("batting")["name"], "value": first("batting")["avg12"]}
    assert a["bowler"] == {"name": first("bowling")["name"], "value": first("bowling")["econ"]}
    assert a["player"] == {"name": first("allround")["name"], "value": first("allround")["avgc"]}
    assert a["player"]["name"].startswith("Our P")

def test_no_award_when_nobody_qualifies(tmp_team):
    d = _season(str(tmp_team / "example-team"), "2026-09-01")       # one game < MIN_GAMES
    assert RD.season_awards(d) == {"batter": None, "bowler": None, "player": None}
