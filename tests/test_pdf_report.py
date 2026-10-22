"""generate_pdf_report.py: per-game letters, warnings, rules. HTML only (no browser)."""
import yaml

FP = "1g51f80a-2026-10-07"
ENV = {"PDF_BROWSER": "none"}


def _run(run_script, teams):
    return run_script("generate_pdf_report.py", env=dict(ENV, TEAMS_DIR=str(teams)))


def _season_html(teams):
    return (teams / "example-team" / ".build" / "season-spring-2026.html").read_text(encoding="utf-8")


def _set_letters(teams, letters):
    (teams / "example-team" / "coach_notes.yaml").write_text(
        yaml.safe_dump({"letters": letters}), encoding="utf-8")


def test_warns_for_missing_letter(tmp_team, run_script):
    _set_letters(tmp_team, [])
    r = _run(run_script, tmp_team)
    assert r.returncode == 0, r.stderr
    assert f"!! coach letter missing: 2026-10-07 {FP}" in r.stdout


def test_uses_the_games_letter(tmp_team, run_script):
    _set_letters(tmp_team, [{"game": "2026-10-07", "fp": FP,
                             "sections": [{"title": "Zebra section", "html": "<p>hello</p>"}],
                             "players": [{"name": "Our P2", "note": "well bowled"}]}])
    r = _run(run_script, tmp_team)
    assert r.returncode == 0, r.stderr
    assert "!! coach letter" not in r.stdout
    html = _season_html(tmp_team)
    assert "Zebra section" in html and "well bowled" in html


def test_stale_letter_warns(tmp_team, run_script):
    _set_letters(tmp_team, [{"game": "2026-10-07", "fp": "old",
                             "sections": [{"title": "Zebra section", "html": "x"}], "players": []}])
    r = _run(run_script, tmp_team)
    assert f"!! coach letter stale: 2026-10-07 {FP}" in r.stdout
    assert "Zebra section" not in _season_html(tmp_team)


def test_coach_off_means_no_letter(tmp_team, run_script):
    team_yaml = tmp_team / "example-team" / "team.yaml"
    cfg = yaml.safe_load(team_yaml.read_text(encoding="utf-8"))
    cfg["coach"] = {"enabled": False}
    team_yaml.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    _set_letters(tmp_team, [])
    r = _run(run_script, tmp_team)
    assert "!! coach letter" not in r.stdout
    assert "Letter from the AI Coach" not in _season_html(tmp_team)


def test_runs_lost_uses_wicket_value(tmp_team, run_script):
    team_yaml = tmp_team / "example-team" / "team.yaml"
    cfg = yaml.safe_load(team_yaml.read_text(encoding="utf-8"))
    cfg["rules"] = {"wicket_runs": -3}
    team_yaml.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    _run(run_script, tmp_team)
    html = _season_html(tmp_team)
    assert "3 × outs ÷ games" in html and "5 × outs ÷ games" not in html
