# Daily Rust Short: runbook

Each daily run is a fresh Claude Code cloud session. Follow these steps in order. Today's date is
`TODAY` (YYYY-MM-DD, **Asia/Kolkata** time); the episode folder is `episodes/TODAY/`.

**Golden rules**
- Every factual claim (numbers, dates, features, quotes) must come from a source you actually read
  today, listed in `spec.json → sources`. If you can't source it, cut it.
- Self-reported benchmarks are labelled "author's benchmark" / "claimed" on screen and in narration.
- Never post twice in one day: if `state/history.json` already has an entry for TODAY, stop and report.
- If any step fails and you can't fix it, **do not publish**. Report what failed instead.
- Videos are uploaded **Private** with a scheduled public time (owner reviews in YouTube Studio).

## 1. Setup (about 1 min)
```bash
bash pipeline/setup.sh
```

## 2. Pick today's topic (about 5 min)
Search the web (WebSearch; "extended" mode for news) for what's trending in Rust in the **last 7 days**:
- Rust releases and RFCs/stabilizations: blog.rust-lang.org, "This Week in Rust" (this-week-in-rust.org)
- New or trending Rust crates/tools: Hacker News "Show HN" Rust, r/rust top posts this week, GitHub trending Rust
- Notable adoption news (a company or project moving to Rust, Linux kernel Rust, etc.)

Pick **one** topic that is (a) fresh, (b) interesting to a broad dev audience, (c) explainable in
under 75 s, and (d) not in the last 60 entries of `state/history.json` (check `topic` and `title`).
Prefer: big news > hot new tool > a new feature in a recent stable release > an evergreen Rust tip
(use a tip only on slow news days). Read at least the primary source (official blog, repo README,
release notes), plus a second source for anything surprising.

