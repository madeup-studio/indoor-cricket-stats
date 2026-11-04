# Architecture — indoor-cricket-stats

Studio pattern (MaDe-uP Studios): a pure domain wrapped by pure use cases, wrapped by
orchestration, wrapped by adapters; dependencies point inward. This app is Python +
plain HTML/JS rather than the studio's TypeScript stack (a deliberate deviation, see
`CLAUDE.md`), so the layers are folders and modules rather than `src/` packages.

## Layers

| Layer | Where | What it is |
|---|---|---|
| Domain | game file schema (`scripts/templates/game-template.json`), `team.yaml`, `<season>/season.yaml`, `scripts/rules.py` | One verified JSON file per game; the team's settings; the season's medal; the scoring rules and presets. |
| Use cases (pure) | `scripts/stats_core.py`, `scripts/report_data.py` (`build()`), `scripts/coach.py` (keys, fingerprints, status), `build_site.derive_records()`, `season_meta.is_finished`, `team_settings.merge_show`, `report_data.season_awards` | Pure functions over match data: stats, rankings, records, which letters are due. No I/O in `report_data.build()`. |
| Orchestration | `validate_ballbyball.py`, `build_scorecards.py`, `build_site.py`, `generate_stats.py`, `generate_pdf_report.py`, `publish.py`, `new_team.py` | Load files, call the use cases, write outputs, commit and push. |
| Adapters | `viewer/` (the phone app), the PDF stat cards, the Claude Code skills (`.claude/skills/`), `viewer/functions/_middleware.js` (the gate) | Present the outputs; collect input through Claude. |

## Ports

- **Scorecard reading**: Claude (the `add-scorecard` skill + `scripts/TRANSCRIBE.md`),
  checked by the validator — the model never touches a total the validator hasn't
  reconciled.
- **Coach letter**: Claude (the `ai-coach` skill), keyed per game, never rewritten.
- **Hosting**: Cloudflare Pages via `wrangler` (GitHub Actions, or `setup.py --deploy`);
  provisioning via the Cloudflare API in `setup.py`, whose HTTP client is injectable
  (`http=`) so tests never touch the network.
- **Storage and history**: git. No database.
- **Engine distribution**: GitHub release archives (`update_engine.py`), vendored into
  each team repo's `engine/`.

## Invariants

1. **The viewer never computes stats.** It renders `data/<team>.json` as built by
   `build_site.py` from `report_data.build()` — the same numbers as the PDF.
2. **The engine never reads the viewer** (or any UI state). `build_site.py` copies
   `viewer/` and writes JSON; nothing flows back.
3. **Nothing unreconciled is published.** A game reaches `site/` only after
   `validate_ballbyball.py` prints `ALL RECONCILE`.
4. **Rules come from data.** Scoring constants are read from `team.yaml` → `rules`,
   overridden per game by `meta.rules`; never hard-coded.
5. **Letters are history.** A letter belongs to one game (its key) and is never
   rewritten; its fingerprint covers the games up to and including it.
6. **The public repo holds no team data.** Only `Teams/example-team/` exists here;
   `scripts/leak_check.py` and CI enforce it.
7. **The gate fails closed.** `GATE=pin` without `TEAM_PIN`/`PIN_SECRET` answers 503.

## Glossary (used identically in code, docs and the app)

**team** (never "club"), **arena** (the venue, owned by a franchise), **league** (an
ability tier with promotion/relegation), **season** (a folder named by its start date),
**skin** (a pair's four overs), **RS / RC / C** (runs scored / conceded / contribution
= RS − RC), **letter** (the coach's letter for one game), **gate** (pin | email | none).
