"""Generic cinematic Shorts renderer.

Usage: python3 render.py EPISODE_DIR
Reads EPISODE_DIR/spec.json, EPISODE_DIR/build/{voice.wav,music.wav,durs.json}
Writes EPISODE_DIR/build/video.mp4 (1080x1920, 30 fps, -14 LUFS).
Preview stills: python3 render.py EPISODE_DIR --preview 0.3,0.6   (fractions of each scene)
"""
import subprocess, math, sys, os, json, re
import numpy as np
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont, ImageFilter

EP = os.path.abspath(sys.argv[1]); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); BUILD = os.path.join(EP, "build")
SPEC = json.load(open(os.path.join(EP, "spec.json")))
SCENES = SPEC["scenes"]
DURS = json.load(open(os.path.join(BUILD, "durs.json")))
W, H, FPS = 1080, 1920, 30
STARTS = np.cumsum([0] + DURS[:-1]).tolist(); TOTAL = sum(DURS); NFR = int(round(TOTAL * FPS))
DROP = 8.0
BRAND = SPEC.get("brand", "RUST  ·  DAILY")

FD = "/usr/share/fonts/truetype/dejavu/"
_fc = {}
def font(n, s):
    k = (n, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(FD + n, max(8, int(s)))
    return _fc[k]
B = lambda s: font("DejaVuSans-Bold.ttf", s)
R = lambda s: font("DejaVuSans.ttf", s)
M = lambda s: font("DejaVuSansMono.ttf", s)
MB = lambda s: font("DejaVuSansMono-Bold.ttf", s)

WHITE = (240, 242, 245); DIM = (150, 158, 170); GREEN = (70, 210, 95)
PANEL = (24, 30, 40); PURPLE = (190, 120, 255); YELLOW = (240, 200, 90)
# colour themes: accent, second, blob colours (warm, cool, extra)
THEMES = {
    "rust":   dict(A=(255, 104, 36), A2=(88, 166, 255),  b1=(90, 30, 8),  b2=(10, 30, 75), b3=(60, 18, 40)),
    "ocean":  dict(A=(40, 200, 255), A2=(120, 110, 255), b1=(5, 50, 85),  b2=(30, 20, 80), b3=(0, 45, 55)),
    "matrix": dict(A=(60, 235, 130), A2=(40, 170, 255),  b1=(5, 60, 30),  b2=(5, 30, 60),  b3=(20, 50, 20)),
    "neon":   dict(A=(255, 70, 190), A2=(140, 100, 255), b1=(80, 10, 60), b2=(30, 15, 90), b3=(70, 10, 30)),
    "gold":   dict(A=(255, 190, 40), A2=(255, 110, 60),  b1=(80, 55, 5),  b2=(60, 20, 10), b3=(50, 35, 0)),
}
TH = THEMES[SPEC.get("theme", "rust")]
RUST = TH["A"]; BLUE = TH["A2"]; BLUE_BAR = tuple(int(c * 0.65) for c in TH["A2"])
import visuals as VIS
VIS.setpal(A=RUST, A2=BLUE)

def clamp(t): return max(0.0, min(1.0, t))
def ease(t): t = clamp(t); return 1 - (1 - t) ** 3
def backout(t):
    t = clamp(t); c = 1.9; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2
def mix(c, a): a = clamp(a); return tuple(int(v * a) for v in c)
def appear(t, start, dur=0.5):
    e = ease((t - start) / dur); return e, (1 - e) * 70

def wrap(d, text, fn, size, maxw, maxlines=3, minsize=28):
    """Greedy word wrap; shrink font until it fits in maxlines."""
    while True:
        f = fn(size); words = text.split(); lines = []; cur = ""
        for w_ in words:
            trial = (cur + " " + w_).strip()
            if d.textlength(trial, font=f) <= maxw or not cur: cur = trial
            else: lines.append(cur); cur = w_
        if cur: lines.append(cur)
        if (len(lines) <= maxlines and all(d.textlength(l, font=f) <= maxw for l in lines)) or size <= minsize:
            return lines, f, size
        size = int(size * 0.92)

def ctext(d, y, s, f, c, a=1.0, dy=0, x=0):
    w = d.textlength(s, font=f); d.text(((W - w) / 2 + x, y + dy), s, font=f, fill=mix(c, a))

def cblock(d, y, text, fn, size, c, a=1.0, dy=0, maxw=W - 160, maxlines=3, gap=1.18):
    lines, f, sz = wrap(d, text, fn, size, maxw, maxlines)
    for i, l in enumerate(lines): ctext(d, y + i * sz * gap, l, f, c, a, dy)
    return y + len(lines) * sz * gap

def stagger(n, dur, start=0.6, end_frac=0.72):
    span = max(0.5, dur * end_frac - start)
    return [start + i * span / max(1, n) for i in range(n)]

# ---------------- scene types ----------------
def dimmed_visual(d, name, t, dur, s, k=0.5):
    from PIL import ImageChops
    tmp = Image.new("RGB", (W, H)); VIS.VISUALS[name](ImageDraw.Draw(tmp), t, dur, s)
    base = d._image; base.paste(ImageChops.add(base, tmp.point(lambda v: int(v * k))))

def sc_visual(d, t, s, dur):
    if s.get("heading"):
        a, dy = appear(t, 0.0); y = cblock(d, 290, s["heading"], B, 80, WHITE, a, dy, maxlines=2)
        if s.get("sub"): a, dy = appear(t, 0.3); cblock(d, y + 5, s["sub"], R, 44, DIM, a, dy, maxlines=2)
    VIS.VISUALS[s["visual"]](d, t, dur, s)
    if s.get("caption"):
        a, dy = appear(t, dur * 0.62); cblock(d, 1440, s["caption"], B, 60, RUST, a, dy, maxlines=2)

def sc_hook(d, t, s, dur):
    if s.get("visual"):
        dimmed_visual(d, s["visual"], t, dur, s, 0.42)
        a, dy = appear(t, 0.1); ybig = 470
        if s.get("top"):
            lines, f, sz = wrap(d, s["top"], MB, 90, 960, 1, 40)
            ctext(d, 330, lines[0], f, WHITE, a, dy); ybig = 330 + sz * 1.25
        big = s.get("big", "")
        if "count" in s and "{n}" in big:
            n = s["count"] * ease((t - 0.6) / 1.0)
            big = big.replace("{n}", f"{n:.0f}" if float(s["count"]).is_integer() else f"{n:.2f}")
        sc = backout((t - 0.5) / 0.5)
        lines, f, sz = wrap(d, big, B, int(140 * (0.7 + 0.3 * sc)), 960, 2)
        for i, l in enumerate(lines): ctext(d, ybig + (1 - sc) * 40 + i * sz * 1.05, l, f, RUST, clamp(sc))
        a, dy = appear(t, 1.9); y = 1460
        for l in s.get("sub", []): y = cblock(d, y, l, B, 54, WHITE, a, dy, maxlines=2)
        return
    p = ease((t - 0.6) / 1.0); cx, cy, r = 540, 880, 470
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=mix((60, 30, 20), ease(t / 0.4)), width=6)
    if p > 0:
        d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * p, fill=RUST, width=14)
        a = math.radians(-90 + 360 * p)
        d.ellipse((cx + r * math.cos(a) - 18, cy + r * math.sin(a) - 18, cx + r * math.cos(a) + 18, cy + r * math.sin(a) + 18), fill=WHITE)
    for i in range(60):
        a = math.radians(i * 6); r1 = r - 30 if i % 5 == 0 else r - 18
        d.line((cx + r1 * math.cos(a), cy + r1 * math.sin(a), cx + (r - 6) * math.cos(a), cy + (r - 6) * math.sin(a)),
               fill=mix((110, 60, 40), ease(t / 0.6)), width=4 if i % 5 == 0 else 2)
    a, dy = appear(t, 0.1)
    if s.get("top"):
        lines, f, sz = wrap(d, s["top"], MB, 96, 780, 2)
        for i, l in enumerate(lines): ctext(d, 700 - (len(lines) - 1) * sz * 1.1 + i * sz * 1.1, l, f, WHITE, a, dy)
    big = s.get("big", "")
    if "count" in s and "{n}" in big:
        n = s["count"] * ease((t - 0.6) / 1.0)
        big = big.replace("{n}", f"{n:.0f}" if float(s["count"]).is_integer() else f"{n:.2f}")
    sc = backout((t - 0.5) / 0.5)
    lines, f, sz = wrap(d, big, B, int(138 * (0.7 + 0.3 * sc)), 820, 2)
    for i, l in enumerate(lines): ctext(d, 830 + (1 - sc) * 40 + i * sz * 1.05, l, f, RUST, clamp(sc))
    a, dy = appear(t, 1.9)
    y = 1440
    for l in s.get("sub", []): y = cblock(d, y, l, R, 52, DIM, a, dy, maxlines=2)

