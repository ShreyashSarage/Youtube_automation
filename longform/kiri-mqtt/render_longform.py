"""Render the horizontal screencast tutorial from script.py.

python3 render_longform.py            full render -> build/kiri_mqtt_tutorial.mp4 (+ .srt, thumbnail)
python3 render_longform.py --stills   contact sheet of a few frames per shot -> build/stills.png
"""
import hashlib, json, math, os, random, re, subprocess, sys, bisect
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import script as S
BUILD = os.path.join(HERE, "build"); os.makedirs(BUILD, exist_ok=True)
W, H, FPS = 1920, 1080, 30
FD = "/usr/share/fonts/truetype/dejavu/"; _fc = {}
def font(n, s):
    k = (n, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(FD + n, s)
    return _fc[k]
MONO = lambda s: font("DejaVuSansMono.ttf", s); MONOB = lambda s: font("DejaVuSansMono-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s); SANSB = lambda s: font("DejaVuSans-Bold.ttf", s)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(t): t = clamp(t); return t * t * (3 - 2 * t)
def eout(t): t = clamp(t); return 1 - (1 - t) ** 3

# ------------------------------------------------------------------ audio: narration
def voice_for(text, key):
    path = os.path.join(BUILD, f"vo_{key}_{hashlib.md5((text + '|1.08').encode()).hexdigest()[:8]}.wav")
    if not os.path.exists(path):
        import soundfile as sf
        from kokoro_onnx import Kokoro
        global _K
        if "_K" not in globals():
            kd = os.path.expanduser("~/.cache/kokoro"); _K = Kokoro(kd + "/kokoro-v1.0.onnx", kd + "/voices-v1.0.bin")
        a, sr = _K.create(text, voice="am_michael", speed=1.08, lang="en-us"); sf.write(path, a, sr)
    import soundfile as sf
    a, sr = sf.read(path); return a.astype(np.float32), sr

# ------------------------------------------------------------------ timeline
rng = random.Random(7)
EV = {"t1": [], "t2": [], "t3": [], "ed": [], "keys": [], "clicks": [], "mouse": [], "badge": []}
SHOTS = []  # dicts: start, dur, shot
CHAPTERS = []

def type_times(text, cps, t0):
    """Human-ish keystroke times."""
    ts = []; t = t0
    for i, ch in enumerate(text):
        base = 1.0 / cps
        dt = base * rng.uniform(0.55, 1.6)
        if ch == " ": dt *= 1.25
        if i and text[i - 1] in ",.;({": dt *= 1.4
        if rng.random() < 0.025: dt += rng.uniform(0.2, 0.5)  # tiny hesitation
        t += dt; ts.append(t)
    return ts

TERM_POS = {"single": {1: (70, 64, 1780, 970)}, "split": {1: (30, 64, 920, 970), 2: (970, 64, 920, 970)}}
def prompt_text(d): return f"dev@ubuntu:{S.PROMPT_DIR[d]}$ "

def schedule():
    t = 0.0; last_dir = {1: "home", 2: "proj"}
    for si, sh in enumerate(S.SHOTS):
        a, sr = voice_for(sh["say"], sh["id"]); vdur = len(a) / sr
        start = t; cur = t + 0.6
        scene = sh["scene"]
        if sh.get("chapter"): CHAPTERS.append((start + 0.2, sh["chapter"]))
        if scene in ("terminal", "split"):
            layout = "split" if scene == "split" else "single"
            for act in sh.get("actions", []):
                term = act.get("term", 1); key = f"t{term}"
                if act["kind"] == "cmd":
                    d = act.get("dir", "proj"); last_dir[term] = d
                    EV["mouse"].append((cur, ("term", layout, term)))
                    if scene == "split": EV["clicks"].append(cur + 0.45); cur += 0.6
                    EV[key].append((cur, "prompt", prompt_text(d)))
                    cmd = act["cmd"]; cps = 11 if len(cmd) < 45 else 19
                    ts = type_times(cmd, cps, cur + 0.25)
                    for i, tt in enumerate(ts): EV[key].append((tt, "set_input", cmd[:i + 1])); EV["keys"].append(tt)
                    cur = ts[-1] + rng.uniform(0.25, 0.45); EV[key].append((cur, "enter", None)); EV["keys"].append(cur)
                    if cmd == "clear":
                        EV[key].append((cur + 0.05, "clear", None)); cur += 0.3
                        continue
                    if act.get("keys"):  # sudo password prompt
                        EV[key].append((cur + 0.2, "line", act["keys"])); cur += 1.4
                        for k in range(8): EV["keys"].append(cur - 1.0 + k * 0.1)
                    if act.get("stream"):
                        st = act["stream"]; t_first = st[0][0]; tt0 = cur + 0.3
                        build_end = max((x for x, l in st if "exporting" in l or "Built" in l), default=t_first)
                        for x, l in st:
                            rel = x - t_first
                            # the image build is shown 3x faster than real time
                            dt = rel / 3.0 if x <= build_end else (build_end - t_first) / 3.0 + (x - build_end)
                            EV[key].append((tt0 + dt / act.get("speed", 1.0), "line", l))
                        last = tt0 + ((build_end - t_first) / 3.0 + (st[-1][0] - build_end)) / act.get("speed", 1.0)
                        if any(x <= build_end and "#" in l for x, l in st): EV["badge"].append((tt0, tt0 + (build_end - t_first) / 3.0, "▶▶  3× speed"))
                        cur = last + act.get("pause", 0.6)
                    elif act.get("bg"):
                        bg = act["bg"]; L = bg["lines"]; anchor = cur + 0.25; t_a = L[0][0]
                        bgt = [anchor + (x - t_a) for x, _ in L]
                        for (x, l), tt in zip(L, bgt): EV[f"t{bg['term']}"].append((tt, "line", l))
                        outl = act.get("out", "").split("\n"); times = []
                        for l, pat in zip(outl, bg["sync"]):
                            tt = next(tt for (x, ll), tt in zip(L, bgt) if pat in ll) + 0.03; EV[key].append((tt, "line", l)); times.append(tt)
                        cur = max(bgt[-1], times[-1]) + act.get("pause", 0.6)
                        EV[f"t{bg['term']}"].append((bgt[-1] + 0.01, "noop", None))
                    else:
                        out = act.get("out", "")
                        lines = out.split("\n") if out else []
                        sp = act.get("speed"); tt = cur + rng.uniform(0.12, 0.35); times = []
                        for l in lines:
                            EV[key].append((tt, "line", l)); times.append(tt)
                            tt += (1.0 / sp) if sp else 0.0
                        act["_times"] = times
                        cur = tt + act.get("pause", 0.6)
                    EV[key].append((cur, "prompt_idle", prompt_text(last_dir[term])))
                elif act["kind"] == "reveal":
                    prev = sh["actions"][sh["actions"].index(act) - 1]; times = prev.get("_times", [])[1:]
                    for l, tt in zip(act["text"].split("\n"), times): EV[key].append((tt + 0.04, "line", l))
                elif act["kind"] == "keys":
                    EV["mouse"].append((cur, ("term", layout, term)))
                    if scene == "split": EV["clicks"].append(cur + 0.45); cur += 0.6
                    EV["badge"].append((cur, cur + 1.6, act["keys"])); EV["keys"].append(cur + 0.1)
                    for i, l in enumerate(act["text"].split("\n")):
                        EV[key].append((cur + 0.15 + i * 0.35, "input_line" if i == 0 else "line", l))
                    cur += 0.25 + 0.35 * len(act["text"].split("\n")) + 0.8
                    EV[key].append((cur, "prompt_idle", prompt_text(last_dir[term])))
        elif scene == "editor":
            f = sh["file"]; full = S.FILES[f]
            EV["mouse"].append((cur, ("file", f))); EV["clicks"].append(cur + 0.55)
            EV["ed"].append((cur + 0.6, "open", f)); cur += 0.9
            if sh.get("show"):
                EV["ed"].append((cur, "set", (f, len(full), 0)))
                for i, ln in enumerate(sh.get("highlight", [])): EV["ed"].append((cur + 1.0 + i * 0.4, "hl", ln))
            else:
                a0, b0 = sh["type"]; b0 = min(b0, len(full))
                EV["ed"].append((cur, "set", (f, a0, 0)))
                chunk = "\n".join(full[a0:b0]); typed = re.sub(r"(?m)^ +", "", chunk)  # indentation is auto
                avail = max(4.0, vdur * 0.9 - 1.2); cps = clamp(len(typed) / avail, 9, 24)
                ts = type_times(typed, cps, cur + 0.3); k = 0
                # map typed chars back to (line, col) in the full file
                pos = []
                for li in range(a0, b0):
                    line = full[li]; ind = len(line) - len(line.lstrip(" "))
                    for c in range(ind, len(line)): pos.append((li, c + 1))
                    pos.append((li + 1, 0))  # newline
                pos = pos[:len(typed)]
                for tt, (li, col) in zip(ts, pos):
                    EV["ed"].append((tt, "set", (f, li, col))); EV["keys"].append(tt)
                cur = (ts[-1] if ts else cur) + 0.6
                EV["ed"].append((cur, "set", (f, b0, 0)))
        else:
            cur = start + 1.0
        dur = max(vdur + 1.4, cur - start + 0.8)
        if scene == "title" and sh.get("outro"): dur += 2.0
        SHOTS.append(dict(start=start, dur=dur, shot=sh, voice=(a, sr)))
        t = start + dur
    return t

TOTAL = schedule()
NFR = int(TOTAL * FPS)
STARTS = [s["start"] for s in SHOTS]
for k in EV: EV[k].sort(key=lambda e: e[0] if isinstance(e, tuple) else e)
EVT = {k: [e[0] if isinstance(e, tuple) else e for e in v] for k, v in EV.items()}

def shot_at(t):
    i = max(0, bisect.bisect_right(STARTS, t) - 1); return i, SHOTS[i]

# ------------------------------------------------------------------ state reconstruction
def term_state(key, t):
    lines = []; inp = None; prompt = None
    n = bisect.bisect_right(EVT[key], t)
    for (_, op, val) in EV[key][:n]:
        if op == "prompt": prompt = val; inp = ""
        elif op == "set_input": inp = val
        elif op == "enter": lines.append(("cmd", prompt or "", inp or "")); inp = None; prompt = None
        elif op == "clear": lines = []
        elif op == "line": lines.append(("out", "", val))
        elif op == "input_line":
            if prompt is not None: lines.append(("cmd", prompt, (inp or "") + val)); prompt = None; inp = None
            else: lines.append(("out", "", val))
        elif op == "prompt_idle": prompt = val; inp = ""
        elif op == "noop": pass
    return lines, prompt, inp

def editor_state(t):
    n = bisect.bisect_right(EVT["ed"], t); f = None; opened = []; cur = {}; hl = []
    for (tt, op, val) in EV["ed"][:n]:
        if op == "open":
            f = val; hl = []
            if val not in opened: opened.append(val)
        elif op == "set": cur[val[0]] = (val[1], val[2])
        elif op == "hl": hl.append((val, tt))
    return f, opened, cur, hl

# ------------------------------------------------------------------ desktop
def make_wallpaper():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    a = np.zeros((H, W, 3), np.float32)
    g = (x / W * 0.6 + y / H * 0.4)
    c1, c2 = np.array([24, 18, 46]), np.array([92, 34, 70])
    a[:] = c1 * (1 - g[..., None]) + c2 * g[..., None]
    for cx, cy, r, col in ((0.8, 0.25, 0.45, (200, 80, 60)), (0.15, 0.85, 0.5, (40, 90, 160))):
        d = np.exp(-(((x / W - cx) ** 2 + (y / H - cy) ** 2) / (r * r)) * 3)[..., None]
        a += d * np.array(col) * 0.35
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img); d.rectangle((0, 0, W, 34), fill=(14, 14, 16))
    d.text((18, 7), "Activities", font=SANSB(17), fill=(235, 235, 235))
    for i, xx in enumerate((W - 120, W - 90, W - 60)): d.ellipse((xx, 11, xx + 12, 23), outline=(220, 220, 220), width=2)
    return img
WALL = make_wallpaper()
def clock_str(t):
    m = 41 + int(t // 60); return f"Tue Nov 17  {14 + m // 60:02d}:{m % 60:02d}"

def win_frame(img, x, y, w, h, title, focused=True, light=False):
    d = ImageDraw.Draw(img)
    sh = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((30, 36, w + 30, h + 36), 14, fill=(0, 0, 0, 120))
    img.paste(sh.filter(ImageFilter.GaussianBlur(14)), (x - 30, y - 30), sh.filter(ImageFilter.GaussianBlur(14)))
    head = (235, 235, 235) if light else ((48, 48, 52) if focused else (40, 40, 44))
    d.rounded_rectangle((x, y, x + w, y + h), 12, fill=(250, 250, 250) if light else (30, 30, 32))
    d.rounded_rectangle((x, y, x + w, y + 46), 12, fill=head); d.rectangle((x, y + 30, x + w, y + 46), fill=head)
    tc = (40, 40, 40) if light else (225, 225, 225)
    tw = d.textlength(title, font=SANSB(17)); d.text((x + (w - tw) / 2, y + 13), title, font=SANSB(17), fill=tc)
    for i, c in enumerate(((120, 120, 120), (120, 120, 120), (200, 70, 60))):
        cx = x + w - 30 - i * 34; d.ellipse((cx - 9, y + 14, cx + 9, y + 32), fill=c if i == 0 or not light else c)
    return x, y + 46

# ------------------------------------------------------------------ terminal drawing
TFS = 22; TCW = MONO(TFS).getlength("M"); TLH = 30
SERVICE_COL = {"broker": (90, 200, 230), "subscriber": (230, 200, 90), "publisher": (130, 220, 120)}
def out_segments(l):
    m = re.match(r"^(\s*)(Compiling|Finished|Adding|Updating|Locking|Creating|Downloaded|Downloading)\b(.*)$", l)
    if m: return [(m.group(1), (220, 220, 220), False), (m.group(2), (120, 220, 90), True), (m.group(3), (220, 220, 220), False)]
    m = re.match(r"^(\w+)-1(\s*\|)(.*)$", l)
    if m: return [(m.group(1) + "-1" + m.group(2), SERVICE_COL.get(m.group(1), (200, 200, 200)), False), (m.group(3), (225, 225, 225), False)]
    if l.startswith("note:"): return [("note", (110, 190, 255), True), (l[4:], (220, 220, 220), False)]
    if re.match(r"^\s+\+ ", l): return [(l, (150, 210, 150), False)]
    if re.match(r"^\s+- ", l): return [(l, (150, 150, 150), False)]
    if re.match(r"^#\d+ ", l) or l.startswith(" Image") or l.startswith(" Container") or l.startswith(" Network"): return [(l, (165, 165, 175), False)]
    if l.endswith(": OK") or l in ("active", "cgroup2fs") or "can use Kiri now" in l: return [(l, (120, 220, 90), True)]
    return [(l, (225, 225, 225), False)]

def draw_terminal(img, rect, key, t, title, focused):
    x, y, w, h = rect; bx, by = win_frame(img, x, y, w, h, title, focused)
    d = ImageDraw.Draw(img); cols = int((w - 36) / TCW); rows = int((h - 46 - 24) / TLH)
    lines, prompt, inp = term_state(key, t)
    vis = []
    for kind, p, txt in lines:
        if kind == "cmd": segs = [(p.split(":")[0], (138, 226, 52), True), (":", (225, 225, 225), False), (p.split(":", 1)[1][:-2], (114, 159, 207), True), ("$ ", (225, 225, 225), False), (txt, (235, 235, 235), False)]
        else: segs = out_segments(txt)
        vis += wrap_segs(segs, cols)
    caret = None
    if prompt is not None:
        segs = [(prompt.split(":")[0], (138, 226, 52), True), (":", (225, 225, 225), False), (prompt.split(":", 1)[1][:-2], (114, 159, 207), True), ("$ ", (225, 225, 225), False), (inp or "", (235, 235, 235), False)]
        wl = wrap_segs(segs, cols); vis += wl; caret = (len(vis) - 1, sum(len(s[0]) for s in wl[-1]))
    start = max(0, len(vis) - rows)
    for r, segs in enumerate(vis[start:]):
        xx = bx + 18; yy = by + 12 + r * TLH
        for txt, col, bold in segs:
            d.text((xx, yy), txt, font=(MONOB if bold else MONO)(TFS), fill=col); xx += TCW * len(txt)
    focus = None
    if caret:
        r = caret[0] - start; cx = bx + 18 + caret[1] * TCW; cy = by + 12 + r * TLH
        if focused and (int(t * 2) % 2 == 0 or inp): d.rectangle((cx, cy + 2, cx + TCW - 1, cy + TLH - 4), fill=(225, 225, 225))
        focus = (cx, cy)
    elif vis:
        r = min(len(vis), rows) - 1; focus = (bx + 18 + 20 * TCW, by + 12 + r * TLH)
    return focus

def wrap_segs(segs, cols):
    out = [[]]; n = 0
    for txt, col, bold in segs:
        while txt:
            room = cols - n
            if room <= 0: out.append([]); n = 0; continue
            piece, txt = txt[:room], txt[room:]
            out[-1].append((piece, col, bold)); n += len(piece)
    return out

# ------------------------------------------------------------------ editor drawing
EFS = 22; ECW = MONO(EFS).getlength("M"); ELH = 31
KW = set("fn let mut pub struct enum impl use mod match if else for while loop return async await move ref as in const static type unsafe dyn self Self crate super true false Some None Ok Err break".split())
def hl_rust(line):
    out = []
    for m in re.finditer(r'(//.*$)|(r#".*?"#|"(?:[^"\\]|\\.)*")|(#\[[^\]]*\])|([A-Za-z_][A-Za-z0-9_]*!?)|(\d[\d_\.]*)|(\s+)|(.)', line):
        tok = m.group(0)
        if m.group(1): out.append((tok, (106, 153, 85)))
        elif m.group(2): out.append((tok, (206, 145, 120)))
        elif m.group(3): out.append((tok, (190, 190, 120)))
        elif m.group(4):
            if tok.endswith("!"): out.append((tok, (86, 156, 214)))
            elif tok in KW: out.append((tok, (197, 134, 192)))
            elif tok[0].isupper(): out.append((tok, (78, 201, 176)))
            else: out.append((tok, (156, 220, 254)))
        elif m.group(5): out.append((tok, (181, 206, 168)))
        else: out.append((tok, (212, 212, 212)))
    return out
def hl_conf(line, lang):
    if line.strip().startswith("#"): return [(line, (106, 153, 85))]
    if lang == "dockerfile":
        m = re.match(r"^(\s*)([A-Z]+)(\b.*)$", line)
        if m: return [(m.group(1), (212, 212, 212)), (m.group(2), (86, 156, 214)), (m.group(3), (206, 145, 120))]
    if lang in ("yaml", "toml"):
        m = re.match(r'^(\s*-?\s*)([\w\-\.]+)(\s*[:=])(.*)$', line)
        if m: return [(m.group(1), (212, 212, 212)), (m.group(2), (156, 220, 254)), (m.group(3), (212, 212, 212)), (m.group(4), (206, 145, 120))]
        if re.match(r"^\s*\[.*\]\s*$", line): return [(line, (78, 201, 176))]
    if lang == "conf":
        p = line.split(" ", 1); return [(p[0], (156, 220, 254))] + ([(" " + p[1], (206, 145, 120))] if len(p) > 1 else [])
    return [(line, (206, 145, 120) if lang == "yaml" else (212, 212, 212))]
def lang_of(f):
    return "rust" if f.endswith(".rs") else "toml" if f.endswith(".toml") else "yaml" if f.endswith(".yaml") else "dockerfile" if f.endswith("Dockerfile") else "conf"

ED_RECT = (40, 64, 1840, 980)
TREE_ORDER = ["mosquitto/", "mosquitto/mosquitto.conf", "src/", "src/bin/", "src/bin/publisher.rs", "src/bin/subscriber.rs", ".dockerignore", ".gitignore", "Cargo.lock", "Cargo.toml", "compose.yaml", "Dockerfile"]
def files_known(t):
    known = {".gitignore", "Cargo.toml", "Cargo.lock", "mosquitto/", "src/", "src/bin/"}
    for f in S.FILES:
        if any(e[0] <= t and e[1] == "open" and e[2] == f for e in EV["ed"]): known.add(f)
    if t >= SHOTS[[s["shot"]["id"] for s in SHOTS].index("dockerfile")]["start"]: known.add(".dockerignore")
    return known
def tree_rows(t):
    k = files_known(t); rows = []
    for p in TREE_ORDER:
        if p not in k: continue
        depth = p.rstrip("/").count("/"); name = p.rstrip("/").split("/")[-1]
        rows.append((p, depth, name, p.endswith("/")))
    return rows
def draw_editor(img, t, hl_now):
    x, y, w, h = ED_RECT; f, opened, cur, hls = editor_state(t)
    bx, by = win_frame(img, x, y, w, h, f"{f.split('/')[-1] if f else 'mqtt-demo'} — mqtt-demo — Code")
    d = ImageDraw.Draw(img)
    d.rectangle((bx, by, bx + 54, y + h - 30), fill=(44, 44, 46))
    for i in range(4): d.rounded_rectangle((bx + 15, by + 20 + i * 56, bx + 39, by + 44 + i * 56), 5, outline=(150, 150, 155) if i else (230, 230, 230), width=2)
    sx = bx + 54; sw = 290
    d.rectangle((sx, by, sx + sw, y + h - 30), fill=(37, 37, 38))
    d.text((sx + 20, by + 14), "EXPLORER", font=SANSB(14), fill=(190, 190, 190))
    d.text((sx + 14, by + 46), "⌄ MQTT-DEMO", font=SANSB(15), fill=(220, 220, 220))
    rowpos = {}
    for i, (p, depth, name, is_dir) in enumerate(tree_rows(t)):
        ry = by + 76 + i * 28; sel = p == f
        if sel: d.rectangle((sx, ry - 3, sx + sw, ry + 23), fill=(55, 75, 110))
        d.text((sx + 22 + depth * 16, ry), ("⌄ " if is_dir else "  ") + name, font=SANS(16), fill=(225, 225, 225) if not is_dir else (200, 200, 200))
        rowpos[p] = (sx + 60 + depth * 16, ry + 10)
    ex = sx + sw; d.rectangle((ex, by, x + w, by + 38), fill=(37, 37, 38))
    tx = ex
    for of in opened[-4:]:
        name = of.split("/")[-1]; tw = d.textlength(name, font=SANS(16)) + 48; act = of == f
        d.rectangle((tx, by, tx + tw, by + 38), fill=(30, 30, 30) if act else (45, 45, 46))
        d.text((tx + 16, by + 10), name, font=SANS(16), fill=(240, 240, 240) if act else (160, 160, 160)); tx += tw + 1
    d.rectangle((bx, y + h - 30, x + w, y + h), fill=(0, 122, 204))
    focus = None
    if f:
        full = S.FILES[f]; nl, col = cur.get(f, (len(full), 0)); lang = lang_of(f)
        lines = full[:nl] + ([full[nl][:col]] if col and nl < len(full) else [])
        ln_cur = len(lines) if not col else nl + 1
        rows = int((h - 46 - 38 - 30 - 16) / ELH); top = max(0, ln_cur - rows + 3)
        ox, oy = ex + 70, by + 50
        for hi, ht in hls:
            r = hi - 1 - top
            if 0 <= r < rows: d.rectangle((ex, oy + r * ELH - 3, x + w, oy + r * ELH + ELH - 5), fill=(int(55 * ease((t - ht) / 0.4)) + 30, int(50 * ease((t - ht) / 0.4)) + 30, 30))
        for r, line in enumerate(lines[top:top + rows]):
            i = top + r; yy = oy + r * ELH
            d.text((ex + 54 - d.textlength(str(i + 1), font=MONO(18)), yy + 3), str(i + 1), font=MONO(18), fill=(200, 200, 200) if i + 1 == ln_cur else (110, 110, 110))
            xx = ox
            for tok, c in (hl_rust(line) if lang == "rust" else hl_conf(line, lang)):
                d.text((xx, yy), tok, font=MONO(EFS), fill=c); xx += ECW * len(tok)
        cl = (lines[-1] if lines else "") if col else ""
        cr = (ln_cur - 1 - top); cxp = ox + ECW * (len(cl) if col else len(full[nl]) - len(full[nl].lstrip(" ")) if nl < len(full) else 0)
        if int(t * 2) % 2 == 0 or col: d.rectangle((cxp, oy + cr * ELH, cxp + 2, oy + cr * ELH + ELH - 6), fill=(230, 230, 230))
        focus = (cxp, oy + cr * ELH)
        d.text((x + w - 330, y + h - 25), f"Ln {ln_cur}, Col {(len(cl) if col else 0) + 1}   UTF-8   {dict(rust='Rust', toml='TOML', yaml='YAML', dockerfile='Dockerfile', conf='Properties')[lang]}", font=SANS(15), fill=(255, 255, 255))
    else:
        d.text((ex + 300, by + 380), "mqtt-demo", font=SANSB(40), fill=(70, 70, 75))
    return focus, rowpos

# ------------------------------------------------------------------ whiteboard diagrams
def sketch_line(d, p0, p1, col, w=4, seed=0):
    r = random.Random(seed)
    for k in range(2):
        j = lambda: r.uniform(-2.2, 2.2)
        d.line([(p0[0] + j(), p0[1] + j()), ((p0[0] + p1[0]) / 2 + j() * 1.5, (p0[1] + p1[1]) / 2 + j() * 1.5), (p1[0] + j(), p1[1] + j())], fill=col, width=w - k, joint="curve")
def sketch_box(d, x0, y0, x1, y1, col, prog, seed, fill=None):
    if fill and prog > 0.99: d.rounded_rectangle((x0 + 3, y0 + 3, x1 - 3, y1 - 3), 10, fill=fill)
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    for i in range(4):
        p = clamp(prog * 4 - i)
        if p <= 0: break
        a, b = pts[i], pts[i + 1]; sketch_line(d, a, (a[0] + (b[0] - a[0]) * p, a[1] + (b[1] - a[1]) * p), col, 4, seed + i)
def sketch_arrow(d, a, b, col, prog, seed, label=None, lc=None):
    if prog <= 0: return
    e = (a[0] + (b[0] - a[0]) * prog, a[1] + (b[1] - a[1]) * prog); sketch_line(d, a, e, col, 4, seed)
    if prog > 0.95:
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        for s_ in (2.6, -2.6): sketch_line(d, b, (b[0] + 22 * math.cos(ang + s_), b[1] + 22 * math.sin(ang + s_)), col, 4, seed + 7)
    if label and prog > 0.6:
        tw = d.textlength(label, font=SANS(22)); d.text(((a[0] + b[0]) / 2 - tw / 2, (a[1] + b[1]) / 2 - 38), label, font=SANS(22), fill=lc or col)
def text_c(d, cx, y, s, f, col):
    d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=col)

def draw_diagram(img, which, lt, dur):
    x, y, w, h = 120, 70, 1680, 960; bx, by = win_frame(img, x, y, w, h, f"{which}-diagram — Whiteboard", light=True)
    d = ImageDraw.Draw(img); ink = (40, 40, 48); acc = (215, 90, 40); blue = (40, 110, 200)
    for gx in range(bx + 40, x + w, 40):
        for gy in range(by + 40, y + h, 40): d.point((gx, gy), fill=(215, 215, 220))
    step = lambda i, n=8: clamp((lt - 0.5 - i * (dur * 0.75 / n)) / 1.2)
    if which == "kiri":
        text_c(d, x + w / 2, by + 30, "How Kiri works on Linux", SANSB(40), ink)
        for i, name in enumerate(["docker CLI", "docker compose", "buildx"]):
            p = step(0); yy = by + 170 + i * 150
            sketch_box(d, x + 90, yy, x + 420, yy + 100, ink, p, 10 + i, fill=(240, 244, 255))
            if p > 0.9: text_c(d, x + 255, yy + 32, name, SANSB(28), ink)
            sketch_arrow(d, (x + 430, yy + 50), (x + 690, by + 400), blue, step(1), 20 + i)
        if step(1) > 0.7: text_c(d, x + 565, by + 250, "Docker Engine API", SANSB(24), blue)
        p = step(2); sketch_box(d, x + 700, by + 300, x + 1060, by + 500, acc, p, 30, fill=(255, 240, 230))
        if p > 0.9: text_c(d, x + 880, by + 345, "kiri daemon", SANSB(32), ink); text_c(d, x + 880, by + 395, "written in Rust", SANS(24), (90, 90, 90)); text_c(d, x + 880, by + 430, "~15 MB", SANS(24), (90, 90, 90))
        sketch_arrow(d, (x + 1070, by + 400), (x + 1240, by + 400), ink, step(3), 40)
        for i in range(3):
            p = step(3.5 + i * 0.3); yy = by + 230 + i * 120
            sketch_box(d, x + 1250, yy, x + 1560, yy + 90, (60, 150, 80), p, 50 + i, fill=(232, 248, 236))
            if p > 0.9: text_c(d, x + 1405, yy + 28, f"container {i + 1}", SANSB(26), ink)
        p = step(4.5); sketch_box(d, x + 640, by + 620, x + 1600, by + 700, ink, p, 60, fill=(245, 245, 245))
        if p > 0.9: text_c(d, x + 1120, by + 643, "Linux kernel  (namespaces + cgroup v2)", SANSB(28), ink)
        if step(5.5) > 0.5:
            text_c(d, x + 1120, by + 740, "On Linux: no VM, containers run straight on your kernel", SANSB(28), acc)
            text_c(d, x + 1120, by + 790, "(Mac & Windows: one tiny Linux VM)", SANS(24), (110, 110, 110))
        if step(6.5) > 0.5: text_c(d, x + 300, by + 700, "Apache-2.0  ·  v0.2.1", SANSB(28), (110, 110, 110))
    else:
        text_c(d, x + w / 2, by + 30, "What we'll build", SANSB(40), ink)
        p = step(0); sketch_box(d, x + 70, by + 120, x + w - 70, by + 760, (150, 150, 160), p, 70)
        if p > 0.9: d.text((x + 100, by + 135), "docker compose  ·  running on Kiri", font=SANSB(24), fill=(130, 130, 140))
        boxes = [(x + 140, "Rust publisher", "publisher.rs", (232, 248, 236), (60, 150, 80)),
                 (x + 660, "Mosquitto broker", ":1883", (255, 240, 230), acc),
                 (x + 1180, "Rust subscriber", "subscriber.rs", (240, 244, 255), blue)]
        for i, (bx0, title, sub, fill, col) in enumerate(boxes):
            p = step(1 + i * 1.6); sketch_box(d, bx0, by + 320, bx0 + 360, by + 520, col, p, 80 + i, fill=fill)
            if p > 0.9: text_c(d, bx0 + 180, by + 375, title, SANSB(30), ink); text_c(d, bx0 + 180, by + 425, sub, MONO(24), (90, 90, 90))
        sketch_arrow(d, (x + 505, by + 420), (x + 655, by + 420), (60, 150, 80), step(2), 90)
        sketch_arrow(d, (x + 1025, by + 420), (x + 1175, by + 420), blue, step(4), 91)
        if step(2.4) > 0.5: text_c(d, x + 580, by + 560, "PUBLISH", SANSB(24), (60, 150, 80)); text_c(d, x + 580, by + 595, "sensors/room1/temperature", MONO(22), ink); text_c(d, x + 580, by + 630, "every 2 s", SANS(22), (110, 110, 110))
        if step(4.4) > 0.5: text_c(d, x + 1100, by + 560, "SUBSCRIBE", SANSB(24), blue); text_c(d, x + 1100, by + 595, "sensors/#", MONO(22), ink); text_c(d, x + 1100, by + 630, "# = everything below", SANS(22), (110, 110, 110))
        if step(5.5) > 0.5:
            k = (lt * 0.8) % 1.0  # a message dot travelling
            px = x + 505 + (x + 1175 - x - 505) * k; d.ellipse((px - 10, by + 410, px + 10, by + 430), fill=acc)
            text_c(d, x + w / 2, by + 230, '{"reading":1,"celsius":22.5}', MONO(26), acc)

# ------------------------------------------------------------------ title cards, overlays, cursor
def draw_title(img, sh, lt):
    d = ImageDraw.Draw(img); a = eout(lt / 0.7)
    cw, ch = 1100, 420; x0, y0 = (W - cw) / 2, (H - ch) / 2 + (1 - a) * 40
    card = Image.new("RGBA", (cw, ch), (18, 18, 24, int(225 * a))); img.paste(card, (int(x0), int(y0)), card)
    text_c(d, W / 2, y0 + 90, sh["title"], SANSB(78), (255, 255, 255))
    text_c(d, W / 2, y0 + 200, sh["subtitle"], SANS(32), (215, 215, 220))
    chips = ["Linux", "Kiri", "Rust", "MQTT"] if not sh.get("outro") else ["👍  Like", "🔔  Subscribe", "💬  Comment"]
    chips = [c.replace("👍  ", "").replace("🔔  ", "").replace("💬  ", "") for c in chips]
    tot = sum(d.textlength(c, font=SANSB(26)) + 70 for c in chips); xx = W / 2 - tot / 2
    for i, c in enumerate(chips):
        p = eout((lt - 0.6 - i * 0.25) / 0.4); cwd = d.textlength(c, font=SANSB(26)) + 50
        if p > 0:
            col = [(215, 90, 40), (60, 150, 80), (40, 110, 200), (150, 90, 200)][i % 4]
            d.rounded_rectangle((xx, y0 + 290, xx + cwd, y0 + 345), 28, fill=col); d.text((xx + 25, y0 + 302), c, font=SANSB(26), fill=(255, 255, 255))
        xx += cwd + 20

CURSOR = [(0, 0), (0, 26), (6, 20), (11, 31), (15, 29), (10, 18), (18, 18)]
def draw_cursor(d, x, y, click):
    if click > 0: r = 10 + 26 * (1 - click); d.ellipse((x - r, y - r, x + r, y + r), outline=(255, 255, 255), width=3)
    pts = [(x + px, y + py) for px, py in CURSOR]; d.polygon([(px + 2, py + 2) for px, py in pts], fill=(0, 0, 0)); d.polygon(pts, fill=(255, 255, 255), outline=(0, 0, 0))

def lower_third(d, t):
    for (ct, text) in CHAPTERS:
        lt = t - ct
        if 0 <= lt < 4.2:
            a = eout(lt / 0.45) * (1 - ease((lt - 3.6) / 0.6)); tw = d.textlength(text, font=SANSB(30))
            x0 = 60 - (1 - a) * 500; y0 = H - 140
            d.rounded_rectangle((x0, y0, x0 + tw + 70, y0 + 64), 14, fill=(215, 90, 40)); d.rectangle((x0, y0, x0 + 10, y0 + 64), fill=(255, 220, 190))
            d.text((x0 + 38, y0 + 14), text, font=SANSB(30), fill=(255, 255, 255))

def badges(d, t):
    for (a0, a1, text) in EV["badge"]:
        if a0 <= t <= a1:
            f = SANSB(34) if "speed" in text else MONOB(34); tw = d.textlength(text, font=f)
            x0, y0 = W - tw - 110, 70
            d.rounded_rectangle((x0, y0, x0 + tw + 50, y0 + 64), 14, fill=(20, 20, 24)); d.rounded_rectangle((x0, y0, x0 + tw + 50, y0 + 64), 14, outline=(255, 255, 255), width=2)
            d.text((x0 + 25, y0 + 12), text, font=f, fill=(255, 255, 255))

# ------------------------------------------------------------------ mouse path + camera (precomputed)
def mouse_target(t, si):
    sh = SHOTS[si]["shot"]; n = bisect.bisect_right(EVT["mouse"], t)
    ev = EV["mouse"][n - 1][1] if n else None
    if sh["scene"] in ("terminal", "split"):
        layout = "split" if sh["scene"] == "split" else "single"; term = ev[2] if ev and ev[0] == "term" else 1
        x, y, w, h = TERM_POS[layout].get(term, TERM_POS[layout][1]); return (x + w * 0.62, y + h * 0.55)
    if sh["scene"] == "editor" and ev and ev[0] == "file":
        rows = tree_rows(t + 0.5); idx = [r[0] for r in rows].index(ev[1]) if ev[1] in [r[0] for r in rows] else 0
        return (ED_RECT[0] + 54 + 120 + rows[idx][1] * 16, ED_RECT[1] + 46 + 76 + idx * 28 + 10) if t < SHOTS[si]["start"] + 1.6 else (ED_RECT[0] + 1500, ED_RECT[1] + 760)
    return (W * 0.78, H * 0.8)

def precompute_paths():
    mx, my = W * 0.7, H * 0.7; vx = vy = 0.0; cam = []
    zx, zy, zs = W / 2, H / 2, 1.0; mouse = []
    for i in range(NFR):
        t = i / FPS; si, s = shot_at(t); sh = s["shot"]
        tx, ty = mouse_target(t, si)
        # critically damped spring + tiny idle wander
        k, c = 60.0, 2 * math.sqrt(60.0); dt = 1 / FPS
        ax = k * (tx + 6 * math.sin(t * 0.9) - mx) - c * vx; ay = k * (ty + 5 * math.cos(t * 0.7) - my) - c * vy
        vx += ax * dt; vy += ay * dt; mx += vx * dt; my += vy * dt; mouse.append((mx, my))
        # camera: follow typing focus with a gentle zoom
        want = sh.get("zoom", 1.15 if sh["scene"] == "editor" else (1.08 if sh["scene"] == "terminal" else 1.0))
        fx, fy = FOCUS[i] if FOCUS[i] else (W / 2, H / 2)
        zs += (want - zs) * 0.06; zx += (fx - zx) * 0.08; zy += (fy - zy) * 0.08
        cam.append((zx, zy, zs))
    return mouse, cam

# ------------------------------------------------------------------ frame
def compose_base(t):
    si, s = shot_at(t); sh = s["shot"]; lt = t - s["start"]
    img = WALL.copy(); d = ImageDraw.Draw(img)
    cs = clock_str(t); d.text((W / 2 - d.textlength(cs, font=SANSB(17)) / 2, 7), cs, font=SANSB(17), fill=(235, 235, 235))
    focus = None
    if sh["scene"] == "terminal":
        tk = "t%d" % next((a.get("term", 1) for a in sh.get("actions", []) if a.get("term")), 1)
        focus = draw_terminal(img, TERM_POS["single"][1], tk, t, "dev@ubuntu: " + S.PROMPT_DIR.get("proj"), True)
    elif sh["scene"] == "split":
        n = bisect.bisect_right(EVT["mouse"], t); ev = EV["mouse"][n - 1][1] if n else None
        act = ev[2] if ev and ev[0] == "term" else 1
        f1 = draw_terminal(img, TERM_POS["split"][1], "t1", t, "Terminal 1", act == 1)
        f2 = draw_terminal(img, TERM_POS["split"][2], "t2", t, "Terminal 2", act == 2)
        focus = f1 if act == 1 else f2
    elif sh["scene"] == "editor":
        focus, _ = draw_editor(img, t, None)
    elif sh["scene"] == "diagram":
        draw_diagram(img, sh["diagram"], lt, s["dur"])
    elif sh["scene"] == "title":
        draw_title(img, sh, lt)
    return img, focus

def render_frame(i):
    t = i / FPS; img, _ = compose_base(t); d = ImageDraw.Draw(img)
    si, s = shot_at(t)
    mx, my = MOUSE[i]
    n = bisect.bisect_right(EV["clicks"], t); click = 0.0
    if n and t - EV["clicks"][n - 1] < 0.35: click = 1 - (t - EV["clicks"][n - 1]) / 0.35
    if s["shot"]["scene"] != "title": draw_cursor(d, mx, my, click)
    zx, zy, zs = CAM[i]
    if zs > 1.001:
        cw, ch = W / zs, H / zs; x0 = clamp(zx - cw / 2, 0, W - cw); y0 = clamp(zy - ch / 2, 0, H - ch)
        img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
    d = ImageDraw.Draw(img); lower_third(d, t); badges(d, t)
    # scene fades between different scene types
    st = s["start"]; lt = t - st
    if si > 0 and SHOTS[si - 1]["shot"]["scene"] != s["shot"]["scene"] and lt < 0.25:
        prev = Image.frombytes("RGB", (W, H), FRAME_CACHE.get(i, b"")) if False else None
        img = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), img, 0.4 + 0.6 * lt / 0.25)
    if t < 0.6: img = Image.blend(Image.new("RGB", (W, H)), img, t / 0.6)
    if TOTAL - t < 1.2: img = Image.blend(Image.new("RGB", (W, H)), img, clamp((TOTAL - t) / 1.2))
    return img.tobytes()
