# Season Awards, Medals, Playoff Games and Admin Switches — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give a season a shape in the app (playoff tags, a stated medal, engine-computed awards), let the admin switch records and features on or off from `team.yaml`, and close four stage-1 gaps (coach yes/no in setup, a hard duplicate-game guard, "add an admin" instructions, a coach persona line).

**Architecture:** The engine keeps computing everything; new facts travel through the one payload the viewer reads (`site/data/<team>.json`): `team.show`, per-season `medal/finish/finished/awards`, per-game `stage`, per-player award counts. A new optional `Teams/<team>/<season>/season.yaml` holds the admin-stated medal. Viewer logic that needs testing lives in a new pure module `viewer/model.js` (like `scope.js`); the DOM screens only call it. No admin UI: every setting is a line in YAML that Claude edits, applied on the next publish.

**Tech Stack:** Python 3 (pyyaml), pytest; plain ES modules tested with `node --test` (Node 22); no build step.

**Spec:** `docs/superpowers/specs/2026-11-03-season-awards-and-switches-design.md`

## Global Constraints

- No real team or player identifier anywhere; the example vocabulary is `Our Team` vs `Opponents`, players `Our P1…P8` / `Opp P1…P8`, seasons named like `Spring 2026`. `python scripts/leak_check.py` must stay clean.
- Every game file reconciles: `python scripts/validate_ballbyball.py` ends with `ALL RECONCILE`. Never change a number to make it fit.
- Rules constants come from `team.yaml → rules` (never hard-code −5 / 2 / 6).
- Viewer: plain HTML/CSS/JS, colours and spacing only via tokens in `viewer/tokens.css`; no prose on screens, explanations behind `?` HelpIcons; phone width first.
- Engine never reads viewer state; `viewer/model.js` and `viewer/scope.js` import nothing that touches `document`.
- Scripts run on Windows and Linux (use `os.path`, `encoding="utf-8"`, `newline="\n"` for generated files).
- Awards use the rankings exactly as `report_data.build()` orders them, with its `ranked` flag (`MIN_GAMES = 3` in a season).
- Allowed `meta.stage` values: `"league"`, `"playoff"`, `"semi-final"`, `"final"`; absent means league.
- Allowed `season.yaml → medal` values: `gold`, `silver`, `bronze`; absent means none.
- Default switches: everything on except `awards: false`.
- Run from the repo root; tests set `TEAM=example-team` (see `tests/conftest.py`).
- Commit after each task on the working branch; the owner decides when anything is pushed.

## Review Focus

1. A `season.yaml` with a misspelled or capitalised medal (`Silver`, `2nd`) must stop the build with a message naming the file, not silently show no icon. → Task 4.
2. A finished season where nobody reaches `MIN_GAMES` must produce three `null` awards and no Awards block in the viewer, never a block of dashes. → Tasks 5 and 8.
3. A `team.yaml` with no `show:` block, a partial one, or unknown keys must behave as defaults (old teams keep working). → Task 4.
4. A legitimate double-header (same date, two different opponents) must pass the duplicate guard; the same date and opponent twice must fail. → Task 3.
5. Awards won in a past season must reach the player index, which is built from all-time players, so the tally shows even when the player is absent from the current season. → Task 6 (`test_payload_seasons_medal_finished_awards`: winners of the finished season carry counts while the current season is a different one).

---

### Task 1: Test helpers — clone and mirror the example game

**Files:**
- Modify: `tests/conftest.py`
- Test: `tests/test_conftest_helpers.py`

**Interfaces:**
- Produces: `clone_game(teams_dir: Path, date: str, *, season_folder: str = "2026-09-01", season_label: str | None = None, mirror: bool = False, stage: str | None = None) -> Path` (module-level in `tests/conftest.py`). Copies `Teams/example-team/2026-09-01/data/2026-10-07.json` from the tmp copy under `teams_dir` to `<season_folder>/data/<date>.json` with `date` replaced, `meta.season` set to `season_label` when given, `meta.stage` set when given, creating `<season_folder>/{data,scorecards}` as needed. `mirror=True` swaps the two sides so Our Team wins 80–51: swap the strings `"Our Team"`↔`"Opponents"` and `Our P<n>`↔`Opp P<n>` everywhere in the serialised JSON (two-step placeholder replace), then restore the top-level `team` to `"Our Team"` and `opponent` to `"Opponents"` (the text swap flipped them), and in `result` swap `team_total`↔`opponent_total`, `team_skins`↔`opponent_skins`, `team_skins_won`↔`opponent_skins_won`, and set `outcome` to `"win"`. `summaries` keys and `innings[].batting_team` stay swapped: that is the point. Does not run `build_scorecards.py`.
- Produces fixtures: `tmp_team_three_games(tmp_path) -> str` (team dir): example + straight clone `2026-10-14` + mirrored clone `2026-10-21`, then `build_scorecards.py` run with `TEAMS_DIR`. `tmp_team_two_seasons(tmp_path) -> str`: the three games, plus `2026-09-01/season.yaml` containing `medal: silver` and `finish: "2nd in Mens E"`, plus folder `2027-01-12` with a straight clone dated `2027-01-14` and `season_label="Summer 2027"`; `build_scorecards.py` run.

- [ ] **Step 1: Write the failing test** `tests/test_conftest_helpers.py`

