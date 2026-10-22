"""Same cases as viewer/tests/sanitize.test.js: one allowlist for the app and the PDF."""
import pytest

CASES = [
    ("<p>Lost <b>51–80</b>, <i>again</i>.</p><p>Next: <strong>run</strong></p>",
     "<p>Lost <b>51–80</b>, <i>again</i>.</p><p>Next: <strong>run</strong></p>"),
    ("a<br>b<ul><li>x</li></ul>", "a<br>b<ul><li>x</li></ul>"),
    ('<p onclick="x()">hi</p>', "<p>hi</p>"),
    ('<img src=x onerror="alert(1)">ok', "ok"),
    ("<script>alert(1)</script>", "alert(1)"),
    ("<scr<script>ipt>alert(1)</script>", "ipt&gt;alert(1)"),
    ('<a href="javascript:alert(1)">x</a>', "x"),
    ("<!-- c --> 1 < 2 > 0", "&lt;!-- c --&gt; 1 &lt; 2 &gt; 0"),
    ('<svg><g onload="x"></g></svg>', ""),
    ('<iframe src="file:///etc/passwd"></iframe>', ""),
    ("Q&A &amp; R&#38;D &mdash;", "Q&amp;A &amp; R&#38;D &mdash;"),
    (None, ""),
]


@pytest.mark.parametrize("html,expected", CASES)
def test_safe_html(html, expected):
    import safe_html
    assert safe_html.safe_html(html) == expected


def test_pdf_letter_is_sanitised(tmp_team, run_script):
    import yaml
    (tmp_team / "example-team" / "coach_notes.yaml").write_text(yaml.safe_dump({"letters": [{
        "game": "2026-10-07", "fp": "1g51f80a-2026-10-07",
        "sections": [{"title": "The game", "html": '<p>ok</p><iframe src="file:///etc/passwd"></iframe><img src=x onerror="alert(1)">'}],
        "players": [{"name": "Our P2", "note": '<b>+5</b><script>alert(2)</script>'}]}]}), encoding="utf-8")
    r = run_script("generate_pdf_report.py", env={"PDF_BROWSER": "none", "TEAMS_DIR": str(tmp_team)})
    assert r.returncode == 0, r.stderr
    html = (tmp_team / "example-team" / ".build" / "season-spring-2026.html").read_text(encoding="utf-8")
    assert "<p>ok</p>" in html and "<b>+5</b>" in html
    assert "<iframe" not in html and "onerror" not in html and "alert(2)</script>" not in html