def sc_title(d, t, s, dur):
    cx, cy = 540, 760; a0 = ease(t / 0.6)
    for i in range(48):
        ang = math.radians(i * 7.5 + t * 25); r1, r2 = 330, 360 if i % 4 else 385
        d.line((cx + r1 * math.cos(ang), cy + r1 * math.sin(ang), cx + r2 * math.cos(ang), cy + r2 * math.sin(ang)),
               fill=mix(RUST if i % 4 == 0 else (120, 55, 25), a0), width=6)
    for i in range(24):
        ang = i * 15 - t * 40
        d.arc((cx - 300, cy - 300, cx + 300, cy + 300), ang, ang + 7, fill=mix((70, 110, 170), a0), width=4)
    a, dy = appear(t, 0.0)
    if s.get("kicker"): ctext(d, 460, s["kicker"], R(72), DIM, a, dy)
    sc = backout((t - 0.25) / 0.55)
    lines, f, sz = wrap(d, s["title"], B, int(230 * (0.6 + 0.4 * sc)), 560, 2, 60)
    y0 = cy - len(lines) * sz * 1.02 / 2 - sz * 0.1
    for i, l in enumerate(lines): ctext(d, y0 + i * sz * 1.02, l, f, RUST, clamp(sc * 1.5))
    items = s.get("bullets", [])
    for i, (it, st) in enumerate(zip(items, stagger(len(items), dur, 1.2))):
        e = ease((t - st) / 0.5)
        lines, f, sz = wrap(d, it, B, 58, W - 160, 1, 34)
        ctext(d, 1240 + i * 115, lines[0], f, WHITE, e, 0, x=(1 - e) * (-500 if i % 2 == 0 else 500))

