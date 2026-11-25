# Rust Projects: long-form video runbook (every other day, 18:00 IST)

A fresh Claude Code cloud session makes **one 10-14 minute, horizontal (1920x1080) project video** that
builds a real, useful Rust project from scratch, then posts it on the owner's YouTube channel.
`TODAY` = today's date in Asia/Kolkata. Follow the steps in order.

**Golden rules**
- Everything shown in a terminal is **real output** from `engine/capture.py`. Never type an output by hand.
- Code must compile and work: the capture fails the run if any command fails (unless marked `may_fail`).
- Explain like a friendly human teacher: why, not just what. Connect concepts to the daily Shorts
  ("structs, from Rust Day 18"). No hype, no filler.
- Never post twice: if `state/longform_history.json` has an entry with `date` == TODAY, stop and report.
- If anything fails and you can't fix it, do not publish; report what failed.

## 1. Setup
```bash
bash pipeline/setup.sh          # ffmpeg, Kokoro voice, Python deps (same as the Shorts)
```

## 2. Pick the project
The first project in `state/longform_plan.json` whose `slug` is not in `state/longform_history.json`.
Its `covers` and `crates` say what to teach. Projects must run offline here (crates.io is reachable;
other internet hosts may not be): use local servers, sample files you create, etc.

## 3. Build the project for real: `longform/<slug>/`
```
longform/<slug>/project/...      the finished source files (Cargo.toml comes from `cargo add` in the capture)
longform/<slug>/capture.json     the commands the video shows, in order (see engine/capture.py docstring)
```
Write clean, idiomatic, commented code (~60-150 lines total; lines ≤ 80 chars so the editor stays readable).
Then run:
```bash
python3 longform/engine/capture.py longform/<slug>      # runs every command in a fresh fake home
```
Fix the project until every step succeeds and the outputs show what you want to teach
(happy path, a helpful error, a release build). Re-run the capture after every change.
For servers: a step with `"background": true` then `{"kill": "<id>"}` after the client commands.
When the capture is final, save the real `Cargo.toml` it produced (a `cat Cargo.toml` step) as
`longform/<slug>/project/Cargo.toml` and add a `.gitignore` with `/target`, so the code link in the description builds as-is.

## 4. Write `longform/<slug>/script.py`
Copy the structure of **`longform/todo-cli/script.py`** (the reference): PROJECT, PROMPT_DIR, TREE,
TREE_INITIAL, TREE_LATER, FILES, DIAGRAMS, and SHOTS. Shot types:
- `terminal` with `actions`: `C("<capture id>")` replays a captured command + its real output
  (`speed` = lines per second for long outputs). `T("clear")` clears. `term=3` for a separate terminal.
- `editor` with `file` + `type=(start, end)`: types those lines (0-based, end exclusive) of FILES[file];
  or `show=True` + `highlight=[line numbers]`.
- `diagram` with `diagram="<key in DIAGRAMS>"`: hand-drawn whiteboard; nodes/edges/notes appear in order
  (board coordinates: 1680 x 890; colors orange/blue/green/purple/gray/red).
- `title` (intro: `chips`; outro: `outro=True`).
Structure (≈ 1,400-1,800 words of narration total):
cold open (the finished app working) → intro → plan diagram → create project → crates → code in
4-8 editor chunks (explain each chunk: what and why) → a flow diagram → run it (happy path) → edge cases
and errors → release build / install / next steps → outro with a practice challenge.
Add `chapter="Step N · ..."` to the first shot of each section (becomes YouTube chapters).

## 5. Check, then render
```bash
python3 longform/engine/render_longform.py longform/<slug> --stills   # build/stills.png, 2 tiles per shot
```
Look at every tile: nothing overlapping or cut off, code readable, terminal output matches the narration.
Fix and re-check. Then:
```bash
python3 longform/engine/render_longform.py longform/<slug>             # build/video.mp4, video.srt, chapters.txt
```
(The first run generates the narration and camera paths: allow ~45-60 min in total.)

## 6. Thumbnail (16:9, 1280x720)
Make `longform/<slug>/thumbnail_16x9.jpg` in the style of `longform/kiri-mqtt/thumbnail_16x9.jpg`:
big 2-3 word title, a crop of the real terminal/code from the video, a small "STEP BY STEP" badge.
Long videos DO accept custom thumbnails: pass it as `options.youtube.thumbnailMediaId` (upload it with
`media_presign` like the video). If YouTube refuses it (unverified channel), publish without it and say so.

## 7. Publish (Uplika "ulika" tools)
Title (search phrase first: the OUTCOME a viewer searches for, not the project name), e.g.
`Automatically Organize Your Downloads Folder with Rust (Beginner Project) | Rust Projects #2` or
`Rust Project for Beginners: Build a Todo CLI App Step by Step | Rust Projects #1`. ≤ 100 chars, no `<` or `>` anywhere.
Description: 2-line summary, `🔗 Code: https://github.com/ShreyashSarage/Youtube_automation/tree/main/longform/<slug>/project`,
the chapters from `build/chapters.txt`, the commands, versions, "Related Shorts" (the Rust Day N videos
for the concepts used, from `state/history.json`), 8-12 hashtags.
`media_presign` → `curl -X PUT` (must print 200) → `media_complete` → `publish` with
`options.youtube = {title, tags, privacyStatus: "private", publishAt: "<TODAY>T18:00:00+05:30",
categoryId: "28", defaultLanguage: "en", containsSyntheticMedia: false}` (if 18:00 has passed: public now).

## 8. Record and push
Append `{"slug", "date", "url", "title"}` to `state/longform_history.json`; commit `longform/<slug>/`
(project, capture.json, captures/, script.py, thumbnail; not build/) and push to `main`.
Final report: project, title, link, public time, and anything to check.
