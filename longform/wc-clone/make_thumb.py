"""16:9 thumbnail (clean style): title + the real rwc vs wc output from captures/cap.json."""
import json, os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); CAP = json.load(open(os.path.join(HERE, "captures/cap.json")))
W, H = 1280, 720; FD = "/usr/share/fonts/truetype/dejavu/"
B = lambda s: ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", s); M = lambda s: ImageFont.truetype(FD + "DejaVuSansMono.ttf", s)
MB = lambda s: ImageFont.truetype(FD + "DejaVuSansMono-Bold.ttf", s)
img = Image.new("RGB", (W, H), (14, 16, 21)); d = ImageDraw.Draw(img)
tw = d.textlength("RUST PROJECT #3", font=B(34)); d.rounded_rectangle((50, 50, 50 + tw + 52, 108), 29, fill=(222, 105, 50)); d.text((76, 59), "RUST PROJECT #3", font=B(34), fill=(14, 16, 21))
d.text((48, 140), "REWRITE", font=B(96), fill=(240, 242, 245)); d.text((48, 250), "wc", font=MB(170), fill=(222, 105, 50))
d.text((50, 450), "IN RUST", font=B(84), fill=(240, 242, 245)); d.text((52, 580), "+ unit tests · same output", font=B(34), fill=(150, 158, 170))
def term(y, title, cmd, outp, col):
    x0, x1 = 610, 1250; lines = outp.split("\n"); h = 66 + 42 * len(lines)
    d.rounded_rectangle((x0, y, x1, y + h), 16, fill=(24, 27, 34), outline=col, width=3)
    d.text((x0 + 22, y + 14), title, font=B(24), fill=col)
    for i, l in enumerate(lines): d.text((x0 + 22, y + 58 + i * 42), l, font=M(28), fill=(232, 234, 238))
    return y + h
y = term(110, "real wc  (GNU coreutils)", "wc *.txt", CAP["wc_both"]["out"], (110, 165, 245))
term(y + 40, "our rwc  (Rust)", "rwc *.txt", CAP["run_both"]["out"], (222, 105, 50))
img.save(os.path.join(HERE, "thumbnail_16x9.jpg"), quality=92); print("ok")