def sc_bullets(d, t, s, dur):
    a, dy = appear(t, 0.0); y = cblock(d, 330, s["heading"], B, 84, WHITE, a, dy, maxlines=2)
    if s.get("sub"): a, dy = appear(t, 0.3); y = cblock(d, y + 10, s["sub"], R, 46, DIM, a, dy, maxlines=2)
    items = s.get("items", []); y0 = max(y + 90, 640)
    for i, (it, st) in enumerate(zip(items, stagger(len(items), dur, 0.8))):
        e = ease((t - st) / 0.55); off = (1 - e) * (800 if i % 2 else -800)
        if e <= 0: continue
        yy = y0 + i * 210
        d.rounded_rectangle((100 + off, yy, W - 100 + off, yy + 170), 26, fill=PANEL, outline=(60, 68, 80), width=3)
        d.ellipse((140 + off, yy + 60, 190 + off, yy + 110), fill=RUST)
        d.text((153 + off, yy + 62), str(i + 1), font=B(38), fill=(0, 0, 0))
        lines, f, sz = wrap(d, it, B, 50, W - 360, 2, 30)
        ty = yy + 85 - len(lines) * sz * 1.15 / 2
        for j, l in enumerate(lines): d.text((230 + off, ty + j * sz * 1.15), l, font=f, fill=WHITE)

