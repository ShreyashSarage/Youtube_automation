"""16:9 thumbnail: title + the real organizer output from captures/cap.json."""
import json, os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); CAP = json.load(open(os.path.join(HERE, "captures/cap.json")))
W, H = 1280, 720; FD = "/usr/share/fonts/truetype/dejavu/"
B = lambda s: ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", s); M = lambda s: ImageFont.truetype(FD + "DejaVuSansMono.ttf", s)
MB = lambda s: ImageFont.truetype(FD + "DejaVuSansMono-Bold.ttf", s)
y, x = np.mgrid[0:H, 0:W].astype(np.float32); g = x / W * 0.6 + y / H * 0.4
a = np.array([20, 16, 34]) * (1 - g[..., None]) + np.array([60, 26, 52]) * g[..., None]
a += np.exp(-(((x / W - 0.8) ** 2 + (y / H - 0.25) ** 2) / 0.15))[..., None] * np.array([150, 60, 50]) * 0.5
img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
st = lambda xy, s, f, c, w=7: d.text(xy, s, font=f, fill=c, stroke_width=w, stroke_fill=(0, 0, 0))
tw = d.textlength("RUST PROJECT #2", font=B(36)); d.rounded_rectangle((50, 50, 50 + tw + 56, 112), 30, fill=(255, 122, 40)); d.text((78, 60), "RUST PROJECT #2", font=B(36), fill=(20, 20, 20))
st((44, 150), "FILE", B(150), (255, 255, 255)); st((44, 320), "ORGANIZER", B(84), (255, 140, 60), 6); st((50, 450), "in RUST", B(80), (120, 220, 110), 6)
d.rounded_rectangle((50, 600, 470, 668), 18, fill=(24, 24, 30)); d.text((76, 612), "walkdir + clap", font=MB(38), fill=(120, 220, 110))
# terminal card with the real "Moved 14 files" output
px, py, pw, ph = 680, 150, 560, 470
d.rounded_rectangle((px, py, px + pw, py + ph), 18, fill=(28, 28, 32), outline=(255, 122, 40), width=4)
for i, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))): d.ellipse((px + 22 + i * 30, py + 18, px + 40 + i * 30, py + 36), fill=c)
d.text((px + 24, py + 56), "$ cargo run -q -- ~/Downloads", font=MB(26), fill=(138, 226, 52))
lines = CAP["real"]["out"].split("\n"); summary = lines[lines.index(next(l for l in lines if l.startswith("Moved"))):]
yy = py + 104
for l in summary:
    d.text((px + 24, yy), l, font=(MB if l.startswith("Moved") else M)(30), fill=(250, 210, 90) if l.startswith("Moved") else (230, 230, 230)); yy += 41
img.save(os.path.join(HERE, "thumbnail_16x9.jpg"), quality=90); print("ok", summary)