```python
import json
from conftest import clone_game, _copy_example, _run_script

def test_clone_and_mirror_reconcile(tmp_path):
    teams = _copy_example(tmp_path)
    clone_game(teams, "2026-10-14")
    p = clone_game(teams, "2026-10-21", mirror=True)
    g = json.loads(p.read_text(encoding="utf-8"))
    assert g["date"] == "2026-10-21" and g["result"]["outcome"] == "win"
    assert (g["team"], g["opponent"], g["innings"][0]["batting_team"]) == ("Our Team", "Opponents", "Opponents")
    assert (g["result"]["team_total"], g["result"]["opponent_total"]) == (80, 51)
    assert g["result"]["player_of_match"] == "Our P7" and g["result"]["player_of_match_team"] == "Our Team"
    assert {r["name"] for r in g["summaries"]["Our Team"]} == {f"Our P{i}" for i in range(1, 9)}
    r = _run_script("build_scorecards.py", env={"TEAMS_DIR": str(teams)})
    assert r.returncode == 0, r.stderr
    r = _run_script("validate_ballbyball.py", env={"TEAMS_DIR": str(teams)})
    assert "ALL RECONCILE" in r.stdout, r.stdout[-1500:]

def test_two_seasons_fixture(tmp_team_two_seasons):
    import os, yaml
    assert os.path.exists(os.path.join(tmp_team_two_seasons, "2027-01-12", "data", "2027-01-14.json"))
    meta = yaml.safe_load(open(os.path.join(tmp_team_two_seasons, "2026-09-01", "season.yaml"), encoding="utf-8"))
    assert meta == {"medal": "silver", "finish": "2nd in Mens E"}
    r = _run_script("validate_ballbyball.py", env={"TEAMS_DIR": os.path.dirname(tmp_team_two_seasons)})
    assert "ALL RECONCILE" in r.stdout
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pytest tests/test_conftest_helpers.py -v`
Expected: FAIL with `ImportError: cannot import name 'clone_game'`

- [ ] **Step 3: Implement `clone_game` and the two fixtures in `tests/conftest.py`**

Keep `tmp_team_two_games_same_day` as it is. The placeholder swap on the JSON text: `Our Team`→`@@T@@`, `Opponents`→`Our Team`, `@@T@@`→`Opponents`; then with `re.sub`: `Our P(\d)`→`@@P\1@@`, `Opp P(\d)`→`Our P\1`, `@@P(\d)@@`→`Opp P\1`. Then `json.loads`, fix `team`/`opponent`/`result`, and write with `indent=1`.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/test_conftest_helpers.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add tests/conftest.py tests/test_conftest_helpers.py
git commit -m "test: clone/mirror helpers and multi-game fixtures for the example team"
```

---

### Task 2: `meta.stage` — validator, scorecard frontmatter, transcription notes

**Files:**
- Modify: `scripts/validate_ballbyball.py` (in `main()`, right after the `=== date team vs opp ===` print)
- Modify: `scripts/build_scorecards.py:112-117` (the `F` frontmatter list)
- Modify: `scripts/TRANSCRIBE.md:87-88` (meta schema line) and `scripts/templates/game-template.json` (`meta.notes` text)
- Test: `tests/test_stage.py`

**Interfaces:**
- Produces: `STAGES = ("league", "playoff", "semi-final", "final")` in `scripts/validate_ballbyball.py`. A game whose `meta.stage` is present and not in `STAGES` prints `  [M] meta.stage '<value>' not one of league/playoff/semi-final/final  FAIL` and counts as a failed check.
- Produces: the scorecard frontmatter line `stage: <value>` (unquoted) emitted only when `meta.stage` is present; `stats_core.load_matches()` therefore yields `m.get("stage")` = the value or `None`.

- [ ] **Step 1: Write the failing tests** `tests/test_stage.py`

```python
import json, os
from conftest import clone_game, _copy_example, _run_script
import stats_core

def _env(teams): return {"TEAMS_DIR": str(teams)}

def test_stage_round_trips_through_frontmatter(tmp_path):
    teams = _copy_example(tmp_path)
    clone_game(teams, "2026-10-14", stage="final")
    assert _run_script("build_scorecards.py", env=_env(teams)).returncode == 0
    ms = stats_core.load_matches(str(teams / "example-team" / "2026-09-01" / "scorecards"))
    assert [m.get("stage") for m in ms] == [None, "final"]
    text = (teams / "example-team" / "2026-09-01" / "scorecards" / "2026-10-07-our-team-vs-opponents.md").read_text(encoding="utf-8")
    assert "stage:" not in text.split("---")[1]

def test_validator_accepts_each_stage_and_rejects_others(tmp_path):
    teams = _copy_example(tmp_path)
    for i, st in enumerate(("league", "playoff", "semi-final", "final")):
        clone_game(teams, f"2026-11-{10 + i:02d}", stage=st)
    assert "ALL RECONCILE" in _run_script("validate_ballbyball.py", env=_env(teams)).stdout
    clone_game(teams, "2026-11-20", stage="cup")
    r = _run_script("validate_ballbyball.py", env=_env(teams))
    assert r.returncode == 1 and "[M] meta.stage 'cup'" in r.stdout
```

- [ ] **Step 2: Run them to verify they fail**

Run: `pytest tests/test_stage.py -v`
Expected: both FAIL (`stage` missing from frontmatter; `cup` accepted)

- [ ] **Step 3: Implement**

In `build_scorecards.py`, after the `source_image` line append `"stage: %s" % meta["stage"]` only `if meta.get("stage")`. In `validate_ballbyball.py` add the `STAGES` tuple and the `[M]` check. In `TRANSCRIBE.md` meta line add `"stage": one of league|playoff|semi-final|final, only when the card's league line or the user says so (omit otherwise)`. In `game-template.json` `meta.notes` append one sentence saying the same.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest tests/test_stage.py tests/test_build_scorecards.py tests/test_pipeline_smoke.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/validate_ballbyball.py scripts/build_scorecards.py scripts/TRANSCRIBE.md scripts/templates/game-template.json tests/test_stage.py
git commit -m "feat: meta.stage (league/playoff/semi-final/final) validated and carried into scorecards"
```

---

### Task 3: Duplicate game guard in the validator

**Files:**
- Modify: `scripts/validate_ballbyball.py` (`main()`: before the per-file loop, group files per season folder)
- Test: `tests/test_validate_duplicates.py`

**Interfaces:**
- Produces: for every season folder, files whose `(date, opponent)` repeat print `!! duplicate game: <first> and <second> both record <date> vs <opponent>` (basenames in sorted order, so `2026-10-07-again.json` comes before `2026-10-07.json`), count one failed check per extra file, and the run exits 1. Different opponents on one date are not duplicates.

- [ ] **Step 1: Write the failing tests**

```python
import json
from conftest import clone_game, _copy_example, _run_script

