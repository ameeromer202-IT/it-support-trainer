# IT Support Trainer — a Service Desk RPG

A single-file, pixel-art browser game for drilling **Tier 1/2 IT support** interview
material — troubleshooting method, the PC boot chain, Windows internals, networking,
Active Directory, Apple/MDM, service-desk ops, and security basics. Study turns into a
retro RPG: earn XP, climb ranks, walk an overworld map of "realms," and face **the Board**
(a mock interview panel) as the final boss.

> **▶ Live demo:** https://ameeromer202-it.github.io/it-support-trainer/
> The full game — Course, Match, the overworld, XP and progress — runs entirely in the
> browser with no backend. Two features (the **Sensei** tutor and **Spar** answer-grading)
> call a local Claude Code CLI via the included server; without it the rest of the game is
> unaffected (see [Running the Claude-powered features](#running-the-claude-powered-features)).

## Screenshots

**The dashboard** — level, XP bar, streak, next-up card, and the countdown to the Board.

![The dashboard: XP bar, streak, continue-where-you-left-off card, and Claude training modes](screenshots/dashboard.png)

**The overworld** — a Canvas-2D star map of the eight realms; walk the hero between nodes,
each showing your mastery %, and follow the road to the boss castle.

![The overworld map: eight realm nodes with mastery percentages, linked by paths to the Board](screenshots/overworld.png)

## What's inside

- **The Course** — chapters of bite-sized cards across 8 realms (Hardware & Boot, Windows,
  Networking, Identity/AD, Apple/MDM, Service Desk, Security, Scenarios). Each card teaches
  one concept fundamentals-first, with the "one sentence that separates a tech from a good tech."
- **Match** — a timed arcade drill with a decaying **chain multiplier** and best-time chase.
- **The Board** — a 16-scenario boss run: 3 hearts, real-world tickets, headline-first answers.
- **Overworld** — a hand-rolled Canvas-2D star map; walk a pixel hero between realm nodes and
  a boss castle, each showing your mastery %.
- **Sensei** — an in-game tutor NPC that teaches your weakest realm, powered by Claude.
- **Spar** — say an answer out loud, type it, and Claude grades the **beats** (content and
  structure) — never your phrasing or tone.
- **Progress & juice** — persistent XP/level/streak, ZzFX sound effects, confetti, screen-shake,
  level-up flashes, and a light/dark retro theme.

## Tech

- **One file, zero build.** `index.html` is vanilla HTML/CSS/JS — no framework, no bundler,
  no runtime dependencies. Open it and it runs.
- **Pixel-art UI** in an indie-game design language: `Press Start 2P` / `JetBrains Mono`,
  sharp 0-radius components, tinted-outline chips and cards, segmented progress bars, and
  ~50 hand-rendered pixel icons drawn to inline SVG from grid data.
- **Canvas-2D overworld** drawn synchronously (not `requestAnimationFrame`-gated) so it renders
  deterministically everywhere.
- **Audio** via [ZzFX](https://github.com/KilledByAPixel/ZzFX) (SFX only), confetti via
  [canvas-confetti], motion via [anime.js] — all inlined.
- **AI features** shell out to a local [Claude Code](https://claude.com/claude-code) CLI
  through `serve.py` (Python standard library only) — no API key, runs on your subscription.

## Run it locally

Static (everything except Sensei/Spar):

```bash
# any static server works, e.g.
python -m http.server 8377
# then open http://localhost:8377/
```

### Running the Claude-powered features

The **Sensei** tutor and **Spar** grading need `serve.py` (adds `/ask-claude`) and a local
[Claude Code](https://claude.com/claude-code) CLI on your `PATH`:

```bash
python serve.py
# open http://localhost:8377/
```

`serve.py` uses only the Python standard library. It runs `claude -p` headless on your machine,
so it uses your local Claude Code install/subscription — **no API key required**. If the CLI
isn't found, the game detects it and those two features go quietly offline while the rest keeps
working.

## Notes

- Set your own interview date near the top of `index.html` (`const INTERVIEW = ...`) to make the
  dashboard countdown real; it defaults to 14 days out so the countdown is always live.
- Game state saves to `localStorage` in the browser, and (when the server is running) a coaching
  snapshot is written to `game/dojo-progress.json` for the Sensei to read.

## License

MIT — see [LICENSE](LICENSE).
