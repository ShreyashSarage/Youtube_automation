"""16:9 thumbnail from the real benchmark medians."""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import script as S
W, H = 1280, 720; FD = "/usr/share/fonts/truetype/dejavu/"
B = lambda s: ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", s); M = lambda s: ImageFont.truetype(FD + "DejaVuSansMono-Bold.ttf", s)
y, x = np.mgrid[0:H, 0:W].astype(np.float32); g = x / W * 0.6 + y / H * 0.4
a = np.array([18, 14, 30]) * (1 - g[..., None]) + np.array([70, 24, 48]) * g[..., None]
a += np.exp(-(((x / W - 0.85) ** 2 + (y / H - 0.2) ** 2) / 0.12))[..., None] * np.array([160, 60, 40]) * 0.5
img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
def stroke_text(xy, s, f, fill, sw=6): d.text(xy, s, font=f, fill=fill, stroke_width=sw, stroke_fill=(0, 0, 0))
# left: headline
tw = d.textlength("REAL BENCHMARKS", font=B(38)); d.rounded_rectangle((44, 40, 44 + tw + 56, 104), 32, fill=(255, 122, 40)); d.text((72, 50), "REAL BENCHMARKS", font=B(38), fill=(20, 20, 20))
stroke_text((40, 120), "RUST", B(150), (255, 255, 255), 8)
stroke_text((44, 290), f"{S.PY_X}x", B(170), (255, 130, 50), 8)
stroke_text((44, 480), "FASTER?", B(92), (255, 255, 255), 6)
d.rounded_rectangle((44, 610, 600, 680), 20, fill=(24, 24, 30)); d.text((70, 622), "vs Python · JS · Go · Java · C", font=B(34), fill=(130, 220, 120))
# right: mini chart from the real medians (seconds, Collatz below 1M)
px0, py0, pw, ph = 650, 120, 590, 500
d.rounded_rectangle((px0, py0, px0 + pw, py0 + ph), 18, fill=(14, 14, 20), outline=(255, 122, 40), width=4)
langs = ["Rust", "Go", "Java", "JavaScript", "Python"]; vmax = S.sec("collatz", "Python")
for i, l in enumerate(langs):
    yy = py0 + 40 + i * 90; v = S.sec("collatz", l); col = {"Rust": (255, 122, 40), "Go": (60, 175, 200), "Java": (220, 70, 70), "JavaScript": (230, 200, 60), "Python": (70, 120, 200)}[l]
    d.text((px0 + 24, yy), l if l != "JavaScript" else "JS", font=B(34), fill=(255, 255, 255))
    bw = max(10, (pw - 200 - 30) * v / vmax); d.rounded_rectangle((px0 + 200, yy + 4, px0 + 200 + bw, yy + 44), 10, fill=col)
    lab = f"{v:.2f}s" if v < 10 else f"{v:.1f}s"; f = M(30); tw = d.textlength(lab, font=f)
    if bw > tw + 30: d.text((px0 + 200 + bw - tw - 12, yy + 7), lab, font=f, fill=(15, 15, 15))
    else: d.text((px0 + 200 + bw + 12, yy + 7), lab, font=f, fill=(255, 255, 255))
img.convert("RGB").save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "thumbnail_16x9.jpg"), quality=90)
print("ok")
