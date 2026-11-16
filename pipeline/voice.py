"""Narration: one Kokoro TTS clip per scene ("say" field) -> build/voice.wav + build/durs.json.
Usage: python3 voice.py EPISODE_DIR
"""
import json, os, sys, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

EP = os.path.abspath(sys.argv[1]); BUILD = os.path.join(EP, "build"); os.makedirs(BUILD, exist_ok=True)
spec = json.load(open(os.path.join(EP, "spec.json")))
KD = os.environ.get("KOKORO_DIR", os.path.expanduser("~/.cache/kokoro"))
VOICE = spec.get("voice", "am_michael"); SPEED = spec.get("speed", 1.08)
MIN = dict(hook=4.0, title=4.5, terminal=7.5, code=8.0, bars=7.0, cards=5.0, bullets=5.5, timeline=5.0, cta=5.0, visual=5.0)
LEAD, TAIL = 0.25, 0.55

k = Kokoro(os.path.join(KD, "kokoro-v1.0.onnx"), os.path.join(KD, "voices-v1.0.bin"))
parts, durs, sr0, cues, t0 = [], [], 24000, [], 0.0
for sc in spec["scenes"]:
    if sc.get("say"): a, sr = k.create(sc["say"], voice=VOICE, speed=SPEED, lang="en-us"); sr0 = sr
    else: a, sr = np.zeros(1, np.float32), sr0
    dur = round(max(sc.get("dur", MIN.get(sc["type"], 5.0)), LEAD + len(a) / sr + TAIL) * 30) / 30
    buf = np.zeros(int(round(dur * sr)), dtype=np.float32); s = int(LEAD * sr); buf[s:s + len(a)] = a[: len(buf) - s]
    parts.append(buf); durs.append(dur); cues.append([t0 + LEAD, t0 + LEAD + len(a) / sr, sc.get("say", "")]); t0 += dur
sf.write(os.path.join(BUILD, "voice.wav"), np.concatenate(parts), sr0)
json.dump(durs, open(os.path.join(BUILD, "durs.json"), "w"))
json.dump(cues, open(os.path.join(BUILD, "cues.json"), "w"))
print("voice", round(sum(durs), 2), "s", [round(d, 2) for d in durs])
if sum(durs) > 170: sys.exit("TOO LONG: Shorts must be under 3 minutes; trim the narration")
