# Daily "Rust Zero to Pro" Short: runbook

Each daily run is a fresh Claude Code cloud session that makes **one beginner-friendly lesson** and
schedules it to go public at **12:00 IST (noon)**. Follow these steps in order.

`TODAY` = today's date in **Asia/Kolkata** (YYYY-MM-DD). Episode folder: `episodes/TODAY/`.

**Golden rules**
- Audience: someone learning Rust from zero. One concept per video, plain words, define any jargon.
- Everything taught must match the official docs (The Rust Book / std docs / the crate's docs).
  Read the lesson's `source` page today before writing. If unsure, leave it out.
- All code shown must compile; `pipeline/check_code.py` enforces it (it runs in the build).
- Never post twice in one day: if `state/history.json` already has an entry with `date` == TODAY,
  stop and report. If any step fails and you can't fix it, **do not publish**; report what failed.

## 1. Setup (about 1 min)
```bash
bash pipeline/setup.sh
```

## 2. Pick today's lesson
Open `state/curriculum.json` and take the **first lesson whose `day` is not in `state/history.json`**
(field `day`). Also note the lesson after it (for the "Tomorrow:" teaser). Read its `source` URL
(WebFetch or the web-fetch agent) and, if needed, the matching std docs page.

## 3. Write `episodes/TODAY/spec.json`
Look at **`samples/kiri-ocean`** and **`samples/ownership-matrix`**: these are the owner's reference
styles (theme + motion graphics). Day parity picks the theme: **odd day → `"ocean"`, even day → `"matrix"`**.

Required top level:
```jsonc
{
  "day": 4,
  "topic": "Variables & mutability",            // lesson title
  "theme": "matrix",                             // odd=ocean, even=matrix
  "brand": "RUST  ·  DAY 4",
  "sources": ["<lesson source url>", "..."],
  "youtube": { "title": "...", "description": "...", "tags": [...] },
  "scenes": [ ... ]
}
```

### Scene structure (6-7 scenes, 45-70 s total)
1. `hook` with a `visual` from the lesson's `visuals`: `top` = "Rust Day N", `big` = a 2-5 word
   curiosity hook ("Why can't I change x?"), `sub` = [one short line].
2. `visual`: show the concept (e.g. `vars`, `ownership`, `flow`, `pipeline`, `layers`, `tree`).
3. `code`: the minimal real example. Add `expect` with the exact output when it prints something.
4. `visual`: what happens when the code runs (the "aha" moment).
5. `code` with `expect_error` (a common beginner mistake + the compiler error code), **or** a
   `visual` tip such as `shield`. Say the fix in the narration.
6. `bullets` heading "Recap": 3 items, each ≤ 32 chars.
7. `cta`: `heading` "Day N ✓", `link` = short docs link (no https://), `question` = ["Tomorrow: <next lesson>"],
   `sub` "Follow to learn Rust daily".

At least 2 `visual` scenes (the spec check enforces it). The hook must have a `visual`.

### Visuals (pick what *shows* the narration)
| visual | shows | params |
|---|---|---|
| `vars` | variable boxes; `mut` ones change value, immutable ones shake + "cannot assign twice" | `items` [{name, value, mut, change}] ≤ 3 |
| `flow` | a value tests match/if arms in order, lands on the matching one | `input`, `kind` ("match"/"if"), `arms` [{pattern, result}] ≤ 4, `hit` (index) |
| `pipeline` | iterator stages, values flow down and transform | `stages` [{name, out: [values]}] ≤ 4 (values must be correct!) |
| `ownership` | stack vars → heap value; `mode: "move"` (default) strikes the old owner, `"borrow"` draws a dashed reference | `a`, `b`, `value`, `note`, `mode` |
| `shield` | memory grid, a bad pointer gets blocked | `label` |
| `compiler` | file → gears → binary ✓ | `file`, `output`, `badge` |
| `layers` | isometric stack, highlighted layer drops in | `layers` [bottom→top] ≤ 5, `highlight` |
| `tree` | tree growing from a root | `root`, `children` [{name, children: [..]}] |
| `lanes` | runtime dispatching tasks/threads | `labels` ≤ 5, `hub` |
| `network` | hub + nodes + packets | `center`, `nodes` |
| `race` / `gauge` | comparisons / one big number | see `pipeline/visuals.py` (real numbers only) |
| `containers` | isometric containers | `label`, `count` |

Other scene types: `code` (`heading`, `sub`, `file`, `code` ≤ 12 lines × ≤ 34 chars, `highlight`
[line numbers], `caption`, `check`, `expect`, `expect_error`), `bullets` (`heading`, `items`), `cta`.
Every scene needs `say` (narration, ≤ 40 words is ideal). On-screen text must match what's said.
Spell out symbols for the voice: "let mut x", "x equals five", "ampersand s" for `&s`,
"double colon" for `::`, "vec bang" for `vec!`, "println bang".

### Code scenes must compile
`code` is what's shown (short lines). If it's a snippet, put a **full program** in `check` that
contains it, e.g. code `let mut x = 5;\nx = 6;\nprintln!("{x}");` with
check `fn main() {\n    let mut x = 5;\n    x = 6;\n    println!("{x}");\n}` and expect `6`.
Mistake scenes: `expect_error: "E0384"` (the build fails if it compiles or the code differs).

### Thumbnail (cover frame)
YouTube does not accept uploaded thumbnails for Shorts, so the pipeline renders a designed cover
(`build/thumbnail.png`) and uses it as the **first frames** of the video. Add to the spec:
```jsonc
"thumbnail": { "lines": ["WHY LEARN", "RUST?"],   // 1-2 punchy lines, ≤ 11 chars each, CAPS; line 2 is accent-coloured
               "visual": "shield",                 // the most telling visual for the lesson
               "params": { "label": "memory safe · no GC" } }   // optional overrides for that visual
```
`DAY N`, `IN 60 SECONDS` and the series name are added automatically. The render also writes
`build/thumbnail_16x9.jpg` (1280×720) and `build/thumbnail_vertical.jpg` (1080×1920), both < 2 MB,
for the owner to upload by hand in YouTube Studio. Check `thumbnail.png` (it is
also the first tile of `preview.png`) before rendering.

### Title, description, tags (trendy, searchable)
- Title (≤ 70 chars): `Rust Day N: <Lesson> in 60 Seconds 🦀` or a hook form like
  `Why Rust Won't Let You Change x 🦀 | Rust Day N`.
- Description: use this template, 10-13 hashtags total (YouTube ignores all if > 15):
```
Rust Day N: <lesson>. <one-sentence hook / what you'll learn>.

📌 In this short:
✅ <point 1>
✅ <point 2>
✅ <point 3>

💻 Code from the video:
<the main code snippet, plain text>

📖 Learn more: <source url>
⏭️ Tomorrow: <next lesson title>

Follow for a new Rust lesson every day at 12 PM IST, from zero to pro 🦀
💬 Questions? Drop them in the comments 👇

#rust #rustlang #learnrust #rustprogramming #programming #coding #codingforbeginners #learntocode #100daysofcode #developer #<1-2 lesson tags> #shorts
```
- Tags (≤ 480 chars total): `rust`, `rust programming`, `learn rust`, `rust tutorial`,
  `rust for beginners`, `rust day N`, `rustlang`, `<lesson keywords x3-5>`, `programming`, `coding`.

## 4. Build
```bash
pipeline/build.sh episodes/TODAY --preview   # spec + code checks, then build/preview.png
```
Read `preview.png`. Fix any overflow, overlap or tiny text, then:
```bash
pipeline/build.sh episodes/TODAY             # about 3-5 min → build/video.mp4 (captions burned in)
```

## 5. Upload and schedule (Uplika connector)
1. `select_channels` scope `["youtube"]` → account id (handle `shreyashsarage`). Missing/unhealthy →
   stop and report: reconnect at https://uplika.com/dashboard/connections.
2. `media_presign` (fileName `rust-day-N.mp4`, `video/mp4`, bytes, width 1080, height 1920, durationMs, aiGenerated false).
3. `curl -sS --retry 3 -o /dev/null -w "%{http_code}\n" -X PUT -H "Content-Type: video/mp4" --upload-file episodes/TODAY/build/video.mp4 "<uploadUrl>"` → must print 200.
4. `media_complete`.
5. `publish` with `wait: true`, `content` = description, `options.youtube` =
   `{ title, tags, privacyStatus: "private", publishAt: "<TODAY>T12:00:00+05:30", categoryId: "27",
   defaultLanguage: "en", containsSyntheticMedia: false }` (27 = Education). If 12:00 IST has
   passed (or is less than 20 min away), use tomorrow 12:00.
6. Confirm status `published` (uploaded + scheduled); note permalink and warnings.

## 6. Record and push
Append to `state/history.json → posted`:
`{"date": TODAY, "day": N, "topic": ..., "title": ..., "url": ..., "publishAt": ..., "sources": [...]}`.
Copy `build/thumbnail_16x9.jpg` and `build/thumbnail_vertical.jpg` into `episodes/TODAY/`.
Commit `episodes/TODAY/spec.json`, the two thumbnails and `state/history.json` (videos are git-ignored) and push to `main`:
`git -c push.negotiate=true push origin main` (retry up to 4 times on network errors).

## 7. Final report (last message)
Day number, lesson, title, YouTube link, scheduled time (IST), and anything the owner should check.
Attach both thumbnails with SendUserFile if that tool exists, and give their GitHub links
(`https://github.com/ShreyashSarage/Youtube_automation/blob/main/episodes/TODAY/thumbnail_16x9.jpg`, same for `thumbnail_vertical.jpg`)
with the reminder: YouTube Studio → Content → the video → Thumbnail → Upload file.
If something failed, say which step and why.
