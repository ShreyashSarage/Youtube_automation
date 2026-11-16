# rust-shorts-bot

Automated daily "Rust Zero to Pro" YouTube Short (beginner to advanced lessons, see state/curriculum.json).
- When a run asks you to make today's video, follow **RUNBOOK.md** step by step.
- Pipeline code is in `pipeline/` (render, voice, music, captions). Don't change it during a daily run
  unless a bug blocks the video; if you fix something, commit it separately with a clear message.
- Example specs: `samples/` (`samples/library` shows every visual). Posted history: `state/history.json`.
