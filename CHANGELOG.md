# Changelog

## 1.0.0 — 2026-11-05, first release

- Scorecard photo → verified game file → stats, with configurable scoring rules
  (presets; each game keeps the rules it was scored under).
- A coach's letter per game, kept for good; banter, encouraging or serious tone.
- Phone-first app: rankings, player pages, games, records, seasons and all-time,
  several teams per site, dark mode, installable.
- Team-code gate (or email list via Cloudflare Access, or an open link).
- Team template with the engine vendored in `engine/`, `/setup` wizard, publish step.
- Records opens on the current season, like every other screen.
- Games can be tagged playoff, semi-final or final (`meta.stage`).
- A season's medal (gold, silver, bronze) shows in the season menu, set in `season.yaml`.
- Finished seasons get awards (player, batter and bowler of the season); off by default.
- `show:` switches in `team.yaml` hide or show awards, medals, tags, streaks and records.
- Setup asks whether you want the AI coach.
- A scorecard for a date and opponent already recorded is refused, not doubled.
- "Add an admin" instructions in the skills and guides.
- The coach can have a persona (`coach.persona`) on top of its tone.
