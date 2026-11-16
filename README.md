# Rust Shorts Bot 🦀

Researches a trending Rust topic every day, writes a script, renders a cinematic vertical video
(animated background, motion graphics, AI voiceover, synthesized BGM), and uploads it to YouTube
as Private with a scheduled public time, so the owner can review it first.

```
pipeline/setup.sh      install deps (ffmpeg, Kokoro TTS model, scipy, pillow)
pipeline/build.sh EP   spec.json → voice.wav → music.wav → captions.srt → video.mp4
pipeline/render.py     generic scene renderer (hook, title, bullets, terminal, code, bars, cards, timeline, cta)
RUNBOOK.md             step-by-step instructions the daily Claude session follows
state/history.json     what's been posted (topic de-duplication)
```

Try it locally:
```bash
bash pipeline/setup.sh
pipeline/build.sh samples/async-neon --preview
pipeline/build.sh samples/async-neon
```
