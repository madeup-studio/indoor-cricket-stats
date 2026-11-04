import pytest, season_meta as SM
def test_missing_file_is_empty(tmp_path):
    assert SM.load(str(tmp_path)) == {"medal": None, "finish": None, "closed": False}
def test_reads_fields(tmp_path):
    (tmp_path / "season.yaml").write_text('medal: gold\nfinish: "Won the final"\nclosed: true\n', encoding="utf-8")
    assert SM.load(str(tmp_path)) == {"medal": "gold", "finish": "Won the final", "closed": True}
@pytest.mark.parametrize("bad", ["Silver", "2nd", "none"])
def test_bad_medal_raises_naming_file(tmp_path, bad):
    (tmp_path / "season.yaml").write_text(f"medal: {bad}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="season.yaml.*gold/silver/bronze"):
        SM.load(str(tmp_path))
def test_is_finished():
    empty = {"medal": None, "finish": None, "closed": False}
    assert SM.is_finished(0, 2, empty) and not SM.is_finished(1, 2, empty)
    assert SM.is_finished(1, 2, dict(empty, closed=True)) and SM.is_finished(1, 2, dict(empty, medal="bronze"))
