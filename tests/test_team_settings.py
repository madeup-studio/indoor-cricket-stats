import team_settings as TS
def test_defaults_shape():
    assert TS.SHOW_DEFAULTS["awards"] is False and TS.SHOW_DEFAULTS["medals"] is True
    assert set(TS.SHOW_DEFAULTS) == {"awards", "medals", "stage_tags", "streaks", "partnerships", "hattricks", "records"}
    assert set(TS.SHOW_DEFAULTS["records"]) == {"high_total", "low_total", "biggest_win", "heaviest_loss", "best_skin",
        "most_wkts_game", "fewest_extras_game", "best_contribution", "most_runs_game", "best_econ", "most_runouts_created"}
    assert set(TS.SHOW_NOTES) == set(TS.SHOW_DEFAULTS)
def test_merge_partial_unknown_and_absent():
    assert TS.merge_show({}) == TS.SHOW_DEFAULTS
    m = TS.merge_show({"show": {"awards": True, "records": {"best_econ": False}, "bogus": False}})
    assert m["awards"] is True and m["records"]["best_econ"] is False and m["records"]["high_total"] is True
    assert "bogus" not in m and TS.SHOW_DEFAULTS["awards"] is False       # defaults untouched
