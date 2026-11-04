---
# Match meta
date: 2026-10-21
time: "19:30"
season: "Spring 2026"
arena: Example Arena
league: Mens E
umpire: Umpire Name
court: null
venue: null
source_image: scorecards/example.jpeg
stage: final

# Teams & result (innings order: 1=Our Team batted first)
team: Our Team
opponent: "Opponents"
outcome: win
team_total: 80
team_skins_won: 3
opponent_total: 51
opponent_skins_won: 1
team_skins: [15, 21, 15, 29]
opponent_skins: [28, 6, 6, 11]
player_of_match: "Our P7"
player_of_match_team: "Our Team"

# Clean summary stats (VALIDATED to team/skin totals; C = RS - RC)
team_summary:
  - {name: "Our P1", skin: 1, rs: 16, ob: 2, rc: 3, wkts: 3, econ: 1.5, c: 13}
  - {name: "Our P2", skin: 1, rs: -1, ob: 2, rc: 20, wkts: 0, econ: 10.0, c: -21}
  - {name: "Our P3", skin: 2, rs: 11, ob: 2, rc: -15, wkts: 5, econ: -7.5, c: 26}
  - {name: "Our P4", skin: 2, rs: 10, ob: 2, rc: 17, wkts: 1, econ: 8.5, c: -7}
  - {name: "Our P5", skin: 3, rs: 5, ob: 2, rc: 11, wkts: 2, econ: 5.5, c: -6}
  - {name: "Our P6", skin: 3, rs: 10, ob: 2, rc: 8, wkts: 2, econ: 4.0, c: 2}
  - {name: "Our P7", skin: 4, rs: 22, ob: 2, rc: -5, wkts: 3, econ: -2.5, c: 27}
  - {name: "Our P8", skin: 4, rs: 7, ob: 2, rc: 12, wkts: 1, econ: 6.0, c: -5}
opponent_summary:
  - {name: "Opp P1", skin: 1, rs: 17, ob: 2, rc: 19, wkts: 0, econ: 9.5, c: -2}
  - {name: "Opp P2", skin: 1, rs: 11, ob: 2, rc: 6, wkts: 3, econ: 3.0, c: 5}
  - {name: "Opp P3", skin: 2, rs: -7, ob: 2, rc: -6, wkts: 4, econ: -3.0, c: -1}
  - {name: "Opp P4", skin: 2, rs: 13, ob: 2, rc: 15, wkts: 2, econ: 7.5, c: -2}
  - {name: "Opp P5", skin: 3, rs: 5, ob: 2, rc: 7, wkts: 2, econ: 3.5, c: -2}
  - {name: "Opp P6", skin: 3, rs: 1, ob: 2, rc: 11, wkts: 1, econ: 5.5, c: -10}
  - {name: "Opp P7", skin: 4, rs: 15, ob: 2, rc: 15, wkts: 0, econ: 7.5, c: 0}
  - {name: "Opp P8", skin: 4, rs: -4, ob: 2, rc: 13, wkts: 0, econ: 6.5, c: -17}

