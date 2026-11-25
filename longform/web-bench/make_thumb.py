"""16:9 thumbnail from the real medians (project/results)."""
import os, sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import script as S
W, H = 1280, 720; FD = "/usr/share/fonts/truetype/dejavu/"
B = lambda s: ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", s); M = lambda s: ImageFont.truetype(FD + "DejaVuSansMono-Bold.ttf", s)
y, x = np.mgrid[0:H, 0:W].astype(np.float32); g = x / W * 0.6 + y / H * 0.4
a = np.array([14, 18, 34]) * (1 - g[..., None]) + np.array([30, 40, 70]) * g[..., None]
a += np.exp(-(((x / W - 0.85) ** 2 + (y / H - 0.2) ** 2) / 0.12))[..., None] * np.array([170, 70, 40]) * 0.5
img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
st = lambda xy, s, f, c, w=7: d.text(xy, s, font=f, fill=c, stroke_width=w, stroke_fill=(0, 0, 0))
tw = d.textlength("REAL LOAD TEST", font=B(36)); d.rounded_rectangle((44, 40, 44 + tw + 56, 102), 30, fill=(255, 122, 40)); d.text((72, 50), "REAL LOAD TEST", font=B(36), fill=(20, 20, 20))
st((40, 120), "RUST", B(140), (255, 255, 255)); st((44, 280), f"{S.X_NODE:.0f}x", B(170), (255, 130, 50), 8)
st((44, 470), "MORE", B(86), (255, 255, 255), 6); st((44, 565), "REQUESTS?", B(64), (255, 255, 255), 5)
px, py, pw, ph = 660, 130, 580, 470
d.rounded_rectangle((px, py, px + pw, py + ph), 18, fill=(14, 14, 20), outline=(255, 122, 40), width=4)
d.text((px + 24, py + 18), "requests / second", font=B(28), fill=(170, 170, 190))
vmax = max(S.GET.values())
for i, l in enumerate(S.LANGS):
    yy = py + 80 + i * 95; v = S.GET[l]
    d.text((px + 24, yy), l, font=B(34), fill=(255, 255, 255))
    bw = max(10, (pw - 190 - 30) * v / vmax); d.rounded_rectangle((px + 180, yy + 4, px + 180 + bw, yy + 44), 10, fill=S.COL[l])
    lab = f"{v / 1000:.0f}K"; f = M(30); w_ = d.textlength(lab, font=f)
    if bw > w_ + 30: d.text((px + 180 + bw - w_ - 12, yy + 7), lab, font=f, fill=(15, 15, 15))
    else: d.text((px + 180 + bw + 12, yy + 7), lab, font=f, fill=(255, 255, 255))
img.save(os.path.join(HERE, "thumbnail_16x9.jpg"), quality=90); print("ok")
