"""Architecture figure for the Term-I manuscript (SKU-level shelf recognition).

Draws fig_arch.svg; render_fig.py turns it into a vector PDF with Chromium.
Photograph: "Tesco Supermarket (Cereal)" by Vauxford, Wikimedia Commons, CC BY-SA 4.0.
Crops of the same photograph stand in for the studio reference images of each SKU.
"""
import base64, io, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SHELF = Image.open(os.path.join(HERE, "..", "img_raw", "tesco.jpg")).convert("RGB")

W, H = 1200, 520
FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"
INK, MUTED, LINE = "#16202E", "#5B6575", "#334155"
DET, SKU, GT, LOSS = "#2F6FEB", "#0E9F6E", "#E8A317", "#D93B3B"
PANEL = ["#F2F5FA", "#F3F1FA", "#EEF7F2", "#FBF4EA"]
FROZEN_FILL, TRAIN_FILL = "#DCE7FB", "#FFE2C2"

out = []
add = out.append


# ------------------------------------------------------------------ helpers
def b64(im, q=85):
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=q)
    return base64.b64encode(buf.getvalue()).decode()


def crop(box):
    """box in normalised (x0, y0, x1, y1) of the shelf photo."""
    w, h = SHELF.size
    return SHELF.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))


_clip = [0]
def photo(x, y, w, h, im, rx=3, stroke=LINE, sw=1):
    im = im.copy(); im.thumbnail((int(w * 3), int(h * 3)))
    _clip[0] += 1; cid = f"cp{_clip[0]}"
    add(f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/></clipPath>')
    add(f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" '
        f'clip-path="url(#{cid})" href="data:image/jpeg;base64,{b64(im)}"/>')
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="none" stroke="{stroke}" stroke-width="{sw}"/>')


def sb(t, size=9):
    """Subscript as a tspan pair (works in Chromium without baseline-shift)."""
    return f'<tspan dy="3" font-size="{size}">{t}</tspan><tspan dy="-3"> </tspan>'


def sp(t, size=9):
    return f'<tspan dy="-5" font-size="{size}">{t}</tspan><tspan dy="5"> </tspan>'


def text(x, y, s, size=12, fill=INK, anchor="middle", weight="normal", italic=False):
    st = ' font-style="italic"' if italic else ""
    add(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}" font-weight="{weight}"{st}>{s}</text>')


def rect(x, y, w, h, fill="#fff", stroke=LINE, sw=1.2, rx=6, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def arrow(pts, color=LINE, sw=1.5, dash=None):
    d = " ".join(f"{'M' if i == 0 else 'L'}{x},{y}" for i, (x, y) in enumerate(pts))
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    mid = {LINE: "ah", LOSS: "ahr", DET: "ahb", SKU: "ahg"}[color]
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}"{ds} marker-end="url(#{mid})"/>')


def snow(x, y, r=6, c="#2F6FEB"):
    for a in (0, 60, 120):
        add(f'<line x1="{x - r}" y1="{y}" x2="{x + r}" y2="{y}" stroke="{c}" stroke-width="1.6" '
            f'stroke-linecap="round" transform="rotate({a} {x} {y})"/>')
    add(f'<circle cx="{x}" cy="{y}" r="1.6" fill="{c}"/>')


def flame(x, y, s=1.0):
    add(f'<path transform="translate({x},{y}) scale({s})" d="M0,-8 C5,-3 7,1 5,5 C3.5,8.5 -3.5,8.5 -5,5 '
        f'C-6.5,1.5 -4,-1 -2.5,-3 C-2,0 -0.5,1 0.5,0.5 C1.5,-2 0.5,-5 0,-8 Z" fill="#F26B1D"/>')
    add(f'<path transform="translate({x},{y + 2.5}) scale({s * 0.5})" d="M0,-6 C4,-1 4,4 0,6 C-4,4 -3,0 0,-6 Z" fill="#FFC23D"/>')


def det_box(x, y, w, h, color=DET, label=None, dash="4 2", lab_w=None):
    rect(x, y, w, h, fill="none", stroke=color, sw=1.6, rx=1, dash=dash)
    if label:
        lw = lab_w or (6.3 * len(label) + 8)
        add(f'<rect x="{x - 0.8}" y="{y - 14}" width="{lw}" height="14" fill="{color}"/>')
        text(x + 3, y - 3.5, label, size=10.5, fill="#fff", anchor="start", weight="bold")


def encoder(x, y, w, h, name, sub, frozen=True):
    """Trapezoid encoder (wide input side on the left)."""
    fill = FROZEN_FILL if frozen else TRAIN_FILL
    add(f'<path d="M{x},{y} L{x + w},{y + h * 0.22} L{x + w},{y + h * 0.78} L{x},{y + h} Z" '
        f'fill="{fill}" stroke="{LINE}" stroke-width="1.2" stroke-linejoin="round"/>')
    for i in range(1, 4):                           # transformer blocks
        xi = x + w * i / 4
        top = y + h * 0.22 * i / 4; bot = y + h - h * 0.22 * i / 4
        add(f'<line x1="{xi}" y1="{top + 3}" x2="{xi}" y2="{bot - 3}" stroke="#9DB4DE" stroke-width="1"/>')
    text(x + w / 2, y + h / 2 + 1, name, size=12, weight="bold")
    text(x + w / 2, y + h / 2 + 15, sub, size=10.5, fill=MUTED)
    if frozen: snow(x + 13, y + 16)
    else: flame(x + 13, y + 16)


def vec(x, y, n, color, cw=9, ch=7):
    """Embedding as a column of cells."""
    shades = ["0.95", "0.55", "0.8", "0.35", "0.7", "0.5", "0.9", "0.4"]
    for i in range(n):
        add(f'<rect x="{x}" y="{y + i * ch}" width="{cw}" height="{ch}" fill="{color}" '
            f'fill-opacity="{shades[i % len(shades)]}" stroke="#fff" stroke-width="0.6"/>')
    add(f'<rect x="{x}" y="{y}" width="{cw}" height="{n * ch}" fill="none" stroke="{LINE}" stroke-width="0.8"/>')


# ------------------------------------------------------------------ SKU crops
# normalised boxes on the shelf photo (x0, y0, x1, y1)
P = {
    "honey":  (0.370, 0.141, 0.433, 0.262),   # Crunchy Nut Clusters, honey & nut
    "honey2": (0.433, 0.141, 0.502, 0.262),
    "choc":   (0.664, 0.141, 0.733, 0.262),   # Crunchy Nut Clusters, chocolate
    "choc2":  (0.733, 0.141, 0.807, 0.262),
    "gran1":  (0.367, 0.336, 0.429, 0.451),   # Crunchy Nut granola pouches
    "gran2":  (0.430, 0.336, 0.492, 0.451),
    "gran3":  (0.494, 0.336, 0.551, 0.451),
    "gran4":  (0.554, 0.336, 0.611, 0.451),
    "gran5":  (0.614, 0.336, 0.677, 0.451),
    "tesco":  (0.682, 0.336, 0.744, 0.451),   # store-brand clusters
    "coco1":  (0.834, 0.304, 0.902, 0.444),
    "coco2":  (0.902, 0.304, 0.976, 0.444),
    "orig":   (0.437, 0.655, 0.497, 0.762),   # Crunchy Nut original
    "big":    (0.561, 0.693, 0.636, 0.856),   # Crunchy Nut BIG 840 g
}

# ------------------------------------------------------------------ canvas
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
add("<defs>")
for mid, col in (("ah", LINE), ("ahr", LOSS), ("ahb", DET), ("ahg", SKU)):
    add(f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" '
        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{col}"/></marker>')
add("</defs>")
add(f'<rect width="{W}" height="{H}" fill="#fff"/>')

# panels
PX = [(8, 262), (278, 300), (586, 330), (924, 268)]
TITLES = ["(a) Class-agnostic proposals", "(b) Frozen embeddings", "(c) SKU adapter and re-ranker (ours)",
          "(d) SKU-level output"]
for (px, pw), col, t in zip(PX, PANEL, TITLES):
    rect(px, 30, pw, H - 38, fill=col, stroke="none", rx=10)
    text(px + 10, 50, t, size=13.5, weight="bold", anchor="start")

# legend
lx = 640
snow(lx, 14); text(lx + 10, 18, "frozen", size=11.5, anchor="start")
flame(lx + 70, 15, 0.9); text(lx + 80, 18, "trained", size=11.5, anchor="start")
rect(lx + 140, 8, 14, 11, fill="none", stroke=DET, sw=1.6, rx=1, dash="4 2")
text(lx + 160, 18, "proposal", size=11.5, anchor="start")
rect(lx + 225, 8, 14, 11, fill="none", stroke=SKU, sw=1.8, rx=1)
text(lx + 245, 18, "SKU prediction", size=11.5, anchor="start")
add(f'<line x1="{lx + 340}" y1="14" x2="{lx + 362}" y2="14" stroke="{LOSS}" stroke-width="1.5" stroke-dasharray="4 3"/>')
text(lx + 368, 18, "gradient", size=11.5, anchor="start")

# ------------------------------------------------------------------ (a)
ax, ay, aw, ah = 20, 62, 238, 178
photo(ax, ay, aw, ah, SHELF.crop((int(0.17 * 1920), int(0.08 * 1440), int(1.0 * 1920), int(0.88 * 1440))))
# proposals drawn in the coordinates of the displayed crop
def to_a(b):
    x0, y0, x1, y1 = b
    cx0, cy0, cx1, cy1 = 0.17, 0.08, 1.0, 0.88
    return (ax + (x0 - cx0) / (cx1 - cx0) * aw, ay + (y0 - cy0) / (cy1 - cy0) * ah,
            (x1 - x0) / (cx1 - cx0) * aw, (y1 - y0) / (cy1 - cy0) * ah)
for k in ("honey", "honey2", "choc", "choc2", "gran1", "gran2", "gran3", "gran4", "gran5",
          "tesco", "coco1", "orig", "big"):
    det_box(*to_a(P[k]), dash="3 1.5")
text(ax + aw / 2, ay + ah + 14, "shelf image, 1 920 &#215; 1 440 px", size=10.5, fill=MUTED)

arrow([(48, 258), (48, 300)])
rect(66, 266, 182, 22, fill="#fff", stroke=MUTED, sw=1, rx=11)
text(157, 281, "prompt: &#8220;product . box . pouch .&#8221;", size=10.5, italic=True)
arrow([(157, 288), (157, 300)])
rect(30, 300, 218, 54, fill=FROZEN_FILL, rx=7)
snow(42, 312)
text(144, 322, "Grounding DINO / YOLO-World", size=12, weight="bold")
text(139, 339, "open-vocabulary detector", size=10.5, fill=MUTED)
arrow([(139, 354), (139, 376)])
# crop stack
for i, k in enumerate(("big", "choc", "honey")):
    photo(84 + i * 22, 384 + i * 8, 54, 70, crop(P[k]), stroke=DET, sw=1.6)
text(139, 486, "N crops x" + sb("i") + "with scores s" + sp("det"), size=11)
text(139, 501, "(one per product facing)", size=10.5, fill=MUTED)
arrow([(205, 420), (274, 420), (274, 128), (318, 128)])

# ------------------------------------------------------------------ (b)
# crop branch
encoder(322, 84, 128, 96, "DINOv2", "ViT-B/14")
vec(470, 104, 8, "#2F6FEB")
text(474, 98, "f" + sb("i", 10), size=12, italic=True)
arrow([(450, 132), (466, 132)])
text(476, 178, "768-d", size=10.5, fill=MUTED)

# gallery
gx, gy = 292, 236
text(gx + 6, gy, "reference gallery: 1 to 5 images per SKU", size=11, anchor="start", weight="bold")
names = [("honey2", "Clusters honey"), ("choc2", "Clusters choc."), ("orig", "Orig. regular"),
         ("big", "Orig. 840 g")]
for i, (k, nm) in enumerate(names):
    x = gx + 14 + i * 67
    photo(x, gy + 10, 52, 64, crop(P[k]), stroke=GT, sw=1.8)
    text(x + 26, gy + 88, nm, size=9.5, fill=INK)
add(f'<path d="M{gx + 12},{gy + 96} L{gx + 12},{gy + 102} L{gx + 274},{gy + 102} L{gx + 274},{gy + 96}" '
    f'fill="none" stroke="{LOSS}" stroke-width="1.2"/>')
text(gx + 143, gy + 116, "one brand, four SKUs: hard negatives", size=10.5, fill=LOSS)
encoder(322, 362, 128, 70, "DINOv2", "shared weights")
arrow([(450, 397), (466, 397)])
vec(470, 369, 8, GT)
text(474, 363, "e" + sb("k", 10), size=12, italic=True)
arrow([(gx + 12, gy + 42), (gx + 2, gy + 42), (gx + 2, 397), (322, 397)])

# text branch
rect(292, 452, 196, 20, fill="#fff", stroke=MUTED, sw=1, rx=10)
text(390, 466, "&#8220;Kellogg&#8217;s Crunchy Nut Clusters, chocolate&#8221;", size=9.6, italic=True)
arrow([(390, 472), (390, 480)])
rect(318, 480, 144, 28, fill=FROZEN_FILL, rx=6)
snow(452, 488)
text(388, 498, "CLIP text + image", size=11.5, weight="bold")
arrow([(462, 494), (490, 494)])
vec(494, 474, 5, "#8B5CF6")
text(520, 486, "t" + sb("k", 10), size=12, italic=True)

# ------------------------------------------------------------------ (c)
# adapter
cx = 610
rect(cx, 92, 132, 122, fill=TRAIN_FILL, rx=8)
flame(cx + 120, 104, 0.9)
text(cx + 60, 112, "SKU adapter g" + sb("&#952;", 10), size=12.5, weight="bold")
cols = [cx + 24, cx + 66, cx + 108]
nodes = [[128, 145, 162, 179], [136, 153, 170], [128, 145, 162, 179]]
for c0, c1, n0, n1 in ((cols[0], cols[1], nodes[0], nodes[1]), (cols[1], cols[2], nodes[1], nodes[2])):
    for a in n0:
        for b in n1:
            add(f'<line x1="{c0}" y1="{a}" x2="{c1}" y2="{b}" stroke="#E7A770" stroke-width="0.6"/>')
for c, ns in zip(cols, nodes):
    for n in ns:
        add(f'<circle cx="{c}" cy="{n}" r="5" fill="#fff" stroke="#C26A1F" stroke-width="1.3"/>')
text(cx + 66, 199, "residual MLP, 768 &#8594; 256", size=10.5, fill=MUTED)
text(cx + 66, 210, "applied to f" + sb("i", 8) + "and e" + sb("k", 8), size=9.5, fill=MUTED)
arrow([(484, 132), (cx, 132)])
arrow([(484, 397), (560, 397), (560, 182), (cx, 182)])

# similarity matrix
mx, my, cs = 790, 92, 24
text(mx + 2 * cs, my - 6, "cos(z" + sb("i") + ", &#7825;" + sb("k") + ")", size=11.5, italic=True)
vals = [[0.82, 0.71, 0.30, 0.22], [0.66, 0.79, 0.25, 0.20], [0.28, 0.24, 0.74, 0.69], [0.21, 0.27, 0.62, 0.81]]
for r in range(4):
    for c in range(4):
        v = vals[r][c]
        add(f'<rect x="{mx + c * cs}" y="{my + r * cs}" width="{cs}" height="{cs}" fill="#0E9F6E" '
            f'fill-opacity="{v:.2f}" stroke="#fff" stroke-width="1"/>')
        text(mx + c * cs + cs / 2, my + r * cs + 16, f"{v:.2f}".lstrip("0"), size=9, fill="#fff" if v > .5 else INK)
add(f'<rect x="{mx}" y="{my}" width="{4 * cs}" height="{4 * cs}" fill="none" stroke="{LINE}" stroke-width="1"/>')
for r in range(4):
    add(f'<rect x="{mx + r * cs + 1}" y="{my + r * cs + 1}" width="{cs - 2}" height="{cs - 2}" fill="none" '
        f'stroke="{GT}" stroke-width="2"/>')
text(mx - 5, my + 12, "crops", size=10, fill=MUTED, anchor="end")
text(mx + 2 * cs, my + 4 * cs + 14, "gallery SKUs", size=10, fill=MUTED)
arrow([(cx + 132, 147), (mx - 4, 147)])
for c0 in (0, 2):
    add(f'<path d="M{mx + c0 * cs + 2},{my + 4 * cs + 20} L{mx + c0 * cs + 2},{my + 4 * cs + 24} '
        f'L{mx + (c0 + 2) * cs - 2},{my + 4 * cs + 24} L{mx + (c0 + 2) * cs - 2},{my + 4 * cs + 20}" '
        f'fill="none" stroke="{LOSS}" stroke-width="1.1"/>')
text(mx + 2 * cs, my + 4 * cs + 37, "same-brand blocks", size=10, fill=LOSS)

# fusion re-ranker
fy = 262
rect(612, fy, 290, 64, fill=TRAIN_FILL, rx=8)
flame(890, fy + 12, 0.9)
text(757, fy + 20, "Fusion re-ranker", size=12.5, weight="bold")
text(757, fy + 40, "s" + sb("ik") + "= w" + sb("v") + "cos(z" + sb("i") + ", &#7825;" + sb("k") + ") + w" + sb("t") + "cos(c" + sb("i") + ", t" + sb("k") + ") + w" + sb("d") + "s" + sp("det"), size=11.5, italic=True)
text(757, fy + 56, "3 weights + temperature &#964;; top-k SKUs, reject if max s &lt; &#948;", size=10, fill=MUTED)
arrow([(mx + 2 * cs, my + 4 * cs + 42), (mx + 2 * cs, fy)])
arrow([(540, 486), (575, 486), (575, 300), (612, 300)])

# loss
ly = 372
rect(612, ly, 290, 74, fill="#fff", stroke=LOSS, sw=1.6, rx=8)
text(757, ly + 19, "Brand-aware contrastive loss", size=12.5, weight="bold", fill=LOSS)
text(757, ly + 40, "&#8466; = &#8722;log [ exp(s" + sb("i,y") + "/&#964;) / &#931;" + sb("k") + "&#969;" + sb("ik") + "exp(s" + sb("ik") + "/&#964;) ]", size=12, italic=True)
text(757, ly + 60, "&#969;" + sb("ik", 8) + "= &#947; &gt; 1 if SKU k shares the brand of the true SKU y, else 1", size=10, fill=MUTED)
arrow([(757, fy + 64), (757, ly)])
add(f'<path d="M612,{ly + 37} L596,{ly + 37} L596,204 L620,204" fill="none" stroke="{LOSS}" stroke-width="1.5" '
    f'stroke-dasharray="4 3" marker-end="url(#ahr)"/>')
add(f'<path d="M902,{ly + 37} L912,{ly + 37} L912,{fy + 52} L904,{fy + 52}" fill="none" stroke="{LOSS}" '
    f'stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#ahr)"/>')
text(757, ly + 92, "trained on base SKUs; novel SKUs need only a gallery image", size=10.5, fill=MUTED)

# ------------------------------------------------------------------ (d)
arrow([(902, fy + 18), (918, fy + 18), (918, 210), (936, 210)])
dx, dy, dw, dh = 936, 62, 244, 200
reg = (0.355, 0.11, 0.82, 0.48)
photo(dx, dy, dw, dh, crop(reg))
def to_d(b):
    x0, y0, x1, y1 = b
    return (dx + (x0 - reg[0]) / (reg[2] - reg[0]) * dw, dy + (y0 - reg[1]) / (reg[3] - reg[1]) * dh,
            (x1 - x0) / (reg[2] - reg[0]) * dw, (y1 - y0) / (reg[3] - reg[1]) * dh)
for k, lab in (("honey", "honey"), ("choc", "choc."), ("gran2", "gran. H&amp;C"), ("tesco", "own brand")):
    det_box(*to_d(P[k]), color=SKU, dash=None, label=lab)
x, y, w, h = to_d(P["gran4"])
rect(x, y, w, h, fill="none", stroke="#94A3B8", sw=1.6, rx=1)
add(f'<rect x="{x - 0.8}" y="{y + h}" width="50" height="14" fill="#94A3B8"/>')
text(x + 3, y + h + 10.5, "unknown", size=10.5, fill="#fff", anchor="start", weight="bold")

# before / after bars for one crop
by = 306
text(dx + 2, by, "Top-3 for the chocolate crop", size=11.5, weight="bold", anchor="start")
photo(dx, by + 10, 40, 52, crop(P["choc"]), stroke=SKU, sw=1.6)
rows = [("text prompt only", [("Crunchy Nut, orig.", .41, False), ("Clusters, honey", .38, False),
                              ("Clusters, choc.", .36, True)]),
        ("ours (re-ranked)", [("Clusters, choc.", .81, True), ("Clusters, honey", .52, False),
                              ("Original, regular", .31, False)])]
yy = by + 22
for title, items in rows:
    text(dx + 50, yy, title, size=10.5, fill=MUTED, anchor="start", italic=True)
    yy += 6
    for nm, v, ok in items:
        add(f'<rect x="{dx + 150}" y="{yy}" width="{v * 110:.1f}" height="11" rx="2" '
            f'fill="{SKU if ok else "#CBD5E1"}"/>')
        text(dx + 146, yy + 9.5, nm, size=10, anchor="end", fill=INK if ok else MUTED)
        yy += 14
    yy += 14
text(dx + 122, by + 160, "scores are illustrative, not results", size=10, fill=MUTED, italic=True)
text(dx + 122, by + 186, "Metrics: SKU top-1 / top-5,", size=11, anchor="middle")
text(dx + 122, by + 201, "SKU-level mAP&#8325;&#8320;, novel-SKU accuracy", size=11, anchor="middle")

add("</svg>")
with open(os.path.join(HERE, "fig_arch.svg"), "w") as f:
    f.write("\n".join(out))
print("wrote fig_arch.svg")
