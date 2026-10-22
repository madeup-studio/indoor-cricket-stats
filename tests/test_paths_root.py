import os


def test_find_root_team_repo(tmp_path):
    import paths
    scripts = tmp_path / "repo" / "engine" / "scripts"
    scripts.mkdir(parents=True)
    (tmp_path / "repo" / "Teams").mkdir()
    assert paths.find_root(str(scripts)) == str(tmp_path / "repo")


def test_find_root_engine_repo(tmp_path):
    import paths
    scripts = tmp_path / "engine" / "scripts"
    scripts.mkdir(parents=True)
    (tmp_path / "engine" / "Teams").mkdir()
    assert paths.find_root(str(scripts)) == str(tmp_path / "engine")


def test_find_root_falls_back_to_engine(tmp_path):
    import paths
    deep = tmp_path / "a" / "b" / "c" / "d" / "e" / "f"
    deep.mkdir(parents=True)
    (tmp_path / "Teams").mkdir()          # more than 4 levels up: not found
    assert paths.find_root(str(deep)) == paths.ENGINE_ROOT
    assert os.path.isdir(os.path.join(paths.ENGINE_ROOT, "scripts"))
