import test from "node:test"; import assert from "node:assert/strict";
import { GLOSSARY, glossaryText } from "../help.js";

test("glossary has the agreed keys, each with a title and a one-liner", () => {
  assert.deepEqual(Object.keys(GLOSSARY).sort(),
    ["avg12", "big_hits", "c", "econ", "ranked", "rc", "rs", "skin", "sr", "wkts"]);
  for (const k of Object.keys(GLOSSARY)) {
    assert.ok(GLOSSARY[k].title, k);
    assert.ok(glossaryText(k, {}).length > 20, k);
  }
});

test("wicket value comes from the team's rules", () => {
  assert.match(glossaryText("rs", { wicket_runs: -3 }), /\b3\b/);
  assert.doesNotMatch(glossaryText("rs", { wicket_runs: -3 }), /\b5\b/);
  assert.match(glossaryText("rs", {}), /\b5\b/);            // default rules
  assert.match(glossaryText("rc", { wicket_runs: -3 }), /\b3\b/);
});

test("ranked threshold uses the numbers it is given", () => {
  assert.match(glossaryText("ranked", {}, { season: 3, alltime: 10 }), /3 games.*10/);
});