def test_same_date_and_opponent_twice_fails(tmp_path):
    teams = _copy_example(tmp_path)
    p = clone_game(teams, "2026-10-07")                # writes 2026-10-07.json over the original
    g = json.loads(p.read_text(encoding="utf-8"))
    (p.parent / "2026-10-07-again.json").write_text(json.dumps(g), encoding="utf-8")
    r = _run_script("validate_ballbyball.py", env={"TEAMS_DIR": str(teams)})
    assert r.returncode == 1
    assert "duplicate game: 2026-10-07-again.json and 2026-10-07.json both record 2026-10-07 vs Opponents" in r.stdout

def test_double_header_is_not_a_duplicate(tmp_team_two_games_same_day):
    import os
    r = _run_script("validate_ballbyball.py", env={"TEAMS_DIR": os.path.dirname(tmp_team_two_games_same_day)})
    assert "ALL RECONCILE" in r.stdout and "duplicate" not in r.stdout
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/test_validate_duplicates.py -v`
Expected: first test FAILS (returncode 0, no message)

- [ ] **Step 3: Implement the guard** — load each file's `date`/`opponent` once up front per season folder (the file list is already sorted), group by `(str(date), opponent)`, emit one message per extra file naming the files in sorted order, add to `fails`/`total`, then continue with the existing per-file checks.

- [ ] **Step 4: Run to verify pass**

Run: `pytest tests/test_validate_duplicates.py tests/test_pipeline_smoke.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/validate_ballbyball.py tests/test_validate_duplicates.py
git commit -m "feat: validator refuses two game files for the same date and opponent"
```

---

### Task 4: `season_meta.py` and `team_settings.py` (pure modules)

**Files:**
- Create: `scripts/season_meta.py`, `scripts/team_settings.py`
- Test: `tests/test_season_meta.py`, `tests/test_team_settings.py`

**Interfaces:**
- Produces (`season_meta.py`): `MEDALS = ("gold", "silver", "bronze")`; `load(season_dir: str) -> dict` returning `{"medal": str|None, "finish": str|None, "closed": bool}` from `<season_dir>/season.yaml` (missing file → all empty); raises `ValueError(f"{path}: medal must be one of gold/silver/bronze, got {value!r}")` on a bad medal (no case-folding); `is_finished(index: int, n_seasons: int, meta: dict) -> bool` = `index < n_seasons - 1 or meta["closed"] or bool(meta["medal"])`.
- Produces (`team_settings.py`): `SHOW_DEFAULTS` (exactly the spec's block: `awards False`, `medals/stage_tags/streaks/partnerships/hattricks True`, `records` = the 11 keys all True); `SHOW_NOTES` = `{key: comment}` for the top-level keys plus `"records"`, the spec's comments verbatim, so `SHOW_NOTES["awards"] == "player / batter / bowler of the season (finished seasons)"` and `SHOW_NOTES["records"] == "individual record cards; a key set to false hides that card"`; `merge_show(cfg: dict) -> dict` deep-merging `cfg.get("show")` over `SHOW_DEFAULTS`, coercing values with `bool()`, ignoring unknown keys, never mutating inputs.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_season_meta.py
import pytest, season_meta as SM
def test_missing_file_is_empty(tmp_path):
    assert SM.load(str(tmp_path)) == {"medal": None, "finish": None, "closed": False}
def test_reads_fields(tmp_path):
    (tmp_path / "season.yaml").write_text('medal: gold\nfinish: "Won the final"\nclosed: true\n', encoding="utf-8")
    assert SM.load(str(tmp_path)) == {"medal": "gold", "finish": "Won the final", "closed": True}
@pytest.mark.parametrize("bad", ["Silver", "2nd", "none"])
def test_bad_medal_raises_naming_file(tmp_path, bad):
    (tmp_path / "season.yaml").write_text(f"medal: {bad}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="season.yaml.*gold/silver/bronze"):
        SM.load(str(tmp_path))
def test_is_finished():
    empty = {"medal": None, "finish": None, "closed": False}
    assert SM.is_finished(0, 2, empty) and not SM.is_finished(1, 2, empty)
    assert SM.is_finished(1, 2, dict(empty, closed=True)) and SM.is_finished(1, 2, dict(empty, medal="bronze"))
```

```python
# tests/test_team_settings.py
import team_settings as TS
def test_defaults_shape():
    assert TS.SHOW_DEFAULTS["awards"] is False and TS.SHOW_DEFAULTS["medals"] is True
    assert set(TS.SHOW_DEFAULTS) == {"awards", "medals", "stage_tags", "streaks", "partnerships", "hattricks", "records"}
    assert set(TS.SHOW_DEFAULTS["records"]) == {"high_total", "low_total", "biggest_win", "heaviest_loss", "best_skin",
        "most_wkts_game", "fewest_extras_game", "best_contribution", "most_runs_game", "best_econ", "most_runouts_created"}
    assert set(TS.SHOW_NOTES) == set(TS.SHOW_DEFAULTS)
def test_merge_partial_unknown_and_absent():
    assert TS.merge_show({}) == TS.SHOW_DEFAULTS
    m = TS.merge_show({"show": {"awards": True, "records": {"best_econ": False}, "bogus": False}})
    assert m["awards"] is True and m["records"]["best_econ"] is False and m["records"]["high_total"] is True
    assert "bogus" not in m and TS.SHOW_DEFAULTS["awards"] is False       # defaults untouched
```