def sc_terminal(d, t, s, dur):
    a, dy = appear(t, 0.0); y = cblock(d, 300, s["heading"], B, 84, WHITE, a, dy, maxlines=2)
    if s.get("sub"): a, dy = appear(t, 0.3); cblock(d, y + 10, s["sub"], R, 46, DIM, a, dy, maxlines=2)
    cmds = s.get("commands", [])
    e = ease((t - 0.4) / 0.6); x0, x1 = 90, W - 90; yc = 900; hh = 300 * e
    y0 = yc - hh
    if e > 0.02:
        d.rounded_rectangle((x0, y0, x1, yc + hh), 28, fill=PANEL, outline=(70, 80, 95), width=3)
        for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
            d.ellipse((x0 + 40 + i * 50, y0 + 32, x0 + 70 + i * 50, y0 + 62), fill=mix(c, e))
    if e > 0.95:
        y = y0 + 110; tt = t - 1.0; step = max(1.6, (dur * 0.55) / max(1, len(cmds)))
        f = M(38)
        for i, cm in enumerate(cmds[:3]):
            c, outp = (cm[0], cm[1] if len(cm) > 1 else "") if isinstance(cm, list) else (cm, "")
            while d.textlength("$ " + c, font=f) > x1 - x0 - 90 and f.size > 24: f = M(f.size - 2)
            n = int(max(0, min(len(c), (tt - i * step) * 26)))
            if n > 0 or i == 0:
                d.text((x0 + 45, y), "$ ", font=MB(f.size + 4), fill=GREEN)
                d.text((x0 + 45 + d.textlength("$ ", font=MB(f.size + 4)), y), c[:n], font=f, fill=WHITE)
                if n < len(c) and int(t * 3) % 2 == 0:
                    cx = x0 + 45 + d.textlength("$ " + c[:n], font=f); d.rectangle((cx + 4, y + 4, cx + 24, y + 48), fill=WHITE)
                if outp and n == len(c) and tt - i * step > len(c) / 26 + 0.2:
                    d.text((x0 + 45, y + 60), outp[:44], font=M(34), fill=DIM)
            y += 160
    for i, (lab, st) in enumerate(zip(s.get("checks", []), stagger(len(s.get("checks", [])), dur, dur * 0.55, 0.85))):
        sc = backout((t - st) / 0.45)
        if sc > 0:
            lines, f, sz = wrap(d, "✓  " + lab, B, int(56 * (0.5 + 0.5 * sc)), W - 140, 1, 30)
            ctext(d, 1340 + i * 105 + (1 - sc) * 20, lines[0], f, GREEN, clamp(sc * 1.5))

KW = set("fn let mut pub struct enum impl trait use mod match if else for while loop return async await move ref where as in const static type unsafe dyn self Self crate super true false Some None Ok Err".split())
def hl_line(line):
    """Tiny Rust syntax highlighter -> list of (text, color)."""
    out = []
    for m in re.finditer(r'(//.*$)|("(?:[^"\\]|\\.)*")|([A-Za-z_][A-Za-z0-9_]*!?)|(\d[\d_\.]*)|(\s+)|(.)', line):
        tok = m.group(0)
        if m.group(1): out.append((tok, (110, 120, 135)))
        elif m.group(2): out.append((tok, (152, 195, 121)))
        elif m.group(3):
            if tok.endswith("!"): out.append((tok, PURPLE))
            elif tok in KW: out.append((tok, RUST))
            elif tok[0].isupper(): out.append((tok, YELLOW))
            else: out.append((tok, WHITE))
        elif m.group(4): out.append((tok, (209, 154, 102)))
        else: out.append((tok, (190, 196, 205)))
    return out

