"""Render an SVG figure to a vector PDF (for LaTeX) and a PNG preview with Chromium.

Usage: python render_fig.py [arch|teaser]   (default: arch)
"""
import os, re, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
name = sys.argv[1] if len(sys.argv) > 1 else "arch"
svg = open(os.path.join(HERE, f"fig_{name}.svg")).read()
W, H = (int(v) for v in re.search(r'width="(\d+)" height="(\d+)"', svg).groups())
html = (f"<html><head><style>@page{{size:{W}px {H}px;margin:0}}html,body{{margin:0;padding:0}}</style>"
        f"</head><body>{svg}</body></html>")
with sync_playwright() as p:
    try:
        b = p.chromium.launch()
    except Exception:                       # fall back to an installed Google Chrome
        b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=2)
    pg.set_content(html); pg.wait_for_timeout(300)
    pg.screenshot(path=os.path.join(HERE, f"fig_{name}_preview.png"))
    pg.pdf(path=os.path.join(HERE, f"fig_{name}.pdf"), width=f"{W}px", height=f"{H}px",
           print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
    b.close()
print("rendered", name)
