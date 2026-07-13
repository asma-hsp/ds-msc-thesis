"""Re-style the qualitative panels for the slides.

The panels themselves (qual_*_q*.png) come out of
notebooks/final_experimental_results.ipynb (show_panels). Its slide-unfriendly
defaults are fixed here rather than in the notebook, so the thesis figures stay
untouched:

  1. the coloured rule line + header text above each row is erased
  2. correct/incorrect thumbnail borders are recoloured to a high-contrast
     red/green pair (the originals are a muted brick/olive that read as
     yellowish on a projector) and thickened
  3. each row gets a label CARD in a new left margin, with Ours emphasised

Row geometry and border colours are DETECTED, not hard-coded, so this keeps
working if the panels are re-exported.

    python slides/relabel_qual_panels.py
"""
import os

import numpy as np
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

INK = (0x0B, 0x0B, 0x0B)
MUTED = (0x52, 0x51, 0x4E)
RED = (0x9B, 0x00, 0x14)          # UniPD red, for the Ours label
LIGHT = (0xF0, 0xEF, 0xEC)

# source border colours (as emitted by show_panels) -> high-contrast replacements
SRC_WRONG = (156, 74, 60)
SRC_RIGHT = (63, 125, 78)
NEW_WRONG = (214, 31, 31)         # vivid red
NEW_RIGHT = (0, 158, 71)          # vivid green
THICKEN = 5                       # MaxFilter kernel (odd); 5 -> +2px each side

MARGIN = 470                      # width of the new LEFT label column
HDR_BAND = 58                     # header text height to erase (above each rule)

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


def rule_bands(img):
    """(top, bottom) of each coloured header rule — one per row."""
    a = np.asarray(img.convert("RGB"))
    h, w, _ = a.shape
    frac = (a.sum(2) < 700).mean(1)
    ys = [y for y in range(h) if frac[y] > 0.85]
    bands = []
    for y in ys:
        if bands and y - bands[-1][-1] <= 2:
            bands[-1].append(y)
        else:
            bands.append([y])
    out = []
    for i, b in enumerate(bands):
        nxt = bands[i + 1][0] if i + 1 < len(bands) else None
        if nxt is None or nxt - b[-1] < 30:      # followed by the row's top border
            out.append((b[0], b[-1]))
    return out


def recolour(img, src, dst):
    """Replace the border ring near colour `src` with `dst`, thickened.

    Opened (erode then dilate) first: photo content can contain a few pixels of
    the same colour, and dilating those alone would speckle the thumbnails.
    Border lines are several px thick, so they survive the erosion; specks don't.
    """
    a = np.asarray(img).astype(int)
    mask = (np.abs(a - np.array(src)).sum(2) < 30)
    m = Image.fromarray((mask * 255).astype(np.uint8))
    m = m.filter(ImageFilter.MinFilter(3))                # erode: drop specks
    m = m.filter(ImageFilter.MaxFilter(THICKEN))          # dilate: thicker border
    solid = Image.new("RGB", img.size, dst)
    img.paste(solid, (0, 0), m)
    return img


for fname, rows in PANELS.items():
    src = os.path.join(ASSETS, fname)
    im = Image.open(src).convert("RGB")
    w, h = im.size

    bands = rule_bands(im)
    if len(bands) != len(rows):
        raise SystemExit(f"{fname}: found {len(bands)} rules, expected {len(rows)}")

    # 1. erase header text AND the rule line itself
    d0 = ImageDraw.Draw(im)
    for top, bot in bands:
        d0.rectangle([0, top - HDR_BAND, w - 1, bot], fill=(255, 255, 255))

    # 2. high-contrast, thicker thumbnail borders
    im = recolour(im, SRC_RIGHT, NEW_RIGHT)
    im = recolour(im, SRC_WRONG, NEW_WRONG)

    # 3. label cards in a new left margin
    out = Image.new("RGB", (w + MARGIN, h), (255, 255, 255))
    out.paste(im, (MARGIN, 0))
    d = ImageDraw.Draw(out)

    tops = [t for t, _ in bands]
    bounds = [(tops[i], (tops[i + 1] - HDR_BAND) if i + 1 < len(tops) else h)
              for i in range(len(tops))]
    for (name, ap, ours), (y0, y1) in zip(rows, bounds):
        cy = (y0 + y1) // 2
        bx0, bx1 = 24, MARGIN - 40
        bh = 108
        d.rounded_rectangle([bx0, cy - bh // 2, bx1, cy + bh // 2], radius=14,
                            fill=(0xFB, 0xE9, 0xE7) if ours else LIGHT,
                            outline=RED if ours else None,
                            width=3 if ours else 0)
        f_name = ImageFont.truetype(F_BOLD if ours else F_REG, 38 if ours else 33)
        f_ap = ImageFont.truetype(F_BOLD if ours else F_REG, 30 if ours else 27)
        col = RED if ours else INK
        d.text((bx0 + 24, cy - 34), name, font=f_name, fill=col)
        d.text((bx0 + 24, cy + 6), ap, font=f_ap, fill=col if ours else MUTED)

    dst = os.path.join(ASSETS, fname.replace(".png", "_labelled.png"))
    out.save(dst)   # never overwrite the source: this script is not idempotent
    print(f"restyled {fname} -> {os.path.basename(dst)} "
          f"({w}x{h} -> {out.size[0]}x{out.size[1]})")
