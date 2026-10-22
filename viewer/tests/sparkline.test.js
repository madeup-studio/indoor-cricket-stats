import test from "node:test"; import assert from "node:assert/strict";
import { sparkPoints } from "../sparkline.js";

test("points span the box, highest value at the top", () => {
  const { points, zeroY } = sparkPoints([0, 10, 5], 100, 20, 2);
  assert.equal(points.length, 3);
  assert.deepEqual(points[0], [2, 18]);      // min at the bottom (inside the 2px pad)
  assert.deepEqual(points[1], [50, 2]);      // max at the top
  assert.deepEqual(points[2], [98, 10]);
  assert.equal(zeroY, null);                 // never crosses zero: no zero line
});

test("a zero line when the values cross zero", () => {
  const { zeroY } = sparkPoints([-5, 5], 100, 22, 1);
  assert.equal(zeroY, 11);
});

test("one value or a flat line never produces NaN", () => {
  for (const vals of [[3], [4, 4, 4], []]) {
    const { points } = sparkPoints(vals, 120, 32, 2);
    for (const [x, y] of points) assert.ok(Number.isFinite(x) && Number.isFinite(y), String(vals));
  }
});
