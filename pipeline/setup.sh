#!/usr/bin/env bash
# Installs everything the pipeline needs. Idempotent; safe to re-run.
set -euo pipefail
command -v ffmpeg >/dev/null || { apt-get update -qq && apt-get install -y -qq ffmpeg; }
fc-list | grep -q DejaVuSans-Bold || apt-get install -y -qq fonts-dejavu-core
python3 -m pip install -q --disable-pip-version-check kokoro-onnx soundfile scipy numpy pillow 2>&1 | grep -v "WARNING: Running pip" || true
KD="${KOKORO_DIR:-$HOME/.cache/kokoro}"; mkdir -p "$KD"
BASE=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
[ -s "$KD/kokoro-v1.0.onnx" ] || curl -sSfL --retry 3 -o "$KD/kokoro-v1.0.onnx" "$BASE/kokoro-v1.0.onnx"
[ -s "$KD/voices-v1.0.bin" ]  || curl -sSfL --retry 3 -o "$KD/voices-v1.0.bin"  "$BASE/voices-v1.0.bin"
echo "setup ok"
