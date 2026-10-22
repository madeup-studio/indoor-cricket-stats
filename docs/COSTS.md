# What it costs

Each team runs its own copy on its own accounts. Nobody else pays for your games,
and you pay for nobody else's.

## Claude (the admin)

The team admin uses Claude to read each scorecard and write the coach's letter, from
the **Claude app on their phone** (Code tab) or Claude Code on a computer.

- **A Claude Pro or Max subscription** covers it. Each game uses part of the plan's
  normal usage limits (one scorecard, a few questions, one letter) — there is no
  separate charge. The free Claude plan doesn't include Claude Code.
- **An Anthropic API key** instead (pay per use, mainly for Claude Code on a
  computer): roughly a few rand to a few tens of rand per game, depending on how
  much back-and-forth a smudged card needs.

Only the admin needs Claude. Everyone else just opens the link.

## Cloudflare (hosting the app)

- **Cloudflare Pages: free.** The app is a few small static files plus the team-code
  function; a team's traffic is far inside the free limits.
- **Team code or open link: free, no card.**
- **Email list (Cloudflare Access): free** for up to 50 people on the Zero Trust free
  plan. Cloudflare asks for a card on file for Zero Trust; it doesn't charge for the
  free plan.

## GitHub (your team's data)

- **Private repo: free.**
- **GitHub Actions:** each publish runs a deploy of about a minute, well inside the
  free monthly minutes for private repos.

## Summary

| | Team code / open link | Email list |
|---|---|---|
| Claude | your Pro/Max subscription (or a few rand per game on an API key) | same |
| Cloudflare | free, no card | free, card on file |
| GitHub | free | free |