## 3. Write `episodes/TODAY/spec.json`
Schema (see `samples/kiri-ocean`, `samples/ownership-matrix`, `samples/async-neon`):
```jsonc
{
  "topic": "short topic label (used for de-duplication)",
  "sources": ["https://primary-source", "https://second-source"],
  "brand": "RUST  ·  DAILY",            // optional HUD label
  "voice": "am_michael",                 // optional Kokoro voice
  "youtube": {
    "title": "≤ 70 chars ideally (100 max), hook + emoji 🦀; no < or >",
    "description": "see template below",
    "tags": ["10-20 search tags, total < 480 chars"]
  },
  "scenes": [ /* 5-8 scenes; first is hook, last is cta. Every scene has "say" (≤ 45 words ideal). */ ]
}
```
Scene types and fields:
| type | fields |
|---|---|
| `hook` | `top` (small mono line), `big` (big orange; may contain `{n}` with `count` to animate a counter), `sub` [lines] |
| `title` | `kicker`, `title` (big name), `bullets` [≤ 3 short lines] |
| `bullets` | `heading`, `sub`, `items` [≤ 4, ≤ 40 chars each] |
| `terminal` | `heading`, `sub`, `commands` [[cmd, output], ≤ 3], `checks` [≤ 3] |
| `code` | `heading`, `sub`, `file`, `code` (≤ 12 lines, each ≤ 34 chars, real compilable Rust), `highlight` [line numbers], `caption` |
| `bars` | `heading`, `sub`, `bars` [{label, value, unit, highlight, decimals}] ≤ 4, `callout`, `footnote` [lines] |
| `cards` | `heading`, `cards` [{title, text, highlight}] ≤ 4 |
| `timeline` | `heading`, `points` [{top, bottom}] ≤ 3, `callout`, `sub` |
| `cta` | `heading`, `link` (short, no https://), `question` [lines], `sub` |

| `visual` | `visual` (one of the motion graphics below), `heading`, `sub`, `caption`, plus that visual's params |

**Motion graphics come from the title.** Run `python3 pipeline/suggest.py "<your title>"` to get
the colour `theme` (set it top-level in the spec) and visuals ranked for the topic. Then:
- The `hook` gets `"visual": "<best visual>"` so the first frame already shows the subject.
- At least **max(2, scenes − 3)** scenes are `visual` scenes (the spec check enforces it); use `code` / `terminal` / `bars` only where
  real code, commands or numbers are the point. Pick the visual that *shows* what the narration says.

| visual | shows | params |
|---|---|---|
| `containers` | isometric containers dropping onto a platform | `label`, `count` |
| `race` | lanes racing to a checkered finish, times pop in | `lanes` [{label, value, decimals}], `unit` (real numbers only) |
| `gauge` | speedometer needle + counting number | `value`, `max`, `unit`, `label`, `decimals` |
| `ownership` | stack vars → heap value, arrow moves, old owner struck out | `a`, `b`, `value`, `note` |
| `shield` | memory grid, a bad pointer gets blocked by a shield | `label` |
| `lanes` | async runtime dispatching tasks across lanes, `.await` pauses | `labels` [≤ 5], `hub` |
| `compiler` | source file → particles → gears → binary + ✓ badge | `file`, `output`, `badge` |
| `network` | server hub with nodes and packets flowing | `center`, `nodes` [labels] |
| `layers` | isometric stack; highlighted layer drops in | `layers` [bottom→top, ≤ 5], `highlight` (index) |
| `tree` | dependency tree growing from a root crate | `root`, `children` [{name, children: [..]}] |

Themes: `rust` (orange/blue), `ocean` (cyan, containers/cloud/web), `matrix` (green, safety/memory),
`neon` (pink/purple, async), `gold` (releases/compiler). See `samples/*/spec.json` for full examples.

Writing style: punchy, conversational, one idea per scene. On-screen text matches the narration.
Hook in the first 2 s (a question or a surprising number). Total 35-75 s. Spell out
things TTS might misread in `say` (e.g. "github dot com slash ...", "version 1.90").
Code shown on screen must be real Rust; if you're unsure it compiles, test it with `rustc` / `cargo`
if available, or keep it to a snippet you have verified against the docs.

Description template (≤ 13 hashtags total, YouTube ignores all of them if > 15):
```
<2-line hook summary: what + why it matters>

✅ <key point 1>
✅ <key point 2>
✅ <key point 3>

<1-2 sentences of context / caveats>

🔗 Sources:
<url 1>
<url 2>

💬 <question for comments> 👇
🔔 Subscribe for a Rust update every day.

#rust #rustlang #programming #<3-8 topic hashtags> #shorts
```

## 4. Build
```bash
pipeline/build.sh episodes/TODAY --preview   # validates spec, makes episodes/TODAY/build/preview.png
```
Look at `preview.png` with the Read tool. Fix text that overflows, overlaps, or is too small, then
re-run. When it looks right:
```bash
pipeline/build.sh episodes/TODAY             # about 3-5 min → episodes/TODAY/build/video.mp4
```

## 5. Upload and schedule on YouTube (Uplika connector)
1. `select_channels` with scope `["youtube"]` → the account id (expected handle: `shreyashsarage`).
   If it is missing or unhealthy, stop and report: reconnect at https://uplika.com/dashboard/connections.
2. `media_presign` (fileName `rust-short-TODAY.mp4`, contentType `video/mp4`, bytes = file size,
   width 1080, height 1920, durationMs, aiGenerated false).
3. Upload the bytes:
   `curl -sS --retry 3 -X PUT -H "Content-Type: video/mp4" --upload-file episodes/TODAY/build/video.mp4 "<uploadUrl>"`
   (it must print HTTP 200; the host `s3.us-west-004.backblazeb2.com` is allowed in this environment).
4. `media_complete` with the media id.
5. `publish` with `wait: true`, `content` = description, and
   `options.youtube = { title, tags, privacyStatus: "private", publishAt: "<TODAY>T18:00:00+05:30",
   categoryId: "28", defaultLanguage: "en", containsSyntheticMedia: false }`.
   If 18:00 IST today has already passed, use tomorrow 18:00 IST.
6. Confirm the target status is `published` (uploaded) and note the permalink and any warning.

## 6. Record and push
Append to `state/history.json → posted`:
`{"date": TODAY, "topic": ..., "title": ..., "url": permalink, "publishAt": ..., "sources": [...]}`.
Then commit `episodes/TODAY/spec.json` and `state/history.json` (videos are git-ignored) and push to `main`.

## 7. Final report (your last message)
Topic, title, YouTube link, scheduled public time (IST), sources, and anything the owner should check
before it goes public (e.g. a claim that rests on a single source). If something failed, say exactly
which step and why.
