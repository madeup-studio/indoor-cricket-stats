import yaml


def test_new_team_writes_spec_settings(tmp_path, run_script):
    teams = tmp_path / "Teams"
    r = run_script("new_team.py", "Zed Team", "--arena", "Example Arena", "--league", "Mens F",
                   "--folder", "zed", "--season-start", "2026-09-01", env={"TEAMS_DIR": str(teams)})
    assert r.returncode == 0, r.stderr
    cfg = yaml.safe_load((teams / "zed" / "team.yaml").read_text(encoding="utf-8"))
    import rules
    assert rules.load_rules(cfg) == rules.PRESETS["indoor-sa"]
    assert cfg["rules"]["preset"] == "indoor-sa"
    assert cfg["coach"] == {"enabled": True, "tone": "banter", "language": "en"}
    assert (cfg["gate"], cfg["admins"], cfg["pdf"], cfg["publish_unconfirmed"],
            cfg["game_type"], cfg["league"]) == ("pin", [], False, True, "indoor", "Mens F")
    assert (teams / "zed" / "2026-09-01" / "data").is_dir()


def test_new_team_tone_and_preset_options(tmp_path, run_script):
    teams = tmp_path / "Teams"
    r = run_script("new_team.py", "Zed Team", "--folder", "zed", "--tone", "serious",
                   "--gate", "none", env={"TEAMS_DIR": str(teams)})
    assert r.returncode == 0, r.stderr
    cfg = yaml.safe_load((teams / "zed" / "team.yaml").read_text(encoding="utf-8"))
    assert cfg["coach"]["tone"] == "serious" and cfg["gate"] == "none"
