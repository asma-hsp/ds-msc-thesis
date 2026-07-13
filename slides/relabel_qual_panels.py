"""Move the qualitative panels' row labels from cramped left-side headers into a
clean right-hand label column, with OUR method emphasised.

The panels themselves (qual_*_q*.png) come out of
notebooks/final_experimental_results.ipynb (show_panels). That renderer writes the
method name + AP as a header line above each row. On a slide those headers are
small and sit far from the row they describe, so here we:

  1. white out the header text band (the rule line under it is kept as a separator)
  2. paste the panel into a wider canvas
  3. draw "<method>  AP = x%" in the right margin, vertically centred on its row,
     with the Ours row in bold UniPD red

Row geometry is DETECTED (the coloured rule lines), not hard-coded, so this keeps
working if the panels are re-exported at a different size.

    python slides/relabel_qual_panels.py
"""
import os

import numpy as np
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

INK = (0x0B, 0x0B, 0x0B)
MUTED = (0x52, 0x51, 0x4E)
RED = (0x9B, 0x00, 0x14)

MARGIN = 430          # width of the new right-hand label column
HDR_BAND = 58         # height of the header text band to erase (above each rule)

# label, AP text, is_ours  — one per row, top to bottom
PANELS = {
    "qual_homer_success_q832.png": [
        ("Img × Txt", "AP = 4%", False),
        ("BASIC", "AP = 33%", False),
        ("Ours (triplet)", "AP = 88%", True),
        ("Ground truth", "n = 4", False),
    ],
    "qual_dogglasses_failure_q1490.png": [
        ("Img × Txt", "AP = 0%", False),
        ("BASIC", "AP = 0%", False),
        ("Ours (triplet)", "AP = 0%", True),
        ("Ground truth", "n = 1", False),
    ],
}


def find_font(name):
    for f in font_manager.findSystemFonts():
        if os.path.basename(f) == name:
            return f
    raise FileNotFoundError(name)


F_REG = find_font("DejaVuSans.ttf")
F_BOLD = find_font("DejaVuSans-Bold.ttf")


def rule_tops(img):
    """y of the top of each coloured rule line (one per row header)."""
    a = np.asarray(img.convert("RGB"))
    h, w, _ = a.shape
    dark = (a.sum(2) < 700)
    frac = dark.mean(1)
    ys = [y for y in range(h) if frac[y] > 0.85]
    bands, tops = [], []
    for y in ys:
        if bands and y - bands[-1][-1] <= 2:
            bands[-1].append(y)
        else:
            bands.append([y])
    # A header rule is immediately followed (within ~30px) by the top border of
    # its image row; the last rule (ground truth) has no following band nearby.
    for i, b in enumerate(bands):
        nxt = bands[i + 1][0] if i + 1 < len(bands) else None
        if nxt is None or nxt - b[-1] < 30:
            tops.append(b[0])
    return tops


for fname, rows in PANELS.items():
    src = os.path.join(ASSETS, fname)
    im = Image.open(src).convert("RGB")
    w, h = im.size

    tops = rule_tops(im)
    if len(tops) != len(rows):
        raise SystemExit(f"{fname}: found {len(tops)} rules, expected {len(rows)}")

    # 1. erase the old header text (keep the rule line itself)
    d0 = ImageDraw.Draw(im)
    for t in tops:
        d0.rectangle([0, t - HDR_BAND, w - 1, t - 1], fill=(255, 255, 255))

    # 2. wider canvas
    out = Image.new("RGB", (w + MARGIN, h), (255, 255, 255))
    out.paste(im, (0, 0))
    d = ImageDraw.Draw(out)

    # 3. right-hand labels, centred on each row's images
    #    (row spans from just under its rule to just above the next header band)
    bounds = [(tops[i], (tops[i + 1] - HDR_BAND) if i + 1 < len(tops) else h)
              for i in range(len(tops))]
    x = w + 26
    for (name, ap, ours), (y0, y1) in zip(rows, bounds):
        cy = (y0 + y1) // 2
        f_name = ImageFont.truetype(F_BOLD if ours else F_REG, 40 if ours else 34)
        f_ap = ImageFont.truetype(F_BOLD if ours else F_REG, 32 if ours else 28)
        col = RED if ours else INK
        d.text((x, cy - 26), name, font=f_name, fill=col)
        d.text((x, cy + 20), ap, font=f_ap, fill=col if ours else MUTED)
        if ours:   # accent bar so our row is unmistakable
            d.rectangle([x - 14, cy - 34, x - 8, cy + 56], fill=RED)

    dst = os.path.join(ASSETS, fname.replace(".png", "_labelled.png"))
    out.save(dst)   # never overwrite the source: this script is not idempotent
    print(f"relabelled {fname} -> {os.path.basename(dst)} "
          f"({w}x{h} -> {out.size[0]}x{out.size[1]})")
