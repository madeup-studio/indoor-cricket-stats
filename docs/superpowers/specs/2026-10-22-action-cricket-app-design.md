# Action Cricket Stats — phone-first app, match-night upload, open-source engine

Design, 2026-10-21/22. Status: approved by the owner on 2026-10-22 (stage 1).
Copied from the owner's private hub; identifiers sanitised. This is the spec the
plans in `../plans/` implement.

## Intent

Turn a team's action-cricket scorecard photos into a stats app that is readable on
a phone, is updated by the team admin **from the phone on match night** with no PC
involved, and is private to the team. Publish the engine as **Made-Up Studio's first
open-source release** so any other team can run its own copy.

### Why

- The current output is an A4 PDF stat card. On a phone the type is too small and
  there is no way to drill in (menu → ranking → player → game).
- Today a new scorecard is processed by Claude Code on the admin's PC, with the
  admin answering questions (smudged letters, unknown names). The admin wants to
  upload at the arena and have the stats out before the drive home; the PC may be
  off.
- A friendly team already asked to use the pipeline. Other teams will too. The
  owner does **not** want to run a hosted service or an app-store app.

### What exists (reuse, don't rebuild)

The owner's existing private pipeline (Python 3, pyyaml, pillow), team-neutral
since 2026-10-20, which this repo starts from:

- `Teams/<Team>/<season-start>/data/<date>.json` — one file per game, ball-by-ball,
  **the source of truth**. `team.yaml`, `players.yaml`, `coach_notes.yaml`,
  `seasons.md`, `photos/`, `<season>/context/`.
- `scripts/`: `crop_scorecard.py`, `build_scorecards.py`, `validate_ballbyball.py`
  (must print `ALL RECONCILE`), `roster.py`, `stats_core.py`, `report_data.py`
  (`build()` returns the full stats object the PDF renders from), `generate_stats.py`,
  `generate_pdf_report.py`, `new_team.py`, `make_kit.py`, `paths.py`,
  `TRANSCRIBE.md`, `templates/game-template.json` (anonymised example game).
- Skills in `.claude/skills/`: `add-scorecard` (photo → verified game → reports) and
  `ai-coach` (writes the "Letter from the AI Coach", fingerprinted against the stats
  so a stale letter is detected).
- `kit/README.md`, `kit/CLAUDE.md` — docs written for another team.

## Goals

1. **Viewer**: a phone-first web app. Bottom menu — Coach · Batting · Bowling ·
   All-round · Games · Players; season switcher (each season + All-time); tap a
   ranking row → player page (season line, game-by-game, dismissal/shot breakdown,
   coach note); tap a game → skins, both sides' summaries, who starred. Big type,
   one-thumb navigation, "Add to Home Screen" icon (PWA manifest). No app store.
2. **Match-night upload**: an admin opens the app, takes/chooses the scorecard
   photo, uploads. A cloud job runs the existing pipeline unattended and publishes
   the new version. Target: visible in the app within ~10 minutes of upload.
   The admin's PC is never part of the chain.
3. **Flag, don't block**: a game that reconciles is published even if a player
   name is unconfirmed; the name is flagged. The app shows Claude's question in its
   own words with its best guess and a free-text reply; the admin's answer feeds
   the next run, which applies it or asks again. A game that does **not** reconcile
   is never published; the app shows "needs attention" with Claude's notes.
4. **Private per team**: each team's data lives in its own private git repo and is
   served on its own site behind an email allow-list. Nothing of one team is
   visible to another, or to the engine's author.
5. **Open-source engine** under the Made-Up Studio GitHub organisation, MIT
   licence, with a team template so a new team is running in ~20 minutes.
6. **Reuse**: scripts, validator, both skills and the data format stay as they are
   wherever possible. The PDF stat card remains available (optional, off in the
   cloud job by default).
7. **Team, player and rules management in the app** (admin only): create a team
   and edit its settings (name as printed on the cards, badge, colours, arena,
   league); choose a **rules preset** and adjust its scoring constants; switch the
   **AI coach** on/off and choose its tone; manage **players** — confirm a name,
   rename, merge a second printed spelling into an existing player, add a photo,
   or create a player before their first game. No PC needed for any of it.