# Ball-by-ball (VERIFIED: checksums reconcile). balls: int=runs off bat,
# R/C/B/S/L/H/M = dismissal (-5): run out/caught/bowled/stumped/lbw/hit wkt/mankad; w/nb = extras.
# *_batting_seq (when present) = exact delivery order per over: [batter, ball] pairs.
ball_by_ball:
  status: verified
  team_batting:
    - name: "Our P1"
      skin: 1
      rs: 16
      overs:
        - {bowler: "Opp P2", balls: [2, 0, 1], total: 3}
        - {bowler: "Opp P6", balls: [1, 1], total: 2}
        - {bowler: "Opp P4", balls: [4, 4, 0], total: 8}
        - {bowler: "Opp P6", balls: ["w", 1], total: 3}
    - name: "Our P2"
      skin: 1
      rs: -1
      overs:
        - {bowler: "Opp P2", balls: ["R", 2, 2], total: -1}
        - {bowler: "Opp P6", balls: [2, 0, 2, "R"], total: -1}
        - {bowler: "Opp P4", balls: [4, "B", "C"], total: -6}
        - {bowler: "Opp P6", balls: ["w", 1, 0, "w", "w"], total: 7}
    - name: "Our P3"
      skin: 2
      rs: 11
      overs:
        - {bowler: "Opp P5", balls: ["w", "w", 2, "nb"], total: 8}
        - {bowler: "Opp P1", balls: [0, 1], total: 1}
        - {bowler: "Opp P8", balls: [0, 1, 0], total: 1}
        - {bowler: "Opp P5", balls: [1], total: 1}
    - name: "Our P4"
      skin: 2
      rs: 10
      overs:
        - {bowler: "Opp P5", balls: [0, "w"], total: 3}
        - {bowler: "Opp P1", balls: [0, "w", 0, "w"], total: 6}
        - {bowler: "Opp P8", balls: [3, 0, "nb"], total: 6}
        - {bowler: "Opp P5", balls: ["B", "w", 0, "w", "C"], total: -5}
    - name: "Our P5"
      skin: 3
      rs: 5
      overs:
        - {bowler: "Opp P3", balls: ["w", 0, "S", "C", "C"], total: -13}
        - {bowler: "Opp P4", balls: [0, 1, 1, 2], total: 4}
        - {bowler: "Opp P7", balls: [0, 1, 1, "nb"], total: 5}
        - {bowler: "Opp P2", balls: [7, 2], total: 9}
    - name: "Our P6"
      skin: 3
      rs: 10
      overs:
        - {bowler: "Opp P3", balls: [2], total: 2}
        - {bowler: "Opp P4", balls: [5, 4], total: 9}
        - {bowler: "Opp P7", balls: [2, 2], total: 4}
        - {bowler: "Opp P2", balls: ["C", 2, "C", 3], total: -5}
    - name: "Our P7"
      skin: 4
      rs: 22
      overs:
        - {bowler: "Opp P1", balls: ["w", 1, 2, 2], total: 7}
        - {bowler: "Opp P8", balls: [0, 2, 2], total: 4}
        - {bowler: "Opp P7", balls: [2, 0, 1], total: 3}
        - {bowler: "Opp P3", balls: [2, 4, 2], total: 8}
    - name: "Our P8"
      skin: 4
      rs: 7
      overs:
        - {bowler: "Opp P1", balls: [2, "nb"], total: 5}
        - {bowler: "Opp P8", balls: [0, 1, 1], total: 2}
        - {bowler: "Opp P7", balls: [2, 0, 1], total: 3}
        - {bowler: "Opp P3", balls: [1, 1, "R"], total: -3}
  opponent_batting:
    - name: "Opp P1"
      skin: 1
      rs: 17
      overs:
        - {bowler: "Our P2", balls: [0, "w", 0, 2, 2], total: 6}
        - {bowler: "Our P5", balls: [7, 1, 1], total: 9}
        - {bowler: "Our P4", balls: ["nb", "w", "C", 2], total: 1}
        - {bowler: "Our P1", balls: [3, 3, "C"], total: 1}
    - name: "Opp P2"
      skin: 1
      rs: 11
      overs:
        - {bowler: "Our P2", balls: [2], total: 2}
        - {bowler: "Our P5", balls: [2, "nb", 2], total: 6}
        - {bowler: "Our P4", balls: ["nb", 2], total: 4}
        - {bowler: "Our P1", balls: [2, 2, "C"], total: -1}
    - name: "Opp P3"
      skin: 2
      rs: -7
      overs:
        - {bowler: "Our P6", balls: [2, 2], total: 4}
        - {bowler: "Our P3", balls: [1, "R"], total: -4}
        - {bowler: "Our P8", balls: [3, 0, "C", 2], total: 0}
        - {bowler: "Our P5", balls: ["R", "C", 1, 2], total: -7}
    - name: "Opp P4"
      skin: 2
      rs: 13
      overs:
        - {bowler: "Our P6", balls: ["w", 0, 2, 4], total: 8}
        - {bowler: "Our P3", balls: [2, "R", 1, 1], total: -1}
        - {bowler: "Our P8", balls: [1, 2], total: 3}
        - {bowler: "Our P5", balls: [2, 1], total: 3}
    - name: "Opp P5"
      skin: 3
      rs: 5
      overs:
        - {bowler: "Our P4", balls: [2, 2], total: 4}
        - {bowler: "Our P3", balls: [1, "R", 2], total: -2}
        - {bowler: "Our P1", balls: [2, 0, 2], total: 4}
        - {bowler: "Our P7", balls: [2, "B", "w"], total: -1}
    - name: "Opp P6"
      skin: 3
      rs: 1
      overs:
        - {bowler: "Our P4", balls: ["nb", "w", 2, "w"], total: 8}
        - {bowler: "Our P3", balls: ["S", "S", 2], total: -8}
        - {bowler: "Our P1", balls: ["C", 2, 2], total: -1}
        - {bowler: "Our P7", balls: [1, 0, 1], total: 2}
    - name: "Opp P7"
      skin: 4
      rs: 15
      overs:
        - {bowler: "Our P6", balls: ["w", 1, "C", 0, 3], total: 1}
        - {bowler: "Our P8", balls: [3, "w", 1], total: 6}
        - {bowler: "Our P2", balls: [0, 2, 5], total: 7}
        - {bowler: "Our P7", balls: [1], total: 1}
    - name: "Opp P8"
      skin: 4
      rs: -4
      overs:
        - {bowler: "Our P6", balls: ["R"], total: -5}
        - {bowler: "Our P8", balls: [0, 2, 1], total: 3}
        - {bowler: "Our P2", balls: [2, 1, 2], total: 5}
        - {bowler: "Our P7", balls: ["B", 1, "B", 0, 2], total: -7}
  team_batting_seq:
    - {skin: 1, bowler: "Opp P2", seq: [["Our P2", "R"], ["Our P2", 2], ["Our P1", 2], ["Our P2", 2], ["Our P1", 0], ["Our P1", 1]]}
    - {skin: 1, bowler: "Opp P6", seq: [["Our P1", 1], ["Our P2", 2], ["Our P1", 1], ["Our P2", 0], ["Our P2", 2], ["Our P2", "R"]]}
    - {skin: 1, bowler: "Opp P4", seq: [["Our P1", 4], ["Our P2", 4], ["Our P1", 4], ["Our P2", "B"], ["Our P2", "C"], ["Our P1", 0]]}
    - {skin: 1, bowler: "Opp P6", seq: [["Our P2", "w"], ["Our P2", 1], ["Our P1", "w"], ["Our P1", 1], ["Our P2", 0], ["Our P2", "w"], ["Our P2", "w"]]}
    - {skin: 2, bowler: "Opp P5", seq: [["Our P3", "w"], ["Our P3", "w"], ["Our P3", 2], ["Our P4", 0], ["Our P4", "w"], ["Our P3", "nb"]]}
    - {skin: 2, bowler: "Opp P1", seq: [["Our P4", 0], ["Our P4", "w"], ["Our P3", 0], ["Our P3", 1], ["Our P4", 0], ["Our P4", "w"]]}
    - {skin: 2, bowler: "Opp P8", seq: [["Our P4", 3], ["Our P3", 0], ["Our P3", 1], ["Our P4", 0], ["Our P4", "nb"], ["Our P3", 0]]}
    - {skin: 2, bowler: "Opp P5", seq: [["Our P4", "B"], ["Our P4", "w"], ["Our P4", 0], ["Our P4", "w"], ["Our P3", 1], ["Our P4", "C"]]}
    - {skin: 3, bowler: "Opp P3", seq: [["Our P5", "w"], ["Our P5", 0], ["Our P5", "S"], ["Our P5", "C"], ["Our P6", 2], ["Our P5", "C"]]}
    - {skin: 3, bowler: "Opp P4", seq: [["Our P5", 0], ["Our P5", 1], ["Our P6", 5], ["Our P5", 1], ["Our P6", 4], ["Our P5", 2]]}
    - {skin: 3, bowler: "Opp P7", seq: [["Our P5", 0], ["Our P5", 1], ["Our P6", 2], ["Our P5", 1], ["Our P6", 2], ["Our P5", "nb"]]}
    - {skin: 3, bowler: "Opp P2", seq: [["Our P5", 7], ["Our P6", "C"], ["Our P6", 2], ["Our P5", 2], ["Our P6", "C"], ["Our P6", 3]]}
    - {skin: 4, bowler: "Opp P1", seq: [["Our P7", "w"], ["Our P7", 1], ["Our P8", 2], ["Our P7", 2], ["Our P8", "nb"], ["Our P7", 2]]}
    - {skin: 4, bowler: "Opp P8", seq: [["Our P7", 0], ["Our P7", 2], ["Our P8", 0], ["Our P8", 1], ["Our P7", 2], ["Our P8", 1]]}
    - {skin: 4, bowler: "Opp P7", seq: [["Our P8", 2], ["Our P7", 2], ["Our P8", 0], ["Our P8", 1], ["Our P7", 0], ["Our P7", 1]]}
    - {skin: 4, bowler: "Opp P3", seq: [["Our P7", 2], ["Our P8", 1], ["Our P7", 4], ["Our P8", 1], ["Our P7", 2], ["Our P8", "R"]]}
  opponent_batting_seq:
    - {skin: 1, bowler: "Our P2", seq: [["Opp P1", 0], ["Opp P1", "w"], ["Opp P1", 0], ["Opp P1", 2], ["Opp P2", 2], ["Opp P1", 2]]}
    - {skin: 1, bowler: "Our P5", seq: [["Opp P1", 7], ["Opp P2", 2], ["Opp P1", 1], ["Opp P2", "nb"], ["Opp P2", 2], ["Opp P1", 1]]}
    - {skin: 1, bowler: "Our P4", seq: [["Opp P1", "nb"], ["Opp P1", "w"], ["Opp P1", "C"], ["Opp P2", "nb"], ["Opp P2", 2], ["Opp P1", 2]]}
    - {skin: 1, bowler: "Our P1", seq: [["Opp P1", 3], ["Opp P2", 2], ["Opp P1", 3], ["Opp P2", 2], ["Opp P1", "C"], ["Opp P2", "C"]]}
    - {skin: 2, bowler: "Our P6", seq: [["Opp P3", 2], ["Opp P4", "w"], ["Opp P4", 0], ["Opp P4", 2], ["Opp P3", 2], ["Opp P4", 4]]}
    - {skin: 2, bowler: "Our P3", seq: [["Opp P4", 2], ["Opp P4", "R"], ["Opp P4", 1], ["Opp P3", 1], ["Opp P4", 1], ["Opp P3", "R"]]}
    - {skin: 2, bowler: "Our P8", seq: [["Opp P3", 3], ["Opp P4", 1], ["Opp P3", 0], ["Opp P3", "C"], ["Opp P4", 2], ["Opp P3", 2]]}
    - {skin: 2, bowler: "Our P5", seq: [["Opp P3", "R"], ["Opp P4", 2], ["Opp P3", "C"], ["Opp P3", 1], ["Opp P4", 1], ["Opp P3", 2]]}
    - {skin: 3, bowler: "Our P4", seq: [["Opp P5", 2], ["Opp P6", "nb"], ["Opp P6", "w"], ["Opp P6", 2], ["Opp P5", 2], ["Opp P6", "w"]]}
    - {skin: 3, bowler: "Our P3", seq: [["Opp P5", 1], ["Opp P6", "S"], ["Opp P5", "R"], ["Opp P5", 2], ["Opp P6", "S"], ["Opp P6", 2]]}
    - {skin: 3, bowler: "Our P1", seq: [["Opp P6", "C"], ["Opp P5", 2], ["Opp P6", 2], ["Opp P5", 0], ["Opp P5", 2], ["Opp P6", 2]]}
    - {skin: 3, bowler: "Our P7", seq: [["Opp P6", 1], ["Opp P5", 2], ["Opp P6", 0], ["Opp P6", 1], ["Opp P5", "B"], ["Opp P5", "w"]]}
    - {skin: 4, bowler: "Our P6", seq: [["Opp P7", "w"], ["Opp P7", 1], ["Opp P8", "R"], ["Opp P7", "C"], ["Opp P7", 0], ["Opp P7", 3]]}
    - {skin: 4, bowler: "Our P8", seq: [["Opp P7", 3], ["Opp P8", 0], ["Opp P8", 2], ["Opp P7", "w"], ["Opp P7", 1], ["Opp P8", 1]]}
    - {skin: 4, bowler: "Our P2", seq: [["Opp P7", 0], ["Opp P7", 2], ["Opp P8", 2], ["Opp P8", 1], ["Opp P7", 5], ["Opp P8", 2]]}
    - {skin: 4, bowler: "Our P7", seq: [["Opp P8", "B"], ["Opp P8", 1], ["Opp P7", 1], ["Opp P8", "B"], ["Opp P8", 0], ["Opp P8", 2]]}