- [ ] **Step 2: Run to verify failure** — `pytest tests/test_season_meta.py tests/test_team_settings.py -v` → `ModuleNotFoundError`

- [ ] **Step 3: Implement both modules** (yaml only in `season_meta.py`; `team_settings.py` has no imports).

- [ ] **Step 4: Run to verify pass** — same command → PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/season_meta.py scripts/team_settings.py tests/test_season_meta.py tests/test_team_settings.py
git commit -m "feat: season.yaml loader, finished-season rule, show switches with defaults"
```

---

### Task 5: Season awards from the rankings

**Files:**
- Modify: `scripts/report_data.py` (new function after `build`)
- Test: `tests/test_awards.py`

**Interfaces:**
- Consumes: `report_data.build(matches, R)` output (`batting`/`bowling`/`allround` lists with `ranked`, `avg12`, `econ`, `avgc`).
- Produces: `season_awards(d: dict) -> dict` = `{"batter": {"name", "value"}|None, "bowler": ...|None, "player": ...|None}` where batter = first entry of `d["batting"]` with `ranked`, value `avg12`; bowler = first `d["bowling"]` with `ranked`, value `econ`; player = first `d["allround"]` with `ranked`, value `avgc`. Values are plain floats, not rounded.

- [ ] **Step 1: Write the failing tests**

```python
import os, report_data as RD, roster, stats_core as S

def _season(team_dir, folder):
    R = roster.load(os.path.join(team_dir, "players.yaml"))
    return RD.build(S.load_matches(os.path.join(team_dir, folder, "scorecards")), R)

def test_awards_follow_the_rankings(tmp_team_three_games):
    d = _season(tmp_team_three_games, "2026-09-01")
    a = RD.season_awards(d)
    first = lambda k: next(x for x in d[k] if x["ranked"])
    assert a["batter"] == {"name": first("batting")["name"], "value": first("batting")["avg12"]}
    assert a["bowler"] == {"name": first("bowling")["name"], "value": first("bowling")["econ"]}
    assert a["player"] == {"name": first("allround")["name"], "value": first("allround")["avgc"]}
    assert a["player"]["name"].startswith("Our P")

def test_no_award_when_nobody_qualifies(tmp_team):
    d = _season(str(tmp_team / "example-team"), "2026-09-01")       # one game < MIN_GAMES
    assert RD.season_awards(d) == {"batter": None, "bowler": None, "player": None}
```

- [ ] **Step 2: Run to verify failure** — `pytest tests/test_awards.py -v` → `AttributeError: season_awards`
- [ ] **Step 3: Implement `season_awards(d)`** in `report_data.py`.
- [ ] **Step 4: Run to verify pass** — PASS
- [ ] **Step 5: Commit** — `git commit -am "feat: season awards = first ranked batter, bowler and all-rounder"` (add the test file first)

---

### Task 6: Payload — switches, season medal/finish/finished/awards, game stage, player award counts

**Files:**
- Modify: `scripts/build_site.py` (`_load_seasons`, `team_payload`)
- Test: `tests/test_build_site.py` (append tests; existing pins untouched here)

**Interfaces:**
- Consumes: `team_settings.merge_show`, `season_meta.load/is_finished`, `report_data.season_awards`, `m.get("stage")` from Task 2.
- Produces in the payload:
  - `team.show` = `merge_show(cfg)`.
  - each `seasons[i]` gains `medal` (str|None), `finish` (str|None), `finished` (bool), `awards` (the `season_awards` dict when finished, else `None`).
  - each `games[j]` gains `stage` (str|None, as read).
  - `players[name]["awards"]` = `{"player": int, "batter": int, "bowler": int}` counted over finished seasons, present only when at least one count is > 0.
- `_load_seasons` keeps returning `(folder, label, matches)`; `team_payload` derives the season dir as `os.path.join(team_dir, folder)`.

- [ ] **Step 1: Write the failing tests** (append to `tests/test_build_site.py`)

```python
def test_payload_show_defaults_and_override(tmp_team):
    import build_site as B, team_settings as TS, yaml
    team_dir = tmp_team / "example-team"
    assert B.team_payload(str(team_dir), None)["team"]["show"] == TS.SHOW_DEFAULTS
    cfg = yaml.safe_load((team_dir / "team.yaml").read_text(encoding="utf-8"))
    cfg["show"] = {"awards": True, "records": {"low_total": False}}
    (team_dir / "team.yaml").write_text(yaml.safe_dump(cfg), encoding="utf-8")
    show = B.team_payload(str(team_dir), None)["team"]["show"]
    assert show["awards"] is True and show["records"]["low_total"] is False and show["streaks"] is True

def test_payload_seasons_medal_finished_awards(tmp_team_two_seasons):
    import build_site as B
    p = B.team_payload(tmp_team_two_seasons, None)
    s0, s1 = p["seasons"]
    assert (s0["key"], s0["medal"], s0["finish"], s0["finished"]) == ("2026-09-01", "silver", "2nd in Mens E", True)
    assert (s1["key"], s1["label"], s1["medal"], s1["finished"], s1["awards"]) == ("2027-01-12", "Summer 2027", None, False, None)
    assert set(s0["awards"]) == {"batter", "bowler", "player"} and s0["awards"]["player"]["name"].startswith("Our P")
    winners = {a["name"] for a in s0["awards"].values()}
    for n in winners:
        assert sum(p["players"][n]["awards"].values()) >= 1
    assert all("awards" not in v for k, v in p["players"].items() if k not in winners)