8. **Several teams in one repo/site** (decided 2026-10-21): a friendly team can be
   added as a second team on the same site, with its own data folder, admin pages
   and rankings, and a team picker in the viewer. Reason: some people play for, or
   manage, more than one team.
9. **Seasons and all-time, with the right default per section**: every stat is
   available per season and all-time. *Stats* (rankings, averages, form, the
   coach letter) default to the **current season**; *records* (team and
   individual bests, best partnerships, hat-tricks, streaks) default to
   **all-time**; a player page shows the season line first and the career line
   under it. One switcher changes the scope anywhere.
10. **A coach letter per game, kept for good** (2026-10-22): the AI Coach writes
    one letter after every game (the shape of today's page 1: the game, the
    standings, homework, batting, bowling, a word to each player who played).
    The Coach tab shows the latest; every game page shows the letter written
    after *that* game, exactly as it was. Letters are never rewritten when
    later games arrive. The coach can be switched off per team.
11. **Looks like a product, not a report**: cool, dynamic, minimalist. The same
    stats as the PDF, broken into many small screens — one idea per screen, big
    numbers, small labels, lots of air, a bottom menu, smooth transitions, dark
    mode. Built on the Made-Up Studio design tokens with a phone-sized type
    scale (details under Viewer).

## Non-goals (not now)

- A hosted multi-tenant service where teams sign up on one site.
- Native/app-store apps. Live ball-by-ball scoring at the arena.
- Scorecard formats other than Spawtz. (Spawtz is the scoring/centre-management
  software used by many indoor sports centres in South Africa, Australia, New
  Zealand and the UK, so this still covers a lot of arenas.)
- **Outdoor cricket.** It is a different game, not a setting: no pairs or skins,
  a dismissed batter leaves, eleven a side, overs per innings vary, partnerships
  fall by wicket, and the scorecards and stats look nothing like indoor ones. The
  transcription rules, data model and every ranking here are indoor-specific, and
  outdoor is already well served by existing apps. The `game_type` field exists so
  the door is not welded shut, but only `indoor` is implemented.
- One person record shared across teams in the same repo (a player who turns out
  for two teams). Rosters stay per team in v1; a cross-team "career" view is a
  possible later addition.
- User accounts, roles or a database beyond what the email gate and git give us.
- A live chat with Claude inside the app (the review is one question/answer round
  per run; live chat is a possible later addition).
- Porting the Python stats engine to JavaScript.

## Anti-goals (failure even if it works)

- Any team name, player name, photo or coach letter from a real team in the public
  repo or **its git history**.
