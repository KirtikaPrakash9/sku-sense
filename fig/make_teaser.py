"""Teaser figure: same-brand SKUs that a text prompt cannot separate.

Photographs: "Tesco Supermarket (Cereal)" and "Tesco Supermarket (Cereal) (2)" by Vauxford,
Wikimedia Commons, CC BY-SA 4.0. Writes fig_teaser.svg; render with render_fig.py teaser.
"""
import base64, io, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "img_raw")
A = Image.open(os.path.join(RAW, "tesco.jpg")).convert("RGB")
B = Image.open(os.path.join(RAW, "tesco2.jpg")).convert("RGB")

W, H = 500, 324
FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"
INK, MUTED, OVD, SKU, ODD = "#16202E", "#5B6575", "#2F6FEB", "#0E9F6E", "#D93B3B"
out = []
add = out.append


def crop(im, b):
    w, h = im.size
    return im.crop((int(b[0] * w), int(b[1] * h), int(b[2] * w), int(b[3] * h)))


def b64(im):
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=88)
    return base64.b64encode(buf.getvalue()).decode()


n = [0]
def photo(x, y, w, h, im, stroke):
    im = im.copy(); im.thumbnail((w * 4, h * 4)); n[0] += 1
    add(f'<clipPath id="t{n[0]}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/></clipPath>')
    add(f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMin slice" '
        f'clip-path="url(#t{n[0]})" href="data:image/jpeg;base64,{b64(im)}"/>')
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="none" stroke="{stroke}" stroke-width="2"/>')


def text(x, y, s, size=11, fill=INK, anchor="middle", weight="normal", italic=False):
    st = ' font-style="italic"' if italic else ""
    add(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}" font-weight="{weight}"{st}>{s}</text>')


# (image, normalised box, line 1, line 2, colour of the frame)
ROWS = [
    ("Prompt &#8220;Kellogg&#8217;s Crunchy Nut&#8221;: 4 boxes, 4 SKUs", [
        (A, (0.370, 0.141, 0.433, 0.262), "Clusters", "honey &amp; nut", SKU),
        (A, (0.664, 0.141, 0.733, 0.262), "Clusters", "chocolate", SKU),
        (A, (0.437, 0.655, 0.497, 0.762), "Original", "regular box", SKU),
        (A, (0.561, 0.693, 0.636, 0.856), "Original", "BIG 840 g", SKU),
    ]),
    ("Prompt &#8220;Rice Krispies&#8221;: 3 SKUs and a store-brand look-alike", [
        (B, (0.480, 0.447, 0.539, 0.585), "Original", "regular box", SKU),
        (B, (0.614, 0.274, 0.687, 0.422), "Multigrain", "shapes", SKU),
        (B, (0.651, 0.622, 0.720, 0.798), "Original", "BIG 700 g", SKU),
        (B, (0.189, 0.823, 0.255, 0.956), "Tesco Rice", "Snaps", ODD),
    ]),
]

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
add(f'<rect width="{W}" height="{H}" fill="#fff"/>')
cw, ch, gap, x0 = 86, 96, 36, 22
for r, (title, items) in enumerate(ROWS):
    y = 6 + r * 160
    add(f'<rect x="4" y="{y}" width="{W - 8}" height="154" rx="8" fill="{"#F2F5FA" if r == 0 else "#FBF4EA"}"/>')
    text(14, y + 16, title, size=12, weight="bold", anchor="start")
    # one dashed OVD bracket spanning the whole row: the text prompt fires on every box
    add(f'<rect x="{x0 - 6}" y="{y + 24}" width="{4 * cw + 3 * gap + 12}" height="{ch + 10}" rx="5" fill="none" '
        f'stroke="{OVD}" stroke-width="1.4" stroke-dasharray="5 3"/>')
    for i, (im, b, l1, l2, col) in enumerate(items):
        x = x0 + i * (cw + gap)
        photo(x, y + 29, cw, ch, crop(im, b), col)
        text(x + cw / 2, y + ch + 47, l1, size=10.5, weight="bold", fill=col)
        text(x + cw / 2, y + ch + 59, l2, size=10.5, fill=col)
        if i:
            text(x - gap / 2, y + 29 + ch / 2 + 5, "&#8800;", size=18, fill=MUTED)
add("</svg>")
open(os.path.join(HERE, "fig_teaser.svg"), "w").write("\n".join(out))
print("wrote fig_teaser.svg")
