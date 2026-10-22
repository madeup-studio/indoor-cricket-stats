import test from "node:test"; import assert from "node:assert/strict";
import { matchRoute } from "../router.js";
test("routes", () => {
  assert.deepEqual(matchRoute(""), { team: null, name: "home", params: {} });
  assert.deepEqual(matchRoute("#/batting"), { team: null, name: "batting", params: {} });
  assert.deepEqual(matchRoute("#/player/our-p2"), { team: null, name: "player", params: { id: "our-p2" } });
  assert.deepEqual(matchRoute("#/t/our-team/game/2026-10-07-opponents"), { team: "our-team", name: "game", params: { id: "2026-10-07-opponents" } });
  assert.deepEqual(matchRoute("#/nonsense"), { team: null, name: "home", params: {} });
});
test("team prefix with home, unknown names and junk", () => {
  assert.deepEqual(matchRoute("#/t/second-side/home"), { team: "second-side", name: "home", params: {} });
  assert.deepEqual(matchRoute("#/t/second-side"), { team: "second-side", name: "home", params: {} });
  assert.deepEqual(matchRoute("#/t/x/nonsense/1"), { team: "x", name: "home", params: {} });
  assert.deepEqual(matchRoute("#/"), { team: null, name: "home", params: {} });
  assert.deepEqual(matchRoute("#/records/"), { team: null, name: "records", params: {} });
  assert.deepEqual(matchRoute("#/player/our%20p2"), { team: null, name: "player", params: { id: "our p2" } });
});
