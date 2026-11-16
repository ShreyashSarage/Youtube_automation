# Rust Zero to Pro: daily YouTube Shorts 🦀

Every day a Claude Code cloud session makes the next lesson in `state/curriculum.json`
(60 lessons, beginner → advanced), renders a vertical Short with topic-driven motion graphics,
AI voiceover, synthesized music and burned-in captions, and uploads it to YouTube (via Uplika)
as Private, scheduled to go public at **18:00 IST**.

```
RUNBOOK.md              step-by-step instructions each daily run follows
state/curriculum.json   the lesson plan (edit freely; order = beginner → advanced)
state/history.json      what has been posted
episodes/YYYY-MM-DD/    each day's spec.json (video files are not committed)
samples/                reference styles: kiri-ocean, ownership-matrix (+ async-neon, library)
pipeline/
  setup.sh              installs ffmpeg deps, Kokoro TTS model, scipy, pillow
  build.sh EP           check_spec → check_code (rustc) → voice → music → captions → render
  render.py             scene renderer (hook, visual, code, terminal, bars, cards, timeline, bullets, cta)
  visuals.py            13 motion graphics (vars, flow, pipeline, ownership, shield, compiler, ...)
  suggest.py            theme + visuals from a title
  fetch_doc.py          read Rust Book pages (from the Book's Markdown source)
```

Local try-out:
```bash
bash pipeline/setup.sh
pipeline/build.sh samples/ownership-matrix --preview
```