FRAME_CACHE = {}

FOCUS = None; MOUSE = None; CAM = None
def init_paths():
    global FOCUS, MOUSE, CAM
    cache = os.path.join(BUILD, "paths.json")
    key = hashlib.md5(open(os.path.join(HERE, "script.py"), "rb").read() + open(__file__, "rb").read()).hexdigest()
    if os.path.exists(cache):
        j = json.load(open(cache))
        if j.get("key") == key: FOCUS, MOUSE, CAM = j["focus"], j["mouse"], j["cam"]; return
    FOCUS = []
    for i in range(NFR):
        if i % 3 == 0: _, f = compose_base(i / FPS); last = f
        FOCUS.append(last)
    MOUSE, CAM = precompute_paths()
    json.dump({"key": key, "focus": FOCUS, "mouse": MOUSE, "cam": CAM}, open(cache, "w"))

# ------------------------------------------------------------------ audio mix
def build_audio():
    import soundfile as sf
    from scipy.signal import butter, sosfilt
    SR = 44100; N = int(TOTAL * SR) + SR
    voice = np.zeros(N, np.float32)
    for s in SHOTS:
        a, sr = s["voice"]; a = np.interp(np.arange(0, len(a) * SR / sr) * sr / SR, np.arange(len(a)), a).astype(np.float32)
        i0 = int((s["start"] + 0.5) * SR); voice[i0:i0 + len(a)] += a[: N - i0]
    r = np.random.default_rng(5); fx = np.zeros(N, np.float32)
    lp = lambda x, f: sosfilt(butter(2, f, "low", fs=SR, output="sos"), x); hp = lambda x, f: sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)
    clicks = [hp(r.standard_normal(900), 1800) * np.exp(-np.arange(900) / 90) * 0.05 for _ in range(6)]
    thock = lp(r.standard_normal(1600), 900) * np.exp(-np.arange(1600) / 260) * 0.08
    for t in EV["keys"]:
        i0 = int(t * SR); c = clicks[r.integers(0, 6)] * r.uniform(0.6, 1.1)
        fx[i0:i0 + len(c)] += c[: max(0, N - i0)]
        fx[i0:i0 + 1600] += thock[: max(0, min(1600, N - i0))] * 0.35
    for t in EV["clicks"]:
        i0 = int(t * SR); c = hp(r.standard_normal(600), 2500) * np.exp(-np.arange(600) / 60) * 0.12; fx[i0:i0 + 600] += c[: max(0, N - i0)]
    # soft lo-fi bed: 76 BPM, Rhodes-ish chords + brushed beat, ducked under the voice
    bpm = 76; beat = 60 / bpm; bar = beat * 4; tt = np.arange(N) / SR; music = np.zeros(N, np.float32)
    chords = [[57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 65], [52, 55, 59, 62]]
    m2f = lambda m: 440 * 2 ** ((m - 69) / 12)
    for b in range(int(TOTAL / bar) + 1):
        i0 = int(b * bar * SR); L = int(bar * SR) + SR // 2; tl = np.arange(L) / SR
        env = np.minimum(1, tl / 0.05) * np.exp(-tl * 0.9)
        ch = sum(np.sin(2 * np.pi * m2f(m) * tl) * (1 + 0.3 * np.sin(2 * np.pi * 2 * m2f(m) * tl)) for m in chords[b % 4]) * env * 0.018
        ch *= 1 + 0.15 * np.sin(2 * np.pi * 4.5 * tl)
        music[i0:i0 + L] += ch[: max(0, N - i0)].astype(np.float32)
        for k in range(4):
            j0 = int((b * bar + k * beat) * SR)
            if k in (0, 2):
                kl = np.arange(int(0.25 * SR)) / SR; kick = np.sin(2 * np.pi * np.cumsum(45 + 70 * np.exp(-kl * 30)) / SR) * np.exp(-kl * 9) * 0.05
                music[j0:j0 + len(kick)] += kick[: max(0, N - j0)]
            hh = hp(r.standard_normal(int(0.05 * SR)), 6000) * np.exp(-np.arange(int(0.05 * SR)) / 300) * 0.006
            h0 = int((b * bar + k * beat + beat / 2) * SR); music[h0:h0 + len(hh)] += hh[: max(0, N - h0)]
    music = lp(music, 3500)
    env = lp(np.abs(voice), 4); env = env / (np.percentile(env[env > 1e-4], 90) + 1e-9); duck = 1 - 0.65 * np.clip(env, 0, 1)
    fade = np.clip(tt / 2, 0, 1) * np.clip((TOTAL - tt) / 3, 0, 1)
    mix = voice * 1.0 + fx * 0.8 + music * duck * fade * 1.0
    sf.write(os.path.join(BUILD, "mix.wav"), np.stack([mix, mix], 1)[: int(TOTAL * SR)].astype(np.float32), SR)

