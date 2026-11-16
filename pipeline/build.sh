#!/usr/bin/env bash
# Build one episode: voice -> music -> captions -> video.
# Usage: pipeline/build.sh episodes/YYYY-MM-DD            (full render)
#        pipeline/build.sh episodes/YYYY-MM-DD --preview  (contact sheet only)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; EP="$(cd "$1" && pwd)"
python3 "$HERE/check_spec.py" "$EP"
python3 "$HERE/voice.py" "$EP"
python3 "$HERE/music.py" "$EP"
python3 "$HERE/captions.py" "$EP"
if [ "${2:-}" = "--preview" ]; then python3 "$HERE/render.py" "$EP" --preview 0.35,0.9; exit; fi
python3 "$HERE/render.py" "$EP"
ffprobe -v error -show_entries stream=codec_type,width,height,duration -of compact "$EP/build/video.mp4"
ls -la "$EP/build/video.mp4"
