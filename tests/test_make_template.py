import json, os, shutil, subprocess, sys

from conftest import REPO


def test_assemble_template(tmp_path):
    import make_template as MT
    MT.assemble(str(tmp_path))
    for p in ["engine/VERSION", "engine/scripts/paths.py", "engine/scripts/build_site.py",
              "engine/viewer/index.html", "engine/.claude/skills/add-scorecard/SKILL.md",
              ".claude/skills/add-scorecard/SKILL.md", ".claude/skills/setup/SKILL.md",
              ".github/workflows/deploy.yml", "CLAUDE.md", "README.md", "inbox/README.txt"]:
        assert (tmp_path / p).exists(), p
    assert not (tmp_path / "Teams" / "example-team").exists()
    assert not list((tmp_path / "engine" / "viewer").rglob("*.test.js"))


def test_template_details(tmp_path):
    import make_template as MT
    MT.assemble(str(tmp_path))
    assert (tmp_path / "engine" / "VERSION").read_text(encoding="utf-8").strip() == \
        open(os.path.join(REPO, "VERSION"), encoding="utf-8").read().strip()
    assert not list(tmp_path.rglob("__pycache__"))
    assert not (tmp_path / "engine" / "viewer" / "tests").exists()
    assert (tmp_path / "engine" / "scripts" / "templates" / "game-template.json").exists()
    gi = [ln.strip() for ln in (tmp_path / ".gitignore").read_text(encoding="utf-8").splitlines()
          if ln.strip() and not ln.lstrip().startswith("#")]
    assert ".cf-token" in gi and not {"site/", "/site/", "engine/", "/engine/"} & set(gi)
    wrapper = (tmp_path / ".claude" / "skills" / "ai-coach" / "SKILL.md").read_text(encoding="utf-8")
    assert "engine/.claude/skills/ai-coach/SKILL.md" in wrapper and "name: ai-coach" in wrapper
    deploy = (tmp_path / ".github" / "workflows" / "deploy.yml").read_text(encoding="utf-8")
    assert "__PROJECT_NAME__" in deploy and "working-directory: site" in deploy


def test_template_refuses_leaks(tmp_path, run_script):
    lst = tmp_path / "list.txt"
    lst.write_text("# forbidden\nExample Arena\n", encoding="utf-8")   # appears in the engine docs
    r = run_script("make_template.py", "--out", tmp_path / "t", env={"LEAK_LIST": str(lst)})
    assert r.returncode == 1 and "!! leak:" in r.stdout


def test_vendored_engine_runs_in_a_team_repo(tmp_path):
    """The assembled template is a working team repo: the engine under engine/ finds
    the repo's Teams/, builds a game, validates it and builds the site."""
    import make_template as MT
    repo = tmp_path / "team-repo"
    MT.assemble(str(repo))
    env = {k: v for k, v in os.environ.items() if k not in ("TEAM", "TEAMS_DIR")}
    env["PYTHONIOENCODING"] = "utf-8"
    py = lambda *a: subprocess.run([sys.executable, *map(str, a)], cwd=repo, env=env,
                                   capture_output=True, text=True, encoding="utf-8")
    r = py("engine/scripts/new_team.py", "Our Team", "--arena", "Example Arena", "--season-start", "2026-09-01")
    assert r.returncode == 0, r.stderr
    data = repo / "Teams" / "Our-Team" / "2026-09-01" / "data"
    assert data.is_dir() and not (repo / "engine" / "Teams").exists()
    shutil.copy(repo / "engine" / "scripts" / "templates" / "game-template.json", data / "2026-10-07.json")
    assert py("engine/scripts/build_scorecards.py").returncode == 0
    v = py("engine/scripts/validate_ballbyball.py")
    assert "ALL RECONCILE" in v.stdout, v.stdout[-1500:] + v.stderr
    b = py("engine/scripts/build_site.py")
    assert b.returncode == 0, b.stderr
    idx = json.loads((repo / "site" / "data" / "index.json").read_text(encoding="utf-8"))
    assert [t["slug"] for t in idx] == ["our-team"]
    assert (repo / "site" / "functions" / "_middleware.js").exists()


def test_update_engine_dry_run(run_script):
    r = run_script("update_engine.py", "--dry-run", "--tag", "v1.2.3")
    assert r.returncode == 0
    assert "https://github.com/madeup-studio/indoor-cricket-stats/archive/refs/tags/v1.2.3.zip" in r.stdout
