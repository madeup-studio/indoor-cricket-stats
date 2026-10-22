"""The validator reads the wicket value from the rules (team.yaml / meta.rules)."""
import json
from collections import defaultdict

import yaml

DISM = set("RCBSLHM")
GAME = ("example-team", "2026-09-01", "data", "2026-10-07.json")


def retotal(game, wicket_runs, scored_under=-5):
    """Rewrite every over total as if dismissals cost `wicket_runs` instead of
    `scored_under`, then recompute batter RS, bowler RC, C, econ, skins and totals."""
    delta = wicket_runs - scored_under
    team, opp = game["team"], game["opponent"]
    rs, rc = defaultdict(int), defaultdict(int)
    skins = {team: defaultdict(int), opp: defaultdict(int)}
    for inn in game["innings"]:
        for bat in inn["batting"]:
            for o in bat["overs"]:
                o["total"] += delta * sum(1 for b in o["balls"] if isinstance(b, str) and b in DISM)
                rc[o["bowler"]] += o["total"]
            bat["rs"] = sum(o["total"] for o in bat["overs"])
            rs[bat["name"]] += bat["rs"]
            skins[inn["batting_team"]][bat["skin"]] += bat["rs"]
    for side, rows in game["summaries"].items():
        for r in rows:
            r["rs"], r["rc"] = rs[r["name"]], rc[r["name"]]
            r["c"] = r["rs"] - r["rc"]
            r["econ"] = round(r["rc"] / r["ob"], 2) if r["ob"] else 0
    res = game["result"]
    res["team_skins"] = [skins[team][k] for k in sorted(skins[team])]
    res["opponent_skins"] = [skins[opp][k] for k in sorted(skins[opp])]
    res["team_total"], res["opponent_total"] = sum(res["team_skins"]), sum(res["opponent_skins"])
    return game


def test_validator_uses_team_wicket_value(tmp_team, run_script):
    team_dir = tmp_team / "example-team"
    cfg = yaml.safe_load((team_dir / "team.yaml").read_text(encoding="utf-8"))
    cfg["rules"] = {"preset": "indoor-sa", "wicket_runs": -3}
    (team_dir / "team.yaml").write_text(yaml.safe_dump(cfg), encoding="utf-8")
    gpath = tmp_team.joinpath(*GAME)
    game = json.loads(gpath.read_text(encoding="utf-8"))
    game["meta"].setdefault("rules", {})["wicket_runs"] = -3   # scored under -3
    gpath.write_text(json.dumps(retotal(game, -3), indent=1), encoding="utf-8")

    env = {"TEAM": "example-team", "TEAMS_DIR": str(tmp_team)}
    r = run_script("validate_ballbyball.py", env=env)
    assert "ALL RECONCILE" in r.stdout, r.stdout[-2000:]
    r5 = run_script("validate_ballbyball.py", env=dict(env, WICKET_RUNS_OVERRIDE="-5"))
    assert r5.returncode == 1, r5.stdout[-2000:]


def test_unchanged_example_fails_at_minus_three(tmp_team, run_script):
    # the example is scored at -5: forcing -3 must break [B] on its wicket overs
    r = run_script("validate_ballbyball.py",
                   env={"TEAMS_DIR": str(tmp_team), "WICKET_RUNS_OVERRIDE": "-3"})
    assert r.returncode == 1 and "[B] FAIL" in r.stdout