---

# Our Team vs Opponents — 2026-10-21

**Result:** Our Team won **80–51** (3 skins to 1) · **Player of the Match:** Our P7 (Our Team)
Arena: Example Arena · League: Mens E · Spring 2026 · Umpire: Umpire Name

## Skins

| Team | Skin 1 | Skin 2 | Skin 3 | Skin 4 | Total | Skins |
|------|-------:|-------:|-------:|-------:|------:|------:|
| **Our Team** | 15 | 21 | 15 | 29 | **80** | **3** |
| Opponents | 28 | 6 | 6 | 11 | 51 | 1 |

## Our Team players

| # | Player | Skin | RS | OB | RC | Wkts | Econ | Contribution |
|--:|--------|-----:|---:|---:|---:|-----:|-----:|-------------:|
| 1 | Our P1 | 1 | 16 | 2 | 3 | 3 | 1.5 | 13 |
| 2 | Our P2 | 1 | -1 | 2 | 20 | 0 | 10.0 | -21 |
| 3 | Our P3 | 2 | 11 | 2 | -15 | 5 | -7.5 | 26 |
| 4 | Our P4 | 2 | 10 | 2 | 17 | 1 | 8.5 | -7 |
| 5 | Our P5 | 3 | 5 | 2 | 11 | 2 | 5.5 | -6 |
| 6 | Our P6 | 3 | 10 | 2 | 8 | 2 | 4.0 | 2 |
| 7 | Our P7 | 4 | 22 | 2 | -5 | 3 | -2.5 | 27 |
| 8 | Our P8 | 4 | 7 | 2 | 12 | 1 | 6.0 | -5 |

