import os, shutil, subprocess

import pytest

from conftest import REPO


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True,
                          text=True, encoding="utf-8").stdout.strip()


@pytest.fixture
def team_repo(tmp_path, monkeypatch):
    """A git repo holding a copy of the example team as Teams/our-team."""
    repo = tmp_path / "team-repo"
    shutil.copytree(os.path.join(REPO, "Teams", "example-team"), repo / "Teams" / "our-team",
                    ignore=shutil.ignore_patterns(".build", "*.pdf"))
    git(repo.parent, "init", "-q", "-b", "main", str(repo))
    git(repo, "config", "user.email", "admin@example.com")
    git(repo, "config", "user.name", "Team Admin")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "start")
    import paths
    monkeypatch.setattr(paths, "TEAMS_DIR", str(repo / "Teams"))
    return repo


def test_publish_commits_site_once(team_repo):
    import publish
    r = publish.publish("Game x", push=False)
    assert r["committed"] is True and r["pushed"] is False and r["sha"]
    assert git(team_repo, "log", "-1", "--format=%s") == "Game x"
    assert "site/data/our-team.json" in git(team_repo, "ls-files", "site")
    again = publish.publish("Game x", push=False)
    assert again["committed"] is False


def test_publish_refuses_engine_repo(monkeypatch):
    import paths, publish
    monkeypatch.setattr(paths, "TEAMS_DIR", os.path.join(REPO, "Teams"))
    before = os.path.exists(os.path.join(REPO, "site"))
    with pytest.raises(SystemExit):
        publish.publish("nope", push=False)
    assert os.path.exists(os.path.join(REPO, "site")) == before      # nothing built


def test_publish_pushes_session_branch_to_main(team_repo, tmp_path):
    import publish
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "-q", "--bare", "-b", "main", str(remote))
    git(team_repo, "remote", "add", "origin", str(remote))
    git(team_repo, "push", "-q", "origin", "main")
    git(team_repo, "checkout", "-q", "-b", "claude/new-scorecard")      # like a cloud session
    r = publish.publish("Game y", push=True)
    assert r["committed"] and r["pushed"]
    assert git(remote, "log", "-1", "--format=%s", "main") == "Game y"


def test_publish_without_remote_does_not_push(team_repo):
    import publish
    r = publish.publish("Game z", push=True)
    assert r["committed"] is True and r["pushed"] is False and r["note"] == "no remote"
