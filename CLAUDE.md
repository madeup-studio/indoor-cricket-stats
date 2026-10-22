# Indoor Cricket Stats — project instructions

Open-source (MIT), self-hosted stats app for indoor action-cricket teams: a
Python engine that turns Spawtz scorecard photos (transcribed by Claude Code)
into verified game files, stats, an AI coach letter per game, and a phone-first
static web app. Read `docs/superpowers/specs/*-design.md` before changing
anything; the build plan is in `docs/superpowers/plans/`.

## This repo will be PUBLIC — privacy rules

- **No real team or player data, ever** — not in files, not in git history, not
  in docs or examples. Only the anonymised example team (`Teams/example-team/`)
  is allowed under `Teams/`.
- Teams keep their data in their own private repos created from the template;
  the engine never sees it.
- Before any push, run the leak check (`scripts/leak_check.py`); its list of
  forbidden identifiers lives outside this repo (the owner's private hub), never
  here.
- Coach letters, standings, notes and photos are team data. Example content only.

## Deviations from the studio defaults (deliberate)

- **No madeup-auth, no Firebase, no token economy, no React/Vite.** Teams
  self-host on free tiers with no accounts of their own: a private GitHub repo,
  Cloudflare Pages, and a Claude subscription for the admin. The viewer is plain
  HTML/CSS/JS with no build tooling; the engine is Python 3 (pyyaml, pillow).
- **Design tokens apply.** `viewer/tokens.css` is a copy of the studio's
  `shared/design-tokens/tokens.css`; the team's brand colour maps onto the
  accent token. The one deviation: a phone reading scale (18px body, big
  numerals) instead of the studio's desktop sizes. The studio's "lean pages"
  rule applies: no prose on screens, explanations behind `?` popovers.

## Working rules

- Every game file must reconcile (`scripts/validate_ballbyball.py` prints
  `ALL RECONCILE`) before stats are generated. Never bend a total to fit.
- Scripts run on Windows and Linux; the cloud job runs Linux.
- Rules constants (wicket value, extras value, balls per over …) come from
  `team.yaml` → `rules`; never hard-code them again.
- Commit only when the owner asks. No support is promised to users of this
  repo; say so in the README.
- Terminology: action cricket has **teams**, **arenas** (owned by a franchise)
  and **leagues** (ability tiers with promotion/relegation). Never "club".
