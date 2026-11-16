"""Subtitles: split each scene's narration into short cues -> build/captions.srt
Usage: python3 captions.py EPISODE_DIR
"""
import json, os, re, sys
EP = os.path.abspath(sys.argv[1]); BUILD = os.path.join(EP, "build")
cues = json.load(open(os.path.join(BUILD, "cues.json")))
spec = json.load(open(os.path.join(EP, "spec.json")))
# narration is spelled out for the TTS voice; captions should show real code
FIX = [(r"\bF N\b", "fn"), (r"\b(\w+) bang\b", r"\1!"), (r"\brust format\b", "rustfmt"), (r"\bdouble colon\b", "::"),
       (r"\bampersand mut (\w+)", r"&mut \1"), (r"\bampersand (\w+)", r"&\1"), (r"\bdot await\b", ".await"), (r"\bdot unwrap\b", ".unwrap()"),
       (r"\bR S\b", "rs"), (r"\bi thirty two\b", "i32"), (r"\bu thirty two\b", "u32"), (r"\bf sixty four\b", "f64")]
FIX += [(re.escape(a), b) for a, b in spec.get("caption_fix", {}).items()]
for c, sc in zip(cues, spec["scenes"]):
    txt = sc.get("captions", c[2])
    for a, b in FIX: txt = re.sub(a, b, txt, flags=re.I) if a.startswith("\\b") else re.sub(a, b, txt)
    c[2] = txt
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
def timed(maxc):
    out = []
    for a, b, text in cues:
        if not text.strip(): continue
        cs = chunks(text, maxc); tot = sum(len(c) for c in cs) or 1; c0 = a
        for c in cs:
            c1 = c0 + (b - a) * len(c) / tot; out.append([c0, c1, c]); c0 = c1
    return out
srt = [f"{i + 1}\n{ts(a)} --> {ts(b)}\n{c}\n" for i, (a, b, c) in enumerate(timed(42))]
open(os.path.join(BUILD, "captions.srt"), "w").write("\n".join(srt)); n = len(srt) + 1
json.dump(timed(24), open(os.path.join(BUILD, "captions_burn.json"), "w"))  # short phrases burned into the video
print("captions", n - 1, "cues")
