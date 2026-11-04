import os
from conftest import REPO
def _read(*p): return open(os.path.join(REPO, *p), encoding="utf-8").read()
def test_skills_and_docs_carry_the_new_phrases():
    setup = _read(".claude", "skills", "setup", "SKILL.md")
    assert "Do you want the AI coach" in setup and "--no-coach" in setup
    add = _read(".claude", "skills", "add-scorecard", "SKILL.md")
    for s in ("## Other requests", "meta.stage", "season.yaml", "medal: silver", "Add Sam as an admin",
              "Settings → Collaborators", "show:", "re-check the existing game", "Never write a second file"):
        assert s in add, s
    coach = _read(".claude", "skills", "ai-coach", "SKILL.md")
    assert "`persona`" in coach and "tone's rules still win" in coach
    readme = _read("template", "README.md")
    for s in ("We finished second", "Hide best partnership", "Mark the game on", "as an admin", "Give the coach a personality"):
        assert s in readme, s
    assert "season.yaml" in _read("template", "CLAUDE.md") and "season.yaml" in _read("docs", "architecture.md")
    assert "Things you can tell Claude" in _read("docs", "SETUP.md")
    assert "Unreleased" in _read("CHANGELOG.md")
