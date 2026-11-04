# Season awards, medals, playoff games, admin switches — and four small hardenings

Design, 2026-11-03. Status: approved by the owner on 2026-11-04. Builds on
[`2026-10-22-action-cricket-app-design.md`](2026-10-22-action-cricket-app-design.md)
(stage 1, shipped as v1.0.0-pre on `main`). Example data only, as always.

## Intent

Give a team's season a shape in the app — awards, a medal, playoff games marked as
such — and let the admin choose which records and features their team sees, without
adding any admin UI, login or backend. Alongside, close four small gaps found in a
review of the stage-1 flow: the setup wizard never asks whether the team wants a
coach at all; a duplicate scorecard is only caught by an instruction to Claude; there
is no written way to add a second admin; the coach has three tones and no room for
flavour.

### Why

- The owner reviewed stage 1 before its first live run and asked for these. The
  principle that drives every choice below is unchanged from stage 1: **chat is the
  admin panel.** The app is a static site behind a cookie gate; every setting is a
  line in `team.yaml` changed by telling Claude, applied on the next publish.
- Teams remember seasons by how they ended (a medal, who was player of the season),
  not only by the numbers. That is the part the app does not yet show.

## Goals

1. Records opens on the current season like every other screen; all-time is one tap
   away.
2. A game can be marked as a playoff game and the app says so.
3. A season can carry a medal (gold, silver, bronze) that the admin states; it shows
   as an icon on that season in the season switcher.
4. The engine works out three awards per finished season — player, batter and bowler
   of the season — from the rankings it already produces, and the app shows them per
   season and as a career tally on the player page.
5. The admin can switch individual records, awards and medals on or off in
   `team.yaml`, by telling Claude.
6. The four hardenings: setup asks "coach: yes or no" before the tone; the validator
   refuses two game files for the same date and opponent, and the skill asks instead
   of silently skipping; the skills explain how to add an admin; the coach gets an
   optional free-text persona.

## Non-goals

- Any settings screen, admin button or input of any kind inside the app. The app
  stays read-only. (Owner's question, answered: the app has no write path, and adding
  one means identity plus a backend, which stage 1 rejected.)
- Showing the league table (log) in the app, or fetching it from the arena's website.
  The log stays what it is today: context for the coach, transcribed from a
  screenshot. The medal is a fact the admin states, not derived from a log.
- A medal tally, career medal count or "medals since …" line. The owner dropped it:
  the icon on the season is enough.
