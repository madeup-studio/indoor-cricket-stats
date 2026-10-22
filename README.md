# Indoor Cricket Stats

Scorecard photo → phone-first team stats and an AI coach, for indoor cricket (or Action Cricket)

Your team admin photographs the Spawtz scorecard at the arena and hands it to Claude
from their phone. Every ball is transcribed and checked against the card's own
totals, the stats are rebuilt, the AI coach writes the team a letter about the game,
and a small app the whole team opens from a link updates about a minute later.

- **Rankings** for batting, bowling and all-rounders, per season and all-time
- **Player pages** with the season line, the career line and game-by-game form
- **Every game**: the skins, both teams' figures, and the coach's letter for that game
- **Records**: team and individual bests, partnerships, hat-tricks, streaks
- Big type, a bottom menu, dark mode, "Add to Home Screen" — built for phones
- Behind a team code (or an email list, or an open link — your choice)

An open-source release from MaDe-uP Studios, under the [MIT licence](LICENSE).

## What a team needs

Each team runs its own copy on its own accounts. Nothing is hosted for you and no
team's data ever reaches anyone else.

| Account | What it's for | Cost |
|---|---|---|
| GitHub | a private repo holding your team's data and app | free |
| Cloudflare | hosts the app and the team-code gate (Pages) | free |
| Claude Pro or Max (the admin) | reads the scorecards and writes the coach's letter, in the Claude app | your subscription |

Details in [docs/COSTS.md](docs/COSTS.md). Setup takes about 20 minutes:
[docs/SETUP.md](docs/SETUP.md).

## How it fits together

```
Teams/<team>/<season>/data/<date>.json   one verified file per game (the source of truth)
        │  Python engine (scripts/): validate → stats → records → coach letter
        ▼
site/  (viewer/ + data/<team>.json)      plain HTML/CSS/JS, no build step
        │  git push → GitHub Actions → Cloudflare Pages (behind the gate)
        ▼
the team's phones
```

More in [docs/architecture.md](docs/architecture.md). The engine is Python 3 (pyyaml,
pillow); the app is plain HTML/CSS/JS; Claude Code skills drive transcription, the
coach letter, publishing and setup.

## For developers

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest -q                                   # engine
node --test "viewer/**/*.test.js"           # viewer + team-code gate (Node 22)
python scripts/build_site.py --out dist/site && python -m http.server -d dist/site
python scripts/make_template.py             # the team template in dist/team-template
```

The only team data in this repo is the made-up example team in
`Teams/example-team/`. See [CONTRIBUTING.md](CONTRIBUTING.md).

## No support promised

This is shared as-is, free, for teams that want to run it themselves. There is no
support, no service and no guarantee; issues and pull requests are welcome but may
not be answered.