## Opponents players

| # | Player | Skin | RS | OB | RC | Wkts | Econ | Contribution |
|--:|--------|-----:|---:|---:|---:|-----:|-----:|-------------:|
| 1 | Opp P1 | 1 | 17 | 2 | 19 | 0 | 9.5 | -2 |
| 2 | Opp P2 | 1 | 11 | 2 | 6 | 3 | 3.0 | 5 |
| 3 | Opp P3 | 2 | -7 | 2 | -6 | 4 | -3.0 | -1 |
| 4 | Opp P4 | 2 | 13 | 2 | 15 | 2 | 7.5 | -2 |
| 5 | Opp P5 | 3 | 5 | 2 | 7 | 2 | 3.5 | -2 |
| 6 | Opp P6 | 3 | 1 | 2 | 11 | 1 | 5.5 | -10 |
| 7 | Opp P7 | 4 | 15 | 2 | 15 | 0 | 7.5 | 0 |
| 8 | Opp P8 | 4 | -4 | 2 | 13 | 0 | 6.5 | -17 |

## Ball-by-ball

_Format: `Bowler [balls]=over total`. Dismissals worth −5: R=run out, C=caught, B=bowled, S=stumped, L=lbw, H=hit wicket, M=mankad; w/nb=extras._

**Our Team batting**