- A flow that needs the admin's PC, or the engine author's PC, for another team.
- The engine author becoming the operator for other teams (their secrets, their
  data, their costs on the author's accounts).
- A viewer that is the PDF in a browser. It must be navigable with large type.
- A job that silently publishes numbers that do not reconcile.
- Breaking a team's Thursday night with an engine change they did not opt into.

## Constraints

- Weekend/after-hours project; prefer the fewest moving parts and free tiers.
- Free tiers assumed: Cloudflare Pages (static hosting), Cloudflare Access
  (email one-time-code login, ≤50 users per team, Zero Trust free plan — expect a
  card on file, no charge), GitHub private repos with Actions minutes, Cloudflare
  R2 or direct git commits for photos (< 1 MB each).
- Claude access is per team: either a Claude subscription token (`claude
  setup-token`) or an Anthropic API key, stored as a secret in the team repo. The
  docs must state the cost plainly (subscription usage, or roughly a few rand to a
  few tens of rand per game on an API key).
- Development machine is Windows; the cloud job runs Linux. Scripts must work on
  both (they already do).
- Viewer is plain HTML/CSS/JS with no build tooling (a non-developer must be able
  to deploy it by pointing Cloudflare at a folder). Small CDN libraries are fine.
- **Clean slate.** The owner starts the new season in the new app with no team
  data at all — to test it end to end and to begin fresh. The data format is the
  same as the hub's, so historic seasons can be imported later by copying a team
  folder in (see "Historic data"). Until then the hub's pipeline keeps working
  as it is.
- The Made-Up Studio stack (React/Vite, Firebase, madeup-auth, token economy)
  does **not** apply: this is an open-source, self-hosted tool with no accounts
  of its own. The studio's design tokens and "lean pages" rule do apply.

## Decisions already made (by the owner)

- Brand/home: **Made-Up Studio**, first open-source release.
- Hosting: Cloudflare Pages + Cloudflare Access email gate per team.
- Upload from the phone on match night; processing unattended in the cloud.
- Unconfirmed names: publish and flag; Claude asks, admin answers in-app, admin
  decides. (Exposed as a per-team setting anyway; default = publish-and-flag.)
- Public engine + private team repos; a template for new teams; "no support
  promised" stated in the README.
- A coach letter per game, kept historically (2026-10-22); coach on/off per team.
- Start the new season on a clean slate in the new app; import history later.
- Look: cool, dynamic, minimalist; same stats, many small pages, phone-first.
- Project home: `C:\VSCodeProjects-MDP\madeup-studio\indoor-cricket-stats\`
  (its own git repo, like every studio product), public GitHub repo
  `indoor-cricket-stats` under the Made-Up Studio account.

## Decisions made in this design (my calls — change them if wrong)

- Licence **MIT**.
- Compute for the job: **GitHub Actions** in the team's own repo, calling a
  **reusable workflow** published by the engine repo and pinned to a major tag
  (`@v1`). Rationale: free, runs Python unchanged, no server to keep alive, each
  team's secrets stay in their repo.
- The team repo is the deploy source: the job commits the built `site/` folder
  (viewer + `data/*.json` + `status.json` + `review.json`) and Cloudflare Pages
  deploys it with **no build step**.
- Photos uploaded from the app are committed straight into the team repo
  (`Teams/<Team>/inbox/`) by a small Pages Function using a fine-grained GitHub
  token; the push triggers the job. (R2 is the fallback if the GitHub contents API
  proves awkward; builder's choice.)
- The viewer reads one JSON per team produced from `report_data.build()` plus the
  coach letter — the same object the PDF renders from. No database.
- Job state is committed JSON, not a service: `site/status.json` (last run:
  state, started/finished, photo, messages) and `site/review.json` (open
  questions). The app polls them.
- Repos: `indoor-cricket-stats` (engine, public, under the Made-Up Studio
  GitHub account), `indoor-cricket-stats-team` (public template; tiny), and one
  private repo per team (the owner's first, created from the template).
- **Where the engine sits in a team repo:** in `engine/`, gitignored, fetched by
  `bootstrap.py` at the version pinned in `engine.lock`. `paths.py` finds `Teams/`
  from the repo root it is run in (falling back to its own parent as today). The
  cloud job does the same fetch, so the PC fallback is simply "open the team repo
  in Claude Code" — the team repo's `CLAUDE.md` tells Claude to bootstrap first.
- **Uploads are not only scorecards.** The upload page has a kind: *scorecard* /
  *league table* / *note*. A league-table screenshot is transcribed by the job into
  `<season>/context/<date>-standings.md` (unattended, no review round — it is
  context, not stats); a note becomes `<season>/context/<date>-note.md`. Without
  this the coach letter's "Where we stand" section dies within weeks of leaving
  the PC behind.
- **Versioning:** the template pins the moving major tag `@v1`. The engine's release
  checklist runs the smoke test against the example team before the tag moves; a
  team that wants to freeze pins an exact tag (documented in SETUP).
- **Rules and coach settings live in `team.yaml`** and every game file snapshots
  the rules it was scored under (`meta.rules`), so a team that changes arena or
  the arena changing its rules never rewrites history.

## Resolved: several teams in one repo/site — yes (owner, 2026-10-21)

It costs a team dimension through the job (loop over teams), the upload/answer
functions, `status.json`/`review.json` and the admin pages; every admin of the
repo administers every team in it; and the repo owner's Claude access pays for
the other team's games. The template path stays for teams the owner does not
want on his own accounts.

**An admin per team.** `team.yaml` lists `admins:` (email addresses). What that
enforces depends on the stage:

- *Stage 1 (chat):* an admin works in their **own** Claude Code session on the
  shared repo, so their games run on their own subscription, not the owner's.
  They need a free GitHub login and collaborator access to the repo. GitHub
  cannot restrict a collaborator to one folder on a free private repo (path
  rules need GitHub Pro, ~$4/month, which the owner may add), so a second admin
  is trusted like a co-editor of a shared spreadsheet; git history records who
  changed what and every change is reversible. Fine for a friend's team; a
  stranger's team runs its own copy instead. Every admin's session must respect
  `admins:` by convention: the skills refuse to touch a team the current user
  is not listed for (a guard, not a security boundary).
- *Stage 2 (button):* enforced. Admin pages are per team (`/admin/<team>/…`)
  behind an Access policy for that team's `admins:`; the upload/answer/admin
  functions check the signed-in email against the team's list before committing
  anything; team admins never need GitHub access at all. Each team may store
  its own Claude token as a secret (`CLAUDE_TOKEN_<TEAM>`), which the job picks
  by team, so nobody pays for another team's games.

**How viewers get in — a per-site choice made in the setup wizard** (2026-10-22):

- `pin` (**default**): one team code, posted in the team's WhatsApp group. The
  site's own small middleware function shows a code page, and on the right code
  sets a signed cookie that keeps that phone in for 6 months; the admin changes
  the code when someone leaves and everyone re-enters it once. No email
  addresses needed, no Cloudflare Zero Trust step (so no card on file), one
  fewer account step in the wizard. Same trust model as the WhatsApp group
  itself: anyone given the code gets in. Codes are 6+ characters and the
  function slows repeated wrong attempts.
- `email`: Cloudflare Access with an email allow-list and one-time codes by
  email (codes cannot be sent by SMS or WhatsApp). Per-person control and
  instant removal; costs collecting everyone's email once and a code per device
  per month. The right choice for a team that wants to know who is looking.
- `none`: an unlisted link. Zero friction, no protection beyond the link.

Stage 2's admin pages and functions need to know *who* is acting, so admins
always sign in by email (Access) regardless of the viewer gate; stage 1 has no
admin pages, so `pin` needs no Access at all.

Viewers are per site, not per team: everyone who gets past the gate sees every
team on it. A team that wants its own viewer list gets the same `site/` deployed as a
second Cloudflare project with its own gate and a default team — possible later,
not v1.

**People who play for more than one team.** Rosters stay per team (a printed
name on a scorecard belongs to a team's `players.yaml`). To recognise one person
across teams, a roster entry may carry `person: <slug>` and a repo-level
`people.yaml` lists each person once (display name, photo). v1 uses it for "also
plays for …" on the player page and for sharing one photo; a combined career
view across teams is the natural v1.1 once the link exists. Opponent names are
never linked.

## Delivery: two stages on the same foundation

Everything above the delivery layer is fixed: data format, rules, coach settings,
multi-team, seasons/records, the viewer file, the engine repo and the template.
The viewer is hosted on **Cloudflare Pages behind Cloudflare Access in both
stages**, deployed automatically from the team repo on every push.

Platform facts checked on 2026-10-21 (official Claude Code docs; sources in the
conversation log):

- The Claude app's Code tab (iOS/Android) accepts a photo in the prompt; cloud
  sessions run on private GitHub repos and load the repo's `.claude/skills/`.
  → the chat flow from the arena works without a PC.
- Claude Code cloud sessions (and the GitHub Action by default) **cannot publish
  claude.ai artifacts** — only the CLI/desktop app can. → hosting the viewer as
  an artifact would put the PC back in the chain; dropped. Cloudflare it is.
- A public-link artifact can be viewed without a Claude account, and email
  invites exist — noted for completeness; not used.
- A Pro/Max subscription can authenticate Claude Code in GitHub Actions with a
  one-year token from `claude setup-token` (`claude_code_oauth_token`). The docs
  recommend an API key only for secrets shared across an organisation, since the
  token is tied to one person's subscription. → fine for a team's own repo.

- **Stage 1 — the chat.** The admin opens the team repo in a Claude Code cloud
  session from the phone, attaches the photo, says "new scorecard", answers the
  skill's one or two questions in chat; the session commits the game, stats,
  letter and the built `site/`; Cloudflare deploys it within a minute. **After
  the game reconciles and before the coach letter, the skill asks once for the
  league table** ("Got a screenshot of the standings? Attach it and I'll add it
  for the coach — or say skip"), and in the same breath for any note or banter
  worth passing on. A table is transcribed into `<season>/context/<date>-standings.md`
  and the letter's "Where we stand" uses it; a skip just means the letter drops
  that section (existing rule). Standings never feed the stats. No
  Actions job, no upload/answer/admin functions or pages — admin edits (team
  settings, players, seasons) are also done by telling Claude. Other teams:
  template copy, their own Claude subscription, their own Cloudflare project.
  Build: rules/coach settings, `build_site.py`, the viewer, the skills' "publish"
  step, the template and docs.
- **Stage 2 — the button.** Adds the unattended mode, the reusable Actions
  workflow, `status.json`/`review.json`, the upload/answer/admin functions and
  pages. Nothing from stage 1 is thrown away; stage 1 remains the fallback.

Stage 2 is built only if the chat flow proves annoying in practice, or when a
team wants to capture without a Claude subscription for the admin.

## Architecture

```
phone (admin) ──upload──▶ team site /api/upload  (Pages Function, Access-gated)
                                 │  commits photo to Teams/<Team>/inbox/
                                 ▼
                     team repo (private, GitHub) ──push──▶ GitHub Actions job
                                 ▲                         (reusable workflow from
                                 │ commits game JSON,       the public engine @v1)
                                 │ players/notes, site/     • Claude Code, headless
                                 │                          • add-scorecard (unattended)
                                 │                          • validate → stats → data.json
                                 │                          • ai-coach letter
                                 │                          • status.json / review.json
                                 ▼
                   Cloudflare Pages (deploys site/ on push) ◀── team + admin on phones
                   behind Cloudflare Access (email allow-list; admins on /admin*, /api/*)
```

### Team repo layout (private; created from the template)

```
Teams/<Team>/                 exactly as today (team.yaml, players.yaml, coach_notes.yaml,
                              seasons.md, photos/, <season-start>/{data,scorecards,stats,context}/)
Teams/<Team>/inbox/           photos uploaded from the app, awaiting processing
site/                         built output deployed by Cloudflare Pages (committed by the job)
  index.html, app.js, app.css, manifest.webmanifest, icons/
  data/<team-slug>.json       stats + coach letters (from report_data.build())
  status.json, review.json
  functions/api/upload.js     Pages Function: accept photo, commit to inbox/
  functions/api/answer.js     Pages Function: accept review answers, commit answers
.github/workflows/stats.yml   ~10 lines: on push to Teams/**/inbox/** → call
                              madeup-studio/indoor-cricket-stats/.github/workflows/process.yml@v1
README.md                     the team's own notes (from the template)
```

Cloudflare Access itself is configured in the Cloudflare dashboard, not in the repo.

`team.yaml` gains (all editable from the admin pages):

```yaml
league: "Mens E"              # current league at the arena (informational)
publish_unconfirmed: true     # publish a reconciled game even if a name is unconfirmed (flagged)
pdf: false                    # also build the PDF stat cards in the cloud job

game_type: indoor             # the only implemented type (see non-goals)
rules:
  preset: indoor-sa           # starting point; any value below overrides the preset
  wicket_runs: -5             # a dismissal's run penalty (some arenas use -3)
  extra_runs: 2               # base value of a wide / no-ball (plus any runs scored off it)
  balls_per_over: 6
  extra_ball_last_over: true  # the optional 7th ball in a skin's last over
  skins: 4
  overs_per_pair: 4
  players_per_side: 8

coach:
  enabled: true               # false = no Coach tab, no letter
  tone: banter                # banter | encouraging | serious
  language: en                # the letter's language (e.g. af); optional
```

The engine reads `rules` wherever a constant is literal today (validator, stats,
contribution, the transcription guide's worked numbers); the shipped defaults are
exactly today's behaviour, so existing data is unaffected. Presets are a small
table in the engine (`indoor-sa` for now; others can be added by pull request).

Coach tones are voice rules in the `ai-coach` skill: **banter** is today's voice;
**encouraging** leads with praise, keeps the humour gentle and the homework
concrete; **serious** reads like a match report — numbers, trends, homework, no
jokes. The page-budget rule applies only when `pdf` is on.

### Coach letters: one per game

`coach_notes.yaml` holds a list of letters keyed by game (the date, plus the
opponent slug when two games fall on one day):

```yaml
letters:
  - game: "2026-10-15"
    fp: "…"                   # fingerprint of the stats up to and including this game
    sections: [{title, html}, …]
    players: [{name, note}, …]
```

- The `ai-coach` skill writes a letter for each new game, in date order, and
  never rewrites an earlier one. The fingerprint covers the games up to and
  including that game, so later games cannot make an old letter stale.
- The viewer's Coach tab shows the latest letter; a game page shows its own
  letter, or "no letter for this game" (e.g. imported history).
- A season's PDF card, if built, uses the latest letter of that season.
- Today's one-letter-per-season file converts on import: each season letter
  becomes the letter of that season's last game.

### The job (reusable workflow `process.yml`)

1. Check out the team repo; fetch the engine at the pinned version (`scripts/`,
   `.claude/skills/`, `viewer/`); install Python deps.
2. Install Claude Code; authenticate from the team's secret (`CLAUDE_CODE_OAUTH_TOKEN`
   or `ANTHROPIC_API_KEY`).
3. For each item in `inbox/` (oldest first), by kind: a **scorecard** photo → the
   `add-scorecard` skill in **unattended mode** (see below) via `claude -p`; a
   **league table** photo → a small unattended Claude task that transcribes it to
   `<season>/context/<date>-standings.md`; a **note** → written to `context/` as
   is; an **admin edit** (team/player/season change) → applied to the YAML and
   folders. Then `build_scorecards.py`, `validate_ballbyball.py`, `roster.py
   --check`, `generate_stats.py`, the `ai-coach` skill (if `coach.enabled`),
   `build_site.py` (new: viewer + `data/*.json`).
4. Outcomes:
   - reconciles, no flags → commit game, stats, letter, site; move photo to
     `<season>/scorecards/`; `status.json: published`.
   - reconciles, flags (names, uncertain cells, card anomalies) → same, plus the
     questions in `review.json`; `status.json: published-with-questions`.
   - does not reconcile, or Claude cannot read the card → commit nothing to
     `data/`; leave the photo in `inbox/`; `status.json: needs-attention` with
     Claude's notes; `review.json` holds Claude's questions.
5. On a push that contains review answers: re-run the affected game with the
   answers applied (names → `players.yaml`; cells → the game JSON; anomalies →
   `meta.ball_count_exceptions`/`meta.notes`), then steps 3–4 again.
6. If the job itself fails (tooling, auth), `status.json: failed` with the log tail
   so the admin sees it in the app rather than in GitHub.

### Unattended mode for the skills

`add-scorecard` keeps its interactive behaviour for Claude Code on a PC and gains an
unattended mode (triggered by an env var or flag the workflow sets):

- Never ask a question in chat. Where the skill would ask (which team is ours on
  first run, new season start date, ambiguous/unknown names, card anomalies,
  unreadable cells that affect totals) it makes the documented best guess where a
  safe one exists (names: register the printed spelling; season: this game's date;
  cells: the best-guess rule) and writes a **question** to `review.json`:
  `{id, kind: name|cell|anomaly|season|team, question, suggested_answer, options[],
  context}` — plain language, as the coach would ask it, with Claude's own best
  guess and why. Where no safe guess exists (team identity on first run, a total
  that will not reconcile) it stops and marks the game `needs-attention`.
- `ai-coach` already runs from data alone; in unattended mode it must never
  mention bookkeeping (already a rule) and must not fail the job if the letter
  does not fit the page budget (the page budget is a PDF concern; the viewer has
  no page).

### Review in the app

`/admin` (Access policy: admins only) shows `status.json` and the open questions
from `review.json`, each with Claude's suggested answer as a one-tap option plus a
free-text box. Submitting posts to `/api/answer`, which commits
`Teams/<Team>/inbox/answers-<id>.json`; the push re-triggers the job. Answered
questions disappear from `review.json` on the next successful run.

### Team and player management in the app

All admin edits use the same mechanism as uploads and answers: a Pages Function
commits a small change to the team repo, the job regenerates, Cloudflare deploys.
There is no second store.

- **Teams** (`/admin/teams`): create a team — name exactly as printed on the
  cards, badge, colours, arena, league, rules preset (with the constants shown
  and editable), coach settings. Creating commits a `team.yaml`; the job runs the
  equivalent of `new_team.py` to lay out the folders. Editing commits the changed
  `team.yaml`. The first-run setup of a fresh repo is this same form, so the
  "which team is yours" question never needs to go through `review.json`.
- **Players** (`/admin/players`): the roster from `players.yaml`, grouped into
  *to confirm* (printed spellings with no confirmed name — the same items the
  review questions raise, so they can be answered here too) and *confirmed*. Per
  player: rename (display name), **merge** a printed spelling into an existing
  player (adds it to that player's `aka:`), unmerge, upload a photo (to
  `photos/`), and **create** a player before their first game so the next
  scorecard spelling can be mapped to them straight away. Opponent names are
  listed read-only (they only matter for head-to-head pages).
- **Seasons** (`/admin/seasons`): start a new season (start date; the job creates
  the folder). Today's `new_team.py --season-start`.

### Several teams in one repo (if the open question is answered yes)

`Teams/` may hold several team folders. The job loops over them (`TEAM` env per
pass); uploads, answers, status and review carry a team key
(`site/<team-slug>/status.json`, `review.json`); the viewer shows a team picker
when `site/data/` has more than one file; the admin pages have a team switcher.
Access policies stay per site, not per team: everyone with access sees all teams
on that site, and every admin administers all of them.

### Viewer

- Plain HTML/CSS/JS, hash routes (`#/batting`, `#/player/sam`, `#/game/2026-10-15`),
  reads `data/<team-slug>.json`. Team colours, badge and arena from the data file.
- Sections: Coach (the letter, per season), Batting, Bowling, All-round rankings
  (same metrics and order as the PDF ladders), Games (results list → game page),
  Players (grid → player page), **Records**. One scope switcher (each season +
  All-time) applies everywhere; each section has its own default:
  - Batting / Bowling / All-round / Coach / Games → **current season** (the
    season of the team's latest game).
  - Records → **all-time**: team records (highest and lowest total, biggest win
    and heaviest loss, best skin, most wickets and fewest extras in a game,
    longest winning and losing streaks) and individual records (best
    contribution, most runs, most wickets and best economy in a game, best
    partnership, hat-tricks, most run outs created). Each record names the game
    and date; tapping it opens the game page.
  - Player page → both: the season line on top, the career (all-time) line under
    it, game-by-game for the selected scope.
  - Switching scope is remembered for the visit only; reopening the app returns
    to the defaults.
  The numbers come from the same `report_data.build()` calls per season plus an
  all-time build; what today's all-time PDF card shows is the minimum.
- Phone-first: 18px base type, tappable rows, sticky bottom menu, no horizontal
  scroll. Works on desktop too, unchanged.
- PWA manifest + icons so "Add to Home Screen" gives an app icon.
- **Look and feel.** Built on the Made-Up Studio design tokens (`tokens.css`
  copied into the viewer: colours, spacing, radii, shadows, system font stack,
  two weights, dark theme via `prefers-color-scheme`), with the team's brand
  colour mapped onto the accent token. One deliberate deviation, documented in
  the project's CLAUDE.md: a phone reading scale — 18px body, big numerals for
  the headline stat on every card — instead of the studio's desktop sizes.
  Minimalist: one idea per screen, section labels in small caps, no prose on
  pages (stat definitions behind a `?` popover, per the studio's lean-pages
  rule), cards that respond to touch, short slide/fade transitions between
  screens, sparklines as inline SVG, no chart library unless a screen needs one.
- A small "processing…" banner after an upload until `status.json` changes.
- Multi-team: if `site/data/` holds several team files, a team picker appears
  (lets a friendly team be hosted inside another team's repo as a second team).

### Public engine repo (`indoor-cricket-stats`)

- `scripts/` (incl. new `build_site.py`), `viewer/`, `.claude/skills/`,
  `functions/` (the two Pages Functions), `.github/workflows/process.yml`
  (reusable), `templates/game-template.json`, `TRANSCRIBE.md`, `README.md`,
  `docs/SETUP.md` (the 20-minute team setup, with screenshots later),
  `docs/COSTS.md`, `CONTRIBUTING.md` ("no support promised"), `LICENSE` (MIT).
- A **fresh** repo with a clean history. Before every push a leak check runs
  (today's `make_kit.py` guard, repointed: the list of forbidden identifiers lives
  in the owner's private repo, never in the public one). CI in the public repo
  additionally fails if anything but the example exists under `Teams/`.
- Versioning: semantic tags; `v1` is a moving major tag that the template pins.
  Breaking changes bump the major; the template's README tells teams how to move.
- `make_kit.py` and `kit/` retire; their docs become the public README/SETUP.

### Team template repo (`indoor-cricket-stats-team`)

"Use this template" → private copy. Contains the layout above with an empty
`Teams/`, `bootstrap.py` + `engine.lock`, a `CLAUDE.md` for the PC fallback, the
10-line workflow, the `site/functions/`, and a README that walks through: create
the Cloudflare project pointing at `site/`, enable Access with the team's emails
(viewers) and the admin's (admins on `/admin*` and `/api/*`), add the two secrets
(Claude token, GitHub token for the functions), open `/admin/teams` and create the
team, upload the first scorecard.

### Historic data (later, optional)

The owner starts clean. When history is wanted: copy the hub's `Teams/<team>/`
folder into the team repo (same format), convert the season letters into
per-game letters (last game of each season), run the pipeline, push. The hub's
pipeline keeps working until then; afterwards the hub folder becomes a README
pointing at the two repos.

## Left to the builder

- Exact viewer design, typography and charts; how much of `report_data.build()`
  to ship (trim what the viewer does not use if the file is large).
- GitHub contents API vs R2 for photos; how the "processing…" state is detected
  before the job's first commit.
- The exact Claude Code invocation in Actions (official action vs `claude -p`),
  model choice, timeouts, retry on transient failures, and a concurrency guard so
  two uploads do not race.
- The shape of `context` in a review question (e.g. a cropped image of the cell
  or name, committed alongside) — nice to have, not required for v1.
- Tests: the validator already guards the data; add a smoke test that builds the
  site from the example game, and a leak-check test. Rules parameterisation gets a
  test that the defaults reproduce today's numbers for the example game exactly.
- How the admin functions validate input (a team name must match the card
  spelling; a merge must not create a loop) and how they report a failed commit.
- Which literals in the scripts and `TRANSCRIBE.md` become `rules` lookups; the
  preset table's home.
- Everything about look and copy in the docs.

## Build order (suggested)

Stage 1:

1. Project skeleton in `indoor-cricket-stats`: engine scripts copied in and
   sanitised, skills, example game, docs, licence, leak check, tests running.
2. Rules parameterisation, coach settings and per-game coach letters in the
   pipeline (defaults reproduce today's numbers for the example game; tests
   prove it).
3. `build_site.py` + the viewer (multi-team, seasons/records defaults, look and
   feel), run against the example team; ship to Cloudflare behind the PIN gate
   as soon as it reads well on a phone.
4. The skills' publish step (build `site/`, commit), the team repo's
   `CLAUDE.md`/`bootstrap.py`, the `/setup` wizard; prove the chat flow from the
   phone on a cloud session with the example game, then with the owner's first
   real scorecard of the new season.
5. Public engine repo on GitHub (fresh history, MIT, docs), team template.

Stage 2 (when wanted):

5. Unattended mode for the skills, `status.json`/`review.json`, the reusable
   workflow; prove it on a cloud run of an already-transcribed game.
6. Upload/answer/admin functions and pages.
