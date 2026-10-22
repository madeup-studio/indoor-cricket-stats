#!/usr/bin/env python3
"""Set up a team folder (first run) or add a new season folder to it.

  python scripts/new_team.py "Team Name" --arena "Example Arena" [--badge ABC]
      creates Teams/<folder>/ with team.yaml, players.yaml, seasons.md,
      coach_notes.yaml and photos/  (folder defaults to the name, spaces -> '-')

  python scripts/new_team.py --season-start 2026-10-12
      adds Teams/<TEAM>/2026-10-12/{data,scorecards,stats,context}/ for a new season
      (name the folder by the season's START date; the arena website lists it)

Both can be combined on first run. The team name must be spelled exactly as it is
printed on the scorecards.
"""
import argparse, datetime, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEAMS_DIR = os.path.join(ROOT, "Teams")


def write(path, text):
    if os.path.exists(path):
        print("  exists, kept:", os.path.relpath(path, ROOT))
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(text)
    print("  created:", os.path.relpath(path, ROOT))


def default_badge(name):
    words = re.findall(r"[A-Za-z0-9]+", name)
    if len(words) > 1:
        return "".join(w[0] for w in words).upper()[:4]
    return name[:4].upper()


def create_team(name, folder, arena, badge):
    team_dir = os.path.join(TEAMS_DIR, folder)
    print(f"Team '{name}' -> {os.path.relpath(team_dir, ROOT)}")
    write(os.path.join(team_dir, "team.yaml"),
          "# Team settings — read by every script (see scripts/paths.py).\n"
          f'name: "{name}"{" " * max(1, 30 - len(name))}# exactly as printed on the scorecards\n'
          f'badge: "{badge}"{" " * max(1, 29 - len(badge))}# short text for the report logo (max ~4 chars)\n'
          f'arena: "{arena}"{" " * max(1, 29 - len(arena))}# where the team plays (the arena runs the leagues)\n'
          f"colours:{' ' * 30}# report brand colours (hex)\n"
          '  brand: "#d21f2a"\n'
          '  gold: "#f5b301"\n')
    write(os.path.join(team_dir, "players.yaml"),
          "# Team player list & name registry (one per team).\n"
          "#   as    : exactly how the name is printed on a scorecard (do not change).\n"
          "#   name  : the confirmed full name. Fill this in to clear an ambiguity; the\n"
          "#           reports then show this instead of the scorecard spelling.\n"
          "#   aka   : optional OTHER scorecard spellings that are the SAME person\n"
          "#           (they get merged together in the season stats).\n"
          "# Check new names after adding scorecards:  python scripts/roster.py --check\n"
          "roster: []\n")
    write(os.path.join(team_dir, "seasons.md"),
          f"# {name} — seasons & game inventory\n\n"
          "One folder per season, named by the season **start date** (YYYY-MM-DD). Every\n"
          "transcribed game has fully-reconciled ball-by-ball (each batter's runs, each\n"
          "bowler's runs/wickets and the skin totals cross-check).\n\n"
          "| Season | League | Folder | Games transcribed |\n"
          "|--------|--------|--------|-------------------|\n")
    write(os.path.join(team_dir, "coach_notes.yaml"),
          "# AI Coach letters — one `_letter` per SEASON (key = season name as printed on the\n"
          "# scorecards, e.g. \"Spring 2026\"), rendered as page 1 of that season's stat card.\n"
          "#   _letter: {fp, sections: [{title, html}], players: [{name, note}]}\n"
          "# Written by Claude with the ai-coach skill; a new scorecard makes a letter stale.\n")
    write(os.path.join(team_dir, "photos", "README.txt"),
          "Player photos for the PDF report's player pages.\n\n"
          "One image per player, named by the player's display name in lowercase-kebab\n"
          "form, as .jpg / .jpeg / .png (e.g. sam.jpg, sam-smith.png). Square images look\n"
          "best. Until a photo exists the report shows the player's initials.\n")
    return team_dir


def create_season(team_dir, start):
    datetime.date.fromisoformat(start)   # validates YYYY-MM-DD
    sd = os.path.join(team_dir, start)
    print(f"Season folder {os.path.relpath(sd, ROOT)}")
    for sub in ("data", "scorecards", "stats"):
        os.makedirs(os.path.join(sd, sub), exist_ok=True)
    write(os.path.join(sd, "context", "README.md"),
          "# Season context (supplemental, non-scorecard info)\n\n"
          "Anything that is NOT a scorecard but should inform the reports and the AI Coach\n"
          "letter: league table screenshots transcribed to text, fixtures, comments about a\n"
          "game, guest players, banter material.\n\n"
          "- One file per upload, named `YYYY-MM-DD-<topic>.md` (date = when the info was true).\n"
          "- Keep data faithful to the source (transcribe tables as markdown tables).\n"
          "- Context only: never parsed by the stats pipeline, never overrides scorecards.\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", nargs="?", help="team name exactly as printed on the scorecards")
    ap.add_argument("--arena", default="", help='e.g. "Example Arena"')
    ap.add_argument("--badge", help="2-4 characters for the report logo (default: initials)")
    ap.add_argument("--folder", help="folder name under Teams/ (default: the name)")
    ap.add_argument("--season-start", help="YYYY-MM-DD: also create this season's folder")
    a = ap.parse_args()

    if a.name:
        folder = a.folder or re.sub(r"[^A-Za-z0-9]+", "-", a.name).strip("-")
        team_dir = create_team(a.name, folder, a.arena, a.badge or default_badge(a.name))
    elif a.season_start:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import paths      # resolves the existing team (TEAM env var or the only team)
        team_dir = paths.TEAM_DIR
    else:
        ap.error("give a team name (first run) and/or --season-start YYYY-MM-DD")
    if a.season_start:
        create_season(team_dir, a.season_start)


if __name__ == "__main__":
    main()