- **Our P1** (16): Opp P2 [2, 0, 1]=3  Opp P6 [1, 1]=2  Opp P4 [4, 4, 0]=8  Opp P6 [w, 1]=3
- **Our P2** (-1): Opp P2 [R, 2, 2]=-1  Opp P6 [2, 0, 2, R]=-1  Opp P4 [4, B, C]=-6  Opp P6 [w, 1, 0, w, w]=7
- **Our P3** (11): Opp P5 [w, w, 2, nb]=8  Opp P1 [0, 1]=1  Opp P8 [0, 1, 0]=1  Opp P5 [1]=1
- **Our P4** (10): Opp P5 [0, w]=3  Opp P1 [0, w, 0, w]=6  Opp P8 [3, 0, nb]=6  Opp P5 [B, w, 0, w, C]=-5
- **Our P5** (5): Opp P3 [w, 0, S, C, C]=-13  Opp P4 [0, 1, 1, 2]=4  Opp P7 [0, 1, 1, nb]=5  Opp P2 [7, 2]=9
- **Our P6** (10): Opp P3 [2]=2  Opp P4 [5, 4]=9  Opp P7 [2, 2]=4  Opp P2 [C, 2, C, 3]=-5
- **Our P7** (22): Opp P1 [w, 1, 2, 2]=7  Opp P8 [0, 2, 2]=4  Opp P7 [2, 0, 1]=3  Opp P3 [2, 4, 2]=8
- **Our P8** (7): Opp P1 [2, nb]=5  Opp P8 [0, 1, 1]=2  Opp P7 [2, 0, 1]=3  Opp P3 [1, 1, R]=-3