def test_payload_current_season_without_medal_is_not_finished(tmp_team_three_games):
    import build_site as B
    s = B.team_payload(tmp_team_three_games, None)["seasons"][0]
    assert s["finished"] is False and s["awards"] is None and s["medal"] is None

def test_payload_game_stage(tmp_path):
    import build_site as B
    from conftest import clone_game, _copy_example, _run_script
    teams = _copy_example(tmp_path)
    clone_game(teams, "2026-10-14", stage="final")
    assert _run_script("build_scorecards.py", env={"TEAMS_DIR": str(teams)}).returncode == 0
    p = B.team_payload(str(teams / "example-team"), None)
    assert [g["stage"] for g in p["games"]] == [None, "final"]

def test_bad_medal_fails_the_build(tmp_team):
    import build_site as B, pytest
    (tmp_team / "example-team" / "2026-09-01" / "season.yaml").write_text("medal: Silver\n", encoding="utf-8")
    with pytest.raises(ValueError, match="season.yaml"):
        B.team_payload(str(tmp_team / "example-team"), None)
```

- [ ] **Step 2: Run to verify failure** — `pytest tests/test_build_site.py -v -k "show or medal or stage or finished"` → KeyErrors
- [ ] **Step 3: Implement in `team_payload`** — merge show; per season `meta = season_meta.load(sd)`, `finished = season_meta.is_finished(i, len(seasons), meta)`, `awards = RD.season_awards(d) if finished else None`; accumulate player award counts; add `stage=m.get("stage")` to each game dict.
- [ ] **Step 4: Run to verify pass** — `pytest tests/test_build_site.py -v` → PASS (all, including the old pins: the example itself is unchanged in this task)
- [ ] **Step 5: Commit** — `git add scripts/build_site.py tests/test_build_site.py && git commit -m "feat: payload carries show switches, season medal/awards, game stage, player award counts"`

---

### Task 7: `new_team.py` — `show:` block, coach persona, `--no-coach`

**Files:**
- Modify: `scripts/new_team.py` (`team_yaml`, `create_team`, `main`)
- Test: `tests/test_new_team.py`

**Interfaces:**
- Consumes: `team_settings.SHOW_DEFAULTS`, `SHOW_NOTES`.
- Produces: `team_yaml(name, arena, badge, league="", preset=..., tone="banter", gate="pin", coach_enabled=True)`; `create_team(..., coach_enabled=True)`; CLI flag `--no-coach`. The written `team.yaml` has, after the `coach:` block's `language` line, `  persona: ""` with comment `optional: one line of flavour for the coach, e.g. "a grumpy old pro"`, and after `admins`, a blank line then the `show:` block: every key of `SHOW_DEFAULTS` with its `SHOW_NOTES` comment, the `records:` sub-keys indented two more spaces with the comment on the `records:` line only.

- [ ] **Step 1: Update and add tests**

In `test_new_team_writes_spec_settings` change the coach assertion to
`assert cfg["coach"] == {"enabled": True, "tone": "banter", "language": "en", "persona": ""}` and add
`import team_settings as TS; assert cfg["show"] == TS.SHOW_DEFAULTS`. Add:

```python
def test_new_team_no_coach(tmp_path, run_script):
    teams = tmp_path / "Teams"
    r = run_script("new_team.py", "Zed Team", "--folder", "zed", "--no-coach", env={"TEAMS_DIR": str(teams)})
    assert r.returncode == 0, r.stderr
    cfg = yaml.safe_load((teams / "zed" / "team.yaml").read_text(encoding="utf-8"))
    assert cfg["coach"]["enabled"] is False
    text = (teams / "zed" / "team.yaml").read_text(encoding="utf-8")
    assert "show:" in text and "# player / batter / bowler of the season" in text
```

- [ ] **Step 2: Run to verify failure** — `pytest tests/test_new_team.py -v` → FAIL (no `show`, no `persona`, unknown flag)
- [ ] **Step 3: Implement** using the existing `line()` helper.
- [ ] **Step 4: Run to verify pass** — PASS
- [ ] **Step 5: Commit** — `git commit -am "feat: new_team writes show switches and coach persona; --no-coach"`

---

### Task 8: `viewer/model.js` (pure view-model) and the awards glossary entry

**Files:**
- Create: `viewer/model.js`
- Modify: `viewer/help.js` (`GLOSSARY`)
- Test: `viewer/tests/model.test.js`, `viewer/tests/help.test.js`

**Interfaces (all exported from `viewer/model.js`, no imports):**
- `MEDAL_ICON = { gold: "🥇", silver: "🥈", bronze: "🥉" }`
- `seasonOptionLabel(season) -> string`: `"<icon> <label>"` when `season.medal` maps to an icon, else `season.label`.
- `seasonHeading(season) -> string`: label, then `" · <icon>"` when medal, then `" <finish>"` when finish (e.g. `"Spring 2026 · 🥈 2nd in Mens E"`).
- `STAGE_LABEL = { playoff: "Playoff", "semi-final": "Semi-final", final: "Final" }`; `stageLabel(game) -> string|null` (`league`, absent, unknown → `null`).
- `isShown(show, key) -> boolean`: `show` falsy → `true`; `key` in `show.records` → that value; `key` in `show` → that value; else `true`.
- `recordVisible(show, key) -> boolean`: maps `best_partnership→partnerships`, `longest_win_streak|longest_loss_streak→streaks`, `hattricks→hattricks`, else `isShown(show, key)` (which hits `show.records`). Also honours `medals` via `isShown(show, "medals")` and `stage_tags` via `isShown(show, "stage_tags")`, used by callers.
- `AWARD_TITLES = { player: "Player of the season", batter: "Batter of the season", bowler: "Bowler of the season" }`; `AWARD_UNITS = { player: "avg contribution", batter: "per 12 balls", bowler: "economy" }`.
- `awardRows(season) -> Array<{key, title, name, value, unit}>` in order player, batter, bowler, skipping `null` awards; `[]` when `!season.finished || !season.awards`.
- `awardsBySeason(data) -> Array<{season, heading, rows}>`: finished seasons with at least one row, newest first.
- `awardTally(player) -> string|null`: `"Player of the season ×1 · Bowler of the season ×2"` (order player, batter, bowler; zero counts skipped; `null` when none or no `awards`).
- `help.js` gains `GLOSSARY.awards = { title: "Season awards", text: (r, n) => ... }` mentioning that they are worked out from the season's rankings once the season is over and need at least `n.season` (default 3) games.

- [ ] **Step 1: Write the failing tests** `viewer/tests/model.test.js`

```js
import test from "node:test"; import assert from "node:assert/strict";
import { seasonOptionLabel, seasonHeading, stageLabel, isShown, recordVisible, awardRows, awardsBySeason, awardTally } from "../model.js";

