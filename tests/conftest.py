"""Shared test setup: point every script at the example team and make scripts/
importable. The env var must be set before any scripts module is imported."""
import os, subprocess, sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO, "scripts")

os.environ["TEAM"] = "example-team"
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)


def _run_script(name, *args, env=None):
    """Run `python scripts/<name> args...` from the repo root with TEAM=example-team
    (plus any `env` overrides); returns the CompletedProcess with text output."""
    full_env = dict(os.environ, TEAM="example-team", PYTHONIOENCODING="utf-8")
    full_env.update(env or {})
    return subprocess.run([sys.executable, os.path.join(SCRIPTS, name), *map(str, args)],
                          cwd=REPO, env=full_env, capture_output=True, text=True,
                          encoding="utf-8")


@pytest.fixture
def run_script():
    return _run_script
