import test from "node:test"; import assert from "node:assert/strict";
import { seasonOptionLabel, seasonHeading, stageLabel, isShown, recordVisible, awardRows, awardsBySeason, awardTally } from "../model.js";

const show = { awards: true, medals: true, stage_tags: true, streaks: false, partnerships: true, hattricks: false,
  records: { high_total: true, best_econ: false } };

test("season labels carry the medal", () => {
  assert.equal(seasonOptionLabel({ label: "Spring 2026", medal: "silver" }), "🥈 Spring 2026");
  assert.equal(seasonOptionLabel({ label: "Spring 2026", medal: null }), "Spring 2026");
  assert.equal(seasonHeading({ label: "Spring 2026", medal: "silver", finish: "2nd in Mens E" }), "Spring 2026 · 🥈 2nd in Mens E");
  assert.equal(seasonHeading({ label: "Spring 2026" }), "Spring 2026");
});
test("stage labels", () => {
  assert.equal(stageLabel({ stage: "final" }), "Final");
  assert.equal(stageLabel({ stage: "semi-final" }), "Semi-final");
  assert.equal(stageLabel({ stage: "league" }), null);
  assert.equal(stageLabel({}), null);
});
test("switches: missing means shown, records keys, grouped keys", () => {
  assert.equal(isShown(undefined, "awards"), true);
  assert.equal(isShown(show, "streaks"), false);
  assert.equal(isShown(show, "best_econ"), false);
  assert.equal(isShown(show, "low_total"), true);
  assert.equal(recordVisible(show, "longest_win_streak"), false);
  assert.equal(recordVisible(show, "best_partnership"), true);
  assert.equal(recordVisible(show, "hattricks"), false);
  assert.equal(recordVisible(show, "best_econ"), false);
});
const fin = { key: "s1", label: "Spring 2026", medal: "silver", finish: "2nd", finished: true,
  awards: { player: { name: "Our P2", value: 4.5 }, batter: null, bowler: { name: "Our P3", value: -1.25 } } };
test("award rows only for finished seasons with winners", () => {
  assert.deepEqual(awardRows(fin).map((r) => [r.key, r.name, r.unit]),
    [["player", "Our P2", "avg contribution"], ["bowler", "Our P3", "economy"]]);
  assert.deepEqual(awardRows({ ...fin, finished: false }), []);
  assert.deepEqual(awardRows({ ...fin, awards: { player: null, batter: null, bowler: null } }), []);
  const by = awardsBySeason({ seasons: [fin, { key: "s2", label: "Summer 2027", finished: false, awards: null }] });
  assert.deepEqual(by.map((b) => b.heading), ["Spring 2026 · 🥈 2nd"]);
});
test("award tally", () => {
  assert.equal(awardTally({ awards: { player: 1, batter: 0, bowler: 2 } }), "Player of the season ×1 · Bowler of the season ×2");
  assert.equal(awardTally({ awards: { player: 0, batter: 0, bowler: 0 } }), null);
  assert.equal(awardTally({}), null);
});