- Team-voted awards. The engine decides from the numbers (owner's decision).
- Custom layouts, dashboards, or per-viewer preferences.
- Changing how a season starts. It still starts when the first card of a new season
  arrives (or the admin says "new season starts on …").

## Anti-goals (a failure even if it works)

- A number on screen that cannot be traced to a reconciled game file. Awards and
  medals must be shown as what they are: awards come from the rankings, medals from
  the admin's statement.
- An award that flips every week. Awards are for finished seasons only.
- Any real team or player identifier in this repo, its tests or its docs.
- A `team.yaml` that a non-programmer cannot read. Switches are plain words with a
  comment each.

## Constraints

- Static viewer (plain HTML/CSS/JS, no build step), Python 3 engine (pyyaml,
  pillow). Design tokens from `viewer/tokens.css`; the lean-pages rule: no prose on
  screens, explanations behind `?` HelpIcons.
- `team.yaml` is the only settings file. Rules constants keep coming from
  `team.yaml → rules`.
- Every game file must still print `ALL RECONCILE` before stats are generated.
- Engine never reads viewer state; viewer reads only the published payload
  (`site/data/<team>.json`).
- Works in a Claude Code cloud session on a phone and on a PC; scripts run on Windows
  and Linux.
- Example team only under `Teams/`; leak check must stay clean.

## Decisions (as decided, with who decided)

### 1. Records defaults to the current season — owner

`viewer/scope.js` `defaultScope` returns the latest season for every route, Records
included. The switcher still offers all-time and is the only affordance; no new
popover (designer's call after review: the top bar has no room on a phone).

### 2. Playoff games — owner asked; shape is the designer's call

- A game file may carry `meta.stage`: one of `"league"`, `"playoff"`, `"semi-final"`,
  `"final"`. Absent means `"league"`. The validator rejects any other value.
- Playoff games **count in the season's stats and records** like any other game
  (designer's call: same team, same season; splitting them would halve small
  samples).
- The viewer shows a small tag — "Playoff", "Semi-final", "Final" — on the game's card
  in the Games list and on the game page header. Nothing else changes.
- How it gets set: in `add-scorecard`, step 2 (Transcribe) adds: if the card's
  league line or the user says playoff / semi / final, set `meta.stage`; otherwise
  leave it out. Never ask unprompted. `TRANSCRIBE.md` documents the field.
- Later: "mark the game on 2026-11-20 as the final" edits the file; re-run the
  pipeline and publish.

### 3. Season medal — owner

- New optional file `Teams/<team>/<season>/season.yaml`:

  ```yaml
  medal: silver          # gold | silver | bronze — how the season ended; leave out for none
  finish: "2nd in Mens E" # optional, free text; see below for where it shows
  closed: true           # optional; a season with a medal counts as closed anyway
  ```

- `finish` is stored for the record and for the coach's context. It shows in one
  place only: as part of that season's heading in the all-time **Awards** block
  (decision 4), e.g. "Spring 2026 · 🥈 2nd in Mens E". With awards switched off it is
  not shown anywhere (designer's call after review: there is no season-level `?` and
  the top bar has no room for one).

- Set through chat: "we finished second this season" → Claude writes `medal: silver`
  (and `finish:` if the user gave detail) into the current season's `season.yaml`,
  then publishes. The `add-scorecard` skill gets a "Season over?" note under "Other
  requests": the mapping 1st → gold, 2nd → silver, 3rd → bronze, league or playoff
  alike; anything else → no medal; record `finish:` and `closed: true` so the season still counts as finished.
- The viewer shows the medal as an icon in front of the season's label in the season
  switcher (`fillScope`): `🥇`, `🥈`, `🥉`. The switcher is a native `<select>`, so
  the icon is part of the option text (designer's call; an SVG icon would need a
  custom popover, which is more than this earns). Nowhere else.
- `build_site.py` passes `medal` and `finish` through on each season entry in the
  payload. `build_site.py` reads each team directory itself (`_load_cfg`), so the
  `season.yaml` loader and the `show` defaults merge are plain functions taking a
  directory, not `paths.py` module constants.

### 4. Season awards — owner: "the engine should know from stats"

- Three awards per season, derived from the season's rankings exactly as
  `report_data.py` already ranks them, with the same qualification (`MIN_GAMES`):
  - **Batter of the season**: first ranked player in the batting ranking (Avg/12).
  - **Bowler of the season**: first ranked bowler in the bowling ranking.
  - **Player of the season**: first ranked all-rounder (average contribution).
  - Ties resolve as the ranking already resolves them (its existing tiebreaks).
    If nobody qualifies, that award is not given.
- **Finished seasons only** (designer's call, owner informed): a season is finished
  when a later season folder exists, or its `season.yaml` has `closed: true` or a
  `medal`. For the current season the rankings already show who is leading.
- Where they show (designer's call):
  - Records screen, scoped to a finished season: an **Awards** block above the team
    records, three cards (title, player name, the ranking figure that won it). A `?`
    popover explains "worked out from this season's rankings; needs at least N games".
  - Records screen, all-time: an **Awards** block listing each finished season's
    three winners, newest first, each season headed by its label plus medal icon and
    `finish` text when present.
  - Player page: a tally line under the name when the player has any, e.g.
    "Player of the season ×1 · Bowler of the season ×2".
- Payload: each season entry gets `awards: {player, batter, bowler}` (each
  `{name, value}` or `null`); the player index gets per-player award counts.
- Off by default (owner: "let the admin decide"). See switches.

### 5. Admin switches — owner asked; keys are the designer's call

A `show:` block in `team.yaml`, written by `new_team.py` with every key present and a
comment, so the admin (or Claude) can read it:

```yaml
show:                       # what the app shows; false hides it (stats still computed)
  awards: false             # player / batter / bowler of the season (finished seasons)
  medals: true              # the season's medal icon in the season menu
  stage_tags: true          # "Playoff" / "Final" tags on games
  streaks: true             # longest winning / losing runs
  partnerships: true        # best partnership record
  hattricks: true           # the hat-trick records (there is no player-page count)
  records:                  # individual record cards; a key set to false hides that card
    high_total: true
    low_total: true
    biggest_win: true
    heaviest_loss: true
    best_skin: true
    most_wkts_game: true
    fewest_extras_game: true
    best_contribution: true
    most_runs_game: true
    best_econ: true
    most_runouts_created: true
```

- **The engine keeps computing everything.** Switches only decide what the viewer
  renders. `build_site.py` merges the block over defaults (missing key → default) and
  passes it through as `team.show`. The viewer reads `team.show` and skips hidden
  rows, blocks and tags. Reason: no stats drift between switched states, and switching
  back on needs nothing but a publish.
- Changing: "hide best partnership", "show awards", "turn off streaks" → Claude edits
  `team.yaml → show`, publishes. Documented in `template/CLAUDE.md` ("Other things you
  can ask") and in `add-scorecard` "Other requests".
- A `show:` block missing entirely (older teams) behaves as all defaults.

### 6. Four hardenings — designer recommended, owner approved

- **Setup asks about the coach.** `setup` step 6 asks "Do you want the AI coach's
  letter after each game? (yes / no)" before the tone; `no` → `coach.enabled: false`
  and no tone question. `new_team.py` gains `--no-coach`.
- **Duplicate game guard.** `validate_ballbyball.py` fails (non-zero, clear message)
  when two game files in one season share `date` and `opponent`. `add-scorecard`
  step 1 changes from "skip it" to: "If that date + opponent already exists, say so
  and ask: re-check the existing game against this photo, or leave it? Never write a
  second file." Re-checking means re-transcribing into the **same** file.
- **Add an admin.** `add-scorecard` "Other requests" and `template/README.md` gain
  "Add Sam as an admin": (1) on GitHub, repo → Settings → Collaborators → Add people
  (the real permission), (2) Sam connects Claude Code to the repo, (3) add Sam's git
  email to `team.yaml → admins` (the courtesy guard). Note that in a cloud session the
  git email may not identify the person; the guard is best effort, GitHub access is
  the permission.
- **Coach persona.** `team.yaml → coach.persona`: optional one line of free text
  ("sounds like a grumpy old pro who played in the 90s"). The `ai-coach` skill applies
  it on top of the tone; the tone's rules still win where they conflict (an
  encouraging coach with a grumpy persona is still kind). Setup does not ask for it;
  the admin adds it later ("give the coach a personality: …").

## Interfaces touched

| Piece | Change |
|---|---|
| `scripts/templates/game-template.json`, `TRANSCRIBE.md` | `meta.stage` (optional) |
| `scripts/validate_ballbyball.py` | reject bad `stage`; fail on duplicate date+opponent |
| `scripts/build_scorecards.py` | emit `stage` in the scorecard frontmatter (stats are built from the frontmatter, not the JSON) |
| `scripts/new_team.py` | write `show:` block and `coach.persona` comment; `--no-coach` |
| `scripts/paths.py` | load `season.yaml` per season (`medal`, `finish`, `closed`); `TEAM_SHOW` defaults merge |
| `scripts/report_data.py` | per-season awards from existing rankings; finished-season rule |
| `scripts/build_site.py` | pass `show`, season `medal`/`finish`/`awards`, player award counts, game `stage` |
| `viewer/scope.js` | Records defaults to latest season |
| `viewer/model.js` (new, pure, no DOM) | `isShown(show, key)`, `seasonLabel(season)` with medal icon, `stageLabel(game)`, `awardTally(player)`, awards-block rows; unit-tested in Node like `scope.js` (`app.js` touches `document` at import) |
| `viewer/app.js` | medal icon in `fillScope` via `model.js` |
| `viewer/screens/records.js` | awards blocks; honour switches |
| `viewer/screens/games.js` | stage tag on card and page |
| `viewer/screens/players.js` | award tally line |
| `.claude/skills/setup/SKILL.md` | coach yes/no before tone |
| `.claude/skills/add-scorecard/SKILL.md` | duplicate ask; stage; new **"Other requests"** section (season over → medal, switches, add an admin, coach persona) |
| `.claude/skills/ai-coach/SKILL.md` | persona |
| `template/README.md` ("Other things you can ask"), `template/CLAUDE.md`, `docs/SETUP.md` | the new phrases |
| `Teams/example-team/` | see "Example team" below |

### Example team (designer's call after review)

Awards need a finished season with at least `MIN_GAMES` (3) ranked games; the example
has one. Extend it by **cloning** the existing reconciled game (as
`tests/conftest.py` already does) with new dates and opponent names from the same
`Our P*` / `Opp P*` vocabulary, never new identifiers:

- Spring 2026 (`2026-09-01/`) keeps its game and its committed coach letter and gains
  two cloned games dated after 2026-10-07, without letters (the app shows "No coach
  letter for this game" for them, which is what a real team sees before Claude writes
  one). Its `season.yaml` gets `medal: silver`, `finish: "2nd in Mens E"`.
- A new later season folder (e.g. `2027-01-12/`, label from the cloned card) holds
  one cloned game, so Spring 2026 counts as finished and the app opens on a season
  with a single game, like a real team's first week.
- Every clone must print `ALL RECONCILE`; the leak check stays clean. Pinned test
  values that change because the example grew are updated with the change.

## Tests (what must exist)

- `tests/`: `stage` validation (good, bad, absent); duplicate date+opponent fails and
  the message names both files; `season.yaml` loading and the finished-season rule
  (later folder / `closed` / `medal`); awards equal the first ranked entry of each
  ranking, none when nobody qualifies; `show` defaults merge; payload carries `show`,
  `medal`, `awards`, `stage`, award counts; `new_team.py --no-coach`.
- `tests/`: `build_scorecards.py` carries `stage` into the frontmatter and
  `load_matches` reads it back.
- `viewer/tests/` (Node, no DOM, against `model.js` and `scope.js`):
  `defaultScope("records")` is the latest season; season label carries the medal
  icon; a record key switched off is not shown; awards rows exist only for finished
  seasons and only when `show.awards`; stage label for each value and for absent.
- Leak check clean; `pytest -q` and `node --test "viewer/**/*.test.js"` green.

## Left to the builder

- Exact wording of the awards `?` popover and the tags; CSS for the stage tag and
  awards cards (use existing card and label classes; tokens only).
- Whether the all-time Awards block collapses past some number of seasons.
- Order of the "Other requests" entries in the skills.
- How `paths.py` exposes season metadata (a dict per season dir is fine).

## Out of scope, noted for later

- A `viewer:` block to hide or reorder whole tabs: wait until two or three teams ask.
- Showing the league table in the app, or reading it from the arena site.
- Multiple awards per category on ties, or team-voted awards.
