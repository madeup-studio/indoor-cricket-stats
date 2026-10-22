#!/usr/bin/env python3
"""Shared path resolver. Layout:

  Teams/<TEAM>/                 team folder
    team.yaml                   team settings: name as printed on cards, badge, arena, colours
    players.yaml                team player list (name registry)
    seasons.md                  season inventory
    coach_notes.yaml            AI Coach letters
    <YYYY-MM-DD>/               one folder per season (named by start date)
      scorecards/               source images + rendered per-game .md
      data/                     one combined <date>.json per game (source of truth)
      stats/                    generated season report (.md + .html)
      context/                  league table, banter, anything the AI Coach should know

The team is the TEAM env var if set, otherwise the only folder in Teams/ that has a
team.yaml. Optionally restrict to one season with the SEASON env var
(e.g. SEASON=2026-08-08). Create a team with scripts/new_team.py.
"""
import os, re, sys
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEAMS_DIR = os.path.join(ROOT, "Teams")


def team_folders():
    if not os.path.isdir(TEAMS_DIR):
        return []
    return [n for n in sorted(os.listdir(TEAMS_DIR))
            if os.path.isfile(os.path.join(TEAMS_DIR, n, "team.yaml"))]


def _pick_team():
    if os.environ.get("TEAM"):
        return os.environ["TEAM"]
    teams = team_folders()
    if len(teams) == 1:
        return teams[0]
    if not teams:
        sys.exit("No team set up yet. Run:  python scripts/new_team.py \"<team name as on the scorecard>\"")
    sys.exit(f"Several teams in Teams/ ({', '.join(teams)}). Pick one with the TEAM env var, "
             f"e.g. TEAM={teams[0]} python scripts/generate_stats.py")


TEAM = _pick_team()
TEAM_DIR = os.path.join(TEAMS_DIR, TEAM)
PLAYERS_FILE = os.path.join(TEAM_DIR, "players.yaml")

_cfg_file = os.path.join(TEAM_DIR, "team.yaml")
TEAM_CFG = (yaml.safe_load(open(_cfg_file, encoding="utf-8")) if os.path.exists(_cfg_file) else None) or {}
TEAM_NAME = TEAM_CFG.get("name") or TEAM          # exactly as printed on the scorecards
BADGE = TEAM_CFG.get("badge") or TEAM_NAME[:4]    # short text for the report logo
ARENA = TEAM_CFG.get("arena") or ""               # e.g. "Example Arena"
COLOURS = TEAM_CFG.get("colours") or {}           # optional: brand, gold (hex)

SEASON_RE = re.compile(r"\d{4}-\d{2}-\d{2}$")


def season_dirs():
    """All season folders for the team (or just SEASON if that env var is set)."""
    only = os.environ.get("SEASON")
    if only:
        return [os.path.join(TEAM_DIR, only)]
    if not os.path.isdir(TEAM_DIR):
        return []
    return [os.path.join(TEAM_DIR, n) for n in sorted(os.listdir(TEAM_DIR))
            if SEASON_RE.match(n) and os.path.isdir(os.path.join(TEAM_DIR, n))]


def data_dir(season_dir):       return os.path.join(season_dir, "data")
def cards_dir(season_dir):      return os.path.join(season_dir, "scorecards")
def stats_dir(season_dir):      return os.path.join(season_dir, "stats")