def sc_code(d, t, s, dur):
    a, dy = appear(t, 0.0); y = cblock(d, 300, s["heading"], B, 80, WHITE, a, dy, maxlines=2)
    if s.get("sub"): a, dy = appear(t, 0.3); y = cblock(d, y + 10, s["sub"], R, 44, DIM, a, dy, maxlines=2)
    lines = s["code"].rstrip("\n").split("\n")[:16]
    longest = max(len(l) for l in lines) or 1
    fs = int(min(40, (W - 260) / (longest * 0.602)))
    f = M(fs); lh = fs * 1.45
    e = ease((t - 0.4) / 0.6); x0, x1 = 70, W - 70
    top = max(y + 60, 600); hgt = 120 + lh * len(lines)
    if e > 0.02:
        d.rounded_rectangle((x0, top, x1, top + hgt * e), 26, fill=PANEL, outline=(70, 80, 95), width=3)
        d.text((x0 + 40, top + 25), s.get("file", "main.rs"), font=MB(32), fill=mix(DIM, e))
    if e > 0.95:
        per = max(0.12, (dur * 0.6) / len(lines))
        for i, l in enumerate(lines):
            la = ease((t - 1.0 - i * per) / 0.3)
            if la <= 0: break
            x = x0 + 50; yy = top + 90 + i * lh
            hi = i + 1 in s.get("highlight", [])
            if hi: d.rectangle((x0 + 6, yy - 6, x1 - 6, yy + lh - 8), fill=mix((70, 35, 15), la))
            for tok, col in hl_line(l):
                d.text((x, yy), tok, font=f, fill=mix(col, la)); x += d.textlength(tok, font=f)
    if s.get("caption"):
        a, dy = appear(t, dur * 0.7); cblock(d, min(top + hgt + 70, 1600), s["caption"], B, 56, RUST, a, dy, maxlines=2)

def sc_bars(d, t, s, dur):
    a, dy = appear(t, 0.0); y = cblock(d, 300, s["heading"], B, 80, WHITE, a, dy, maxlines=2)
    if s.get("sub"): a, dy = appear(t, 0.3); cblock(d, y + 5, s["sub"], R, 44, DIM, a, dy, maxlines=2)
    bars = s["bars"][:4]; vmax = max(b["value"] for b in bars); maxw = W - 200
    gap = 330 if len(bars) <= 2 else 250
    sts = stagger(len(bars), dur, 1.0, 0.55)
    for i, (b, st) in enumerate(zip(bars, sts)):
        yy = 640 + i * gap; col = RUST if b.get("highlight") else BLUE_BAR; lc = RUST if b.get("highlight") else BLUE
        a, dy2 = appear(t, 0.6 + i * 0.3)
        d.text((100, yy + dy2), b["label"], font=B(58), fill=mix(WHITE, a))
        d.rounded_rectangle((100, yy + 95, 100 + maxw, yy + 185), 14, outline=mix((50, 58, 70), a), width=2)
        g = ease((t - st) / 1.4)
        if g > 0:
            d.rounded_rectangle((100, yy + 95, 100 + max(14, maxw * b["value"] / vmax * g), yy + 185), 14, fill=col)
            v = b["value"] * g; dec = b.get("decimals", 0 if float(b["value"]).is_integer() else 2)
            lab = f"{v:,.{dec}f} {b.get('unit', '')}".strip()
            d.text((W - 100 - d.textlength(lab, font=B(58)), yy), lab, font=B(58), fill=lc)
    if s.get("callout"):
        sc = backout((t - dur * 0.6) / 0.5)
        if sc > 0: ctext(d, 640 + len(bars) * gap + 40, s["callout"], B(int(74 * (0.6 + 0.4 * sc))), RUST, clamp(sc * 1.5))
    if s.get("footnote"):
        a, _ = appear(t, dur * 0.7); yy = 1560
        for l in s["footnote"][:3]: yy = cblock(d, yy, l, R, 36, DIM, a, 0, maxlines=1)