const show = { awards: true, medals: true, stage_tags: true, streaks: false, partnerships: true, hattricks: false,
  records: { high_total: true, best_econ: false } };

test("season labels carry the medal", () => {
  assert.equal(seasonOptionLabel({ label: "Spring 2026", medal: "silver" }), "🥈 Spring 2026");
  assert.equal(seasonOptionLabel({ label: "Spring 2026", medal: null }), "Spring 2026");
  assert.equal(seasonHeading({ label: "Spring 2026", medal: "silver", finish: "2nd in Mens E" }), "Spring 2026 · 🥈 2nd in Mens E");
  assert.equal(seasonHeading({ label: "Spring 2026" }), "Spring 2026");
});
test("stage labels", () => {
  assert.equal(stageLabel({ stage: "final" }), "Final");
  assert.equal(stageLabel({ stage: "semi-final" }), "Semi-final");
  assert.equal(stageLabel({ stage: "league" }), null);
  assert.equal(stageLabel({}), null);
});
test("switches: missing means shown, records keys, grouped keys", () => {
  assert.equal(isShown(undefined, "awards"), true);
  assert.equal(isShown(show, "streaks"), false);
  assert.equal(isShown(show, "best_econ"), false);
  assert.equal(isShown(show, "low_total"), true);
  assert.equal(recordVisible(show, "longest_win_streak"), false);
  assert.equal(recordVisible(show, "best_partnership"), true);
  assert.equal(recordVisible(show, "hattricks"), false);
  assert.equal(recordVisible(show, "best_econ"), false);
});
const fin = { key: "s1", label: "Spring 2026", medal: "silver", finish: "2nd", finished: true,
  awards: { player: { name: "Our P2", value: 4.5 }, batter: null, bowler: { name: "Our P3", value: -1.25 } } };
