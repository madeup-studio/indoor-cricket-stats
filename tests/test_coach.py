import yaml
import coach


def M(date, opp, tf=50, ta=60):
    return dict(date=date, opponent=opp, team_total=tf, opponent_total=ta, outcome="loss",
                team_skins_won=1, opponent_skins_won=3, team_summary=[], opponent_summary=[],
                team="Our Team", season="Spring")


def test_game_keys_double_header():
    ms = [M("2026-10-07", "A"), M("2026-10-14", "B"), M("2026-10-14", "C")]
    assert coach.game_keys(ms) == ["2026-10-07", "2026-10-14-b", "2026-10-14-c"]


def test_slug():
    assert coach.slug("  Other Side!! ") == "other-side"


def test_fp_prefix_stable():
    ms = [M("2026-10-07", "A"), M("2026-10-14", "B")]
    assert coach.game_fp(ms[:1]) == "1g50f60a-2026-10-07"
    assert coach.game_fp(ms[:1]) == coach.game_fp((ms + [M("2026-10-21", "D")])[:1])


def test_status_and_latest():
    ms = [M("2026-10-07", "A"), M("2026-10-14", "B")]
    letters = {"2026-10-07": {"fp": coach.game_fp(ms[:1]), "sections": [{"title": "t", "html": "<p>x</p>"}], "players": []},
               "2026-10-14": {"fp": "wrong", "sections": [], "players": []}}
    st = coach.status([("d", "Spring", ms)], letters)
    assert [s["state"] for s in st] == ["ok", "stale"]
    assert coach.latest_letter(ms, letters)[0] == "2026-10-07"


def test_status_missing_and_alltime_fp():
    s1 = [M("2026-03-01", "A")]
    s2 = [M("2026-10-07", "B", tf=40, ta=30)]
    letters = {"2026-10-07": {"fp": coach.game_fp(s1 + s2), "sections": [{"title": "t", "html": "x"}], "players": []}}
    st = coach.status([("d1", "Autumn", s1), ("d2", "Spring", s2)], letters)
    assert [(s["key"], s["season"], s["state"]) for s in st] == [
        ("2026-03-01", "Autumn", "missing"), ("2026-10-07", "Spring", "ok")]
    assert st[1]["fp"] == "2g90f90a-2026-10-07"
    # a later season's letter is ok against the all-time history it was written from
    assert coach.latest_letter(s2, letters, history=s1 + s2)[0] == "2026-10-07"
    assert coach.latest_letter(s2, letters) == (None, None)   # season-only prefix differs


def test_convert_legacy():
    ms = [M("2026-10-07", "A"), M("2026-10-14", "B")]
    notes = {"Spring": {"_letter": {"fp": "old", "sections": [{"title": "t", "html": "x"}], "players": []}}}
    out = coach.convert_legacy(notes, [("d", "Spring", ms)])
    assert out[0]["game"] == "2026-10-14" and out[0]["fp"] == coach.game_fp(ms)


def test_load_letters_new_format(tmp_path):
    (tmp_path / "coach_notes.yaml").write_text(yaml.safe_dump({"letters": [
        {"game": "2026-10-07", "fp": "1g1f1a-2026-10-07", "sections": [{"title": "t", "html": "x"}],
         "players": [{"name": "Our P2", "note": "n"}]}]}), encoding="utf-8")
    L = coach.load_letters(str(tmp_path))
    assert L == {"2026-10-07": {"fp": "1g1f1a-2026-10-07", "sections": [{"title": "t", "html": "x"}],
                                "players": [{"name": "Our P2", "note": "n"}]}}
    assert coach.load_letters(str(tmp_path / "nope")) == {}


def test_coach_settings_default():
    import paths
    assert paths.COACH["enabled"] is True and paths.COACH["tone"] == "banter"


def test_status_cli_lists_missing(tmp_team, run_script):
    r = run_script("coach.py", "--status", env={"TEAMS_DIR": str(tmp_team)})
    assert r.returncode == 0
    (tmp_team / "example-team" / "coach_notes.yaml").write_text("letters: []\n", encoding="utf-8")
    r = run_script("coach.py", "--status", env={"TEAMS_DIR": str(tmp_team)})
    assert r.returncode == 0
    assert r.stdout.strip().split("\t") == ["2026-10-07", "1g51f80a-2026-10-07", "Spring 2026", "missing"]


def test_convert_legacy_cli(tmp_team, run_script):
    notes = tmp_team / "example-team" / "coach_notes.yaml"
    notes.write_text(yaml.safe_dump({"Spring 2026": {"_letter": {
        "fp": "old", "sections": [{"title": "The last game", "html": "<p>x</p>"}], "players": []}}}),
        encoding="utf-8")
    r = run_script("coach.py", "--convert-legacy", env={"TEAMS_DIR": str(tmp_team)})
    assert r.returncode == 0, r.stderr
    data = yaml.safe_load(notes.read_text(encoding="utf-8"))
    assert data["letters"][0]["game"] == "2026-10-07"
    assert data["letters"][0]["fp"] == "1g51f80a-2026-10-07"
    assert (tmp_team / "example-team" / "coach_notes.legacy.yaml").exists()
