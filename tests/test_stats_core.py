def test_norm_ball_keeps_wides_lowercase():
    import stats_core as S
    assert [S.norm_ball(b) for b in ["w", "W", "nb", "NB", "c", "R", 4]] == ["w", "w", "nb", "nb", "C", "R", 4]


def test_season_report_counts_wides_and_no_balls():
    """The example game: our bowlers sent down 13 wides + 4 no-balls = 17 extras
    (the same figure the app's records and the coach's letter use)."""
    import report_data as RD, stats_core as S
    _, allm, _ = RD.load_all()
    season = S.aggregate(allm)["Spring 2026"]
    assert sum(p["extras_conceded"] for p in season["ours"].values()) == 17
