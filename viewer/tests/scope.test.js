import test from "node:test"; import assert from "node:assert/strict";
import { defaultScope, resolveScope } from "../scope.js";

const data = { seasons: [{ key: "2026-03-01" }, { key: "2026-09-01" }] };

test("every screen defaults to the latest season", () => {
  assert.equal(defaultScope("records", data), "2026-09-01");
  for (const r of ["home", "batting", "coach", "games", "player"]) assert.equal(defaultScope(r, data), "2026-09-01");
  assert.equal(defaultScope("batting", { seasons: [] }), "alltime");
});

test("a scope the viewer chose wins on every route while it is valid", () => {
  assert.equal(resolveScope("records", data, null), "2026-09-01");
  assert.equal(resolveScope("records", data, "2026-03-01"), "2026-03-01");
  assert.equal(resolveScope("batting", data, "alltime"), "alltime");
  assert.equal(resolveScope("batting", data, "1999-01-01"), "2026-09-01");   // another team's season
});
