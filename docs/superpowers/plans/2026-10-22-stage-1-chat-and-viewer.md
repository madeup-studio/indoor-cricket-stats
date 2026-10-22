# Stage 1 — Chat flow + phone-first viewer: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the owner's private scorecard pipeline into the public `indoor-cricket-stats` engine with configurable rules, per-game coach letters, a phone-first static viewer behind a team-PIN gate on Cloudflare Pages, a team template, and a `/setup` wizard — so a team admin can add a scorecard from a phone via a Claude Code cloud session and the team sees the result from a link minutes later.

**Architecture:** Python engine (unchanged where possible) reads `Teams/<team>/<season>/data/*.json` (source of truth) → `report_data.build()` per season + all-time → `build_site.py` writes `site/` (plain HTML/JS viewer + one JSON per team + Pages Function PIN gate). A team repo (from `template/`) vendors the engine under `engine/`, commits `site/`, and a 10-line GitHub Action deploys `site/` to Cloudflare Pages on push. Claude Code skills drive transcription, the coach letter, publishing and setup. No database, no server, no accounts.

**Tech Stack:** Python 3.10+ (pyyaml, pillow; pytest for tests), plain HTML/CSS/JS (no build step, no CDN), Cloudflare Pages + Pages Functions (`_middleware.js`), `cloudflare/wrangler-action` in GitHub Actions, Node 18+ only for JS unit tests and wrangler.

**Spec:** `docs/superpowers/specs/2026-10-22-action-cricket-app-design.md` (read it first; this plan argues from it). Stage 2 (unattended job, upload/admin pages) is NOT in this plan.

## Global Constraints

- **Public repo, private data:** nothing but `Teams/example-team/` may exist under `Teams/`; no real team, player, arena-specific or letter content anywhere, including tests and docs. `scripts/leak_check.py` must pass before every commit that will be pushed.
- Python 3.10+; only `pyyaml` and `pillow` at runtime; `pytest` for tests. Scripts run on Windows and Linux (use `os.path`, `encoding="utf-8"`, no shell-isms).
- Viewer: plain HTML/CSS/JS, **no build tooling, no external requests** (no CDN, no fonts); design tokens from `viewer/tokens.css` (copied from the studio); body text 18px; 16px side gutter; no horizontal page scroll at 360px width; dark mode via `prefers-color-scheme`.
- Rules defaults (preset `indoor-sa`): `wicket_runs: -5`, `extra_runs: 2`, `balls_per_over: 6`, `extra_ball_last_over: true`, `skins: 4`, `overs_per_pair: 4`, `players_per_side: 8`. With defaults, every number the engine produces must equal today's behaviour.
- Coach settings default: `coach: {enabled: true, tone: banter, language: en}`. Tones: `banter | encouraging | serious`.
- Gate choices: `pin` (default) | `email` | `none`. PIN cookie lifetime 180 days. The gate fails **closed**: missing `TEAM_PIN`/`PIN_SECRET` with `GATE=pin` denies.
- Terminology in all copy: **team**, **arena**, **league**; never "club".
- Dismissal letters `R C B S L H M`, extras `w nb`, every cell is one delivery; a skin holds `overs_per_pair × balls_per_over` balls, +1 if `extra_ball_last_over`.
- Engine version string lives in `VERSION` (semver); team repos pin it in `engine/VERSION`.
- Commit after every task with the message given; do not push (the owner pushes).

## Review Focus

Inputs the spec implies but no feature test covers by default; each has a pinned test in the owning task:

1. **Two games on the same day** (a double-header): game keys, letters and the game page must stay distinct → Task 4 `test_game_keys_double_header`, Task 5 `test_games_payload_double_header`.
2. **A player with no balls faced or no overs bowled in a scope** (e.g. only ever a substitute fielder): rankings and player pages must show them without dividing by zero or `NaN` → Task 7c `test_player_page_no_balls` (Playwright step) and Task 5 `jsonable` never emits `NaN`/`Infinity` (`test_jsonable_no_nan`).
3. **An older `team.yaml` with no `rules`/`coach`/`gate` keys** must behave exactly as today → Task 3 `test_rules_defaults_when_absent`, Task 4 `test_coach_settings_default`.
4. **A season with no verified ball-by-ball** (summaries only): records and partnerships are empty, pages render an empty state, nothing crashes → Task 5 `test_build_site_summaries_only`.
5. **Gate env misconfiguration:** `GATE=pin` with no `TEAM_PIN` or no `PIN_SECRET` → 503 "gate not configured", never pass-through → Task 8 `gate fails closed` test.

---

## File structure (what gets created / where)

```
indoor-cricket-stats/                     public engine repo (this repo)
  VERSION                                  "1.0.0"
  LICENSE                                  MIT
  requirements.txt  requirements-dev.txt   pyyaml, pillow | pytest
  scripts/
    paths.py          MOD  find_root() walks up to the dir holding Teams/; RULES, COACH, GATE
    rules.py          NEW  presets, load_rules(), game_rules(), skin_ball_counts()
    coach.py          NEW  per-game letters: keys, fingerprints, status, legacy conversion
    build_site.py     NEW  site/ builder: viewer copy + data/<slug>.json + records
    publish.py        NEW  build site, commit, push (if remote)
    setup.py          NEW  Cloudflare Pages provisioning (urllib only)
    leak_check.py     NEW  forbidden-identifier scan + Teams/ structure guard
    make_template.py  NEW  assemble dist/team-template/ from template/ + engine files
    update_engine.py  NEW  (runs inside a team repo) replace engine/ with a tagged release
    validate_ballbyball.py MOD rules-driven [B] and [E]
    build_scorecards.py    MOD rules-driven footnote
    generate_pdf_report.py MOD letter via coach.latest_letter(); warnings list game keys
    new_team.py       MOD  writes rules/coach/gate/admins/league/publish_unconfirmed/pdf
    stats_core.py, report_data.py, roster.py, crop_scorecard.py, generate_stats.py  (copied; report_data unchanged)
    TRANSCRIBE.md     MOD  rules wording, neutral examples, meta.rules snapshot
    templates/game-template.json MOD arena "Example Arena", meta.rules snapshot
  viewer/
    index.html app.js router.js app.css tokens.css manifest.webmanifest icons/  sw.js
    functions/_middleware.js   PIN gate
    tests/router.test.js  functions/_middleware.test.js   (node --test)
  Teams/example-team/  team.yaml players.yaml coach_notes.yaml seasons.md photos/README.txt
                       2026-09-01/{data/2026-10-07.json, scorecards/, stats/, context/README.md}
  .claude/skills/add-scorecard/SKILL.md  MOD   ai-coach/SKILL.md  MOD   setup/SKILL.md NEW
  template/            the team repo skeleton (see Task 9)
  tests/               pytest (conftest sets TEAM=example-team)
  docs/  README.md CONTRIBUTING.md docs/SETUP.md docs/COSTS.md docs/architecture.md
  .github/workflows/ci.yml
```

---

### Task 1: Repo skeleton, engine copy, example team, first test

**Files:**
- Create: `VERSION`, `LICENSE`, `requirements.txt`, `requirements-dev.txt`, `tests/conftest.py`, `tests/test_pipeline_smoke.py`, `.github/workflows/ci.yml`, `Teams/example-team/**`
- Copy from the owner's private hub (its engine folder; path not recorded here): `scripts/*.py` (all except `make_kit.py`), `scripts/TRANSCRIBE.md`, `scripts/templates/game-template.json`, `.claude/skills/add-scorecard/SKILL.md`, `.claude/skills/ai-coach/SKILL.md`
- Modify: `scripts/templates/game-template.json` (`meta.arena` → `"Example Arena"`, `meta.source_image` → `"scorecards/example.jpeg"`), `scripts/TRANSCRIBE.md` (replace the real arena name and the "precedent: 2026-05-20 …" clause with neutral wording)

