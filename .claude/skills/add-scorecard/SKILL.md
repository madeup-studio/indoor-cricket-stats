---
name: add-scorecard
description: Turn a new action-cricket scorecard photo into a verified game record, then refresh the season stats, PDF stat cards and the AI Coach letter. Use when the user shares or mentions a new scorecard (photo, WhatsApp image, "latest scorecard", "update the stats"), points at a photo in inbox/ or Downloads, or is setting up their team for the first time.
---

# Add a scorecard

One Spawtz action-cricket scorecard photo in → a verified game file, updated stats,
PDFs and a fresh coach letter out. **Accuracy is the whole point: every number must
reconcile.** Claude reads the photo and writes the letter; the scripts do all the maths.

## 0. First run — set up the team

If no folder under `Teams/` has a `team.yaml`:

1. Read the scorecard. The two team names are in the Skins box at the top. Ask the
   user which one is theirs (it must be spelled exactly as printed).
2. The card's `League:` line reads `<arena> - <season> - <league>`, e.g.
   `Example Arena - Spring 2026 - Mens E`.
3. Run `python scripts/new_team.py "<team name as printed>" --arena "<arena>"`.
   Optional: `--badge ABC` (2–4 characters for the report logo); brand colours can be
   changed later in `team.yaml`.

## 1. Find the photo and its season

- New photos are in `inbox/` unless the user says otherwise (e.g. Downloads).
- The season is printed on the card. Find `Teams/<TEAM>/<YYYY-MM-DD>/` whose games
  are that season (check `meta.season` in one of its `data/*.json`). If there is none,
  it's a new season: ask the user for the season's start date (the arena website
  lists it; if they don't know, use this game's date) and run
  `python scripts/new_team.py --season-start <YYYY-MM-DD>`.
- Skip it if that date + opponent is already in `data/`.
- Move the photo into `<season>/scorecards/` (keep its filename).

## 2. Transcribe

Follow `scripts/TRANSCRIBE.md` exactly: enlarge the grid with `crop_scorecard.py`,
header, bottom summary tables first (they're authoritative), then both innings
ball-by-ball with the delivery order (`over_seq`). Write
`<season>/data/<YYYY-MM-DD>.json` (add `-<opponent-slug>` when there are two games
that day). `team` is our name exactly as in `team.yaml`; the `result` fields are
from our side; `meta.arena` + `meta.league` come from the `League:` line.

## 3. Build and verify

```bash
python scripts/build_scorecards.py
python scripts/validate_ballbyball.py      # must end with "ALL RECONCILE"
```

Fix any failure by re-reading the card (re-crop that band larger), never by bending
a total to fit a guess. A genuinely unreadable cell: best-guess it so the over, the
batter's RS and the bowler's RC/Wkts all reconcile (rule in TRANSCRIBE.md). If the
card itself breaks the 6-balls-an-over law, ask the user, then record it in
`meta.ball_count_exceptions`.

## 4. Player names

```bash
python scripts/roster.py --check
```

- If `players.yaml` has no entries yet (first game), run
  `python scripts/roster.py --refresh` to create them.
- Otherwise add each new name to `players.yaml` by hand (this keeps the comments):
  `- as: "<exactly as printed>"  # <team>` with `name: "<display name>"`.
- **Our players:** ask the user whether a new spelling is an existing player (add it
  to that player's `aka:` list) or a new one. Names printed as `X Unknown` had no
  surname; ask what to show.
- **Opponents:** register them; ask only if a name matches someone on another team.
  If both teams field the same printed name in one game, add a marker to the
  opponent's (e.g. `"sam Unknown (K)"`) in the game JSON and say so in `meta.notes`.

## 5. Reports and the coach letter

```bash
python scripts/generate_stats.py
python scripts/generate_pdf_report.py
```

If the PDF step warns about a stale coach letter, use the **ai-coach** skill to write
a fresh one, then re-run `generate_pdf_report.py` until there are no warnings.

## 6. Wrap up

- Add the game to `Teams/<TEAM>/seasons.md` (date, opponent, result, score, skins,
  league, one-line note).
- Tell the user: the result, anything you best-guessed or still need them to
  confirm, and where the PDFs are: `Teams/<TEAM>/<season>/<TEAM>-<season>.pdf`
  (season card) and `Teams/<TEAM>/<TEAM>-all-time.pdf`.
- League table screenshots, fixtures or banter the user sends go into
  `<season>/context/YYYY-MM-DD-<topic>.md`; the coach reads that folder.
