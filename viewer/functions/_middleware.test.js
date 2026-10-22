import test from "node:test"; import assert from "node:assert/strict";
import { onRequest, sign, verify } from "./_middleware.js";

const SECRET = "0123456789abcdef0123456789abcdef";
const ENV = { GATE: "pin", TEAM_PIN: "123456", PIN_SECRET: SECRET };
const now = () => Math.floor(Date.now() / 1000);

function ctx(env, { path = "/", method = "GET", cookie, form } = {}) {
  const headers = new Headers();
  if (cookie) headers.set("Cookie", cookie);
  let body;
  if (form) {
    body = new URLSearchParams(form).toString();
    headers.set("Content-Type", "application/x-www-form-urlencoded");
  }
  return {
    request: new Request(`https://team.example.dev${path}`, { method, headers, body }),
    env,
    next: () => new Response("page"),
  };
}
const cookieFor = async (pin, exp) => `ac_auth=${await sign(`${SECRET}:${pin}`, exp)}`;

test("gate none passes through", async () => {
  const r = await onRequest(ctx({ GATE: "none" }));
  assert.equal(await r.text(), "page");
});

test("gate email passes through (Cloudflare Access guards the site)", async () => {
  const r = await onRequest(ctx({ GATE: "email" }));
  assert.equal(await r.text(), "page");
});

test("gate fails closed", async () => {
  for (const env of [{ GATE: "pin", PIN_SECRET: SECRET }, { GATE: "pin", TEAM_PIN: "123456" }, {}]) {
    const r = await onRequest(ctx(env));
    assert.equal(r.status, 503, JSON.stringify(env));
    assert.match(await r.text(), /gate not configured/);
  }
});

test("no cookie shows pin page", async () => {
  const r = await onRequest(ctx(ENV, { path: "/data/our-team.json" }));
  assert.equal(r.status, 200);
  const body = await r.text();
  assert.ok(body.includes('name="pin"') && body.includes('inputmode="numeric"'));
  assert.ok(!body.includes("page"));
  assert.equal(r.headers.get("Cache-Control"), "no-store");
});

test("correct pin sets cookie", async () => {
  const r = await onRequest(ctx(ENV, { path: "/__pin", method: "POST", form: { pin: "123456" } }));
  assert.equal(r.status, 302);
  assert.equal(r.headers.get("Location"), "/");
  const c = r.headers.get("Set-Cookie");
  assert.ok(c.includes("ac_auth=") && c.includes("Max-Age=15552000"));
  assert.ok(c.includes("HttpOnly") && c.includes("Secure") && c.includes("SameSite=Lax") && c.includes("Path=/"));
  const value = c.match(/ac_auth=([^;]+)/)[1];
  const back = await onRequest(ctx(ENV, { cookie: `ac_auth=${value}` }));
  assert.equal(await back.text(), "page");
});

test("valid cookie passes", async () => {
  const r = await onRequest(ctx(ENV, { cookie: `other=1; ${await cookieFor("123456", now() + 60)}` }));
  assert.equal(await r.text(), "page");
});

test("expired cookie rejected", async () => {
  const r = await onRequest(ctx(ENV, { cookie: await cookieFor("123456", now() - 1) }));
  assert.ok((await r.text()).includes('name="pin"'));
});

test("tampered or foreign cookies rejected", async () => {
  const good = await sign(`${SECRET}:123456`, now() + 60);
  const [exp, mac] = good.split(".");
  for (const c of [`${Number(exp) + 999}.${mac}`, `${exp}.${"0".repeat(64)}`, "garbage", "", `${exp}`]) {
    const r = await onRequest(ctx(ENV, { cookie: `ac_auth=${c}` }));
    assert.ok((await r.text()).includes('name="pin"'), c);
  }
});

test("changing the team code signs everyone out", async () => {
  const old = await cookieFor("123456", now() + 60);
  const r = await onRequest(ctx({ ...ENV, TEAM_PIN: "654321" }, { cookie: old }));
  assert.ok((await r.text()).includes('name="pin"'));
});

test("wrong pin is 401", async () => {
  const t0 = Date.now();
  const r = await onRequest(ctx(ENV, { path: "/__pin", method: "POST", form: { pin: "000000" } }));
  assert.equal(r.status, 401);
  assert.ok(Date.now() - t0 >= 950, "slowed down");
  assert.match(await r.text(), /That code didn.t work/);
  assert.equal(r.headers.get("Set-Cookie"), null);
});

test("sign/verify round trip", async () => {
  const v = await sign("s", now() + 10);
  assert.match(v, /^\d+\.[0-9a-f]{64}$/);
  assert.equal(await verify("s", v), true);
  assert.equal(await verify("t", v), false);
});

test("parallel guessing from one address is throttled; other addresses are not", async () => {
  const guess = (ip, pin) => {
    const c = ctx(ENV, { path: "/__pin", method: "POST", form: { pin } });
    c.request = new Request(c.request, { headers: new Headers([...c.request.headers, ["CF-Connecting-IP", ip]]) });
    return onRequest(c);
  };
  const t0 = Date.now();
  const res = await Promise.all(Array.from({ length: 12 }, (_, i) => guess("203.0.113.9", String(100000 + i))));
  const codes = res.map((r) => r.status);
  assert.ok(codes.filter((s) => s === 429).length >= 7, codes.join(","));
  assert.ok(Date.now() - t0 < 2500, "throttled requests answer at once");
  assert.equal((await guess("203.0.113.9", "123456")).status, 429);       // even the right code waits
  assert.equal((await guess("198.51.100.4", "123456")).status, 302);      // a teammate elsewhere is fine
});