**Opponents batting**

- **Opp P1** (17): Our P2 [0, w, 0, 2, 2]=6  Our P5 [7, 1, 1]=9  Our P4 [nb, w, C, 2]=1  Our P1 [3, 3, C]=1
- **Opp P2** (11): Our P2 [2]=2  Our P5 [2, nb, 2]=6  Our P4 [nb, 2]=4  Our P1 [2, 2, C]=-1
- **Opp P3** (-7): Our P6 [2, 2]=4  Our P3 [1, R]=-4  Our P8 [3, 0, C, 2]=0  Our P5 [R, C, 1, 2]=-7
- **Opp P4** (13): Our P6 [w, 0, 2, 4]=8  Our P3 [2, R, 1, 1]=-1  Our P8 [1, 2]=3  Our P5 [2, 1]=3
- **Opp P5** (5): Our P4 [2, 2]=4  Our P3 [1, R, 2]=-2  Our P1 [2, 0, 2]=4  Our P7 [2, B, w]=-1
- **Opp P6** (1): Our P4 [nb, w, 2, w]=8  Our P3 [S, S, 2]=-8  Our P1 [C, 2, 2]=-1  Our P7 [1, 0, 1]=2
- **Opp P7** (15): Our P6 [w, 1, C, 0, 3]=1  Our P8 [3, w, 1]=6  Our P2 [0, 2, 5]=7  Our P7 [1]=1
- **Opp P8** (-4): Our P6 [R]=-5  Our P8 [0, 2, 1]=3  Our P2 [2, 1, 2]=5  Our P7 [B, 1, B, 0, 2]=-7

## Our Team delivery sequence

_Every ball in the order bowled; the pair's second batter in italics._

- **Skin 1** — Our P1 / *Our P2*
  - Opp P2: *R* *2* 2 *2* 0 1
  - Opp P6: 1 *2* 1 *0* *2* *R*
  - Opp P4: 4 *4* 4 *B* *C* 0
  - Opp P6: *w* *1* w 1 *0* *w* *w*
- **Skin 2** — Our P3 / *Our P4*
  - Opp P5: w w 2 *0* *w* nb
  - Opp P1: *0* *w* 0 1 *0* *w*
  - Opp P8: *3* 0 1 *0* *nb* 0
  - Opp P5: *B* *w* *0* *w* 1 *C*
- **Skin 3** — Our P5 / *Our P6*
  - Opp P3: w 0 S C *2* C
  - Opp P4: 0 1 *5* 1 *4* 2
  - Opp P7: 0 1 *2* 1 *2* nb
  - Opp P2: 7 *C* *2* 2 *C* *3*
- **Skin 4** — Our P7 / *Our P8*
  - Opp P1: w 1 *2* 2 *nb* 2
  - Opp P8: 0 2 *0* *1* 2 *1*
  - Opp P7: *2* 2 *0* *1* 0 1
  - Opp P3: 2 *1* 4 *1* 2 *R*

## Opponents delivery sequence

_Every ball in the order bowled; the pair's second batter in italics._

- **Skin 1** — Opp P1 / *Opp P2*
  - Our P2: 0 w 0 2 *2* 2
  - Our P5: 7 *2* 1 *nb* *2* 1
  - Our P4: nb w C *nb* *2* 2
  - Our P1: 3 *2* 3 *2* C *C*
- **Skin 2** — Opp P3 / *Opp P4*
  - Our P6: 2 *w* *0* *2* 2 *4*
  - Our P3: *2* *R* *1* 1 *1* R
  - Our P8: 3 *1* 0 C *2* 2
  - Our P5: R *2* C 1 *1* 2
- **Skin 3** — Opp P5 / *Opp P6*
  - Our P4: 2 *nb* *w* *2* 2 *w*
  - Our P3: 1 *S* R 2 *S* *2*
  - Our P1: *C* 2 *2* 0 2 *2*
  - Our P7: *1* 2 *0* *1* B w
- **Skin 4** — Opp P7 / *Opp P8*
  - Our P6: w 1 *R* C 0 3
  - Our P8: 3 *0* *2* w 1 *1*
  - Our P2: 0 2 *2* *1* 5 *2*
  - Our P7: *B* *1* 1 *B* *0* *2*
