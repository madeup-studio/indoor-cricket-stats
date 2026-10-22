import json, os, re, shutil

import pytest

from conftest import REPO

BASE = "https://api.cloudflare.com/client/v4"


class FakeHttp:
    """Records calls; answers from a {(method, path): (status, json)} table."""
    def __init__(self, answers):
        self.answers, self.calls = answers, []

    def __call__(self, method, url, headers, data):
        path = url[len(BASE):]
        self.calls.append((method, path, headers, json.loads(data) if data else None))
        return self.answers[(method, path)]


@pytest.fixture(autouse=True)
def token(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "tok-123")


def ok(result):
    return 200, {"success": True, "errors": [], "result": result}


def test_verify_token():
    import setup as S
    h = FakeHttp({("GET", "/user/tokens/verify"): ok({"status": "active", "id": "x"})})
    assert S.verify_token(http=h)["status"] == "active"
    assert h.calls[0][2]["Authorization"] == "Bearer tok-123"
    bad = FakeHttp({("GET", "/user/tokens/verify"): ok({"status": "disabled"})})
    with pytest.raises(S.SetupError, match="token invalid"):
        S.verify_token(http=bad)


def test_account_id():
    import setup as S
    h = FakeHttp({("GET", "/accounts"): ok([{"id": "acc1", "name": "A"}, {"id": "acc2"}])})
    assert S.account_id(http=h) == "acc1"
    with pytest.raises(S.SetupError):
        S.account_id(http=FakeHttp({("GET", "/accounts"): ok([])}))


def test_project_exists():
    import setup as S
    path = "/accounts/acc1/pages/projects/our-team"
    assert S.project_exists("acc1", "our-team", http=FakeHttp({("GET", path): ok({"name": "our-team"})}))
    missing = FakeHttp({("GET", path): (404, {"success": False, "errors": [{"code": 8000007, "message": "Project not found"}]})})
    assert S.project_exists("acc1", "our-team", http=missing) is False


def test_create_project():
    import setup as S
    h = FakeHttp({("POST", "/accounts/acc1/pages/projects"): ok({"name": "our-team", "subdomain": "our-team-3x9.pages.dev"})})
    assert S.create_project("acc1", "our-team", http=h) == "https://our-team-3x9.pages.dev"
    assert h.calls[0][3] == {"name": "our-team", "production_branch": "main"}


def test_set_env_secrets_are_secret():
    import setup as S
    path = "/accounts/acc1/pages/projects/our-team"
    h = FakeHttp({("PATCH", path): ok({})})
    S.set_env("acc1", "our-team", {"GATE": "pin", "TEAM_PIN": "12345678", "PIN_SECRET": "s"}, http=h)
    method, p, _, body = h.calls[0]
    env = body["deployment_configs"]["production"]["env_vars"]
    assert env["GATE"] == {"type": "plain_text", "value": "pin"}
    assert env["TEAM_PIN"] == {"type": "secret_text", "value": "12345678"}
    assert env["PIN_SECRET"]["type"] == "secret_text"


def test_api_errors_are_readable():
    import setup as S
    h = FakeHttp({("GET", "/accounts"): (403, {"success": False, "errors": [{"code": 9109, "message": "Unauthorized to access requested resource"}]})})
    with pytest.raises(S.SetupError, match="Unauthorized"):
        S.account_id(http=h)


def test_random_pin_and_secret():
    import setup as S
    pins = {S.random_pin() for _ in range(50)}
    assert all(re.fullmatch(r"\d{8}", p) for p in pins) and len(pins) > 40
    assert re.fullmatch(r"[0-9a-f]{32}", S.random_secret())


def test_write_workflow(tmp_path):
    import setup as S
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    shutil.copy(os.path.join(REPO, "template", ".github", "workflows", "deploy.yml"), wf / "deploy.yml")
    S.write_workflow("our-team", str(tmp_path))
    text = (wf / "deploy.yml").read_text(encoding="utf-8")
    assert "__PROJECT_NAME__" not in text and "--project-name=our-team" in text
    S.write_workflow("renamed", str(tmp_path))                     # idempotent: can change it later
    assert "--project-name=renamed" in (wf / "deploy.yml").read_text(encoding="utf-8")
    assert S.workflow_project(str(tmp_path)) == "renamed"


def test_token_file_and_forget(tmp_path, monkeypatch):
    import setup as S
    monkeypatch.delenv("CLOUDFLARE_API_TOKEN")
    with pytest.raises(S.SetupError, match="token"):
        S.get_token(str(tmp_path))
    (tmp_path / ".cf-token").write_text("  tok-file\n", encoding="utf-8")
    assert S.get_token(str(tmp_path)) == "tok-file"
    S.forget_token(str(tmp_path))
    assert not (tmp_path / ".cf-token").exists()


def test_gate_settings_for_each_choice():
    import setup as S
    pin = S.gate_env("pin", pin="24681357")
    assert pin["GATE"] == "pin" and pin["TEAM_PIN"] == "24681357" and len(pin["PIN_SECRET"]) == 32
    assert S.gate_env("none") == {"GATE": "none"} and S.gate_env("email") == {"GATE": "email"}
    with pytest.raises(S.SetupError):
        S.gate_env("pin", pin="123")          # codes are 6+ characters
    assert re.fullmatch(r"\d{8}", S.gate_env("pin")["TEAM_PIN"])


def test_blocked_network_gets_a_plain_answer(monkeypatch):
    import urllib.error, urllib.request
    import setup as S
    def blocked(*a, **k):
        raise urllib.error.URLError("Tunnel connection failed: 403 Forbidden")
    monkeypatch.setattr(urllib.request, "urlopen", blocked)
    with pytest.raises(S.SetupError, match="can't reach api.cloudflare.com"):
        S.account_id()


def test_gate_change_marks_site_for_redeploy(tmp_path):
    import setup as S
    site = tmp_path / "site"
    S.mark_redeploy(str(site))
    first = (site / ".redeploy").read_text(encoding="utf-8")
    assert first.strip()
    import time; time.sleep(1.1)
    S.mark_redeploy(str(site))
    assert (site / ".redeploy").read_text(encoding="utf-8") != first   # a new commit, a new deploy
