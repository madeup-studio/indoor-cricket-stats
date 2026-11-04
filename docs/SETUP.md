# Set up your team's stats app (about 20 minutes)

You'll end up with a private copy of the app for your team: a link your teammates open
on their phones, behind a team code, updated from your phone after every game.
Claude does the technical parts; you click a few buttons and paste a few things.

## What you need

Only the admin (the person who adds the scorecards) needs any of this. Teammates just
open a link and enter the team code.

- A **GitHub** account (free): https://github.com/signup
- A **Cloudflare** account (free): https://dash.cloudflare.com/sign-up
- A **Claude Pro or Max** plan: https://claude.ai/upgrade (costs: [COSTS.md](COSTS.md))
- The **Claude app** on your phone (iPhone or Android), signed in.

> **Never used GitHub?** It's a website that stores folders of files ("repositories")
> and keeps every change. Your team's repository will hold the scorecards, the stats
> and the app. Sign up at https://github.com/signup with any email, confirm the email
> it sends you, and you're set; you won't need to learn anything else about it. Pick
> **Free** if it asks about plans.

## 1. Make your team's copy

1. Open https://github.com/madeup-studio/indoor-cricket-stats-team (sign in if asked).
2. Tap the green **Use this template** button at the top → **Create a new repository**.
3. Name it (e.g. `our-team-stats`), choose **Private**, then **Create repository**.

You now have your own copy. Nothing in it is shared with anyone.

## 2. Connect Claude to it

1. Open https://claude.ai/code (or the Claude app → **Code**).
2. The first time, it asks to connect GitHub. Allow it. GitHub then shows a page
   asking where to install the Claude app: choose **Only select repositories**, pick
   your new repo, and confirm (**Install & Authorize**).
3. Back in Claude, your repo appears in the list. Choose it to start a session.

## 3. Let Claude reach Cloudflare (once)

Claude's cloud sessions only reach an approved list of websites. Setup needs one more:

1. At https://claude.ai/code, open your environment's settings (the environment name
   next to the repo picker → edit).
2. **Network access** → **Custom**, keep the default list included, and add
   `api.cloudflare.com`.

Prefer not to? Run step 4 once from Claude Code on a computer instead (the desktop
app's **Code** tab with the repo cloned); everything after setup works from the phone.

## 4. Run the setup wizard

Start a session on your repo and type **`/setup`**. Claude walks you through:

1. a Cloudflare **API token** (you create it on Cloudflare's site and paste it in);
2. **how your team gets in**: a team code (recommended), an email list, or an open link;
3. the **Cloudflare project** — your app's address, e.g. `our-team-stats.pages.dev`;
4. two **GitHub secrets** (you paste two values into your repo's settings);
5. **your team**: its name exactly as printed on the scorecards, arena, league,
   badge, scoring rules and the coach's tone (banter, encouraging or serious);
6. the **first deploy**.

At the end Claude gives you the link and the team code, ready to post in the team's
WhatsApp group. The saved token is deleted from the repo; GitHub keeps its own copy as
a secret.

## 5. Your first scorecard

After the game: open the Claude app → **Code** → your repo, attach the scorecard
photo and say **"new scorecard"**. Claude checks every ball, asks about anything it
can't read and new player names, asks once for the league table (or say "skip"),
writes the coach's letter and publishes. The app updates about a minute later.

## About the team code

The team code works like your WhatsApp group: anyone you give it to gets in, and a
phone stays in for 6 months. Change it when someone leaves ("change the team code") and
everyone enters the new one once. Generated codes are 8 digits (your own: at least 6
characters) and repeated wrong guesses are slowed down, but it is a shared code, not a password per person. If your team wants to
know exactly who can look, choose the **email list** instead: only listed addresses get
in, each with a one-time code by email.

## Things you can tell Claude later

- "We finished second this season" (adds the medal)
- "Mark the game on 2026-11-20 as the final"
- "Hide best partnership" · "Show awards"
- "Add Sam as an admin"
- "Give the coach a personality: a grumpy old pro"

## Keeping up to date

Your repo carries its own copy of the engine in `engine/` (version in
`engine/VERSION`), so nothing changes unless you ask. To update, tell Claude
"update the engine", or run `python engine/scripts/update_engine.py` (add
`--tag v1.2.3` to pick a version). Then publish once.

## Check it works

- [ ] The link opens a "Enter the team code" page; the code opens the app.
- [ ] After the first scorecard: the game appears under **Games**, with its skins, both
      teams' figures and the coach's letter.
- [ ] **Batting**, **Bowling**, **All-round** and **Players** list your players; tapping
      one opens their page.
- [ ] **Records** shows all-time by default; the season picker changes every screen.
- [ ] On a phone, "Add to Home Screen" gives an app icon.
- [ ] A second scorecard updates everything within about a minute of Claude publishing.

## If something's off

- **The deploy failed** (Claude says so, or GitHub → Actions shows a red cross): usually a
  typo in a secret name. They must be exactly `CLOUDFLARE_API_TOKEN` and
  `CLOUDFLARE_ACCOUNT_ID`. Ask Claude to check with you.
- **The link says "gate not configured"**: the team code wasn't saved. Run `/setup`
  again; it skips what's done.
- **"can't reach api.cloudflare.com"**: step 3.
- **A number looks wrong**: tell Claude which game and what the card says. Games are only
  published when every ball adds up, so it's usually a misread name or cell.

There is no support for this project; Claude in your repo is your best helper.
