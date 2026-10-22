import pytest
import rules


def test_preset_defaults():
    r = rules.load_rules({})
    assert r == dict(wicket_runs=-5, extra_runs=2, balls_per_over=6, extra_ball_last_over=True,
                     skins=4, overs_per_pair=4, players_per_side=8)


def test_rules_defaults_when_absent():
    assert rules.load_rules(None) == rules.load_rules({"name": "X"})


def test_override_and_snapshot():
    r = rules.load_rules({"rules": {"preset": "indoor-sa", "wicket_runs": -3}})
    assert r["wicket_runs"] == -3 and r["extra_runs"] == 2
    g = {"meta": {"rules": {"wicket_runs": -5}}}
    assert rules.game_rules(g, r)["wicket_runs"] == -5


def test_unknown_key_rejected():
    with pytest.raises(ValueError):
        rules.load_rules({"rules": {"wickets": -5}})


def test_unknown_preset_rejected():
    with pytest.raises(ValueError):
        rules.load_rules({"rules": {"preset": "outdoor-uk"}})


def test_skin_ball_counts():
    assert rules.skin_ball_counts(rules.load_rules({})) == {24, 25}
    assert rules.skin_ball_counts(rules.load_rules({"rules": {"extra_ball_last_over": False}})) == {24}


def test_max_cells_last_over():
    assert rules.max_cells_last_over(rules.load_rules({})) == 7
    assert rules.max_cells_last_over(rules.load_rules({"rules": {"extra_ball_last_over": False}})) == 6
