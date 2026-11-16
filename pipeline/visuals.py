"""Topic illustrations: procedural motion graphics drawn on the (black, additive) scene layer.

Each visual is draw(d, t, dur, s) where s is the scene dict (params read from it).
Art occupies roughly y = 560..1360 of the 1080x1920 frame; render.py draws heading/caption.
Available: containers, race, gauge, ownership, shield, lanes, compiler, network, layers, tree
"""
import math
from PIL import ImageFont

W, H = 1080, 1920
PAL = dict(A=(255, 104, 36), A2=(88, 166, 255), WH=(240, 242, 245), DIM=(150, 158, 170), PANEL=(24, 30, 40), BAD=(255, 70, 70))
def setpal(**k): PAL.update(k)

FD = "/usr/share/fonts/truetype/dejavu/"; _fc = {}
def font(n, s):
    k = (n, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(FD + n, max(8, int(s)))
    return _fc[k]
B = lambda s: font("DejaVuSans-Bold.ttf", s); R = lambda s: font("DejaVuSans.ttf", s); MB = lambda s: font("DejaVuSansMono-Bold.ttf", s)

def clamp(t): return max(0.0, min(1.0, t))
def ease(t): t = clamp(t); return 1 - (1 - t) ** 3
def inout(t): t = clamp(t); return t * t * (3 - 2 * t)
def backout(t):
    t = clamp(t); c = 1.9; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2
def mix(c, a): a = max(0.0, a); return tuple(min(255, int(v * a)) for v in c)
def C(name, a=1.0): return mix(PAL[name], a)
def text_c(d, x, y, s, f, col):
    d.text((x - d.textlength(s, font=f) / 2, y), s, font=f, fill=col)
def fit(d, s, fn, size, maxw):
    while d.textlength(s, font=fn(size)) > maxw and size > 18: size -= 2
    return fn(size)
def tscale(dur, base=5.0): return max(0.7, min(2.0, dur / base))

def arrow(d, pts, prog, col, width=8, head=26):
    """Polyline arrow drawn up to fraction prog of its length."""
    if prog <= 0: return
    segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    lens = [math.dist(a, b) for a, b in segs]; total = sum(lens); target = total * clamp(prog); acc = 0; out = [pts[0]]
    for (a, b), L in zip(segs, lens):
        if acc + L >= target:
            f = (target - acc) / L if L else 0; out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)); break
        out.append(b); acc += L
    d.line(out, fill=col, width=width, joint="curve")
    if len(out) >= 2:
        (x0, y0), (x1, y1) = out[-2], out[-1]; ang = math.atan2(y1 - y0, x1 - x0)
        d.polygon([(x1 + head * math.cos(ang), y1 + head * math.sin(ang)),
                   (x1 + head * 0.8 * math.cos(ang + 2.4), y1 + head * 0.8 * math.sin(ang + 2.4)),
                   (x1 + head * 0.8 * math.cos(ang - 2.4), y1 + head * 0.8 * math.sin(ang - 2.4))], fill=col)
def bez(p0, p1, p2, n=24):
    return [((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0], (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1]) for u in [i / n for i in range(n + 1)]]
def ring(d, x, y, r, col, w=5):
    if sum(col) < 6: return
    d.ellipse((x - r, y - r, x + r, y + r), outline=col, width=w)
def check(d, x, y, sz, col, w=12): d.line([(x - sz * 0.5, y), (x - sz * 0.12, y + sz * 0.4), (x + sz * 0.55, y - sz * 0.45)], fill=col, width=w, joint="curve")

# ------------------------------------------------------------------ containers
def iso_cube(d, x, y, s, col, a=1.0, glow=0.0):
    u, v = s * 0.87, s * 0.5
    N, E, S, Wp = (x, y - v), (x + u, y), (x, y + v), (x - u, y)
    top = mix(col, a * (1.0 + glow)); left = mix(col, a * 0.5); right = mix(col, a * 0.3)
    d.polygon([Wp, S, (S[0], S[1] + s), (Wp[0], Wp[1] + s)], fill=left)
    d.polygon([S, E, (E[0], E[1] + s), (S[0], S[1] + s)], fill=right)
    d.polygon([N, E, S, Wp], fill=top)
    for k in range(1, 5):  # container ribs
        f = k / 5
        d.line([(Wp[0] + (S[0] - Wp[0]) * f, Wp[1] + (S[1] - Wp[1]) * f + 6), (Wp[0] + (S[0] - Wp[0]) * f, Wp[1] + (S[1] - Wp[1]) * f + s - 6)], fill=mix(col, a * 0.75), width=3)
        d.line([(S[0] + (E[0] - S[0]) * f, S[1] + (E[1] - S[1]) * f + 6), (S[0] + (E[0] - S[0]) * f, S[1] + (E[1] - S[1]) * f + s - 6)], fill=mix(col, a * 0.55), width=3)
    d.line([Wp, N, E, S, Wp], fill=mix((255, 255, 255), a * 0.45), width=2)

