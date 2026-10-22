import test from "node:test"; import assert from "node:assert/strict";
import { safeHtml } from "../sanitize.js";

test("keeps the formatting the coach uses", () => {
  assert.equal(safeHtml("<p>Lost <b>51–80</b>, <i>again</i>.</p><p>Next: <strong>run</strong></p>"),
    "<p>Lost <b>51–80</b>, <i>again</i>.</p><p>Next: <strong>run</strong></p>");
  assert.equal(safeHtml("a<br>b<ul><li>x</li></ul>"), "a<br>b<ul><li>x</li></ul>");
});

test("drops attributes and every other tag; escapes stray markup", () => {
  assert.equal(safeHtml('<p onclick="x()">hi</p>'), "<p>hi</p>");
  assert.equal(safeHtml('<img src=x onerror="alert(1)">ok'), "ok");
  assert.equal(safeHtml("<script>alert(1)</script>"), "alert(1)");
  assert.equal(safeHtml("<scr<script>ipt>alert(1)</script>"), "ipt&gt;alert(1)");
  assert.equal(safeHtml('<a href="javascript:alert(1)">x</a>'), "x");
  assert.equal(safeHtml("<!-- c --> 1 < 2 > 0"), "&lt;!-- c --&gt; 1 &lt; 2 &gt; 0");
  assert.equal(safeHtml('<svg><g onload="x"></g></svg>'), "");
});

test("keeps entities, escapes bare ampersands", () => {
  assert.equal(safeHtml("Q&A &amp; R&#38;D &mdash;"), "Q&amp;A &amp; R&#38;D &mdash;");
  assert.equal(safeHtml(undefined), "");
});
