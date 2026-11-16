"""Subtitles: split each scene's narration into short cues -> build/captions.srt
Usage: python3 captions.py EPISODE_DIR
"""
import json, os, re, sys
EP = os.path.abspath(sys.argv[1]); BUILD = os.path.join(EP, "build")
cues = json.load(open(os.path.join(BUILD, "cues.json")))
def ts(x):
    return f"{int(x // 3600):02}:{int(x % 3600 // 60):02}:{x % 60:06.3f}".replace(".", ",")
def chunks(text, maxc=42):
    parts = re.split(r"(?<=[.!?,;:])\s+", text.strip()); out = []
    for p in parts:
        words, cur = p.split(), ""
        for w in words:
            if len(cur) + len(w) + 1 > maxc and cur: out.append(cur); cur = w
            else: cur = (cur + " " + w).strip()
        if cur: out.append(cur)
    return out
srt, n = [], 1
for a, b, text in cues:
    cs = chunks(text); tot = sum(len(c) for c in cs) or 1; c0 = a
    for c in cs:
        c1 = c0 + (b - a) * len(c) / tot
        srt.append(f"{n}\n{ts(c0)} --> {ts(c1)}\n{c}\n"); n += 1; c0 = c1
open(os.path.join(BUILD, "captions.srt"), "w").write("\n".join(srt))
print("captions", n - 1, "cues")
