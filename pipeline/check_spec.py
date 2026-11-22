"""Validate an episode spec before spending time on rendering.  Usage: python3 check_spec.py EPISODE_DIR"""
import json, os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from visuals import VISUALS as VIS
EP = sys.argv[1]; s = json.load(open(os.path.join(EP, "spec.json"))); errs = []
REQ = dict(run=["heading", "from_code"], hook=["big"], title=["title"], bullets=["heading", "items"], terminal=["heading", "commands"], code=["heading", "code"],
           bars=["heading", "bars"], cards=["heading", "cards"], timeline=["heading", "points"], cta=[], visual=["visual"])
for k in ("topic", "sources", "youtube", "scenes"):
    if k not in s: errs.append(f"missing top-level '{k}'")
yt = s.get("youtube", {})
if not yt.get("title") or len(yt["title"]) > 100 or "<" in yt["title"] or ">" in yt["title"]: errs.append("youtube.title missing, >100 chars, or contains < >")
if len(yt.get("description", "").encode()) > 4900: errs.append("youtube.description > 4900 bytes")
tags = yt.get("tags", []); tl = sum(len(t) + (2 if " " in t else 0) for t in tags) + max(0, len(tags) - 1)
if tl > 480: errs.append(f"youtube.tags too long ({tl} > 480)")
if yt.get("description", "").count("#") > 15: errs.append("more than 15 hashtags: YouTube would ignore all of them")
if not s.get("sources"): errs.append("no sources listed: every claim needs a source")
sc = s.get("scenes", [])
if not 5 <= len(sc) <= 10: errs.append(f"{len(sc)} scenes; use 5-10")
if sc and sc[0].get("type") != "hook": errs.append("first scene should be type 'hook'")
if sc and sc[-1].get("type") != "cta": errs.append("last scene should be type 'cta'")
for i, x in enumerate(sc):
    if x.get("type") not in REQ: errs.append(f"scene {i}: unknown type {x.get('type')}"); continue
    if x.get("visual") and x["visual"] not in VIS: errs.append(f"scene {i}: unknown visual {x['visual']} (have: {', '.join(VIS)})")
    for f in REQ[x["type"]] + ([] if x.get("dur") else ["say"]):
        if not x.get(f): errs.append(f"scene {i} ({x['type']}): missing '{f}'")
    if x.get("type") == "code":
        cl = x.get("code", "").rstrip("\n").split("\n")
        if len(cl) > 12: errs.append(f"scene {i}: code has {len(cl)} lines (max 12)")
        lw = max(len(l) for l in cl) if cl else 0
        if lw > 34: errs.append(f"scene {i}: code line {lw} chars (max 34, phones need big text)")
    if len(x.get("say", "").split()) > 55: errs.append(f"scene {i}: narration over 55 words")
nv = sum(1 for x in sc if x.get("type") == "visual")
need = 2
if nv < need: errs.append(f"only {nv} 'visual' scenes; use at least {need} (motion graphics from the title)")
if sc and not sc[0].get("visual"): errs.append("hook has no 'visual'; set one from pipeline/suggest.py")
if s.get("theme") not in (None, "rust", "ocean", "matrix", "neon", "gold"): errs.append(f"unknown theme {s.get('theme')}")
th = s.get("thumbnail")
if not th or not th.get("lines"): errs.append("missing thumbnail.lines (1-2 punchy CAPS lines for the cover frame)")
elif any(len(l) > 14 for l in th["lines"]): errs.append("thumbnail lines must be 14 chars or fewer each")
if th and th.get("visual") and th["visual"] not in VIS: errs.append(f"thumbnail.visual {th['visual']} unknown")
words = sum(len(x.get("say", "").split()) for x in sc)
if words > 190: errs.append(f"narration is {words} words; keep it <= 185 so the Short stays under 1:20")
if words < 120: errs.append(f"narration is only {words} words; explain the topic in detail (140-185 words)")
if "#shorts" not in yt.get("title", "").lower(): errs.append("youtube.title must end with #Shorts")
if s.get("day", 0) >= 9:  # hook + title rules (owner, Nov 22): search phrase first, payoff in the first second
    title = yt.get("title", "")
    if re.match(r"\s*rust day", title, re.I): errs.append("title must START with the search phrase, not 'Rust Day N' (put '| Rust Day N' at the end)")
    if not re.search(r"\|\s*Rust Day %d\b" % s["day"], title): errs.append(f"title must end with '| Rust Day {s['day']} #Shorts'")
    if len(title) > 90: errs.append(f"title is {len(title)} chars; keep it <= 90 so the search phrase isn't cut off")
    if sc:
        hs = sc[0].get("say", "")
        if re.search(r"\bday\s+\w+", hs.split(".")[0], re.I) or hs.lower().startswith("rust,"): errs.append("hook narration must not open with 'Rust, day N': open with the payoff (a surprising result, error or question)")
        if len(hs.split()) > 16: errs.append(f"hook narration is {len(hs.split())} words; keep it <= 16 (the first 2 seconds decide the swipe)")
    first = yt.get("description", "").split("\n")[0]
    if re.match(r"\s*rust day", first, re.I): errs.append("description's first line must lead with the search phrase, not 'Rust Day N'")
if len(sc) > 10: errs.append("use at most 10 scenes so the Short stays under 1:20")
from collections import Counter
for vname, cnt in Counter(x.get("visual") for x in sc if x.get("visual")).items():
    if cnt > 2: errs.append(f"visual '{vname}' is used {cnt} times; use each at most twice")
if not any(x.get("type") == "run" for x in sc): errs.append("add a 'run' scene (from_code) so viewers see the real program output or compiler error")
if not any(x.get("type") == "code" and x.get("steps") for x in sc): errs.append("at least one code scene needs 'steps' (line-by-line walkthrough)")
LIM = {"heading": 30, "sub": 40, "caption": 34, "top": 22}
for i, x in enumerate(sc):
    for f_, n_ in LIM.items():
        if isinstance(x.get(f_), str) and len(x[f_]) > n_: errs.append(f"scene {i}: {f_} is {len(x[f_])} chars (max {n_})")
    if isinstance(x.get("big"), str) and len(x["big"]) > 26: errs.append(f"scene {i}: big is {len(x['big'])} chars (max 26)")
    for it in x.get("items", []) if x.get("type") == "bullets" else []:
        if len(it) > 30: errs.append(f"scene {i}: bullet '{it}' > 30 chars")
    for st in x.get("steps", []):
        if len(st.get("note", "")) > 34: errs.append(f"scene {i}: step note '{st.get('note')}' > 34 chars")
        if not st.get("at") or st["at"].lower() not in x.get("say", "").lower(): errs.append(f"scene {i}: step 'at' must be a phrase from this scene's say, so the highlight moves with the voice ({st.get('at')!r})")
        if any(ln < 1 or ln > len(x.get("code", "").split("\n")) for ln in st.get("lines", [])): errs.append(f"scene {i}: step line out of range")
if errs: print("SPEC ERRORS:\n  " + "\n  ".join(errs)); sys.exit(1)
print("spec ok:", len(sc), "scenes")