**Interfaces:**
- Produces: `Teams/example-team/` — `team.yaml` with `name: "Our Team"`, `badge: "OURS"`, `arena: "Example Arena"`, `league: "Mens E"`, `colours: {brand: "#4f46e5", gold: "#f5b301"}`; season folder `2026-09-01/` holding the example game `data/2026-10-07.json` (the template file, unchanged apart from the arena); `players.yaml` produced by `roster.py --refresh` then every `name:` set to the printed spelling; `coach_notes.yaml` containing `letters: []`.
- Produces: `tests/conftest.py` setting `os.environ["TEAM"] = "example-team"` before any `scripts` import and adding `scripts/` to `sys.path`.
- Produces: helper `run_script(name, *args, env=None) -> subprocess.CompletedProcess` in `tests/conftest.py` (runs `python scripts/<name>` from the repo root with `TEAM=example-team`).

- [ ] **Step 1: Create `VERSION` (`1.0.0`), `LICENSE` (MIT, "MaDe-uP Studios"), `requirements.txt` (`pyyaml`, `pillow`), `requirements-dev.txt` (`pytest`)**

- [ ] **Step 2: Copy the engine files listed above; apply the two sanitising edits; `grep -ri` the copied files for the owner's arena name and any name that is not `Our Team`/`Opponents`/`Our P*`/`Opp P*` — must find nothing**

- [ ] **Step 3: Create the example team folder** by running `python scripts/new_team.py "Our Team" --arena "Example Arena" --badge OURS --folder example-team --season-start 2026-09-01`, copying `scripts/templates/game-template.json` to `Teams/example-team/2026-09-01/data/2026-10-07.json`, then `TEAM=example-team python scripts/build_scorecards.py` and `python scripts/roster.py --refresh`. Set `colours` and `league` in `team.yaml` as in Interfaces. Set `coach_notes.yaml` to `letters: []`.

- [ ] **Step 4: Write the failing smoke test** `tests/test_pipeline_smoke.py`:

```python
def test_example_game_reconciles(run_script):
    r = run_script("validate_ballbyball.py")
    assert r.returncode == 0 and "ALL RECONCILE" in r.stdout

def test_example_team_stats():
    import report_data as RD
    seasons, allm, R = RD.load_all()
    d = RD.build(allm, R)
    t = d["team"]
    assert (t["played"], t["won"], t["lost"]) == (1, 0, 1)
    assert (t["runs_for"], t["runs_against"]) == (51, 80)
    assert (t["skins_for"], t["skins_against"]) == (1, 3)
```

- [ ] **Step 5: Run `pytest -q`** — expected: both pass (the engine is copied working). If `test_example_team_stats` fails on skins, check `team_skins`/`opponent_skins` in the example file ([28,6,6,11] vs [15,21,15,29] → 1–3).