def containers(d, t, dur, s):
    cx, cy, sz = 540, 800, 118; u, v = sz * 0.87, sz * 0.5; ts = tscale(dur)
    def P(i, j, k=0): return (cx + (i - j) * u, cy + (i + j) * v - k * sz)
    a0 = ease(t / 0.6)
    pl = [P(-0.5, -0.5), P(2.5, -0.5), P(2.5, 2.5), P(-0.5, 2.5)]; pl = [(x, y + sz) for x, y in pl]
    d.polygon(pl, outline=C("A", 0.6 * a0)); d.line(pl + [pl[0]], fill=C("A", 0.7 * a0), width=4)
    for q in range(1, 3):
        for (i0, j0, i1, j1) in ((q - 0.5, -0.5, q - 0.5, 2.5), (-0.5, q - 0.5, 2.5, q - 0.5)):
            p0, p1 = P(i0, j0), P(i1, j1); d.line([(p0[0], p0[1] + sz), (p1[0], p1[1] + sz)], fill=C("A", 0.3 * a0), width=2)
    pos = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (2, 0, 0), (1, 1, 0), (0, 2, 0), (2, 1, 0), (1, 2, 0), (2, 2, 0), (0, 0, 1), (1, 0, 1), (0, 1, 1), (0, 0, 2)]
    n = min(len(pos), s.get("count", 12)); span = (dur * 0.6) / n
    order = sorted(range(n), key=lambda q: (pos[q][2], pos[q][0] + pos[q][1]))
    land = {q: 0.5 + r * span for r, q in enumerate(order)}
    for q in sorted(range(n), key=lambda q: (pos[q][0] + pos[q][1], pos[q][2])):
        p = (t - land[q] + 0.45) / 0.45
        if p <= 0: continue
        i, j, k = pos[q]; x, y = P(i, j, k); y -= (1 - backout(p)) * 650
        glow = 0.8 * math.exp(-max(0, t - land[q]) * 5) if t > land[q] else 0
        iso_cube(d, x, y, sz, PAL["A2"] if q % 3 == 2 else PAL["A"], clamp(p * 2), glow)
    if s.get("label"):
        f = fit(d, s["label"], MB, 54, 600); a = ease((t - 0.8) / 0.5); text_c(d, cx, cy + 5.6 * v + sz + 20, s["label"], f, C("WH", a))