def write_srt():
    def ts(x): return f"{int(x // 3600):02}:{int(x % 3600 // 60):02}:{x % 60:06.3f}".replace(".", ",")
    out = []; n = 1
    for s in SHOTS:
        a, sr = s["voice"]; a0 = s["start"] + 0.5; dur = len(a) / sr
        sents = re.split(r"(?<=[.!?])\s+", s["shot"]["say"]); chunks = []
        for se in sents:
            words = se.split(); cur = ""
            for w_ in words:
                if len(cur) + len(w_) > 70: chunks.append(cur); cur = w_
                else: cur = (cur + " " + w_).strip()
            if cur: chunks.append(cur)
        tot = sum(len(c) for c in chunks); t0 = a0
        for c in chunks:
            t1 = t0 + dur * len(c) / tot; out.append(f"{n}\n{ts(t0)} --> {ts(t1)}\n{c}\n"); n += 1; t0 = t1
    open(os.path.join(BUILD, "kiri_mqtt_tutorial.srt"), "w").write("\n".join(out))

def chapters_txt():
    out = ["0:00 What we're building"]
    for (ct, text) in [(SHOTS[i]["start"], SHOTS[i]["shot"].get("chapter")) for i in range(len(SHOTS))]:
        if text: m = int(ct // 60); s_ = int(ct % 60); out.append(f"{m}:{s_:02d} {text}")
    open(os.path.join(BUILD, "chapters.txt"), "w").write("\n".join(out) + "\n"); return out

if __name__ == "__main__":
    print(f"total {TOTAL:.1f}s = {TOTAL / 60:.1f} min, {NFR} frames, {len(EV['keys'])} keystrokes")
    init_paths()
    if "--stills" in sys.argv:
        tiles = []
        for s in SHOTS:
            for f in (0.35, 0.85):
                i = int((s["start"] + s["dur"] * f) * FPS); tiles.append(Image.frombytes("RGB", (W, H), render_frame(i)).resize((480, 270)))
        cols = 6; rows = math.ceil(len(tiles) / cols); sheet = Image.new("RGB", (480 * cols, 270 * rows))
        for k, im in enumerate(tiles): sheet.paste(im, ((k % cols) * 480, (k // cols) * 270))
        sheet.save(os.path.join(BUILD, "stills.png")); print("stills", os.path.join(BUILD, "stills.png")); sys.exit()
    write_srt(); print("\n".join(chapters_txt())); build_audio()
    OUT = os.path.join(BUILD, "kiri_mqtt_tutorial.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", os.path.join(BUILD, "mix.wav"), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-map", "0:v", "-map", "1:a",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-tune", "stillimage", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    with Pool(os.cpu_count() or 4) as pool:
        for i, fr in enumerate(pool.imap(render_frame, range(NFR), chunksize=8)):
            p.stdin.write(fr)
            if i % 1800 == 0: print(f"frame {i}/{NFR}", flush=True)
    p.stdin.close(); p.wait(); print("video", OUT)
