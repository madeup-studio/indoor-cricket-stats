import subprocess


def test_scan_finds_whole_word(tmp_path):
    (tmp_path / "a.md").write_text("Zebra Team won again", encoding="utf-8")
    (tmp_path / "b.md").write_text("Zebrafish are fish", encoding="utf-8")
    import leak_check
    hits = leak_check.scan(str(tmp_path), ["Zebra Team", "Zebra"])
    assert ("a.md", "Zebra Team") in hits and ("a.md", "Zebra") in hits
    assert all(p != "b.md" for p, _ in hits)


def test_structure_guard(tmp_path):
    (tmp_path / "Teams" / "example-team").mkdir(parents=True)
    (tmp_path / "Teams" / "other-team").mkdir()
    import leak_check
    errs = leak_check.structure_errors(str(tmp_path))
    assert any("other-team" in e for e in errs)


def test_cli_exit_code(tmp_path, run_script):
    (tmp_path / "x.txt").write_text("Zebra Team", encoding="utf-8")
    lst = tmp_path / "list.txt"; lst.write_text("Zebra Team\n", encoding="utf-8")
    r = run_script("leak_check.py", "--root", str(tmp_path), "--list", str(lst))
    assert r.returncode == 1 and "!! leak: x.txt: Zebra Team" in r.stdout


def test_structure_guard_skips_team_repo(tmp_path):
    # a team repo (or the template) vendors the engine and keeps real teams + site/
    (tmp_path / "engine").mkdir()
    (tmp_path / "engine" / "VERSION").write_text("1.0.0\n", encoding="utf-8")
    (tmp_path / "Teams" / "Real-Team").mkdir(parents=True)
    (tmp_path / "site").mkdir()
    import leak_check
    assert leak_check.structure_errors(str(tmp_path)) == []


def test_structure_guard_flags_tracked_site(tmp_path):
    (tmp_path / "Teams" / "example-team").mkdir(parents=True)
    (tmp_path / "Teams" / "example-team" / "team.yaml").write_text("name: x\n", encoding="utf-8")
    (tmp_path / "site").mkdir()
    (tmp_path / "site" / "index.html").write_text("<p>x</p>", encoding="utf-8")
    git = lambda *a: subprocess.run(["git", "-C", str(tmp_path), *a], check=True, capture_output=True)
    git("init", "-q"); git("add", "-A")
    import leak_check
    errs = leak_check.structure_errors(str(tmp_path))
    assert any("site/" in e for e in errs)


def test_scan_skips_binaries(tmp_path):
    (tmp_path / "pic.png").write_bytes(b"\x89PNG\x00\x00Zebra Team")
    import leak_check
    assert leak_check.scan(str(tmp_path), ["Zebra Team"]) == []
