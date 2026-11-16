"""Validate an episode spec before spending time on rendering.  Usage: python3 check_spec.py EPISODE_DIR"""
import json, os, sys
EP = sys.argv[1]; s = json.load(open(os.path.join(EP, "spec.json"))); errs = []
REQ = dict(hook=["big"], title=["title"], bullets=["heading", "items"], terminal=["heading", "commands"], code=["heading", "code"],
           bars=["heading", "bars"], cards=["heading", "cards"], timeline=["heading", "points"], cta=[])
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
if not 5 <= len(sc) <= 9: errs.append(f"{len(sc)} scenes; use 5-9")
if sc and sc[0].get("type") != "hook": errs.append("first scene should be type 'hook'")
if sc and sc[-1].get("type") != "cta": errs.append("last scene should be type 'cta'")
for i, x in enumerate(sc):
    if x.get("type") not in REQ: errs.append(f"scene {i}: unknown type {x.get('type')}"); continue
    for f in REQ[x["type"]] + ["say"]:
        if not x.get(f): errs.append(f"scene {i} ({x['type']}): missing '{f}'")
    if x.get("type") == "code":
        cl = x.get("code", "").rstrip("\n").split("\n")
        if len(cl) > 12: errs.append(f"scene {i}: code has {len(cl)} lines (max 12)")
        lw = max(len(l) for l in cl) if cl else 0
        if lw > 34: errs.append(f"scene {i}: code line {lw} chars (max 34, phones need big text)")
    if len(x.get("say", "").split()) > 55: errs.append(f"scene {i}: narration over 55 words")
if errs: print("SPEC ERRORS:\n  " + "\n  ".join(errs)); sys.exit(1)
print("spec ok:", len(sc), "scenes")