def sc_cards(d, t, s, dur):
    a, dy = appear(t, 0.0); cblock(d, 360, s["heading"], B, 88, WHITE, a, dy, maxlines=2)
    cards = s["cards"][:4]; gap = 260 if len(cards) <= 3 else 220
    for i, (c, st) in enumerate(zip(cards, stagger(len(cards), dur, 0.6))):
        e = ease((t - st) / 0.55); off = (1 - e) * (800 if i % 2 else -800)
        if e <= 0: continue
        yy = 620 + i * gap; hl = c.get("highlight")
        d.rounded_rectangle((110 + off, yy, W - 110 + off, yy + gap - 60), 26, fill=PANEL, outline=RUST if hl else (60, 68, 80), width=4 if hl else 3)
        lines, f, _ = wrap(d, c["title"], B, 62, W - 300, 1, 34); d.text((160 + off, yy + 28), lines[0], font=f, fill=RUST)
        lines, f, _ = wrap(d, c.get("text", ""), R, 44, W - 300, 1, 28); d.text((160 + off, yy + 112), lines[0] if lines else "", font=f, fill=WHITE)

def sc_timeline(d, t, s, dur):
    a, dy = appear(t, 0.0); cblock(d, 440, s["heading"], B, 104, WHITE, a, dy, maxlines=2)
    pts = s["points"][:3]; x0, x1, y = 170, 910, 840
    g = ease((t - 0.8) / (dur * 0.4))
    d.line((x0, y, x0 + (x1 - x0) * g, y), fill=(120, 60, 35), width=8)
    xs = [x0 + (x1 - x0) * i / max(1, len(pts) - 1) for i in range(len(pts))]
    for i, (p, x) in enumerate(zip(pts, xs)):
        st = 0.8 + dur * 0.4 * (i / max(1, len(pts) - 1)); sc = backout((t - st) / 0.45)
        if sc <= 0: continue
        r = 26 * sc; d.ellipse((x - r, y - r, x + r, y + r), fill=RUST)
        for txt, fn, sz, yy, col in ((p["top"], B, 52, y - 120, WHITE), (p.get("bottom", ""), R, 38, y + 55, DIM)):
            lines, f, _ = wrap(d, txt, fn, sz, 300, 1, 24)
            if lines: d.text((x - d.textlength(lines[0], font=f) / 2, yy), lines[0], font=f, fill=mix(col, sc))
    if s.get("callout"): a, dy = appear(t, dur * 0.6); cblock(d, 1110, s["callout"], B, 84, RUST, a, dy, maxlines=1)
    if s.get("sub"): a, dy = appear(t, dur * 0.68); cblock(d, 1225, s["sub"], R, 48, WHITE, a, dy, maxlines=2)

def sc_cta(d, t, s, dur):
    a, dy = appear(t, 0.0); ctext(d, 560, s.get("heading", "Try it"), B(120), WHITE, a, dy)
    if s.get("link"):
        e = backout((t - 0.4) / 0.6)
        if e > 0:
            pulse = 0.65 + 0.35 * math.sin(t * 5); hw = (W / 2 - 80) * clamp(e); yc = 880
            d.rounded_rectangle((W / 2 - hw, yc - 70, W / 2 + hw, yc + 70), 30, fill=PANEL, outline=mix(RUST, pulse), width=5)
            if e > 0.8:
                lines, f, sz = wrap(d, s["link"], MB, 54, W - 220, 1, 26)
                ctext(d, yc - sz * 0.62, lines[0], f, RUST, clamp((e - 0.8) * 5))
    a, dy = appear(t, dur * 0.4); y = 1130
    for l in s.get("question", []): y = cblock(d, y, l, B, 64, WHITE, a, dy, maxlines=2)
    if s.get("sub"): a, dy = appear(t, dur * 0.6); cblock(d, y + 80, s["sub"], R, 50, DIM, a, dy, maxlines=2)

TYPES = dict(hook=sc_hook, title=sc_title, bullets=sc_bullets, terminal=sc_terminal, code=sc_code,
             bars=sc_bars, cards=sc_cards, timeline=sc_timeline, cta=sc_cta, visual=sc_visual)