test("award rows only for finished seasons with winners", () => {
  assert.deepEqual(awardRows(fin).map((r) => [r.key, r.name, r.unit]),
    [["player", "Our P2", "avg contribution"], ["bowler", "Our P3", "economy"]]);
  assert.deepEqual(awardRows({ ...fin, finished: false }), []);
  assert.deepEqual(awardRows({ ...fin, awards: { player: null, batter: null, bowler: null } }), []);
  const by = awardsBySeason({ seasons: [fin, { key: "s2", label: "Summer 2027", finished: false, awards: null }] });
  assert.deepEqual(by.map((b) => b.heading), ["Spring 2026 · 🥈 2nd"]);
});
test("award tally", () => {
  assert.equal(awardTally({ awards: { player: 1, batter: 0, bowler: 2 } }), "Player of the season ×1 · Bowler of the season ×2");
  assert.equal(awardTally({ awards: { player: 0, batter: 0, bowler: 0 } }), null);
  assert.equal(awardTally({}), null);
});
```

In `viewer/tests/help.test.js` add `"awards"` to the sorted key list and
`assert.match(glossaryText("awards", {}, { season: 3, alltime: 10 }), /3 games/);`.

- [ ] **Step 2: Run to verify failure** — `node --test "viewer/**/*.test.js"` → model.js not found; help key list mismatch
- [ ] **Step 3: Implement `viewer/model.js` and the glossary entry**
- [ ] **Step 4: Run to verify pass** — `node --test "viewer/**/*.test.js"` → all PASS
- [ ] **Step 5: Commit** — `git add viewer/model.js viewer/help.js viewer/tests && git commit -m "feat(viewer): pure view-model for medals, stages, switches and awards"`

---

### Task 9: Records opens on the current season

**Files:**
- Modify: `viewer/scope.js` (`defaultScope`), `viewer/tests/scope.test.js`

- [ ] **Step 1: Update the test** — rename the first test to `"every screen defaults to the latest season"`, assert `defaultScope("records", data) === "2026-09-01"`, keep the empty-seasons case `"alltime"`; in the second test change the first assertion to `resolveScope("records", data, null) === "2026-09-01"`.
- [ ] **Step 2: Run to verify failure** — `node --test viewer/tests/scope.test.js` → FAIL
- [ ] **Step 3: Implement** — drop the `records` special case and update the module comment.
- [ ] **Step 4: Run to verify pass** — PASS
- [ ] **Step 5: Commit** — `git commit -am "feat(viewer): Records opens on the current season like every other screen"`

---

### Task 10: Screens — medal in the switcher, stage tags, awards blocks, tally, switches

**Files:**
- Modify: `viewer/app.js` (`fillScope`), `viewer/screens/records.js`, `viewer/screens/games.js`, `viewer/screens/players.js`, `viewer/app.css`

**Interfaces:**
- Consumes: everything in `viewer/model.js`; payload fields from Task 6 (`data.team.show`, `season.medal/finish/finished/awards`, `game.stage`, `data.players[name].awards`).
- Produces: `.tag` CSS class (small rounded label, tokens only, next to `.pill` in `app.css`); `.tally` under `.player-head`; awards use the existing `.rec-grid` / `.card.rec` / `h2.group` / `h3.label` classes.

- [ ] **Step 1: `fillScope`** — option text = `seasonOptionLabel(s)` when `isShown(data.team.show, "medals")`, else `s.label`.
- [ ] **Step 2: `games.js`** — when `isShown(show, "stage_tags")` and `stageLabel(g)`: in the list row append `h("span", { class: "tag" }, stageLabel(g))` inside `.what` after `.opp`; on the game page add the same tag after the date `label` in `.game-head`.
- [ ] **Step 3: `records.js`** — filter `TEAM`, `STREAKS`, `PLAYERS` and the hat-trick cards with `recordVisible(data.team.show, key)`. When `isShown(show, "awards")`: for a season scope with `awardRows(season).length`, render `h2.group "Awards"` + `rec-grid` of `card(row.title, <formatted value>, row.name, {}, "awards")` **before** the Team group (format: player `signed(v, 1)`, batter `fmt(v, 1)`, bowler `fmt(v, 2)`; the unit as the `rec-where` line); for `alltime`, render `h2.group "Awards"` then for each `awardsBySeason(data)` entry an `h3.label` with `heading` and its grid. Put the `?` only on the first awards card (the `card()` helper already does this through `rec-wrap`).
- [ ] **Step 4: `players.js`** — in `screens.player`, after the `h1`, `awardTally(p) ? h("p", { class: "muted small tally" }, awardTally(p)) : null`, only when `isShown(data.team.show, "awards")`.
- [ ] **Step 5: CSS** — `.tag` and `.player-head .tally` in `app.css` using `--madeup-*` tokens; the tag must fit on a 360px-wide game row without wrapping the score.
- [ ] **Step 6: Verify in a browser** — build a site from the two-seasons fixture:

```bash
python - <<'EOF'
import os, sys, tempfile, pathlib; sys.path.insert(0, "tests"); sys.path.insert(0, "scripts")
from conftest import _copy_example, clone_game, _run_script
import yaml
tmp = pathlib.Path(tempfile.mkdtemp()); teams = _copy_example(tmp)
clone_game(teams, "2026-10-14"); clone_game(teams, "2026-10-21", mirror=True, stage="final")
(teams/"example-team"/"2026-09-01"/"season.yaml").write_text('medal: silver\nfinish: "2nd in Mens E"\n', encoding="utf-8")
clone_game(teams, "2027-01-14", season_folder="2027-01-12", season_label="Summer 2027")
cfg = teams/"example-team"/"team.yaml"; c = yaml.safe_load(cfg.read_text(encoding="utf-8")); c["show"] = {"awards": True}; cfg.write_text(yaml.safe_dump(c), encoding="utf-8")
assert _run_script("build_scorecards.py", env={"TEAMS_DIR": str(teams)}).returncode == 0
print(_run_script("build_site.py", "--out", "dist/preview", env={"TEAM": "", "TEAMS_DIR": str(teams)}).stdout)
EOF
python -m http.server -d dist/preview 8765
```

Open `http://localhost:8765/#/records` at phone width (Playwright MCP if available, else a browser) and check: the season menu shows `🥈 Spring 2026` and `Summer 2027`; Records opens on Summer 2027 with no Awards block; switching to Spring 2026 shows three award cards above Team; All-time shows the Awards group headed `Spring 2026 · 🥈 2nd in Mens E`; Games shows a `Final` tag on 21 Oct; the game page shows it; a winner's player page shows the tally. Then set `show.awards: false`, `streaks: false` in the temp `team.yaml`, rebuild, and confirm the Awards block, tally and streak cards disappear.

- [ ] **Step 7: Run all viewer tests** — `node --test "viewer/**/*.test.js"` → PASS
- [ ] **Step 8: Commit** — `git add viewer && git commit -m "feat(viewer): medal in the season menu, stage tags, awards blocks and tally, show switches"`

---

### Task 11: Grow the example team and update the pinned tests

**Files:**
- Create: `Teams/example-team/2026-09-01/data/2026-10-14.json` (straight clone), `.../2026-10-21.json` (mirror, `stage: "final"`), `Teams/example-team/2026-09-01/season.yaml`, `Teams/example-team/2027-01-12/data/2027-01-14.json` (straight clone, season `Summer 2027`), `Teams/example-team/2027-01-12/context/README.md` (via `new_team.py --season-start`), the three generated `scorecards/*.md`
- Modify: `Teams/example-team/team.yaml` (`show:` block with `awards: true`, `coach.persona: ""`), `Teams/example-team/seasons.md` (rows for the new games and season)
- Modify tests whose pins change: `tests/test_build_site.py` (`test_build_example_site`, `test_payload_shape_and_records`, `test_games_payload_double_header`), `tests/test_pipeline_smoke.py`, `tests/test_skill_snippets.py`