# ------------------------------------------------------------------ race
def race(d, t, dur, s):
    lanes = s.get("lanes", [{"label": "A", "value": 1}, {"label": "B", "value": 3}])[:3]
    vmax = max(l["value"] for l in lanes); vmin = min(l["value"] for l in lanes); unit = s.get("unit", "")
    x0, x1 = 110, 970; t0 = 0.9; run = min(3.4, dur * 0.55)
    # 3-2-1 lights
    for k in range(3):
        on = t > 0.15 + k * 0.22; text = ["3", "2", "1"][k]
        d.ellipse((380 + k * 120, 570, 460 + k * 120, 650), fill=C("A" if t > t0 else "BAD", 1 if on else 0.15))
        text_c(d, 420 + k * 120, 588, text, B(40), (0, 0, 0) if on else C("DIM", 0.3))
    for i, l in enumerate(lanes):
        y = 760 + i * 240; win = l["value"] == vmin; col = PAL["A"] if win else PAL["A2"]
        a = ease((t - 0.2 - i * 0.15) / 0.5)
        d.text((x0, y - 70), l["label"], font=B(54), fill=C("WH", a))
        d.rounded_rectangle((x0, y, x1, y + 90), 45, outline=C("DIM", 0.5 * a), width=3)
        for k in range(12):  # checkered finish
            d.rectangle((x1 - 30 + (k % 2) * 15, y + (k // 2) * 15, x1 - 15 + (k % 2) * 15, y + 15 + (k // 2) * 15), fill=C("WH", 0.7 * a) if (k + k // 2) % 2 else (0, 0, 0))
        ft = t0 + run * l["value"] / vmax; p = clamp((t - t0) / max(0.04, ft - t0)) ** 1.4 if t > t0 else 0
        hx = x0 + 45 + (x1 - x0 - 120) * p
        for k in range(10):  # motion trail
            tx = hx - k * 26 * (1 if 0 < p < 1 else 0.3)
            if tx > x0 + 30: d.ellipse((tx - 30 + k * 2, y + 15 + k * 1.5, tx + 30 - k * 2, y + 75 - k * 1.5), fill=mix(col, (1 - k / 10) * 0.5))
        d.ellipse((hx - 36, y + 9, hx + 36, y + 81), fill=col)
        if p >= 1:
            sc = backout((t - ft) / 0.4); dec = l.get("decimals", 0 if float(l["value"]).is_integer() else 2)
            lab = f"{l['value']:,.{dec}f} {unit}".strip(); f = B(int(56 * (0.5 + 0.5 * sc)))
            d.text((x1 - d.textlength(lab, font=f), y - 72), lab, font=f, fill=mix(col, clamp(sc * 1.5)))
            if win: ring(d, hx, y + 45, 40 + 60 * clamp((t - ft) / 0.5), mix(col, 1 - clamp((t - ft) / 0.5)), 6)
    if 0 < t - t0 < run + 0.3:  # speed streaks
        for k in range(18):
            yy = 700 + (k * 97) % 700; xx = (W + 300) - ((t * 2600 + k * 337) % (W + 600))
            d.line((xx, yy, xx + 120 + (k % 4) * 40, yy), fill=C("WH", 0.18), width=3)

# ------------------------------------------------------------------ gauge
def gauge(d, t, dur, s):
    cx, cy, r = 540, 1100, 400; val, mx = s.get("value", 80), s.get("max", 100)
    a = ease(t / 0.6); p = backout((t - 0.6) / (1.4 * tscale(dur))) if t > 0.6 else 0
    frac = clamp(val / mx) * p; ang = 180 + 180 * frac
    for k in range(30):  # streaks scale with needle
        yy = 560 + (k * 89) % 560; ln = 80 + (k % 5) * 50; xx = (W + 300) - ((t * 1800 + k * 263) % (W + 600))
        d.line((xx, yy, xx + ln, yy), fill=C("A2", 0.25 * frac), width=3)
    d.arc((cx - r, cy - r, cx + r, cy + r), 180, 360, fill=C("PANEL", 2.0 * a), width=40)
    if frac > 0.005: d.arc((cx - r, cy - r, cx + r, cy + r), 180, ang, fill=C("A"), width=40)
    for k in range(21):
        an = math.radians(180 + k * 9); r1 = r - 70 if k % 5 == 0 else r - 50
        d.line((cx + r1 * math.cos(an), cy + r1 * math.sin(an), cx + (r - 30) * math.cos(an), cy + (r - 30) * math.sin(an)), fill=C("WH", 0.7 * a), width=5 if k % 5 == 0 else 2)
    an = math.radians(ang); d.line((cx, cy, cx + (r - 80) * math.cos(an), cy + (r - 80) * math.sin(an)), fill=C("WH", a), width=12)
    d.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), fill=C("A", a)); ring(d, cx, cy, 50, C("WH", 0.5 * a), 4)
    v = val * clamp((t - 0.6) / (1.4 * tscale(dur))); dec = s.get("decimals", 0 if float(val).is_integer() else 1)
    lab = f"{v:,.{dec}f}"; text_c(d, cx, cy - 300, lab, B(140), C("WH", a))
    text_c(d, cx, cy - 145, s.get("unit", ""), fit(d, s.get("unit", ""), B, 54, 520), C("A", a))
    if s.get("label"): text_c(d, cx, cy + 80, s["label"], fit(d, s["label"], R, 50, 900), C("DIM", ease((t - 1.4) / 0.5)))

# ------------------------------------------------------------------ ownership (move semantics)
def ownership(d, t, dur, s):
    k = tscale(dur); A_, B_, val = s.get("a", "s1"), s.get("b", "s2"), s.get("value", '"hello"')
    def box(x0, y0, x1, y1, label, sub, a, col, dead=0.0):
        d.rounded_rectangle((x0, y0, x1, y1), 22, fill=C("PANEL", a * 1.6), outline=mix(col, a * (1 - 0.6 * dead)), width=5)
        text_c(d, (x0 + x1) / 2, y0 + 22, label, MB(60), mix(PAL["WH"], a * (1 - 0.6 * dead)))
        if sub: text_c(d, (x0 + x1) / 2, y0 + 100, sub, R(34), C("DIM", a * (1 - 0.5 * dead)))
    tA, tH, tArr, tB, tMove = 0.3 * k, 0.8 * k, 1.2 * k, 2.2 * k, 2.7 * k
    text_c(d, 540, 560, "STACK", B(36), C("DIM", ease(t / 0.5))); text_c(d, 540, 1000, "HEAP", B(36), C("DIM", ease((t - tH) / 0.5)))
    borrow = s.get("mode") == "borrow"
    dead = 0.0 if borrow else ease((t - tMove - 0.3) / 0.5)
    if t > tA: box(110, 630, 450, 790, A_, "owner" if dead < 0.5 else "moved", backout((t - tA) / 0.5), PAL["A"], dead)
    if t > tB: box(630, 630, 970, 790, B_, "borrows" if borrow else "owner", backout((t - tB) / 0.5), PAL["A2"] if borrow else PAL["A"])
    if t > tH:
        a = backout((t - tH) / 0.5); d.rounded_rectangle((270, 1070, 810, 1230), 26, fill=C("PANEL", 1.6 * a), outline=C("A2", a), width=5)
        text_c(d, 540, 1115, val, fit(d, val, MB, 64, 480), C("WH", a))
    fade = 1.0 if borrow else 1 - ease((t - tMove) / 0.5)
    arrow(d, bez((280, 800), (280, 980), (470, 1060)), ease((t - tArr) / 0.6), C("A", fade), 9)
    if borrow:  # reference: dashed arrow b -> a
        g = ease((t - tMove) / 0.6); pts = bez((630, 700), (540, 640), (452, 700), 30)
        for q in range(0, int(len(pts) * g) - 1, 2): d.line([pts[q], pts[q + 1]], fill=C("A2"), width=8)
        if g > 0.95: arrow(d, [pts[-3], pts[-1]], 1, C("A2"), 8)
    else:
        arrow(d, bez((800, 800), (800, 980), (610, 1060)), ease((t - tMove) / 0.6), C("A"), 9)
    if dead > 0:
        d.line((140, 650, 420, 770), fill=C("BAD", dead), width=10); d.line((140, 770, 420, 650), fill=C("BAD", dead), width=10)
    if s.get("note"): text_c(d, 540, 1290, s["note"], fit(d, s["note"], B, 46, 920), C("A" if borrow or not s.get("note_bad", True) else "BAD", ease((t - tMove - 0.8) / 0.5)))

# ------------------------------------------------------------------ shield (memory safety)
def shield(d, t, dur, s):
    k = tscale(dur); cols, rows, cs, gx, gy = 7, 6, 104, 540 - 3.5 * 104, 600
    bad = (4, 2)
    for r in range(rows):
        for c in range(cols):
            x, y = gx + c * cs, gy + r * cs; h = (c * 7 + r * 13) % 11
            on = ease((t - 0.1 - h * 0.06) / 0.3)
            used = (c * 3 + r * 5) % 4 != 0
            if (c, r) == bad:
                d.rounded_rectangle((x + 8, y + 8, x + cs - 8, y + cs - 8), 14, outline=C("BAD", on * (0.6 + 0.4 * math.sin(t * 6))), width=4)
                text_c(d, x + cs / 2, y + 28, "free", R(28), C("BAD", on * 0.8))
            else:
                pulse = 0.15 * math.sin(t * 2 + h)
                d.rounded_rectangle((x + 8, y + 8, x + cs - 8, y + cs - 8), 14, fill=C("A2" if used else "PANEL", on * ((0.55 if used else 1.2) + pulse)))
    bx, by = gx + bad[0] * cs + cs / 2, gy + bad[1] * cs + cs / 2
    t_hit = 1.6 * k
    sx, sy = 120, 1320  # pointer flies in from bottom-left
    p = ease((t - 0.8 * k) / (t_hit - 0.8 * k))
    if 0 < p < 1 or t < t_hit:
        if p > 0:
            px, py = sx + (bx - sx) * p, sy + (by - sy) * p
            for q in range(8): d.ellipse((px - 18 + q * 2 - q * (bx - sx) * 0.012, py - 18 + q * 2 - q * (by - sy) * 0.012, px + 18 - q * 2 - q * (bx - sx) * 0.012, py + 18 - q * 2 - q * (by - sy) * 0.012), fill=C("BAD", 1 - q / 8))
    if t >= t_hit:
        e = backout((t - t_hit) / 0.45); R0 = 150 * e
        pts = [(bx - R0, by - R0 * 0.85), (bx, by - R0 * 1.05), (bx + R0, by - R0 * 0.85), (bx + R0 * 0.9, by + R0 * 0.2), (bx, by + R0 * 1.1), (bx - R0 * 0.9, by + R0 * 0.2)]
        d.polygon(pts, fill=C("PANEL", 2.0)); d.line(pts + [pts[0]], fill=C("A"), width=10, joint="curve")
        if e > 0.6: check(d, bx, by, 110 * e, C("A"), 16)
        ring(d, bx, by, 160 + 260 * clamp((t - t_hit) / 0.6), C("A", 1 - clamp((t - t_hit) / 0.6)), 8)
        lab = s.get("label", "caught at compile time")
        text_c(d, 540, 1290, lab, fit(d, lab, B, 54, 940), C("A", ease((t - t_hit - 0.3) / 0.4)))

# ------------------------------------------------------------------ lanes (async / concurrency)
def lanes(d, t, dur, s):
    labels = s.get("labels", ["task A", "task B", "task C", "task D"])[:5]; n = len(labels)
    x0, x1 = 300, 1010; gap = 680 / max(1, n - 1) if n > 1 else 0; ex, ey = 150, 620 + 340
    a = ease(t / 0.5)
    ring(d, ex, ey, 90, C("A", a), 8)
    for k in range(3):
        an = t * 3 + k * 2.09; d.arc((ex - 70, ey - 70, ex + 70, ey + 70), math.degrees(an), math.degrees(an) + 70, fill=C("A2", a), width=10)
    text_c(d, ex, ey + 110, s.get("hub", "runtime"), B(36), C("WH", a))
    for i, lab in enumerate(labels):
        y = 620 + i * gap; la = ease((t - 0.2 - i * 0.12) / 0.5)
        d.line((x0, y, x1, y), fill=C("DIM", 0.35 * la), width=3)
        d.line([(ex + 90, ey), (ex + 130, ey), (x0 - 40, y), (x0, y)], fill=C("A", 0.35 * la), width=3)
        d.text((x0, y - 82), lab, font=B(34), fill=C("DIM", la))
        for kk in range(4):  # tasks: move -> await (pause) -> move
            st = 0.5 + kk * 1.25 + i * 0.37; e = t - st
            if e < 0: continue
            m1, wait, m2 = 0.7, (0.9 if (kk + i) % 2 == 0 else 0.0), 0.9
            mid = x0 + 40 + (x1 - x0 - 200) * 0.45
            if e < m1: x = x0 + (mid - x0) * inout(e / m1); waiting = False
            elif e < m1 + wait: x = mid; waiting = True
            elif e < m1 + wait + m2: x = mid + (x1 - 100 - mid) * inout((e - m1 - wait) / m2); waiting = False
            else: continue
            col = PAL["A"] if (kk + i) % 2 else PAL["A2"]; aa = 0.45 if waiting else 1.0
            d.rounded_rectangle((x - 60, y - 34, x + 60, y + 34), 34, fill=mix(col, aa))
            if waiting:
                pa = 0.6 + 0.4 * math.sin(t * 8); d.rounded_rectangle((x - 70, y - 44, x + 70, y + 44), 44, outline=C("WH", pa), width=3)
                text_c(d, x, y - 23, ".await", MB(30), C("WH", pa))

# ------------------------------------------------------------------ compiler pipeline
def gear(d, cx, cy, r, teeth, rot, col, w=6):
    pts = []
    for k in range(teeth):
        a0 = rot + 2 * math.pi * k / teeth; tw = math.pi / teeth
        for (da, rr) in ((-tw, r * 0.82), (-tw * 0.55, r), (tw * 0.55, r), (tw, r * 0.82)):
            pts.append((cx + rr * math.cos(a0 + da), cy + rr * math.sin(a0 + da)))
    d.polygon(pts, fill=mix(col, 0.25)); d.line(pts + [pts[0]], fill=col, width=w)
    ring(d, cx, cy, r * 0.32, col, w)

def compiler(d, t, dur, s):
    k = tscale(dur); a = backout(t / 0.5)
    fx0, fy0, fx1, fy1 = 380, 560, 700, 790  # source file
    d.polygon([(fx0, fy0), (fx1 - 50, fy0), (fx1, fy0 + 50), (fx1, fy1), (fx0, fy1)], fill=C("PANEL", 1.6 * a), outline=C("WH", 0.8 * a))
    d.line([(fx0, fy0), (fx1 - 50, fy0), (fx1, fy0 + 50), (fx1, fy1), (fx0, fy1), (fx0, fy0)], fill=C("WH", 0.8 * a), width=4)
    for q, (w_, c) in enumerate([(180, "A"), (230, "A2"), (140, "WH"), (200, "A"), (120, "A2")]):
        d.rounded_rectangle((fx0 + 30 + (q % 2) * 30, fy0 + 70 + q * 28, fx0 + 30 + (q % 2) * 30 + w_ * 0.9, fy0 + 84 + q * 28), 6, fill=C(c, 0.8 * a))
    text_c(d, (fx0 + fx1) / 2, fy0 - 50, s.get("file", "main.rs"), MB(36), C("WH", a))
    run = clamp((t - 0.7) / 0.3)
    for q in range(14):  # particles: file -> gears
        ph = (t * 1.4 + q / 14) % 1.0; y = 800 + ph * 160; x = 540 + 60 * math.sin(q * 1.7 + ph * 4)
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=C("A2" if q % 2 else "A", run * (1 - ph)))
    rot = t * 1.6 * run
    gear(d, 470, 1040, 125, 12, rot, C("A", a)); gear(d, 640, 1110, 82, 8, -rot * 125 / 82 + 0.2, C("A2", a))
    out = ease((t - 1.6 * k) / 0.5)
    if out > 0:
        for q in range(10):
            ph = (t * 1.2 + q / 10) % 1.0; y = 1160 + ph * 80
            text_c(d, 470 + (q % 5) * 35, y, "01"[q % 2], MB(26), C("A2", out * (1 - ph)))
        bx0, by0 = 380, 1260; d.rounded_rectangle((bx0, by0, bx0 + 320, by0 + 110), 24, fill=C("PANEL", 1.8), outline=C("A", out), width=5)
        text_c(d, 540, by0 + 28, s.get("output", "binary"), MB(46), C("WH", out))
    done = backout((t - 2.3 * k) / 0.45)
    if done > 0:
        d.ellipse((740 - 55 * done, 1250 - 55 * done, 740 + 55 * done, 1250 + 55 * done), fill=C("A")); check(d, 740, 1250, 60 * done, (0, 0, 0), 10)
        if s.get("badge"):
            f = B(int(60 * done)); bw = d.textlength(s["badge"], font=f) + 60
            d.rounded_rectangle((820 - bw / 2, 600, 820 + bw / 2, 690), 45, fill=C("A", done)); text_c(d, 820, 612, s["badge"], f, (0, 0, 0))