# ---------------- background, camera, post FX ----------------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
BASE = np.zeros((H, W, 3), np.float32); g = yy / H
BASE[..., 0] = 8 + 10 * g; BASE[..., 1] = 9 + 4 * g; BASE[..., 2] = 18 + 10 * (1 - g)
rr = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.45) / (H * 0.62)) ** 2)
VIG = np.clip(1.15 - 0.75 * rr ** 2, 0.25, 1)[..., None].astype(np.float32)
del yy, xx, rr, g
def blob(rad, col):
    y, x = np.mgrid[-rad:rad, -rad:rad].astype(np.float32)
    return (np.exp(-(x * x + y * y) / (2 * (rad / 2.6) ** 2))[..., None] * np.array(col, np.float32)).astype(np.float32)
BLOB1 = blob(560, TH['b1']); BLOB2 = blob(520, TH['b2']); BLOB3 = blob(380, TH['b3'])
rng = np.random.default_rng(3)
GRAIN = [(rng.standard_normal((H // 2, W // 2)).astype(np.float32) * 6).repeat(2, 0).repeat(2, 1)[..., None] for _ in range(6)]
P = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(30, 110), rng.uniform(0.3, 1.2), rng.uniform(0, 6.28), rng.uniform(1.5, 4.5), rng.uniform(0.3, 1)) for _ in range(70)]
HORIZON = 1390

def addblob(out, b, cx, cy, k=1.0):
    h, w = b.shape[:2]; x0, y0 = int(cx - w / 2), int(cy - h / 2)
    sx0, sy0 = max(0, -x0), max(0, -y0); dx0, dy0 = max(0, x0), max(0, y0); dx1, dy1 = min(W, x0 + w), min(H, y0 + h)
    if dx1 > dx0 and dy1 > dy0: out[dy0:dy1, dx0:dx1] += b[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0] * k

def background(T, beat):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img); sp = (T * 0.55) % 1.0
    for i in range(14):
        z = (i + sp) / 14; y = HORIZON + (H - HORIZON) * z ** 2.2
        c = int(25 + 70 * z ** 1.5 * (1 + 0.4 * beat)); d.line((0, y, W, y), fill=tuple(int(c * v / 255) for v in RUST), width=2 + int(2 * z))
    for i in range(-12, 13): d.line((W / 2 + i * 14, HORIZON, W / 2 + i * 190, H), fill=tuple(int(v * 0.24) for v in RUST), width=2)
    for (x, y0, v, f, ph, s, br) in P:
        y = (y0 - T * v) % (H + 60) - 30; x2 = x + 35 * math.sin(T * f + ph)
        d.ellipse((x2 - s, y - s, x2 + s, y + s), fill=mix(tuple(min(255, v + 40) for v in RUST), br * (0.5 + 0.5 * math.sin(T * 3 + ph))))
    arr = BASE + np.asarray(img, np.float32)
    addblob(arr, BLOB1, W * 0.25 + 220 * math.sin(T * 0.31), H * 0.32 + 260 * math.cos(T * 0.23), 1 + 0.35 * beat)
    addblob(arr, BLOB2, W * 0.8 + 200 * math.cos(T * 0.27), H * 0.62 + 240 * math.sin(T * 0.19))
    addblob(arr, BLOB3, W * 0.5 + 300 * math.sin(T * 0.17 + 1), H * 0.85 + 120 * math.cos(T * 0.29))
    return arr

def hud(T):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 8), fill=(30, 36, 44)); d.rectangle((0, 0, W * T / TOTAL, 8), fill=RUST)
    d.text((60, 64), BRAND, font=B(34), fill=RUST)
    d.text((W - 60 - d.textlength("#shorts", font=R(34)), 64), "#shorts", font=R(34), fill=DIM)
    return np.asarray(img, np.float32)

