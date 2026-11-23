---
name: rust-short-preflight
description: Pre-publish gate for the daily "Rust Zero to Pro" Short. Use after writing episodes/TODAY/spec.json and before `pipeline/build.sh` and before any Uplika publish call, or whenever someone asks to check, validate, lint or QA a Rust Short spec. Catches the RUNBOOK rules that pipeline/check_spec.py does not enforce: posting twice in one day, skipping or repeating a curriculum day, wrong odd/even theme, missing lesson source, < or > in the description, a wrong "Tomorrow" teaser, hashtag count, scene order and thumbnail line length.
---

# Rust Short preflight

`check_spec.py` (run by `build.sh`) checks scene fields, word counts and title format. This skill
adds the checks that depend on **state** (history, curriculum, today's IST date) and the
publishing rules from RUNBOOK.md steps 2, 3 and 5.

## When to run

1. Right after writing `episodes/TODAY/spec.json` (RUNBOOK step 3), **before** `build.sh --preview`.
2. Again right before the Uplika `publish` call (RUNBOOK step 5), in case the spec was edited.

## How

```bash
python3 .claude/skills/rust-short-preflight/preflight.py episodes/TODAY
```

- Exit `0`: carry on. `WARN` lines are worth fixing but never block.
- Exit `1`: every `FAIL` line is a reason **not to publish**. Fix the spec and run it again.
  If a FAIL says history already has today's date or the day is already posted, **stop the run
  and report** (RUNBOOK golden rule: never post twice in one day). Don't edit history to get past it.

Options:
- `--date YYYY-MM-DD` uses a different "today" (default: the current date in Asia/Kolkata).
- `--recheck` re-checks an episode that's already posted, skipping the history and curriculum-order checks.
  Use it to audit old specs, never for today's run.

## What it checks

| Check | Blocks? | RUNBOOK rule |
|---|---|---|
| No `history.json` entry dated today | yes | Golden rule: never post twice in one day |
| `day` not posted yet, and equals the first unposted curriculum day | yes | Step 2 |
| Odd day → `ocean`, even day → `matrix` | yes | Step 3 (theme) |
| `sources` includes the lesson's curriculum `source` | yes | Golden rule: matches the official docs |
| No `<` / `>` in the description | yes | Title/description rules |
| First scene `hook`, last scene `cta`, `thumbnail` present, lines ≤ 11 chars | yes | Scene structure / thumbnail |
| 8-10 scenes, an `expect_error` mistake scene | warn | Scene structure |
| CTA and description tease the next curriculum lesson | warn | Step 3 (cta, description template) |
| 10-15 hashtags in the description | warn | Description template |
| `brand` is `RUST  ·  DAY N` | warn | Step 3 |

## Extending it

Each check is a few lines in `preflight.py` that append to `errs` (blocking) or `warns`. When the
owner adds a rule to RUNBOOK.md that `check_spec.py` doesn't enforce, add it here and add a row to the table.
Rules about a single field's format belong in `check_spec.py`. Rules that need history, the curriculum
or the date belong here.