# ------------------------------------------------------------------ network
def network(d, t, dur, s):
    cx, cy = 540, 960; a = ease(t / 0.6); n = 9
    nodes = [(cx + (300 + 60 * ((q * 37) % 3)) * math.cos(q * 2 * math.pi / n + 0.3), cy + (300 + 60 * ((q * 53) % 3)) * math.sin(q * 2 * math.pi / n + 0.3)) for q in range(n)]
    edges = [(-1, q) for q in range(n)] + [(q, (q + 1) % n) for q in range(0, n, 2)]
    pos = lambda q: (cx, cy) if q == -1 else nodes[q]
    for e_i, (p, q) in enumerate(edges):
        g = ease((t - 0.3 - e_i * 0.05) / 0.5)
        if g <= 0: continue
        (x0, y0), (x1, y1) = pos(p), pos(q); d.line((x0, y0, x0 + (x1 - x0) * g, y0 + (y1 - y0) * g), fill=C("DIM", 0.4), width=3)
        if g >= 1:
            for k in range(2):
                ph = (t * (0.6 + 0.1 * (e_i % 4)) + k * 0.5 + e_i * 0.13) % 1.0
                if (e_i + k) % 2: ph = 1 - ph
                x, y = x0 + (x1 - x0) * ph, y0 + (y1 - y0) * ph
                d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=C("A" if k else "A2"))
    labels = s.get("nodes", [])
    for q, (x, y) in enumerate(nodes):
        sc = backout((t - 0.5 - q * 0.08) / 0.4)
        if sc <= 0: continue
        r = 40 * sc; d.ellipse((x - r, y - r, x + r, y + r), fill=C("PANEL", 2), outline=C("A2"), width=4)
        if q < len(labels): text_c(d, x, y + 50, labels[q], fit(d, labels[q], R, 30, 220), C("DIM", sc))
    pr = 0.5 + 0.5 * math.sin(t * 4); sc = backout((t - 0.2) / 0.5)
    ring(d, cx, cy, 100 + 30 * pr, C("A", 0.5 * a), 4)
    d.ellipse((cx - 85 * sc, cy - 85 * sc, cx + 85 * sc, cy + 85 * sc), fill=C("A"))
    lab = s.get("center", "server"); text_c(d, cx, cy - 22, lab, fit(d, lab, B, 40, 150), (0, 0, 0))