def render(idx):
    T = idx / FPS
    si = max(i for i, s in enumerate(STARTS) if s <= T + 1e-6); t = T - STARTS[si]; dur = DURS[si]
    beat = math.exp(-((T % 0.5) * 9)) if T >= DROP else 0.0
    out = background(T, beat)
    layer = Image.new("RGB", (W, H)); sc = SCENES[si]
    TYPES[sc["type"]](ImageDraw.Draw(layer), t, sc, dur)
    last = si == len(SCENES) - 1
    e = ease(t / 0.55); x = 0 if last else clamp((t - (dur - 0.4)) / 0.4)
    s = (1 + 0.045 * t / dur) * (1 + 0.18 * (1 - e)) * (1 + 0.35 * x * x) * (1 + 0.012 * beat)
    rot = math.radians(0.5 * math.sin(T * 0.5) + (3.5 if si % 2 else -3.5) * (1 - e))
    ox = 8 * math.sin(T * 0.7); oy = 10 * math.cos(T * 0.5) + 60 * (1 - e)
    ca, sa = math.cos(rot) / s, math.sin(rot) / s; cx, cy = W / 2, H / 2
    layer = layer.transform((W, H), Image.AFFINE, (ca, sa, cx - ca * (cx + ox) - sa * (cy + oy), -sa, ca, cy + sa * (cx + ox) - ca * (cy + oy)), Image.BILINEAR)
    k = e * (1 - x) * (clamp((TOTAL - T) / 1.2) if last else 1)
    small = layer.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(7)).resize((W, H), Image.BILINEAR)
    out += (np.asarray(layer, np.float32) + np.asarray(small, np.float32) * 1.1) * k
    out *= VIG; out += hud(T)
    fl = 120 * math.exp(-t * 14) if si > 0 and t < 0.35 else 0
    if 0 <= T - DROP < 0.3: fl = max(fl, 90 * math.exp(-(T - DROP) * 12))
    if fl: out += fl
    sh = int(16 * math.exp(-t * 10)) if si > 0 and t < 0.3 else 0
    if si == 0 and (1.55 < t < 1.75 or 3.1 < t < 3.2): sh = 14 + int(8 * math.sin(T * 90))
    if sh:
        out[..., 0] = np.roll(out[..., 0], sh, 1); out[..., 2] = np.roll(out[..., 2], -sh, 1)
        if si == 0:
            for y0 in (820, 900, 960): out[y0:y0 + 40] = np.roll(out[y0:y0 + 40], int(30 * math.sin(T * 50 + y0)), 1)
    out += GRAIN[idx % 6]
    return np.clip(out, 0, 255).astype(np.uint8).tobytes()

if __name__ == "__main__":
    for sc in SCENES: assert sc["type"] in TYPES, f"unknown scene type {sc['type']}"
    if "--preview" in sys.argv:
        fr = [float(v) for v in sys.argv[sys.argv.index("--preview") + 1].split(",")]
        thumbs = []
        for i, (st, du) in enumerate(zip(STARTS, DURS)):
            for f in fr: thumbs.append(Image.frombytes("RGB", (W, H), render(int((st + du * f) * FPS))).resize((270, 480)))
        cols = len(fr) * 4; rows = math.ceil(len(thumbs) / cols)
        sheet = Image.new("RGB", (270 * cols, 480 * rows))
        for i, im in enumerate(thumbs): sheet.paste(im, ((i % cols) * 270, (i // cols) * 480))
        sheet.save(os.path.join(BUILD, "preview.png")); print("preview", os.path.join(BUILD, "preview.png")); sys.exit()
    OUT = os.path.join(BUILD, "video.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", os.path.join(BUILD, "music.wav"), "-i", os.path.join(BUILD, "voice.wav"),
        "-filter_complex",
        "[1:a]volume=0.85[m];[2:a]aresample=44100,pan=stereo|c0=c0|c1=c0,volume=1.5[v];"
        "[m][v]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]",
        "-map", "0:v", "-map", "[a]", "-ar", "44100",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-maxrate", "16M", "-bufsize", "32M", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    with Pool(os.cpu_count() or 4) as pool:
        for i, fr in enumerate(pool.imap(render, range(NFR), chunksize=4)):
            p.stdin.write(fr)
            if i % 300 == 0: print(f"frame {i}/{NFR}", flush=True)
    p.stdin.close(); p.wait()
    if p.returncode: sys.exit("ffmpeg failed")
    print("video", OUT)