**Interfaces:**
- Consumes: `clone_game` from Task 1 (run once from a throwaway snippet with `TEAMS_DIR=Teams`; nothing new is added to the repo's scripts).
- Produces: the public example has a finished, medal-winning season with awards and a one-game current season.

- [ ] **Step 1: Generate the files** — run `python scripts/new_team.py --season-start 2027-01-12` (with `TEAM=example-team`), then a snippet calling `clone_game(Path("Teams"), ...)` for the three games as listed, write `season.yaml` with exactly `medal: silver` and `finish: "2nd in Mens E"`, add the `show:` block (copy the layout `new_team.py` now writes; set `awards: true`) and `persona: ""` to `team.yaml`, then `python scripts/build_scorecards.py` and `python scripts/validate_ballbyball.py` → `ALL RECONCILE`.
- [ ] **Step 2: Run the suite to see which pins moved** — `pytest -q` → expect failures only in the three test files above (and `tests/test_pdf_report.py` if it turns out to pin example figures or to fail on the new games' missing letters; read it before touching it). Before changing any pin, explain the new value from the added games (Spring: played 3, one win, loss streak 2 then win; all-time: played 4, 1–3; `generated == "2027-01-14"`; `high_total` becomes the mirrored game's 80 on `2026-10-21`; double-header fixture keys gain `2026-10-14`, `2026-10-21`, `2027-01-14`). A pin that cannot be explained this way is a bug: stop and fix the code.
- [ ] **Step 3: Update the pins** and add to `test_build_example_site`: `assert p["seasons"][0]["medal"] == "silver" and p["seasons"][0]["awards"]["player"]` and `assert p["games"][2]["stage"] == "final"`.
- [ ] **Step 4: Update `seasons.md`** (one row per game; the 2027 season row) and check `python scripts/coach.py --status` lists the three new games as `missing` and `2026-10-07` as `ok`.
- [ ] **Step 5: Verify** — `pytest -q` PASS; `node --test "viewer/**/*.test.js"` PASS; `python scripts/leak_check.py` clean (and with `--list` if the owner's list is at hand); `python scripts/make_template.py && python scripts/leak_check.py --root dist/team-template` clean.
- [ ] **Step 6: Commit** — `git add Teams/example-team tests && git commit -m "feat: example team gains a finished silver season with awards and a current season"`

---

### Task 12: Skills and docs

**Files:**
- Modify: `.claude/skills/setup/SKILL.md` (step 6), `.claude/skills/add-scorecard/SKILL.md` (step 1 duplicate text, step 2 stage, new "Other requests" section), `.claude/skills/ai-coach/SKILL.md` (Settings + Voice), `template/README.md` ("Other things you can ask"), `template/CLAUDE.md` (how the repo works), `docs/SETUP.md`, `docs/architecture.md` (data layout line), `CHANGELOG.md`
- Test: `tests/test_skill_text.py` (new, string presence only)

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run to verify failure** — `pytest tests/test_skill_text.py -v` → FAIL
- [ ] **Step 3: Write the text.** Exact content the spec fixes:
  - **setup step 6:** before the tone, ask "Do you want the AI coach's letter after each game? (yes / no)"; `no` → add `--no-coach` to the `new_team.py` command and skip the tone.
  - **add-scorecard step 1:** replace "Skip it if that date + opponent is already in `data/`." with: "If that date + opponent already exists in `data/`, say so and ask: re-check the existing game against this photo, or leave it? Re-checking means re-transcribing into the **same** file. Never write a second file (the validator refuses duplicates)."
  - **add-scorecard step 2:** add "If the card's league line or the user says playoff / semi-final / final, set `meta.stage` to `playoff`, `semi-final` or `final`; otherwise leave it out. Never ask unprompted."
  - **add-scorecard "## Other requests"** (new section before "## 7. Wrap up"): *Season over* ("we finished second" → `Teams/<TEAM>/<season>/season.yaml` with `medal: silver` (1st gold, 2nd silver, 3rd bronze, league or playoff alike; anything else → `finish:` only) and optional `finish: "<their words>"`, then publish); *Mark a game as a final* (edit `meta.stage`, re-run `build_scorecards.py`, `validate_ballbyball.py`, `generate_stats.py`, publish); *Show or hide things* ("hide best partnership", "show awards", "turn off streaks" → `team.yaml → show`, keys listed, publish); *Add Sam as an admin* (1. GitHub → repo → Settings → Collaborators → Add people — the real permission; 2. Sam connects Claude Code to the repo; 3. add Sam's git email to `team.yaml → admins`; note the guard is best effort in cloud sessions); *Give the coach a personality* (`coach.persona`).
  - **ai-coach:** Settings gains "`persona`: optional one line of flavour, applied on top of the tone"; Voice gains a paragraph: the persona colours word choice and running gags; the tone's rules still win where they conflict (an encouraging coach with a grumpy persona is still kind).
  - **template/README.md** "Other things you can ask": add bullets in the file's existing quoted style: `"We finished second this season"`, `"Mark the game on 2026-11-20 as the final"`, `"Hide best partnership" · "Show awards"`, `"Add Sam as an admin"`, `"Give the coach a personality: a grumpy old pro"`. **template/CLAUDE.md:** one bullet under "How the repo works" about `season.yaml` (medal/finish/closed) and `team.yaml → show`.
  - **docs/SETUP.md:** a short "Things you can tell Claude later" list (the same phrases) after "About the team code". **docs/architecture.md:** add `season.yaml` to the data layout line. **CHANGELOG.md:** an `## Unreleased` section listing this plan's user-visible changes in one line each.
- [ ] **Step 4: Run to verify pass** — `pytest tests/test_skill_text.py tests/test_skill_snippets.py tests/test_make_template.py -v` → PASS
- [ ] **Step 5: Commit** — `git add .claude template docs CHANGELOG.md tests/test_skill_text.py && git commit -m "docs: skills and guides for stages, medals, switches, admins and the coach persona"`

---

### Task 13: Whole-branch verification

- [ ] `pytest -q` → all pass; `node --test "viewer/**/*.test.js"` → all pass.
- [ ] `python scripts/validate_ballbyball.py` → `ALL RECONCILE`; `python scripts/leak_check.py` → clean; `python scripts/make_template.py && python scripts/leak_check.py --root dist/team-template` → clean.
- [ ] Rebuild the real example site (`python scripts/build_site.py --out dist/site`) and repeat the Task 10 browser checklist on it.
- [ ] Re-read the spec's Goals 1–6 and tick each against the branch.