# ------------------------------------------------------------------ layers (stack)
def layers(d, t, dur, s):
    names = s.get("layers", ["Hardware", "Kernel", "Rust", "Apps"])[:5]; hl = s.get("highlight", len(names) - 1)
    u, v, h = 380, 95, 50; cx = 540; base = 1300; step = 200 if len(names) <= 4 else 160
    for i, name in enumerate(names):
        st = 0.3 + i * 0.45 * tscale(dur); e = backout((t - st) / 0.5) if i != hl else ease((t - st) / 0.6)
        if t < st: continue
        y = base - i * step; col = PAL["A"] if i == hl else PAL["A2"]
        yo = -(1 - e) * 500 if i == hl else (1 - e) * 80; xo = 0
        y += yo; a = clamp(e * 1.5) * (1 if i == hl else 0.75)
        N, E, S, Wp = (cx, y - v), (cx + u, y), (cx, y + v), (cx - u, y)
        d.polygon([Wp, S, (S[0], S[1] + h), (Wp[0], Wp[1] + h)], fill=mix(col, a * 0.45))
        d.polygon([S, E, (E[0], E[1] + h), (S[0], S[1] + h)], fill=mix(col, a * 0.28))
        glow = 0.7 * math.exp(-max(0, t - st - 0.6) * 4) if i == hl else 0
        d.polygon([N, E, S, Wp], fill=mix(col, a * (0.7 + glow)), outline=mix((255, 255, 255), a * 0.5))
        f = fit(d, name, B, 52, 420); text_c(d, cx, y - 30, name, f, (10, 10, 14) if i == hl else C("WH", a))

