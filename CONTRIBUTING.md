# Contributing

Thanks for looking. A few things first:

- **No support is promised.** Issues and pull requests are welcome, but may not get an
  answer, and the project's direction stays with its maintainer.
- **No real team data, ever.** Not in code, tests, docs, examples, screenshots or git
  history. The only team allowed under `Teams/` is the made-up `example-team`
  (`Our Team` vs `Opponents`, players `Our P1…P8` / `Opp P1…P8`). CI fails otherwise.

## Working on it

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
node --test "viewer/**/*.test.js"        # Node 22
python scripts/leak_check.py             # structure guard (+ identifier scan with LEAK_LIST)
python scripts/make_template.py          # builds dist/team-template
```

- Read `docs/superpowers/specs/` and `docs/architecture.md` before changing behaviour.
- Every game file must reconcile (`python scripts/validate_ballbyball.py` →
  `ALL RECONCILE`). Never bend a total to fit.
- Scoring constants come from `team.yaml` → `rules` (presets in `scripts/rules.py`;
  new arena presets welcome).
- Scripts must run on Windows and Linux (`os.path`, `encoding="utf-8"`).
- The viewer is plain HTML/CSS/JS: no build step, no external requests, design tokens
  from `viewer/tokens.css`.
- Write the failing test first.

## Releases (maintainer)

1. Update `VERSION` and `CHANGELOG.md`.
2. `pytest -q`, `node --test "viewer/**/*.test.js"`, and the leak check with the private
   identifier list: `LEAK_LIST=<private list> python scripts/leak_check.py` → clean.
3. Tag `vX.Y.Z` and publish a GitHub release; team repos pick it up with
   `python engine/scripts/update_engine.py`.
4. Rebuild the template repo from `python scripts/make_template.py`.

Repository topics: `indoor-cricket`, `action-cricket`, `cricket-stats`, `spawtz`,
`claude-code`.
