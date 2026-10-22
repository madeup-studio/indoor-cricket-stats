---
name: add-scorecard
description: Turn a new action-cricket scorecard photo into a verified game record, then refresh the stats, write the AI Coach's letter for the game and publish the team's app. Use when the user shares or mentions a new scorecard (photo, WhatsApp image, "new scorecard", "latest scorecard", "update the stats"), a league table or a note for the coach, or is setting up their team for the first time.
---

# Add a scorecard

> **Paths:** run scripts as `python $ENGINE/scripts/<script>.py` from the repo root, where
> `$ENGINE` is `engine` in a team repo and `.` in the engine repo itself.

One Spawtz scorecard photo in → a verified game file, updated stats, the coach's
letter and a published app out. **Accuracy is the whole point: every number must
reconcile.** You read the photo and write the letter; the scripts do all the maths.
The user is usually on a phone: keep questions few, short and in plain words.

## 0. Before you start

- **No team yet** (no `Teams/*/team.yaml`): run the `setup` skill, or for just the
  team: read the card (the two team names are in the Skins box), ask which is theirs
  (spelled exactly as printed) and run
  `python $ENGINE/scripts/new_team.py "<name as printed>" --arena "<arena>" --league "<league>"`.
  The card's `League:` line reads `<arena> - <season> - <league>`.
- **Admins:** if the team's `team.yaml` lists `admins:` and `git config user.email` is
  not one of them, don't touch that team — tell the user and stop.

## 1. Find the photo and its season

- The photo is attached in the chat, or in `inbox/` (or wherever the user says).
  Save it into `<season>/scorecards/` (keep its filename). If the attachment is not
  available as a file, transcribe from the image you see, say so, and set
  `meta.source_image` to null.
- The season is printed on the card. Find `Teams/<TEAM>/<YYYY-MM-DD>/` whose games
  are that season (`meta.season` in its `data/*.json`). None → a new season: ask for
  its start date (the arena's website lists it; else use this game's date) and run
  `python $ENGINE/scripts/new_team.py --season-start <YYYY-MM-DD>`.
- Skip it if that date + opponent is already in `data/`.

## 2. Transcribe

Follow `$ENGINE/scripts/TRANSCRIBE.md` exactly: enlarge the grid with `crop_scorecard.py`,
header, bottom summary tables first (they're authoritative), then both innings
ball-by-ball with the delivery order (`over_seq`). Write
`<season>/data/<YYYY-MM-DD>.json` (add `-<opponent-slug>` when there are two games
that day). `team` is our name exactly as in `team.yaml`; the `result` fields are
from our side; `meta.arena` + `meta.league` come from the `League:` line.

## 3. Build and verify

```bash
python $ENGINE/scripts/build_scorecards.py
python $ENGINE/scripts/validate_ballbyball.py      # must end with "ALL RECONCILE"
```

Fix any failure by re-reading the card (re-crop that band larger), never by bending
a total to fit a guess. A genuinely unreadable cell: best-guess it so the over, the
batter's RS and the bowler's RC/Wkts all reconcile (rule in TRANSCRIBE.md). If the
card itself breaks the ball-count law, ask the user, then record it in
`meta.ball_count_exceptions`. **A game that doesn't reconcile is never published.**

**3b. Rules snapshot.** If the new game file has no `meta.rules`, add the team's
rules (`team.yaml` → `rules`, every key written out: the preset's values plus any
overrides) so the game keeps the rules it was scored under.

## 4. Player names

```bash
python $ENGINE/scripts/roster.py --check
```

- First game (`players.yaml` empty): `python $ENGINE/scripts/roster.py --refresh`.
- Otherwise add each new name to `players.yaml` by hand (keeps the comments):
  `- as: "<exactly as printed>"  # <team>` with `name: "<display name>"`.
- **Our players:** ask whether a new spelling is an existing player (add it to that
  player's `aka:`) or someone new. `X Unknown` = no surname printed; ask what to show.
- **Opponents:** register them; ask only if a name matches someone on another team.

## 5. Stats

```bash
python $ENGINE/scripts/generate_stats.py
```

**5b. Ask for the standings and notes** — once, in one message:
"Got a screenshot of the standings? Attach it and I'll add it for the coach — or
say skip. Anything else from the game worth passing on (a great catch, some banter)?"
- A table → transcribe it faithfully as a markdown table into
  `<season>/context/<date>-standings.md` (date = the game's date).
- A note → `<season>/context/<date>-note.md`, in the user's words.
- "skip" → carry on. Standings never feed the stats.

## 6. The coach's letter

If `team.yaml` → `coach.enabled` is not false, use the **ai-coach** skill:
`python $ENGINE/scripts/coach.py --status` lists the new game; write its letter.
Only if `team.yaml` → `pdf` is true: `python $ENGINE/scripts/generate_pdf_report.py`
(no `!!` warnings).

## 7. Wrap up and publish

- Add the game to `Teams/<TEAM>/seasons.md` (date, opponent, result, score, skins,
  league, one-line note).
- Publish: `python $ENGINE/scripts/publish.py "Game <date> vs <opponent>"`.
- Tell the user in a few lines: the result, anything you best-guessed or still need
  them to confirm, and that the app updates within a minute (or, if the script says
  there is no remote yet, that `/setup` connects the app). Mention PDFs only when
  `pdf` is on.