# ------------------------------------------------------------------ tree (crate dependencies)
def tree(d, t, dur, s):
    root = s.get("root", "my-app"); kids = s.get("children", [{"name": "serde"}, {"name": "tokio"}, {"name": "clap"}])[:4]
    k = tscale(dur)
    def node(x, y, label, sc, col):
        if sc <= 0: return
        f = fit(d, label, MB, 40, 230); w_ = d.textlength(label, font=f) / 2 + 36
        d.rounded_rectangle((x - w_ * sc, y - 45 * sc, x + w_ * sc, y + 45 * sc), 22, fill=C("PANEL", 1.8), outline=col, width=5)
        if sc > 0.7: text_c(d, x, y - 24, label, f, C("WH", clamp((sc - 0.7) * 3)))
    rx, ry = 540, 620; node(rx, ry, root, backout((t - 0.2) / 0.5), C("A"))
    n = len(kids); xs = [540 + (q - (n - 1) / 2) * (900 / max(1, n)) for q in range(n)]
    for q, (kid, x) in enumerate(zip(kids, xs)):
        st = 0.7 * k + q * 0.25 * k; g = ease((t - st) / 0.4)
        if g > 0: d.line(bez((rx, ry + 45), (x, ry + 120), (x, 900 - 45))[: max(2, int(25 * g))], fill=C("A", 0.7), width=5)
        node(x, 900, kid["name"], backout((t - st - 0.3) / 0.4), C("A2"))
        gk = kid.get("children", [])[:2]
        for r_, gname in enumerate(gk):
            gx = x + (r_ - (len(gk) - 1) / 2) * 140; st2 = st + 0.8 * k + r_ * 0.2
            g2 = ease((t - st2) / 0.4)
            if g2 > 0: d.line([(x, 945), (x + (gx - x) * g2, 945 + (1135 - 945) * g2)], fill=C("A2", 0.6), width=4)
            sc = backout((t - st2 - 0.3) / 0.4)
            if sc > 0:
                f = fit(d, gname, MB, 30, 130); r0 = 18 + d.textlength(gname, font=f) / 2
                d.rounded_rectangle((gx - r0 * sc, 1135, gx + r0 * sc, 1195), 18, fill=C("PANEL", 1.8), outline=C("DIM"), width=3)
                if sc > 0.7: text_c(d, gx, 1148, gname, f, C("DIM"))