- [ ] **Step 6: Create `.github/workflows/ci.yml`**: on push/PR, Python 3.12, `pip install -r requirements.txt -r requirements-dev.txt`, `pytest -q`, `python scripts/leak_check.py` (added in Task 2 — leave the step in; it will fail until then only if run, which it won't be before push).

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "chore: engine skeleton, example team, smoke tests"
```

---

### Task 2: Leak check

**Files:**
- Create: `scripts/leak_check.py`, `tests/test_leak_check.py`

**Interfaces:**
- Produces: `def scan(root: str, identifiers: list[str], files: list[str] | None = None) -> list[tuple[str, str]]` — `(relative_path, identifier)` for every whole-word, case-sensitive hit in text files (skips binaries and `.git/`); `files` defaults to `git ls-files` output when `root` is a git repo, else a walk.
- Produces: `def structure_errors(root: str) -> list[str]` — non-empty when `Teams/` holds anything other than `example-team`, or when `site/`, `dist/` or `engine/` are tracked.
- CLI: `python scripts/leak_check.py [--root PATH] [--list FILE]`; the identifier list comes from `--list` or env `LEAK_LIST` (one identifier per line, `#` comments allowed); without a list only `structure_errors` run. Exit 1 and print `!! leak: <path>: <identifier>` lines on any hit.

- [ ] **Step 1: Write failing tests** `tests/test_leak_check.py`:

```python
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
```

- [ ] **Step 2: Run `pytest tests/test_leak_check.py -q`** — expected: FAIL (`No module named leak_check`).

- [ ] **Step 3: Implement `scripts/leak_check.py`** with the three interfaces above. Word boundary: `re.compile(r"(?<!\w)%s(?!\w)" % re.escape(ident))`. Text detection: skip files whose first 1024 bytes contain `\0` or that fail UTF-8 decoding.

- [ ] **Step 4: Run `pytest tests/test_leak_check.py -q`** — expected: PASS. Then `python scripts/leak_check.py` on this repo — expected: exit 0.

- [ ] **Step 5: Commit** — `git commit -am "feat: leak check (identifier scan + Teams/ guard)"` (add the new files first).

---

### Task 3: Rules module and rules-driven validator

**Files:**
- Create: `scripts/rules.py`, `tests/test_rules.py`, `tests/test_validate_rules.py`
- Modify: `scripts/paths.py` (add `RULES`, `COACH`, `GATE`, `find_root()`), `scripts/validate_ballbyball.py` (`[B]`, `[E]`), `scripts/build_scorecards.py` (footnote line 132), `scripts/new_team.py` (team.yaml content), `scripts/TRANSCRIBE.md` (rules wording + `meta.rules`), `scripts/templates/game-template.json` (add `meta.rules`)

**Interfaces:**
- Produces (`rules.py`):
  - `PRESETS: dict[str, dict]` with `"indoor-sa"` = the Global Constraints defaults.
  - `RULE_KEYS = ("wicket_runs", "extra_runs", "balls_per_over", "extra_ball_last_over", "skins", "overs_per_pair", "players_per_side")`
  - `def load_rules(team_cfg: dict | None) -> dict` — preset named by `team_cfg["rules"]["preset"]` (default `indoor-sa`) merged with any overriding keys; unknown preset or unknown key → `ValueError`.
  - `def game_rules(game: dict, team_rules: dict) -> dict` — `game["meta"].get("rules", {})` merged over `team_rules` (the snapshot wins).
  - `def skin_ball_counts(rules: dict) -> set[int]` — `{o*b, o*b+1}` if `extra_ball_last_over` else `{o*b}`.
  - `def max_cells_last_over(rules: dict) -> int` — `balls_per_over + 1` if extra ball allowed else `balls_per_over`.
- Produces (`paths.py`): `RULES = rules.load_rules(TEAM_CFG)`; `COACH = {"enabled": True, "tone": "banter", "language": "en", **(TEAM_CFG.get("coach") or {})}`; `GATE = TEAM_CFG.get("gate") or "pin"`; `def find_root(start: str) -> str` returning the nearest ancestor of `start` (inclusive, max 4 levels) that contains a `Teams/` directory, else the engine's own root. `ROOT = find_root(script_dir)`.
- Consumed by: validator, build_scorecards, build_site (Task 5), new_team.

- [ ] **Step 1: Write failing tests** `tests/test_rules.py`:

```python
import rules
def test_preset_defaults():
    r = rules.load_rules({})
    assert r == dict(wicket_runs=-5, extra_runs=2, balls_per_over=6, extra_ball_last_over=True,
                     skins=4, overs_per_pair=4, players_per_side=8)
def test_rules_defaults_when_absent():
    assert rules.load_rules(None) == rules.load_rules({"name": "X"})
def test_override_and_snapshot():
    r = rules.load_rules({"rules": {"preset": "indoor-sa", "wicket_runs": -3}})
    assert r["wicket_runs"] == -3 and r["extra_runs"] == 2
    g = {"meta": {"rules": {"wicket_runs": -5}}}
    assert rules.game_rules(g, r)["wicket_runs"] == -5
def test_unknown_key_rejected():
    import pytest
    with pytest.raises(ValueError):
        rules.load_rules({"rules": {"wickets": -5}})
def test_skin_ball_counts():
    assert rules.skin_ball_counts(rules.load_rules({})) == {24, 25}
    assert rules.skin_ball_counts(rules.load_rules({"rules": {"extra_ball_last_over": False}})) == {24}
```

- [ ] **Step 2: Run `pytest tests/test_rules.py -q`** — expected: FAIL (no module).

- [ ] **Step 3: Implement `scripts/rules.py`** per Interfaces.

- [ ] **Step 4: Run `pytest tests/test_rules.py -q`** — expected: PASS.

- [ ] **Step 5: Write the failing validator test** `tests/test_validate_rules.py` — builds a temp team folder from the example game with `rules: {wicket_runs: -3}` in `team.yaml` and edits one over so it only reconciles at −3 (e.g. balls `[2, "C", 1]`… keep the over's `total` equal to `numeric − 3·wkts`; adjust the batter's summary `rs`, the bowler's `rc`, the skin total and the team total consistently — write a helper `retotal(game)` in the test that recomputes those from the overs using a given wicket value):

```python
def test_validator_uses_team_wicket_value(tmp_team, run_script):
    # tmp_team: fixture copying Teams/example-team to tmp and returning its Teams dir
    ...  # write team.yaml with rules.wicket_runs = -3; rewrite totals via retotal(game, -3)
    r = run_script("validate_ballbyball.py", env={"TEAM": "example-team", "TEAMS_DIR": str(tmp_team)})
    assert "ALL RECONCILE" in r.stdout
    r5 = run_script("validate_ballbyball.py", env={"TEAM": "example-team", "TEAMS_DIR": str(tmp_team), "WICKET_RUNS_OVERRIDE": "-5"})
    assert r5.returncode == 1
```

  (`TEAMS_DIR` env override in `paths.py` is part of this task: `TEAMS_DIR = os.environ.get("TEAMS_DIR") or os.path.join(ROOT, "Teams")`. `WICKET_RUNS_OVERRIDE` is a test-only hook read by the validator; document it in the validator docstring.)

- [ ] **Step 6: Run it** — expected: FAIL (validator still uses 5).

- [ ] **Step 7: Modify `validate_ballbyball.py`**: `R = rules.game_rules(g, paths.RULES)` per game; `[B]` uses `o["total"] - (runs + R["wicket_runs"] * wkts) < 0`; `[E]` uses `R["balls_per_over"]`, `rules.max_cells_last_over(R)` and `rules.skin_ball_counts(R)`; the `DISM` comment "each worth -5" becomes "each worth rules.wicket_runs". Modify `build_scorecards.py` footnote to print the game's wicket value. Modify `new_team.py` to write the `league`, `publish_unconfirmed`, `pdf`, `game_type`, `rules`, `coach`, `gate`, `admins` blocks exactly as the spec's `team.yaml` example. Add `meta.rules` (full indoor-sa block) to `game-template.json` and to the example game; TRANSCRIBE.md: "copy the team's `rules` into `meta.rules`" and replace literal −5/6-ball wording with "the team's `wicket_runs` / `balls_per_over` (defaults −5 / 6)".

- [ ] **Step 8: Run `pytest -q`** — expected: all PASS (smoke tests unchanged: defaults reproduce today's numbers).

- [ ] **Step 9: Commit** — `git add -A && git commit -m "feat: configurable scoring rules (presets, per-game snapshot)"`

---

### Task 4: Per-game coach letters

**Files:**
- Create: `scripts/coach.py`, `tests/test_coach.py`
- Modify: `scripts/generate_pdf_report.py` (lines ~20–27 COACH loading, `team_fp`, `page_coach_letter`, final warnings), `.claude/skills/ai-coach/SKILL.md`, `Teams/example-team/coach_notes.yaml` (one example letter, written by Claude in `banter` tone from the example game's numbers)

**Interfaces:**
- Produces (`coach.py`):
  - `def game_keys(matches: list[dict]) -> list[str]` — aligned with `matches`; key = `str(m["date"])`, suffixed `-<slug(opponent)>` for every match whose date occurs more than once in `matches`. `slug` = lowercase, non-alphanumerics → `-`, trimmed.
  - `def game_fp(matches_up_to: list[dict]) -> str` — `f"{n}g{runs_for}f{runs_against}a-{last_date}"` over the prefix (same formula as today's `team_fp`).
  - `def load_letters(team_dir: str) -> dict[str, dict]` — `{key: {"fp", "sections", "players"}}` from `coach_notes.yaml` → `letters: [...]`; a legacy file (season-name keys with `_letter`) is converted in memory via `convert_legacy(notes, seasons)`.
  - `def convert_legacy(notes: dict, seasons: list[tuple[str, str, list]]) -> list[dict]` — each season `_letter` becomes the letter of that season's last game (`game` = its key, `fp` = `game_fp(all matches up to it)`).
  - `def status(seasons: list[tuple[str, str, list]], letters: dict) -> list[dict]` — one row per game across all seasons in date order: `{"key", "season", "fp", "state": "ok" | "stale" | "missing"}` where `stale` = letter exists with another fp.
  - `def latest_letter(matches: list[dict], letters: dict) -> tuple[str | None, dict | None]` — newest match (by order) that has an `ok` letter.
  - CLI: `python scripts/coach.py --status` prints one line per non-ok game `KEY<TAB>FP<TAB>SEASON<TAB>STATE`; exit 0. `--convert-legacy` rewrites `coach_notes.yaml` into the `letters:` form (backup to `coach_notes.legacy.yaml`).
- Consumed by: `generate_pdf_report.py`, `build_site.py` (Task 5), the ai-coach skill.

- [ ] **Step 1: Write failing tests** `tests/test_coach.py`:

```python
import coach
def M(date, opp, tf=50, ta=60):
    return dict(date=date, opponent=opp, team_total=tf, opponent_total=ta, outcome="loss",
                team_skins_won=1, opponent_skins_won=3, team_summary=[], opponent_summary=[],
                team="Our Team", season="Spring")
def test_game_keys_double_header():
    ms = [M("2026-10-07", "A"), M("2026-10-14", "B"), M("2026-10-14", "C")]
    assert coach.game_keys(ms) == ["2026-10-07", "2026-10-14-b", "2026-10-14-c"]
def test_fp_prefix_stable():
    ms = [M("2026-10-07", "A"), M("2026-10-14", "B")]
    assert coach.game_fp(ms[:1]) == "1g50f60a-2026-10-07"
    assert coach.game_fp(ms[:1]) == coach.game_fp((ms + [M("2026-10-21", "D")])[:1])
def test_status_and_latest():
    ms = [M("2026-10-07", "A"), M("2026-10-14", "B")]
    letters = {"2026-10-07": {"fp": coach.game_fp(ms[:1]), "sections": [{"title": "t", "html": "<p>x</p>"}], "players": []},
               "2026-10-14": {"fp": "wrong", "sections": [], "players": []}}
    st = coach.status([("d", "Spring", ms)], letters)
    assert [s["state"] for s in st] == ["ok", "stale"]
    assert coach.latest_letter(ms, letters)[0] == "2026-10-07"
def test_convert_legacy():
    ms = [M("2026-10-07", "A"), M("2026-10-14", "B")]
    notes = {"Spring": {"_letter": {"fp": "old", "sections": [{"title": "t", "html": "x"}], "players": []}}}
    out = coach.convert_legacy(notes, [("d", "Spring", ms)])
    assert out[0]["game"] == "2026-10-14" and out[0]["fp"] == coach.game_fp(ms)
def test_coach_settings_default():
    import paths
    assert paths.COACH["enabled"] is True and paths.COACH["tone"] == "banter"
```

- [ ] **Step 2: Run `pytest tests/test_coach.py -q`** — expected: FAIL.

- [ ] **Step 3: Implement `scripts/coach.py`** per Interfaces. `status()` computes each game's fp from the all-time chronological prefix (seasons concatenated in order), not per season.

- [ ] **Step 4: Run `pytest tests/test_coach.py -q`** — expected: PASS.

- [ ] **Step 5: Modify `generate_pdf_report.py`**: replace `COACH_NOTES`/`team_fp` usage in `page_coach_letter` with `key, entry = coach.latest_letter(matches_of_scope, LETTERS)` where `LETTERS = coach.load_letters(paths.TEAM_DIR)`; fallback when `entry is None`; the end-of-run warning lists `coach.status(...)` rows that are not `ok` as `!! coach letter missing/stale: KEY FP`. All-time card unchanged (no letter).

- [ ] **Step 6: Rewrite `.claude/skills/ai-coach/SKILL.md`** for per-game letters: process = `python scripts/coach.py --status` → for each listed game in date order, dump stats as of that game (`RD.build(matches_up_to, R)`), read `context/`, write the letter under `letters:` with that key and fp, **never edit an existing letter**; voice section gains the three tones (read `coach.tone` from `team.yaml`; banter = current rules; encouraging = praise-led, light humour, concrete homework; serious = match-report, no jokes) and `coach.language`; page budget applies only when `pdf: true`; everything else (terminology, pronouns, numbers, no bookkeeping) stays. Keep the file under 150 lines.

- [ ] **Step 7: Write the example letter** for `Teams/example-team` game `2026-10-07` (banter tone, from the example numbers: 51–80, skins 1–3, Our P2 top contributor +5, Opp P7 player of the match) into `coach_notes.yaml`; run `python scripts/coach.py --status` — expected: no output (all ok). Run `python scripts/generate_pdf_report.py` — expected: no `!!` warnings (PDF may be skipped if no browser; HTML must exist).

- [ ] **Step 8: Run `pytest -q` and `python scripts/leak_check.py`** — expected: PASS / exit 0.

- [ ] **Step 9: Commit** — `git add -A && git commit -m "feat: coach letters per game (keys, fingerprints, status, legacy conversion)"`

---

### Task 5: Site builder (`build_site.py`)

**Files:**
- Create: `scripts/build_site.py`, `tests/test_build_site.py`
- Modify: `scripts/paths.py` (nothing new; uses `team_folders()`)

**Interfaces:**
- Produces:
  - `def jsonable(obj)` — recursively converts `Counter`/`defaultdict`/`dict` → dict with `str` keys, `tuple`/`set` → list, `float` NaN/inf → `None`; leaves str/int/bool/None.
  - `def slug(s: str) -> str` (same rule as `coach.slug`; import it from `coach`).
  - `def derive_records(d: dict, games: list[dict]) -> dict` — `{"team": {...}, "individual": {...}}` with exactly these keys: team: `high_total, low_total, biggest_win, heaviest_loss, best_skin, most_wkts_game, fewest_extras_game, longest_win_streak, longest_loss_streak`; individual: `best_contribution, most_runs_game, most_wkts_game, best_econ, best_partnership, hattricks, most_runouts_created`. Every record is `{"value", "name"?, "names"?, "opp", "date", "key"}` or `None`; streaks are `{"value": int, "from": key|None, "to": key|None}`.
  - `def team_payload(team_dir: str, R) -> dict` — `{"team": {slug, name, badge, arena, league, colours, coach: {enabled, tone}, rules, gate}, "seasons": [{key: folder, label, games: [keys], stats: jsonable(build), records}], "alltime": {stats, records}, "games": [{key, season, date, opp, outcome, total, against, skins, oskins, skin_scores, pom, pom_ours, top_c, letter: {sections, players} | None, summaries: {ours: [...], theirs: [...]}}], "players": {name: {slug, photo: "photos/<team-slug>/<file>" | None}}, "generated": ISO-8601}` — `games` are all-time, chronological; `letter` from `coach.load_letters` by key.
  - `def build(out_dir: str) -> list[str]` — for every folder in `paths.team_folders()`: writes `data/<team-slug>.json`, copies `photos/*` to `photos/<team-slug>/`; writes `data/index.json` = `[{slug, name, badge, colours}]`; copies `viewer/` (all files except `tests/` and `*.test.js`) into `out_dir`; returns the list of written files. Teams are built in-process: `team_payload` takes the team directory and never reads `paths.TEAM`/`paths.TEAM_DIR`.
  - `team_payload` loads its own inputs from `team_dir`: season folders matching `\d{4}-\d{2}-\d{2}` → `stats_core.load_matches(<season>/scorecards)`; roster via `roster.load(path)`; rules via `rules.load_rules(team.yaml)`; letters via `coach.load_letters(team_dir)`. `report_data.build(matches, R)` is already team-independent.
  - CLI: `python scripts/build_site.py [--out site]` (default `site/` under `paths.ROOT`).
- Modify `scripts/roster.py`: `def load(path: str | None = None)` — optional players.yaml path, default `paths.PLAYERS_FILE` (existing callers unchanged).
- Consumes: `report_data.build()`, `stats_core.load_matches()`, `coach.*`, `rules.*`, `paths.team_folders()`.

- [ ] **Step 1: Write failing tests** `tests/test_build_site.py`:

```python
import json, os
def test_jsonable_no_nan():
    from collections import Counter
    import build_site as B
    out = B.jsonable({"a": Counter({5: 2}), "b": (1, "x"), "c": float("nan"), "d": {("p", "q"): 1}})
    assert out == {"a": {"5": 2}, "b": [1, "x"], "c": None, "d": {"('p', 'q')": 1}}
def test_build_example_site(tmp_path):
    import build_site as B
    files = B.build(str(tmp_path))
    assert (tmp_path / "index.html").exists() and (tmp_path / "functions" / "_middleware.js").exists()
    idx = json.load(open(tmp_path / "data" / "index.json", encoding="utf-8"))
    assert idx == [{"slug": "our-team", "name": "Our Team", "badge": "OURS", "colours": {"brand": "#4f46e5", "gold": "#f5b301"}}]
    p = json.load(open(tmp_path / "data" / "our-team.json", encoding="utf-8"))
    assert p["seasons"][0]["label"] == "Spring 2026" and p["seasons"][0]["stats"]["team"]["played"] == 1
    assert p["games"][0]["key"] == "2026-10-07" and p["games"][0]["letter"]["sections"]
    assert p["alltime"]["records"]["team"]["longest_win_streak"]["value"] == 0
    assert p["alltime"]["records"]["individual"]["best_contribution"]["name"] == "Our P2"
def test_games_payload_double_header(tmp_team_two_games_same_day):
    # fixture: example team + a copy of the game dated the same day vs "Other Side"
    import build_site as B
    p = B.team_payload(tmp_team_two_games_same_day, None)
    assert sorted(g["key"] for g in p["games"]) == ["2026-10-07-opponents", "2026-10-07-other-side"]
def test_build_site_summaries_only(tmp_team_summaries_only):
    # fixture: example game with innings removed / ball_by_ball status != verified
    import build_site as B
    p = B.team_payload(tmp_team_summaries_only, None)
    assert p["alltime"]["records"]["individual"]["best_partnership"] is None
    assert p["seasons"][0]["stats"]["partnerships"] == []
```

  Fixtures `tmp_team_two_games_same_day` and `tmp_team_summaries_only` go in `tests/conftest.py`; both copy `Teams/example-team` into `tmp_path`, edit the JSON, run `build_scorecards.py` with `TEAMS_DIR` pointing at the copy, and return the team dir. `team_payload(team_dir, R)` must accept `R=None` and load the roster itself from that `team_dir`.

- [ ] **Step 2: Run `pytest tests/test_build_site.py -q`** — expected: FAIL.

- [ ] **Step 3: Implement `scripts/build_site.py`** per Interfaces. `summaries.ours/theirs` come from the game JSON's `summaries` (read the data file named in the card front matter `source`, or re-read `data/<key>.json` by date). Streak algorithm: longest run of consecutive `win` (resp. `loss`) outcomes in chronological `games`.

- [ ] **Step 4: Run `pytest tests/test_build_site.py -q`** — expected: PASS. (The viewer files may not exist yet — `build()` must copy whatever is in `viewer/`; create `viewer/index.html` and `viewer/functions/_middleware.js` as empty placeholders in this task so the test's existence assertions hold; Tasks 6–8 fill them.)

- [ ] **Step 5: Commit** — `git add -A && git commit -m "feat: build_site.py (team payloads, records, multi-team index)"`

---

### Task 6: Viewer shell — tokens, router, layout, home

**Files:**
- Create: `viewer/tokens.css`, `viewer/app.css`, `viewer/router.js`, `viewer/app.js`, `viewer/index.html`, `viewer/manifest.webmanifest`, `viewer/sw.js`, `viewer/icons/icon-192.png`, `viewer/icons/icon-512.png`, `viewer/icons/apple-touch-icon.png`, `viewer/tests/router.test.js`

**Interfaces:**
- Produces (`router.js`, ES module, pure): `export function matchRoute(hash) -> {team: string|null, name: string, params: object}`; grammar: `#/[t/<team>/]<name>[/<param>]` with names `home | coach | batting | bowling | allround | games | game | players | player | records`; empty/unknown → `home`.
- Produces (`app.js`, ES module): `state = {teams, team, data, scope}`; `loadIndex()`, `loadTeam(slug)` (fetch `data/<slug>.json`), `defaultScope(routeName, data)` → `"alltime"` for `records`, else the last season's `key`; `setScope(key)` stores to `sessionStorage["ac.scope"]`; `render()` dispatches to `screens[name](ctx)` where `ctx = {data, scope, params, navigate}`; a `screens` registry other files add to (`window.AC.screens`). Transition: outgoing view gets class `leave`, incoming `enter` (120ms).
- Produces (`app.css`): classes `.shell .topbar .badge .scope .nav .nav a[aria-current] .view .card .big .label .row .row .val .list .empty .pill`; CSS vars `--ac-font-body: 18px; --ac-font-big: 40px; --ac-font-label: 12px; --ac-gutter: 16px;` plus the team accent `--madeup-color-accent` overridden at runtime from `team.colours.brand`.
- Produces (`tokens.css`): the studio file verbatim plus a `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { …same values as [data-theme="dark"]… } }` block.
- Produces (`index.html`): `<title>Action Cricket</title>` (replaced at runtime by the team name), viewport with `viewport-fit=cover`, manifest link, `apple-touch-icon`, `theme-color`, the shell markup: `<header class="topbar">` (badge, team name, scope select), `<main class="view" id="view">`, `<nav class="nav">` with six links (`Coach, Batting, Bowling, All-round, Games, Players`) + `Records` reachable from Games/home (nav holds six; Records is a card on home and a link in the top bar).
- Home screen (`screens.home`): team card (season record `W-L-D`, avg for/against, last result with opponent and date), three tap-through cards (Latest coach letter → `coach`, Records → `records`, Last game → `game/<key>`), and a "finish setup" card when `data/index.json` is empty.

- [ ] **Step 1: Write the failing router test** `viewer/tests/router.test.js` (Node test runner):

```js
import test from "node:test"; import assert from "node:assert/strict";
import { matchRoute } from "../router.js";
test("routes", () => {
  assert.deepEqual(matchRoute(""), { team: null, name: "home", params: {} });
  assert.deepEqual(matchRoute("#/batting"), { team: null, name: "batting", params: {} });
  assert.deepEqual(matchRoute("#/player/our-p2"), { team: null, name: "player", params: { id: "our-p2" } });
  assert.deepEqual(matchRoute("#/t/our-team/game/2026-10-07-opponents"), { team: "our-team", name: "game", params: { id: "2026-10-07-opponents" } });
  assert.deepEqual(matchRoute("#/nonsense"), { team: null, name: "home", params: {} });
});
```

- [ ] **Step 2: Run `node --test viewer/tests/`** — expected: FAIL (module missing).

- [ ] **Step 3: Implement `viewer/router.js`**, then `tokens.css`, `app.css`, `index.html`, `app.js` (shell, loading, scope, home screen, transitions), `manifest.webmanifest` (`name` from team at runtime is not possible — use `"Action Cricket"`, `display: standalone`, `start_url: "./"`, icons), `sw.js` (network-first passthrough, registered from `app.js`; exists only so Android offers "Install"), icons (generate three PNGs with pillow in a one-off script: badge letters on the accent colour).

- [ ] **Step 4: Run `node --test viewer/tests/`** — expected: PASS.

- [ ] **Step 5: Verify on a phone-sized viewport**: `python scripts/build_site.py --out dist/site && python -m http.server 8765 -d dist/site` then with the Playwright tools: `browser_resize` 390×844, `browser_navigate` `http://localhost:8765/#/`, `browser_console_messages` → no errors; `browser_evaluate` `document.documentElement.scrollWidth <= window.innerWidth` → true; `browser_take_screenshot` → home shows the team card and bottom nav; repeat at 360×780. Also emulate dark (`browser_emulate_media` colorScheme dark) and screenshot.

- [ ] **Step 6: Commit** — `git add -A && git commit -m "feat: viewer shell (tokens, router, home, PWA manifest)"`

---

### Task 7a: Rankings screens — Batting, Bowling, All-round, glossary popover

**Files:**
- Create: `viewer/screens/rankings.js`, `viewer/help.js`
- Modify: `viewer/index.html` (script tags), `viewer/app.css` (ranking rows, help popover styles)

**Interfaces:**
- Produces (`help.js`): `export function helpIcon(key) -> HTMLElement` (`?` button; opens one popover at a time, Escape/click-outside closes, bottom-sheet under 500px per the studio standard) and `GLOSSARY` map with keys `rs rc wkts econ c avg12 sr skin big_hits ranked` and plain-English one-liners (wording from the spec's glossary; the wicket value text reads the team's `rules.wicket_runs`).
- Produces (`screens/rankings.js`): registers `screens.batting`, `screens.bowling`, `screens.allround`. Each shows the scope's list from `stats.batting|bowling|allround` in the engine's order; ranked rows numbered, sub-threshold rows under a divider "fewer than N games — not ranked" (N = `stats.min_rank_games`); each row: rank, name, headline number big (`avg12` 1dp / `econ` 2dp / `avgc` +1dp), two small supporting numbers (`rs · games` / `wkts · rc` / `c · games`); tapping a row navigates to `player/<slug>`. Top of each screen: the scope switcher is the top bar's; a `?` beside the title opens the glossary for the headline metric.

- [ ] **Step 1: Implement** the two files and styles per Interfaces. No framework; build DOM with small helper `h(tag, attrs, ...children)` in `app.js` (export it).

- [ ] **Step 2: Verify with Playwright** at 390×844: navigate `#/batting`, `#/bowling`, `#/allround` → each lists 8 players for the example team; `browser_find` the text "Our P2" and click → URL ends with `#/player/our-p2` (page may be a placeholder until 7c); open `?` → popover visible; press Escape → hidden. No console errors. Screenshot each.

- [ ] **Step 3: Commit** — `git add -A && git commit -m "feat: rankings screens + glossary popover"`

---

### Task 7b: Games list, game page, Coach letter screen

**Files:**
- Create: `viewer/screens/games.js`, `viewer/screens/coach.js`, `viewer/letter.css` (styles for letter sections and player notes)
- Modify: `viewer/index.html`, `viewer/app.css`

**Interfaces:**
- `screens.games`: chronological list for the scope (newest first): date, opponent, result pill (W/L/D with team colours), score `total–against`, skins `x–y`; tap → `game/<key>`.
- `screens.game`: header (date, opponent, result, score), skins row (four mini cards `ours vs theirs`, winner highlighted, level skins marked "shared"), "Player of the match" card, both summaries as compact tables (name, RS, Wkts, RC, C; ours first; tapping one of ours → player page), and the **coach letter for this game** (sections then "A word to each player who played" notes) or an empty-state card "No coach letter for this game". A "Latest letter" link when a newer letter exists.
- `screens.coach`: the latest letter for the scope (season → latest in that season; all-time → latest overall) rendered with the same component as the game page; if `team.coach.enabled` is false the nav item is hidden and the route redirects home.
- Shared: `export function renderLetter(letter, players) -> HTMLElement` in `screens/coach.js`; HTML in `sections[].html` is inserted as-is (it is authored by the skill from trusted data — note this in a comment).

- [ ] **Step 1: Implement** per Interfaces.

- [ ] **Step 2: Verify with Playwright** at 390×844: `#/games` shows one row "Opponents · 51–80 · L"; tap → `#/game/2026-10-07` shows four skin cards (28–15, 6–21, 6–15, 11–29), the letter's section titles and 8 player notes; `#/coach` shows the same letter; with `coach.enabled=false` in a temp build the Coach nav item is absent (build a second site from a tmp team copy). No console errors; no horizontal overflow (`scrollWidth` check) on the game page with the summary tables.

- [ ] **Step 3: Commit** — `git add -A && git commit -m "feat: games, game page with per-game coach letter, coach screen"`

---

### Task 7c: Players grid and player page

**Files:**
- Create: `viewer/screens/players.js`, `viewer/sparkline.js`
- Modify: `viewer/index.html`, `viewer/app.css`

**Interfaces:**
- `sparkline.js`: `export function sparkline(values: number[], opts={w:120,h:32}) -> SVGElement` (inline SVG polyline; zero line drawn when values cross 0; no external libs).
- `screens.players`: grid of player cards (photo or initials circle in the accent colour, name, all-rounder avg C for the scope, games). Tap → `player/<slug>`.
- `screens.player`: header (photo/initials, name, "also plays for …" if `people` links exist — show nothing in v1 when absent); **two stat blocks: "This season" (or the selected scope) and "All-time"** each with batting (rs, avg12, balls, outs, big hits 5s+7s, dismissal breakdown bar), bowling (wkts, econ, rc, best figures, wicket types), contribution (c, avgc, games); a game-by-game list for the scope from `stats.gamelog[name]` (date, opp, rs, wkts, rc, c) with a sparkline of `c`; the player's latest coach note (from the newest letter that mentions them) under the header. A player who has no balls faced shows "–" for `avg12`/`sr` and no dismissal bar; a player with no overs shows "–" for econ.

- [ ] **Step 1: Implement** per Interfaces.

- [ ] **Step 2: Verify with Playwright** at 390×844: `#/players` shows 8 cards; `#/player/our-p2` shows both blocks with rs 11, wkts 3 and a game list of 1 row; `test_player_page_no_balls`: build a tmp site from a team copy where one player's `innings` entries are removed (summaries kept) → that player's page shows "–" and no `NaN` anywhere (`browser_evaluate` `!document.body.innerText.includes("NaN")`). No console errors.

- [ ] **Step 3: Commit** — `git add -A && git commit -m "feat: players grid, player page, sparkline"`

---

### Task 7d: Records screen, scope defaults, team picker, polish

**Files:**
- Create: `viewer/screens/records.js`
- Modify: `viewer/app.js` (scope defaults per route, team picker, title), `viewer/app.css`

**Interfaces:**
- `screens.records`: two groups, "Team" and "Players", one card per record from `records.team` / `records.individual` with the value big, the holder(s) and `vs opp · date`, tapping → `game/<key>`; `None` records are omitted; hat-tricks listed (bowler, n, victims, date). Default scope `alltime`; the scope switcher still works here.
- Scope rule in `app.js`: when navigating to `records` with no explicit scope chosen in this visit, scope = `alltime`; any other route defaults to the latest season; a scope the viewer chose (`sessionStorage`) persists for the visit across routes.
- Team picker: when `data/index.json` has more than one team, the badge in the top bar opens a bottom sheet listing teams; choosing one navigates to `#/t/<slug>/home`; single-team sites never show it. `document.title` = team name.

- [ ] **Step 1: Implement** per Interfaces.

- [ ] **Step 2: Verify with Playwright**: `#/records` shows "All-time" selected and the records from the example game (highest total 51, heaviest loss −29, best contribution Our P2 +5, best partnership Our P1 & Our P2 28); navigate to `#/batting` → scope shows "Spring 2026"; choose All-time in the switcher, go to `#/records` and back → still All-time. Multi-team: build a tmp site with a second team folder (copy of example-team renamed, `name: "Second Side"`) → picker appears, switching changes the title and data. Screenshot light + dark.

- [ ] **Step 3: Commit** — `git add -A && git commit -m "feat: records screen, scope defaults, team picker"`

---

### Task 8: PIN gate (`_middleware.js`)

**Files:**
- Create: `viewer/functions/_middleware.js`, `viewer/functions/_middleware.test.js`

**Interfaces:**
- Pages Function middleware `export async function onRequest(context)` reading `context.env.GATE` (`"pin"|"email"|"none"`, default `"pin"`), `TEAM_PIN`, `PIN_SECRET`:
  - `GATE` is `none` or `email` → `context.next()` (email gating is done by Cloudflare Access in front of the site).
  - `GATE=pin` and (`TEAM_PIN` or `PIN_SECRET` missing) → `503` text `gate not configured`.
  - Valid cookie `ac_auth=<exp>.<hex hmac>` (HMAC-SHA256 over `"ok:" + exp` with `PIN_SECRET`, `exp` = unix seconds, not expired) → `context.next()`.
  - `POST /__pin` with form field `pin` equal to `TEAM_PIN` (constant-time compare) → `302` to `/` with `Set-Cookie: ac_auth=…; Max-Age=15552000; Path=/; HttpOnly; Secure; SameSite=Lax`.
  - Wrong pin → wait 1000 ms, then the PIN page with "That code didn't work" (`401`).
  - Anything else → the PIN page (`200`, inline HTML using the token values inline — the middleware cannot load CSS — one input `name=pin` `inputmode=numeric autocomplete=one-time-code`, one button "Open").
- Exports for tests: `export { onRequest, sign, verify }` where `sign(secret, exp) -> Promise<string>` and `verify(secret, cookieValue) -> Promise<boolean>` use Web Crypto (`crypto.subtle`), which Node 18+ and the Pages runtime both provide.

- [ ] **Step 1: Write failing tests** `viewer/functions/_middleware.test.js` (Node test runner; build a fake `context` with `request`, `env`, `next: () => new Response("page")`):

```js
test("gate none passes through", …)        // env.GATE="none" → body "page"
test("gate fails closed", …)               // env.GATE="pin", no TEAM_PIN → status 503
test("no cookie shows pin page", …)        // status 200, body includes 'name="pin"'
test("correct pin sets cookie", …)         // POST /__pin pin=123456 → 302, Set-Cookie includes ac_auth= and Max-Age=15552000
test("valid cookie passes", …)             // Cookie: ac_auth=<sign(secret, now+60)> → body "page"
test("expired cookie rejected", …)         // exp in the past → pin page
test("wrong pin is 401", …)                // (allow ~1s)
```

- [ ] **Step 2: Run `node --test viewer/functions/`** — expected: FAIL.

- [ ] **Step 3: Implement `_middleware.js`** per Interfaces.

- [ ] **Step 4: Run `node --test viewer/`** — expected: all PASS. `python scripts/build_site.py --out dist/site` still copies `functions/` (tests dir excluded: exclude any path containing `.test.js` or `tests/`).

- [ ] **Step 5: Commit** — `git add -A && git commit -m "feat: team PIN gate middleware"`

---

### Task 9: Team template, engine vendoring, root discovery

**Files:**
- Create: `template/README.md`, `template/CLAUDE.md`, `template/.gitignore`, `template/.github/workflows/deploy.yml`, `template/.claude/skills/add-scorecard/SKILL.md`, `template/.claude/skills/ai-coach/SKILL.md`, `template/.claude/skills/setup/SKILL.md` (thin wrappers), `template/Teams/README.txt`, `template/inbox/README.txt`, `template/site/.gitkeep`, `template/engine/README.txt`, `scripts/make_template.py`, `scripts/update_engine.py`, `tests/test_make_template.py`, `tests/test_paths_root.py`
- Modify: `scripts/paths.py` (`find_root` already added in Task 3 — test it here), `.claude/skills/add-scorecard/SKILL.md` and `ai-coach/SKILL.md` (paths written as `python engine/scripts/<x>.py` when `engine/` exists, else `python scripts/<x>.py` — express as "run `$ENGINE/scripts/…`, where `$ENGINE` is `engine` in a team repo and `.` in the engine repo")

**Interfaces:**
- Team repo layout produced by `make_template.py` into `dist/team-template/`: everything in `template/` + `engine/` = `{VERSION, requirements.txt, scripts/ (all), viewer/ (all, minus tests), .claude/skills/ (both engine skills), templates via scripts/templates}`; `engine/` is **committed** in team repos (vendored), replaced by `python engine/scripts/update_engine.py [--tag vX.Y.Z]`.
- `make_template.py`: `def assemble(out_dir: str) -> list[str]`; runs `leak_check.scan` over the output with `LEAK_LIST` if set and `structure_errors`; exits 1 on hits. CLI `python scripts/make_template.py [--out dist/team-template]`.
- `update_engine.py`: downloads `https://github.com/madeup-studio/indoor-cricket-stats/archive/refs/tags/<tag>.zip` (default: latest tag via the GitHub API), extracts the engine file set into `engine/` replacing it, prints the version. Network only; no tests beyond a `--dry-run` that prints the URL.
- `template/.github/workflows/deploy.yml`: on push to `main` touching `site/**`; `actions/checkout@v4`; `cloudflare/wrangler-action@v3` with `apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}`, `accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}`, `command: pages deploy site --project-name=__PROJECT_NAME__` (placeholder replaced by `setup.py`, Task 11).
- `template/.gitignore`: ignores `__pycache__/`, `inbox/*` except `README.txt`, `dist/`, `.cf-token`; does NOT ignore `site/` or `engine/`.
- Thin skills: each `SKILL.md` has the same frontmatter `name`/`description` as the engine's and a body: "Read and follow `engine/.claude/skills/<name>/SKILL.md`. Run scripts as `python engine/scripts/<script>.py` from the repo root."
- `paths.find_root`: from `engine/scripts/` in a team repo → the repo root (contains `Teams/`); from `scripts/` in the engine repo → the engine root.

- [ ] **Step 1: Write failing tests** `tests/test_paths_root.py` (`find_root` for a fake layout `tmp/repo/engine/scripts` with `tmp/repo/Teams` → returns `tmp/repo`; `tmp/engine/scripts` with `tmp/engine/Teams` → `tmp/engine`) and `tests/test_make_template.py`:

```python
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
```

- [ ] **Step 2: Run them** — expected: FAIL.

- [ ] **Step 3: Implement** the template files, `make_template.py`, `update_engine.py`, the thin skills, and the `$ENGINE` wording in both engine skills. `template/README.md` = the end-user "after every game" guide (adapted from the owner's kit README: phone/cloud-session flow first, PC flow second, no PDF talk unless `pdf: true`); `template/CLAUDE.md` = the kit CLAUDE.md adapted (engine under `engine/`, skills are wrappers, `site/` is generated and committed, never hand-edit it).

- [ ] **Step 4: Run `pytest -q`** — expected: PASS. Then `python scripts/make_template.py` → `dist/team-template/` and run `python scripts/leak_check.py --root dist/team-template` → exit 0.

- [ ] **Step 5: Commit** — `git add -A && git commit -m "feat: team template, engine vendoring, update_engine, root discovery"`

---

### Task 10: Publish step and the add-scorecard skill (chat flow)

**Files:**
- Create: `scripts/publish.py`, `tests/test_publish.py`
- Modify: `.claude/skills/add-scorecard/SKILL.md`

**Interfaces:**
- `publish.py`: `REPO = os.path.dirname(paths.TEAMS_DIR)` (the team repo root; equals the engine root in the engine repo). `def publish(message: str, push: bool = True) -> dict(committed: bool, pushed: bool, sha: str|None)` — runs `build_site.build(os.path.join(REPO, "site"))`, then `git -C REPO add Teams site`, `git commit -m message` (skips the commit when nothing changed), `git push` only when `push` and a remote named `origin` exists; refuses (`SystemExit`) when the only team is `example-team`, so the engine repo can never be published. CLI: `python scripts/publish.py "<message>" [--no-push]`.
- Skill changes (`add-scorecard`): after step 3 (build and verify) add **3b. Rules snapshot** (copy `team.yaml → rules` into `meta.rules` of the new game file if absent); after step 5 add **5b. Ask for the standings and notes** exactly as the spec words it (one question, "skip" accepted; a table screenshot is transcribed to `<season>/context/<date>-standings.md`, a note to `<season>/context/<date>-note.md`); replace the PDF wording in step 5 with: run the `ai-coach` skill for the new game (`python $ENGINE/scripts/coach.py --status`), then build PDFs only if `team.yaml → pdf` is true; add **7. Publish**: `python $ENGINE/scripts/publish.py "Game <date> vs <opponent>"` and tell the user the site updates within a minute (or that there is no remote yet). Remove every mention of PDF file locations from the wrap-up unless `pdf` is on.

- [ ] **Step 1: Write failing tests** `tests/test_publish.py` — fixture creates a temp git repo containing a copy of the example team as `Teams/our-team/`, `engine/` not needed (import from `scripts`), with `TEAMS_DIR` env; `publish("Game x", push=False)` → `committed is True`, `git log -1` message matches, `site/data/our-team.json` is tracked; calling again with no changes → `committed is False`; in the engine repo itself (`Teams/example-team` only) → raises `SystemExit`.

- [ ] **Step 2: Run** — expected: FAIL.

- [ ] **Step 3: Implement `publish.py`** and edit the skill per Interfaces (keep the skill ≤ 120 lines).

- [ ] **Step 4: Run `pytest -q`** — expected: PASS.

- [ ] **Step 5: Commit** — `git add -A && git commit -m "feat: publish step; add-scorecard skill: standings ask, rules snapshot, publish"`

---

### Task 11: Cloudflare provisioning (`setup.py`) and the `/setup` wizard skill

**Files:**
- Create: `scripts/setup.py`, `tests/test_setup.py`, `.claude/skills/setup/SKILL.md` (engine copy; the template's thin wrapper points at it)

**Interfaces:**
- `setup.py` uses only `urllib.request`; every call goes through `def api(method: str, path: str, body: dict | None = None, *, http=None) -> dict` where `http` is an injectable callable `(method, url, headers, data) -> (status, json)` so tests never hit the network. Base `https://api.cloudflare.com/client/v4`; header `Authorization: Bearer <token>`. The token comes from env `CLOUDFLARE_API_TOKEN` or, failing that, the file `.cf-token` at the repo root (gitignored by the template; `--forget` deletes it). Because shell env does not persist between Claude Code commands, the wizard writes the pasted token to `.cf-token` and tells the user it is deleted at the end.
  - `def verify_token(http=None) -> dict` — `GET /user/tokens/verify`; raises `SetupError("token invalid")` unless `result.status == "active"`.
  - `def account_id(http=None) -> str` — `GET /accounts` → first account id (`SetupError` if none).
  - `def project_exists(acct, name, http=None) -> bool` — `GET /accounts/{acct}/pages/projects/{name}` (404 → False).
  - `def create_project(acct, name, http=None) -> str` — `POST /accounts/{acct}/pages/projects` body `{"name": name, "production_branch": "main"}` → returns `https://{name}.pages.dev`.
  - `def set_env(acct, name, env: dict, http=None) -> None` — `PATCH /accounts/{acct}/pages/projects/{name}` body `{"deployment_configs": {"production": {"env_vars": {k: {"value": v}}}}}`.
  - `def random_pin() -> str` (6 digits, `secrets`), `def random_secret() -> str` (32 hex).
  - `def write_workflow(project: str, repo_root: str) -> None` — replaces `__PROJECT_NAME__` in `.github/workflows/deploy.yml`.
  - `def deploy(project: str, site_dir: str) -> int` — runs `npx wrangler pages deploy <site_dir> --project-name <project>` (requires Node; returns exit code).
  - CLI: `--check`, `--create NAME`, `--gate pin|email|none [--pin 123456]`, `--deploy NAME`, `--status NAME`; prints plain English lines the skill relays.
- `/setup` skill: the conversation script. Steps, each ending "tell me when done": (0) confirm Claude Code + this repo; (1) Cloudflare account → `https://dash.cloudflare.com/sign-up`; (2) API token → `https://dash.cloudflare.com/profile/api-tokens` → Create Token → "Edit Cloudflare Workers" template (or custom: Account › Cloudflare Pages: Edit; Account › Account Settings: Read) → paste; the skill writes it to `.cf-token` and runs `setup.py --check`; (3) gate choice (the three options as the spec words them; `pin` → generate or accept a code, `email` → list of steps to switch on Zero Trust at `https://one.dash.cloudflare.com/` and add an Access application with the emails they give — manual in stage 1, `none` → nothing); (4) project name (default from the team folder) → `setup.py --create`, `--gate`, `write_workflow`; (5) the two GitHub secrets: link `https://github.com/<owner>/<repo>/settings/secrets/actions`, names `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` with values; (6) first deploy: `setup.py --deploy` if Node is available, else "push once and the Action deploys"; (7) hand over the URL and the PIN, then continue into team creation via `new_team.py` questions (name exactly as printed, arena, league, badge, rules preset, coach tone) and ask for the first scorecard. The skill must never print the token back and must store nothing secret in the repo.

- [ ] **Step 1: Write failing tests** `tests/test_setup.py` using a recording fake `http` (asserts method/url/body per function; `project_exists` on 404; `verify_token` on inactive → `SetupError`; `write_workflow` replaces the placeholder; `random_pin` is 6 digits).

- [ ] **Step 2: Run** — expected: FAIL.

- [ ] **Step 3: Implement `setup.py`** and write the skill.

- [ ] **Step 4: Run `pytest -q`** — expected: PASS.

- [ ] **Step 5: Commit** — `git add -A && git commit -m "feat: Cloudflare setup script and /setup wizard skill"`

---

### Task 12: Public docs, CI, versioning

**Files:**
- Modify: `README.md` (replace the planning stub with the public README: what it is, the three-account truth with costs, "no support promised", links; first line stays the repo description verbatim: "Scorecard photo → phone-first team stats and an AI coach, for indoor cricket (or Action Cricket)"; GitHub topics to set when the repo is created: `indoor-cricket`, `action-cricket`, `cricket-stats`, `spawtz`, `claude-code`), `.github/workflows/ci.yml` (add `node --test viewer/`, `python scripts/make_template.py`, `leak_check` on the template output)
- Create: `docs/SETUP.md` (the 20-minute setup: prerequisites with URLs — GitHub, Cloudflare, Claude Pro/Max; "Use this template"; open in Claude Code (web, app or desktop); `/setup`; first scorecard from the phone), `docs/COSTS.md` (Claude subscription vs API, Cloudflare free, GitHub free; per-game estimate wording "a few rand to a few tens of rand per game on an API key"), `docs/architecture.md` (the studio-required per-app architecture note: engine (pure Python, no I/O in `report_data.build`) → builders → viewer adapters; invariants: viewer never computes stats, engine never reads the viewer), `CONTRIBUTING.md`, `CHANGELOG.md` (`1.0.0 — first release`)

- [ ] **Step 1: Write the docs** per the spec's "Public engine repo" and "Team template repo" sections; every claim about accounts and costs must match the spec's Constraints.

- [ ] **Step 2: Verify**: `python scripts/leak_check.py` → 0; `pytest -q` → PASS; `node --test viewer/` → PASS; `python scripts/make_template.py` → builds; a fresh reader can follow `docs/SETUP.md` without this plan (read it once as that reader).

- [ ] **Step 3: Commit** — `git add -A && git commit -m "docs: public README, SETUP, COSTS, architecture, CONTRIBUTING; CI"`

---

### Task 13: End-to-end rehearsal with the example team (local), then the owner's first real run

**Files:** none new (fixes go to the owning task's files).

- [ ] **Step 1: Local rehearsal** — `python scripts/make_template.py --out dist/rehearsal`; `cd dist/rehearsal && git init -b main`; create a team with `python engine/scripts/new_team.py "Our Team" --arena "Example Arena" --badge OURS --season-start 2026-09-01`; copy `engine/scripts/templates/game-template.json` to `inbox/example.json`-equivalent flow: since there is no photo, copy it straight into `Teams/Our-Team/2026-09-01/data/2026-10-07.json`; run the add-scorecard script sequence (`build_scorecards`, `validate_ballbyball` → ALL RECONCILE, `roster --refresh`, `generate_stats`), write a letter via the ai-coach skill, then `python engine/scripts/publish.py "Game 2026-10-07 vs Opponents" --no-push` → commit exists, `site/` tracked. Serve `site/` and check the three screens on a phone viewport with Playwright (home, game page with letter, records). Then `python engine/scripts/leak_check.py --root .` → 0.

- [ ] **Step 2: Owner's real run (manual, documented in `docs/SETUP.md` as the acceptance checklist)** — owner creates the GitHub repos (public engine from this repo's clean history; public template from `dist/team-template`; private team repo from the template), runs `/setup` from Claude Code on the web, adds a real scorecard from the phone, confirms the site updates. Any defect found is fixed in the owning task above with a test.

- [ ] **Step 3: Tag** — `git tag v1.0.0` on the engine repo when Step 2 passes (owner's call).

---

## Self-review notes (done while writing)

- Spec coverage: rules (T3), coach per game + tones + on/off (T4, T7b), viewer screens incl. records/scope defaults/team picker/look (T6–T7d), PIN/email/none gate (T8, T11), multi-team (T5, T7d), publish + standings ask (T10), template + vendored engine + thin skills + update (T9), setup wizard (T11), public repo docs/CI/leak check (T2, T12), example team (T1), stage-2 items deliberately absent.
- Deviation from the spec recorded here: the engine is **vendored** into team repos (`engine/` committed) rather than fetched into a gitignored folder, because cloud sessions discover skills only from the repo root at session start and must not depend on network at run time; the thin wrapper skills in `template/.claude/skills/` make that work. `update_engine.py` replaces `bootstrap.py`. The spec's `engine.lock` becomes `engine/VERSION`.
- The `people.yaml` cross-team link is intentionally not built in stage 1 (spec: "v1 uses it for 'also plays for'"): the viewer leaves the slot empty when absent; add it in a follow-up plan with the multi-team rehearsal.