# ------------------------------------------------------------------ vars (variables & mutability)
def padlock(d, x, y, sz, col, open_=False):
    d.rounded_rectangle((x - sz, y, x + sz, y + sz * 1.4), 8, fill=col)
    sx = x + (sz * 0.5 if open_ else 0); d.arc((sx - sz * 0.7, y - sz * 0.9, sx + sz * 0.7, y + sz * 0.5), 180, 360, fill=col, width=int(sz * 0.3))
    if not open_: d.line((x - sz * 0.7, y - sz * 0.2, x - sz * 0.7, y + 4), fill=col, width=int(sz * 0.3)); d.line((x + sz * 0.7, y - sz * 0.2, x + sz * 0.7, y + 4), fill=col, width=int(sz * 0.3))

def vars(d, t, dur, s):
    items = s.get("items", [{"name": "x", "value": "5"}, {"name": "y", "value": "10", "mut": True, "change": "11"}])[:3]
    k = tscale(dur); n = len(items); gap = 260
    y0 = 960 - (n - 1) * gap / 2 - 80
    for i, it in enumerate(items):
        y = y0 + i * gap; st = 0.3 + i * 0.35; a = backout((t - st) / 0.5)
        if a <= 0: continue
        mut = it.get("mut"); kw = "let mut " if mut else "let "
        d.text((110, y + 40), kw, font=MB(46), fill=C("A2" if mut else "DIM", clamp(a)))
        d.text((110 + d.textlength(kw, font=MB(46)), y + 40), it["name"], font=MB(46), fill=C("WH", clamp(a)))
        bx0, bx1 = 560, 900
        tc = 1.6 * k + i * 0.5; ch = it.get("change"); e = ease((t - tc) / 0.5) if ch else 0
        shake = 0
        if ch and not mut and 0 < t - tc < 0.6: shake = 14 * math.sin((t - tc) * 60) * (1 - (t - tc) / 0.6)
        col = PAL["BAD"] if (ch and not mut and t > tc) else PAL["A"]
        d.rounded_rectangle((bx0 + shake, y, bx1 + shake, y + 150), 24, fill=C("PANEL", 1.7 * a), outline=mix(col, clamp(a)), width=5)
        cx = (bx0 + bx1) / 2 + shake
        if ch and mut:
            if e < 1: text_c(d, cx, y + 38 - 60 * e, it["value"], fit(d, it["value"], MB, 64, 300), C("WH", clamp(a) * (1 - e)))
            if e > 0: text_c(d, cx, y + 38 + 60 * (1 - e), ch, fit(d, ch, MB, 64, 300), C("A", e))
        else:
            text_c(d, cx, y + 38, it["value"], fit(d, it["value"], MB, 64, 300), C("WH", clamp(a)))
        padlock(d, 970 + shake, y + 50, 26, C("A2" if mut else ("BAD" if ch and t > tc else "DIM"), clamp(a)), open_=bool(mut))
        if ch and not mut and t > tc + 0.2:
            d.text((bx0, y + 165), "cannot assign twice ✗", font=B(36), fill=C("BAD", ease((t - tc - 0.2) / 0.4)))

# ------------------------------------------------------------------ flow (match / if branching)
def flow(d, t, dur, s):
    arms = s.get("arms", [{"pattern": "1", "result": "one"}, {"pattern": "2", "result": "two"}, {"pattern": "_", "result": "other"}])[:4]
    hit = s.get("hit", 1); val = s.get("input", "2"); k = tscale(dur); n = len(arms)
    xs = [540 + (q - (n - 1) / 2) * min(250, 900 / n) for q in range(n)]
    a = backout(t / 0.5)
    w0 = d.textlength(val, font=MB(60)) / 2 + 50
    d.rounded_rectangle((540 - w0, 600, 540 + w0, 700), 50, fill=C("A", a)); text_c(d, 540, 615, val, MB(60), (0, 0, 0))
    text_c(d, 540, 560 - 20, s.get("kind", "match"), MB(34), C("DIM", a))
    for q, (arm, x) in enumerate(zip(arms, xs)):
        g = ease((t - 0.5 - q * 0.12) / 0.5)
        if g <= 0: continue
        d.line(bez((540, 700), (540, 800), (x, 860))[: max(2, int(25 * g))], fill=C("DIM", 0.5), width=4)
        bw = min(115, 900 / n / 2 - 8)
        ok = q == hit and t > 2.2 * k
        d.rounded_rectangle((x - bw, 870, x + bw, 980), 22, fill=C("PANEL", 1.8 * g), outline=C("A" if ok else "DIM", g if ok else 0.6 * g), width=6 if ok else 3)
        text_c(d, x, 895, arm["pattern"], fit(d, arm["pattern"], MB, 46, bw * 2 - 20), C("WH", g))
    # ball tests arms in order, then settles on the hit arm
    tb = t - 1.2 * k
    if tb > 0:
        step = 0.35 * k; idx = min(hit, int(tb / step)); x = xs[idx]
        fr = clamp((tb - idx * step) / step) if idx < hit else 1
        y = 760 + 70 * math.sin(math.pi * min(1, fr)) * (0 if idx == hit else 1)
        bx = xs[idx] + ((xs[min(hit, idx + 1)] - xs[idx]) * ease(fr) if idx < hit else 0)
        d.ellipse((bx - 24, 820 - 24, bx + 24, 820 + 24), fill=C("A2"))
        if idx < hit and fr < 0.5: text_c(d, xs[idx], 990, "✗", B(48), C("BAD", 1 - fr * 2))
    if t > 2.2 * k:
        sc = backout((t - 2.2 * k) / 0.45); x = xs[hit]; res = arms[hit]["result"]
        arrow(d, [(x, 990), (x, 1080)], ease((t - 2.2 * k) / 0.3), C("A"), 7)
        f = fit(d, res, MB, int(58 * (0.6 + 0.4 * sc)), 520); w1 = d.textlength(res, font=f) / 2 + 40
        d.rounded_rectangle((x - w1, 1110, x + w1, 1210), 30, fill=C("A", clamp(sc))); text_c(d, x, 1132, res, f, (0, 0, 0))
        ring(d, x, 925, 90 + 120 * clamp((t - 2.2 * k) / 0.5), C("A", 1 - clamp((t - 2.2 * k) / 0.5)), 5)

# ------------------------------------------------------------------ pipeline (iterator chains)
def pipeline(d, t, dur, s):
    stages = s.get("stages", [{"name": "iter()", "out": ["1", "2", "3", "4"]}, {"name": "filter", "out": ["2", "4"]}, {"name": "map", "out": ["4", "16"]}, {"name": "sum()", "out": ["20"]}])[:4]
    k = tscale(dur); n = len(stages); gap = 200
    y0 = 960 - (n - 1) * gap / 2 - 50
    for i, stg in enumerate(stages):
        st = 0.3 + i * 0.75 * k; y = y0 + i * gap; a = backout((t - st) / 0.45)
        if a <= 0: continue
        f = fit(d, stg["name"], MB, 40, 330); lw = d.textlength(stg["name"], font=f)
        d.rounded_rectangle((90, y, 140 + lw, y + 90), 24, fill=C("PANEL", 1.8), outline=C("A" if i in (0, n - 1) else "A2", clamp(a)), width=4)
        d.text((115, y + 22), stg["name"], font=f, fill=C("WH", clamp(a)))
        vals = stg["out"][:6]; x = 190 + lw
        for q, v in enumerate(vals):
            sc = backout((t - st - 0.2 - q * 0.08) / 0.35)
            if sc <= 0: continue
            fv = fit(d, v, MB, 40, 110); r = max(42, d.textlength(v, font=fv) / 2 + 18) * sc
            cx = x + 20 + r / max(sc, 1e-3); d.ellipse((cx - r, y + 45 - r, cx + r, y + 45 + r) if r < 60 else (cx - r, y + 45 - 45 * sc, cx + r, y + 45 + 45 * sc), fill=C("A" if i == n - 1 else "A2", 0.85))
            if sc > 0.7: text_c(d, cx, y + 23, v, fv, (0, 0, 0))
            x = cx + r / max(sc, 1e-3) + 12
        if i < n - 1 and t > st + 0.5:
            for q in range(5):
                ph = (t * 1.5 + q / 5) % 1.0; py = y + 95 + ph * (gap - 100)
                d.ellipse((140 - 6, py - 6, 140 + 6, py + 6), fill=C("A", 1 - ph))

VISUALS = dict(vars=vars, flow=flow, pipeline=pipeline, containers=containers, race=race, gauge=gauge, ownership=ownership, shield=shield,
               lanes=lanes, compiler=compiler, network=network, layers=layers, tree=tree)
