"""Build the defense deck on the UniPD template.
Output: slides/defense_slides.pptx in ds-msc-thesis.
"""
import os
from PIL import Image, ImageChops
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

REPO = "/extra/ahoseinp/projects/ds-msc-thesis"
FIG = f"{REPO}/figures"
ASSETS = f"{REPO}/slides/assets"
OUT = f"{REPO}/slides/defense_slides.pptx"

INK = RGBColor(0x0B, 0x0B, 0x0B)
MUTED = RGBColor(0x52, 0x51, 0x4E)
RED = RGBColor(0x9B, 0x00, 0x14)      # UniPD red
BLUE = RGBColor(0x2A, 0x78, 0xD6)     # BASIC series blue
GREEN = RGBColor(0x00, 0x63, 0x00)
LIGHT = RGBColor(0xF0, 0xEF, 0xEC)

SLIDE_W, SLIDE_H = Inches(10), Inches(7.5)

# ---------- image prep: trim whitespace ----------
def trimmed(src, name, pad=8):
    dst = f"{ASSETS}/{name}"
    if not os.path.exists(dst):
        im = Image.open(src).convert("RGB")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        diff = ImageChops.difference(im, bg)
        bbox = diff.getbbox()
        if bbox:
            l, t, r, b = bbox
            l, t = max(0, l - pad), max(0, t - pad)
            r, b = min(im.width, r + pad), min(im.height, b + pad)
            im = im.crop((l, t, r, b))
        im.save(dst)
    return dst

IMG = {
    "dataset": trimmed(f"{FIG}/icir_dataset.png", "icir_dataset_trim.png"),
    "grid": trimmed(f"{FIG}/icir_instances_grid.png", "icir_grid_trim.png"),
    "basic": trimmed(f"{FIG}/basic_method.png", "basic_method_trim.png"),
    "success": trimmed(f"{FIG}/qualitative_success.png", "qual_success_trim.png"),
    "failure": trimmed(f"{FIG}/qualitative_failure_q1100.png", "qual_failure_trim.png"),
    "stats": trimmed(f"{FIG}/icir_stats.png", "icir_stats_trim.png"),
    "ref": f"{FIG}/pipeline_samples/ref.jpg",
    "top1": f"{FIG}/pipeline_samples/top1.jpg",
    "tintin": f"{FIG}/caption_example_samples/ref.jpg",
    "tintin_t": f"{FIG}/caption_example_samples/top1.jpg",
    "ladder_l": f"{ASSETS}/ladder_clipl.png",
    "ladder_s2": f"{ASSETS}/ladder_siglip2.png",
    "backbones": f"{ASSETS}/backbones.png",
}

prs = Presentation(f"{REPO}/slides/UniPD_template.pptx")
TITLE_LAYOUT = prs.slide_masters[0].slide_layouts[0]
CONTENT_LAYOUT = prs.slide_masters[0].slide_layouts[1]

# ---------- helpers ----------
def fit_box(img_path, max_w, max_h):
    w, h = Image.open(img_path).size
    scale = min(max_w / w, max_h / h)
    return int(w * scale), int(h * scale)

def add_pic(slide, img, left, top, max_w, max_h, center_in_box=True):
    """Add picture scaled to fit (max_w, max_h) box at (left, top), centered."""
    w, h = Image.open(img).size
    scale = min(max_w / w, max_h / h)
    pw, ph = Emu(int(w * scale * 914400 / 914400)), None
    disp_w, disp_h = int(w * scale), int(h * scale)
    l = left + (max_w - disp_w) // 2 if center_in_box else left
    t = top + (max_h - disp_h) // 2 if center_in_box else top
    return slide.shapes.add_picture(img, l, t, disp_w, disp_h)

def txt(slide, left, top, w, h, text, size=18, bold=False, color=INK,
        align=PP_ALIGN.LEFT, italic=False, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(left, top, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.alignment = align
        for r in p.runs:
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.italic = italic
            r.font.color.rgb = color
    return box

def clean_placeholders(slide, keep_body=False):
    """Remove leftover footer/slide-number junk and (optionally) the body ph."""
    for ph in list(slide.placeholders):
        idx = ph.placeholder_format.idx
        if idx == 0:
            continue
        if idx == 1 and keep_body:
            continue
        ph._element.getparent().remove(ph._element)

def new_slide(title, notes="", keep_body=False):
    slide = prs.slides.add_slide(CONTENT_LAYOUT)
    slide.shapes.title.text = title
    for p in slide.shapes.title.text_frame.paragraphs:
        for r in p.runs:
            r.font.size = Pt(28)
    clean_placeholders(slide, keep_body=keep_body)
    if notes:
        slide.notes_slide.notes_text_frame.text = notes
    return slide

def bullets(slide, items, left=Inches(0.68), top=Inches(1.6), w=Inches(8.6),
            h=Inches(4.6), size=19, gap=True):
    h = min(h, Inches(7.3) - top)
    box = slide.shapes.add_textbox(left, top, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        if isinstance(item, tuple):
            text, opts = item
        else:
            text, opts = item, {}
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = ("•  " + text) if not opts.get("nobullet") else text
        if gap:
            p.space_after = Pt(10)
        for r in p.runs:
            r.font.size = Pt(opts.get("size", size))
            r.font.bold = opts.get("bold", False)
            r.font.italic = opts.get("italic", False)
            r.font.color.rgb = opts.get("color", INK)
    return box

def takeaway(slide, text, top=Inches(6.55)):
    bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.68), top,
                                 Inches(8.6), Inches(0.62))
    bar.fill.solid()
    bar.fill.fore_color.rgb = LIGHT
    bar.line.fill.background()
    tf = bar.text_frame
    tf.word_wrap = True
    tf.margin_left, tf.margin_right = Inches(0.15), Inches(0.15)
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = PP_ALIGN.CENTER
    for r in p.runs:
        r.font.size = Pt(16)
        r.font.bold = True
        r.font.color.rgb = RED

def arrow(slide, left, top, w, h=Inches(0.5)):
    a = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, left, top, w, h)
    a.fill.solid()
    a.fill.fore_color.rgb = RED
    a.line.fill.background()
    return a

def card(slide, left, top, w, h, fill=RGBColor(0xFF, 0xFF, 0xFF), line=MUTED):
    c = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, w, h)
    c.fill.solid()
    c.fill.fore_color.rgb = fill
    c.line.color.rgb = line
    c.line.width = Pt(1)
    return c

# =========================================================
# Slide 1 — title (reuse template's title slide)
# =========================================================
s = prs.slides[0]
s.shapes.title.text = ("Imagining the Target:\nZero-Shot Instance-Level Composed "
                       "Image Retrieval with MLLM-Generated Captions")
for p in s.shapes.title.text_frame.paragraphs:
    for r in p.runs:
        r.font.size = Pt(26)
for ph in s.placeholders:
    if ph.placeholder_format.idx == 1:
        ph.text = ("Asma Hoseinpour Siouki\nMSc Data Science — University of Padova\n"
                   "Supervisor: Prof. Lamberto Ballan · Co-supervisor: Prof. Marco Fiorucci\n"
                   "July 2026")
        for p in ph.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(15)
s.notes_slide.notes_text_frame.text = (
    "0:30 — One-line hook: 'My thesis is about finding a specific object in a large "
    "photo collection when the query is an image plus a text modification — without "
    "training any model.'")

# delete the template's example slide 2 (TOC)
sldIdLst = prs.slides._sldIdLst
prs.part.drop_rel(sldIdLst[1].rId)
sldIdLst.remove(sldIdLst[1])

# =========================================================
# Slide 2 — What is Composed Image Retrieval?
# =========================================================
s = new_slide("What is Composed Image Retrieval?", notes=(
    "1:00 — Anchor example: the Temple of Poseidon photo + 'in an old archival photo'. "
    "You want the SAME place, but as described by the text. Uses: e-commerce ('this bag "
    "but in leather'), photo archives, digital asset search. This example returns "
    "throughout the talk."))
Y = Inches(2.0)
BOXH = Inches(2.6)
add_pic(s, IMG["ref"], Inches(0.68), Y, Inches(2.5), BOXH)
p = txt(s, Inches(3.3), Y, Inches(0.5), BOXH, "+", size=40, bold=True,
        align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
c = card(s, Inches(3.85), Inches(2.75), Inches(2.0), Inches(1.1))
tf = c.text_frame; tf.word_wrap = True
tf.paragraphs[0].text = "“in an old archival photo”"
for r in tf.paragraphs[0].runs:
    r.font.size = Pt(15); r.font.italic = True; r.font.color.rgb = INK
arrow(s, Inches(6.0), Inches(3.05), Inches(0.7))
add_pic(s, IMG["top1"], Inches(6.85), Y, Inches(2.5), BOXH)
txt(s, Inches(0.68), Inches(1.55), Inches(2.5), Inches(0.4), "query image",
    size=13, color=MUTED, align=PP_ALIGN.CENTER)
txt(s, Inches(3.85), Inches(2.35), Inches(2.0), Inches(0.4), "modification text",
    size=13, color=MUTED, align=PP_ALIGN.CENTER)
txt(s, Inches(6.85), Inches(1.55), Inches(2.5), Inches(0.4), "target image",
    size=13, color=MUTED, align=PP_ALIGN.CENTER)
bullets(s, [
    "Query = an image + a text that modifies it: “this, but …”",
    "Useful when neither words nor an image alone can express what you want",
], top=Inches(5.15), size=18)
takeaway(s, "Search with a picture and a sentence at the same time.")

# =========================================================
# Slide 3 — Instance-level: this exact object
# =========================================================
s = new_slide("Instance-level retrieval: this exact object", notes=(
    "1:00 — Category-level CIR: 'a dress like this, but red' — any red dress is fine. "
    "Instance-level: THE Temple of Poseidon, THE mask of Agamemnon — one specific object "
    "under strong appearance changes (night, sketch, scale model). Much less to hold on "
    "to: category features don't identify a single object. The grid shows the 202 "
    "instances in the benchmark: landmarks, products, cartoon characters, artworks."))
add_pic(s, IMG["grid"], Inches(4.7), Inches(1.5), Inches(4.7), Inches(5.6))
bullets(s, [
    ("Category-level:  “a red dress like this” →\nany red dress counts", {}),
    ("Instance-level:  “this exact object” →\nonly the very same one counts", {"bold": True}),
    ("The object must be recognized under strong\nchanges: night, sketch, scale model, painting …", {}),
    ("202 distinct instances: landmarks, products,\ncharacters, artworks", {}),
], w=Inches(4.0), size=17)
takeaway(s, "Harder task: identity must survive drastic appearance changes.")

# =========================================================
# Slide 4 — the i-CIR benchmark
# =========================================================
s = new_slide("The i-CIR benchmark", notes=(
    "1:30 — Walk ONE query: Temple of Poseidon + 5 modification texts. Row 1: composed "
    "positives (same temple, modified condition). Row 2/3: hard negatives — visually "
    "similar temple (visual negative), right condition but wrong object (textual "
    "negatives), and composed negatives that get BOTH almost right. Make sure the "
    "committee sees WHY these make the task hard. Stats: 1,883 queries, 202 instances "
    "(median 6 queries each), 752,092 database images."))
add_pic(s, IMG["dataset"], Inches(0.5), Inches(1.5), Inches(9.0), Inches(3.9))
for i, (num, lab) in enumerate([("1,883", "queries"), ("202", "object instances"),
                                ("752,092", "database images")]):
    c = card(s, Inches(0.9 + i * 2.85), Inches(5.6), Inches(2.6), Inches(0.95))
    tf = c.text_frame
    tf.paragraphs[0].text = num
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    for r in tf.paragraphs[0].runs:
        r.font.size = Pt(24); r.font.bold = True; r.font.color.rgb = RED
    p2 = tf.add_paragraph(); p2.text = lab; p2.alignment = PP_ALIGN.CENTER
    for r in p2.runs:
        r.font.size = Pt(13); r.font.color.rgb = MUTED

# =========================================================
# Slide 5 — zero-shot
# =========================================================
s = new_slide("Constraint: no training — zero-shot", notes=(
    "1:00 — Most CIR systems train a fusion model on (image, text, target) triplets. "
    "Here that's impossible AND undesirable: no training set for these 202 instances, "
    "collecting one per new instance doesn't scale, and a trained model overfits its "
    "training domain. Zero-shot = assemble pre-trained models, add no learned parameters. "
    "Weave related work in here verbally (combiner networks, textual-inversion methods) — "
    "backup slide exists if asked."))
bullets(s, [
    "Prior CIR methods train a fusion network on labelled triplets (image, text → target)",
    "For instance-level search there is no training data — and every new object would need more",
    ("Zero-shot approach: use large pre-trained models as-is, learn nothing", {"bold": True}),
    "Generalizes to any new instance immediately — nothing to re-train, ever",
], top=Inches(1.9), size=20)
takeaway(s, "Everything you will see today involves no training whatsoever.")

# =========================================================
# Slide 6 — evaluation
# =========================================================
s = new_slide("How we measure success", notes=(
    "1:00 — ONE metric explained, the rest named. The system returns a ranked list; "
    "average precision rewards putting the true images near the top. mAP = mean over all "
    "1,883 queries. macro-mAP averages per instance first, so an object with many queries "
    "doesn't dominate — each of the 202 objects counts equally. If the statistics "
    "professor asks: formulas are on a backup slide."))
txt(s, Inches(0.68), Inches(1.55), Inches(8.6), Inches(0.5),
    "The system returns a ranked list — did the true targets come out on top?",
    size=19)
rank_y = Inches(2.4)
pos = {0, 2, 5}
for i in range(8):
    c = card(s, Inches(0.9 + i * 1.05), rank_y, Inches(0.85), Inches(0.85),
             fill=RGBColor(0x0C, 0xA3, 0x0C) if i in pos else LIGHT)
    tf = c.text_frame
    tf.paragraphs[0].text = "✓" if i in pos else ""
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    for r in tf.paragraphs[0].runs:
        r.font.size = Pt(28); r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    txt(s, Inches(0.9 + i * 1.05), Inches(3.3), Inches(0.85), Inches(0.3),
        f"{i+1}", size=12, color=MUTED, align=PP_ALIGN.CENTER)
txt(s, Inches(0.68), Inches(3.75), Inches(8.6), Inches(0.4),
    "rank of the returned images   (green = a true target)", size=13, color=MUTED)
bullets(s, [
    "Average Precision (AP): high when the true targets sit at the top of the list",
    "mAP: the mean AP over all 1,883 queries",
    ("macro-mAP: average per object first — each of the 202 instances counts equally "
     "(main metric)", {"bold": True}),
], top=Inches(4.35), size=18)

# =========================================================
# Slide 7 — CLIP / shared embedding space
# =========================================================
s = new_slide("The tool: images and text in one space", notes=(
    "1:30 — This slide decides whether the non-CV committee follows the rest. CLIP: two "
    "encoders trained on 400M image–caption pairs so that an image and a text meaning the "
    "same thing land on NEARBY POINTS. Everything becomes a vector; similarity = "
    "closeness. Genomics analogy if useful: like embedding heterogeneous data types into "
    "a common latent space. No training by us — we use it off the shelf."))
add_pic(s, IMG["ref"], Inches(0.68), Inches(1.8), Inches(1.9), Inches(1.5))
c = card(s, Inches(0.55), Inches(4.3), Inches(2.3), Inches(1.0))
c.text_frame.paragraphs[0].text = "“temple on a cliff by the sea”"
for r in c.text_frame.paragraphs[0].runs:
    r.font.size = Pt(13); r.font.italic = True
enc1 = card(s, Inches(3.2), Inches(2.05), Inches(1.9), Inches(0.9), fill=LIGHT)
enc1.text_frame.paragraphs[0].text = "image encoder"
enc2 = card(s, Inches(3.2), Inches(4.35), Inches(1.9), Inches(0.9), fill=LIGHT)
enc2.text_frame.paragraphs[0].text = "text encoder"
for e in (enc1, enc2):
    e.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    for r in e.text_frame.paragraphs[0].runs:
        r.font.size = Pt(15); r.font.bold = True
arrow(s, Inches(2.7), Inches(2.3), Inches(0.45), Inches(0.35))
arrow(s, Inches(2.95), Inches(4.6), Inches(0.45), Inches(0.35))
arrow(s, Inches(5.2), Inches(2.3), Inches(0.5), Inches(0.35))
arrow(s, Inches(5.2), Inches(4.6), Inches(0.5), Inches(0.35))
space = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(5.9), Inches(1.7), Inches(3.5), Inches(4.0))
space.fill.solid(); space.fill.fore_color.rgb = RGBColor(0xFA, 0xFA, 0xF8)
space.line.color.rgb = MUTED; space.line.width = Pt(1.2)
txt(s, Inches(6.1), Inches(1.85), Inches(3.1), Inches(0.4), "shared embedding space",
    size=14, color=MUTED, align=PP_ALIGN.CENTER)
for (x, y, col) in [(7.15, 3.15, BLUE), (7.55, 3.45, RED)]:
    d = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(0.28), Inches(0.28))
    d.fill.solid(); d.fill.fore_color.rgb = col; d.line.fill.background()
txt(s, Inches(6.55), Inches(3.95), Inches(2.6), Inches(0.8),
    "same meaning →\nnearby points", size=14, color=INK, align=PP_ALIGN.CENTER)
takeaway(s, "Similarity between any image and any text = distance between two vectors.")

# =========================================================
# Slide 8 — BASIC
# =========================================================
s = new_slide("The starting point: BASIC", notes=(
    "1:30 — BASIC (the i-CIR paper's zero-shot method) scores every database image "
    "twice: does it LOOK like the query image, and does it MATCH the modification text? "
    "Multiplying the two normalized scores acts as a soft logical AND — an image must "
    "satisfy both. Walk the figure top-left to bottom-right at high level only; the "
    "fusion details (min-normalization, Harris, clipping) are one sentence + backup slide."))
add_pic(s, IMG["basic"], Inches(0.4), Inches(1.55), Inches(9.2), Inches(4.5))
takeaway(s, "score  =  image similarity  ×  text similarity   —  a soft logical AND")

# =========================================================
# Slide 9 — the blind spot (hinge)
# =========================================================
s = new_slide("BASIC's blind spot — and our idea", notes=(
    "1:30 — THE hinge of the talk, slow down. BASIC scores the image and the text "
    "SEPARATELY; nothing ever reads them together, so it cannot know the text transforms "
    "the query ('as a painting' ≠ 'a painting nearby'). Our idea: a multimodal LLM reads "
    "BOTH and writes a caption of the imagined target — the thesis title. That caption "
    "becomes a third scoring branch alongside BASIC's two."))
txt(s, Inches(0.68), Inches(1.6), Inches(8.6), Inches(0.9),
    "At no point does BASIC look at the image and the text together.",
    size=22, bold=True, color=RED)
add_pic(s, IMG["ref"], Inches(0.68), Inches(3.0), Inches(1.7), Inches(1.4))
c = card(s, Inches(0.68), Inches(4.6), Inches(1.7), Inches(1.0))
c.text_frame.word_wrap = True
c.text_frame.paragraphs[0].text = "“in an old archival photo”"
for r in c.text_frame.paragraphs[0].runs:
    r.font.size = Pt(12); r.font.italic = True
arrow(s, Inches(2.6), Inches(3.9), Inches(0.6), Inches(0.4))
m = card(s, Inches(3.35), Inches(3.55), Inches(1.9), Inches(1.1),
         fill=RGBColor(0xFB, 0xE9, 0xE7))
m.text_frame.paragraphs[0].text = "multimodal LLM"
m.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
for r in m.text_frame.paragraphs[0].runs:
    r.font.size = Pt(15); r.font.bold = True
arrow(s, Inches(5.45), Inches(3.9), Inches(0.6), Inches(0.4))
cap = card(s, Inches(6.2), Inches(3.35), Inches(3.1), Inches(1.5))
cap.text_frame.word_wrap = True
cap.text_frame.paragraphs[0].text = ("“The Temple of Poseidon in an old archival "
                                     "photo …”")
for r in cap.text_frame.paragraphs[0].runs:
    r.font.size = Pt(14); r.font.italic = True
txt(s, Inches(6.2), Inches(4.95), Inches(3.1), Inches(0.4),
    "a caption of the imagined target", size=13, color=MUTED, align=PP_ALIGN.CENTER)
takeaway(s, "Let a multimodal LLM imagine the target — and describe it in one sentence.")

# =========================================================
# Slide 10 — caption generation
# =========================================================
s = new_slide("Generating the target caption", notes=(
    "1:30 — InternVL (8B) sees the query image + modification text and writes what the "
    "target should look like. The instruction matters: five prompt styles (adaptive "
    "precision, constraint-priority, anti-noise, slot-fill, draft–refine) give five "
    "different captions. The caption is embedded with the SAME CLIP text encoder and "
    "multiplied in as a third branch: image × text × caption."))
add_pic(s, IMG["tintin"], Inches(0.68), Inches(1.7), Inches(1.9), Inches(1.6))
c = card(s, Inches(0.68), Inches(3.5), Inches(1.9), Inches(0.9))
c.text_frame.word_wrap = True
c.text_frame.paragraphs[0].text = "“as an iconic rooftop sign”"
for r in c.text_frame.paragraphs[0].runs:
    r.font.size = Pt(12); r.font.italic = True
arrow(s, Inches(2.75), Inches(2.9), Inches(0.55), Inches(0.4))
m = card(s, Inches(3.45), Inches(2.6), Inches(1.7), Inches(1.0),
         fill=RGBColor(0xFB, 0xE9, 0xE7))
m.text_frame.paragraphs[0].text = "InternVL 8B"
m.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
for r in m.text_frame.paragraphs[0].runs:
    r.font.size = Pt(14); r.font.bold = True
arrow(s, Inches(5.3), Inches(2.9), Inches(0.55), Inches(0.4))
for i, (tag, captxt) in enumerate([
        ("draft–refine", "“Cartoon character in a beige coat and blue shirt appears "
                         "as an iconic rooftop sign.”"),
        ("constraint-priority", "“A character wearing a trench coat, blonde hair, and "
                                "a blue shirt, is an iconic rooftop sign.”")]):
    c = card(s, Inches(6.0), Inches(1.75 + i * 1.75), Inches(3.35), Inches(1.55))
    tf = c.text_frame; tf.word_wrap = True
    tf.paragraphs[0].text = tag
    for r in tf.paragraphs[0].runs:
        r.font.size = Pt(12); r.font.bold = True; r.font.color.rgb = RED
    p2 = tf.add_paragraph(); p2.text = captxt
    for r in p2.runs:
        r.font.size = Pt(12); r.font.italic = True
txt(s, Inches(6.0), Inches(5.15), Inches(3.35), Inches(0.6),
    "… 5 instruction styles → 5 captions", size=14, color=MUTED)
bullets(s, [
    "Caption is embedded with the same text encoder — no new model, still zero-shot",
    ("New score:  image × text × caption", {"bold": True}),
], top=Inches(5.75), size=17, gap=False)

# =========================================================
# Slide 11 — captions help immediately
# =========================================================
s = new_slide("Captions help — immediately", notes=(
    "1:00 — CLIP-L, raw scores, no post-processing (docs/final_ablation_clip_l.csv & "
    "docs/backbone_recall.csv, product rung). One caption: 17.95 → 23.83. Five captions "
    "averaged (one per instruction style): 25.41. Averaging washes out any single "
    "prompt's quirks and needs no selection on the eval set."))
tiles = [("17.95", "BASIC\n(no caption)", False),
         ("23.83", "+ 1 caption", False),
         ("25.41", "+ 5 captions,\naveraged", True)]
for i, (num, lab, hero) in enumerate(tiles):
    c = card(s, Inches(0.75 + i * 3.0), Inches(2.3), Inches(2.5), Inches(2.1),
             fill=LIGHT if not hero else RGBColor(0xFB, 0xE9, 0xE7))
    tf = c.text_frame
    tf.paragraphs[0].text = num
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    for r in tf.paragraphs[0].runs:
        r.font.size = Pt(40); r.font.bold = True
        r.font.color.rgb = RED if hero else INK
    for line in lab.split("\n"):
        p2 = tf.add_paragraph(); p2.text = line; p2.alignment = PP_ALIGN.CENTER
        for r in p2.runs:
            r.font.size = Pt(14); r.font.color.rgb = MUTED
    if i < 2:
        arrow(s, Inches(3.28 + i * 3.0), Inches(3.15), Inches(0.44), Inches(0.4))
txt(s, Inches(0.68), Inches(4.7), Inches(8.6), Inches(0.4),
    "macro-mAP · CLIP-L backbone · raw scores, before any post-processing",
    size=13, color=MUTED, align=PP_ALIGN.CENTER)
bullets(s, [
    "One MLLM caption lifts macro-mAP by ~6 points — the single biggest gain in the thesis",
    "Averaging the 5 instruction variants is more robust than any single prompt",
], top=Inches(5.3), size=18)
takeaway(s, "+42% relative improvement, before any other technique.")

# =========================================================
# Slide 12 — post-processing ladder
# =========================================================
s = new_slide("Stacking post-processing", notes=(
    "1:30 — Ladder on CLIP-L (docs/final_ablation_clip_l.csv). Centering: subtract the "
    "mean database embedding — remove what ALL images share so only the distinctive part "
    "remains. Contextualization: enrich the text with object context. Sim-norm & Harris: "
    "smaller normalization steps, one sentence. Projection & query expansion HURT once "
    "the caption is present (they were tuned for raw CLIP features) → dropped. Note: for "
    "BASIC alone, +proj is a hair above +context (32.48 vs 32.25); the drop applies to "
    "the caption pipeline."))
add_pic(s, IMG["ladder_l"], Inches(0.55), Inches(1.55), Inches(8.9), Inches(4.6))
takeaway(s, "Every step stacks; the pipeline stops at +context — later steps hurt.")

# =========================================================
# Slide 13 — backbones
# =========================================================
s = new_slide("Does it transfer? Four backbones", notes=(
    "1:00 — Same pipeline, four vision–language models (docs/backbone_recall.csv, raw "
    "scores). Captions help on EVERY backbone — biggest jump on SigLIP-L (21→43, doubles) "
    "and SigLIP2 (38→56). SigLIP2 = newer CLIP-style model, better training recipe. One "
    "sentence on what SigLIP is — no more."))
add_pic(s, IMG["backbones"], Inches(0.55), Inches(1.55), Inches(8.9), Inches(4.6))
takeaway(s, "The caption branch helps every backbone — not a CLIP-specific trick.")

# =========================================================
# Slide 14 — final results
# =========================================================
s = new_slide("Final results — best backbone", notes=(
    "1:30 — SigLIP2 ladder (runs/caption_backbone_instancepool/siglip2_ladder/"
    "summary_ladder.csv). Headline: 61.98 macro-mAP vs BASIC's 57.69 at the same rung — "
    "and vs 38.1 raw BASIC. Same shape as CLIP-L: peak at +context, proj/QE hurt. "
    "If asked about the paper's BASIC number: our reproduction gives 32.48 (CLIP-L, "
    "full stack) vs the paper's 34.35 — backup slide."))
add_pic(s, IMG["ladder_s2"], Inches(0.55), Inches(1.55), Inches(8.9), Inches(4.6))
takeaway(s, "62.0 macro-mAP zero-shot — +4.3 over BASIC on its best configuration.")

# =========================================================
# Slide 15 — qualitative success
# =========================================================
s = new_slide("When it works", notes=(
    "1:00 — Pink pencil case, 'without sticky paper notes but filled with pens and "
    "markers'. Image-only ranks lookalikes; BASIC partially recovers; our caption "
    "triplet puts both true targets at ranks 1–3 (AP 15 → 42 → 100). The caption "
    "understands the NEGATION — 'without sticky notes' — which similarity alone cannot."))
add_pic(s, IMG["success"], Inches(0.4), Inches(1.5), Inches(9.2), Inches(5.5))

# =========================================================
# Slide 16 — when it fails
# =========================================================
s = new_slide("When it fails", notes=(
    "1:00 — Mask of Agamemnon 'as a painting': every method returns real masks — visual "
    "identity overwhelms the modification. The target (an actual painting) looks too "
    "different. Honest diagnosis: when the modification demands a drastic domain shift, "
    "image similarity dominates the product. This buys credibility — own it."))
add_pic(s, IMG["failure"], Inches(0.4), Inches(1.5), Inches(9.2), Inches(4.8))
takeaway(s, "Failure mode: visual identity can overpower a drastic modification.")

# =========================================================
# Slide 17 — limitations & future work
# =========================================================
s = new_slide("Limitations & future work", notes=(
    "1:00 — Latency: caption generation is 99.7% of per-query time, ~15 s/query on a "
    "48GB GPU (Appendix C). Levers: fewer captions, shorter generation, smaller/quantized "
    "MLLM. Forward-looking close, not apologetic."))
bullets(s, [
    ("Caption generation is slow: ≈ 15 s per query — 99.7% of inference time", {}),
    ("Drastic modifications (e.g. “as a painting”) can still be overpowered by visual similarity", {}),
    ("Results depend on prompt design — 5-caption averaging mitigates, doesn't remove", {}),
    ("Future:", {"bold": True}),
    ("     smaller / quantized captioners for real-time use", {"nobullet": True}),
    ("     caption-aware fusion instead of a plain product", {"nobullet": True}),
    ("     extending the caption branch to category-level CIR benchmarks", {"nobullet": True}),
], top=Inches(1.8), size=19)

# =========================================================
# Slide 18 — conclusions / thank you
# =========================================================
s = new_slide("Conclusions", notes=(
    "1:00 — Mirror the story: (1) zero-shot CIR works at instance level; (2) one idea — "
    "let an MLLM imagine the target — gives the single largest gain and transfers across "
    "all four backbones; (3) with post-processing, 62.0 macro-mAP, +4.3 over BASIC. "
    "Thank the committee, invite questions."))
bullets(s, [
    ("A specific object can be found among 752k images with an image + a sentence — "
     "with zero training", {}),
    ("One idea drives the gains: a multimodal LLM imagines the target and describes it "
     "— +42% relative on CLIP-L, and it transfers to every backbone tested", {"bold": True}),
    ("Post-processing stacks on top: 62.0 macro-mAP, +4.3 over the best BASIC "
     "configuration", {}),
], top=Inches(1.9), size=20)
txt(s, Inches(0.68), Inches(5.4), Inches(8.6), Inches(0.8), "Thank you!",
    size=32, bold=True, color=RED, align=PP_ALIGN.CENTER)

# =========================================================
# Backup slides
# =========================================================
s = new_slide("Backup — evaluation metrics", notes="Backup for the metrics question.")
bullets(s, [
    ("AP(q) = Σ_k  P(k) · rel(k)  /  #positives(q)   — precision accumulated at each "
     "true target's rank", {}),
    ("mAP = (1/1883) Σ_q AP(q)   (micro: every query equal)", {}),
    ("macro-mAP = (1/202) Σ_i  mean AP of instance i's queries   (every object equal)", {}),
    ("Also reported: Recall@K / Hit@K — is at least one true target in the top K?", {}),
], top=Inches(1.9), size=18)

s = new_slide("Backup — BASIC score fusion details", notes="Backup: fusion internals.")
bullets(s, [
    "Cosine similarities from image and text branch have different ranges → min-normalization per query",
    "Harris criterion: harmonic-style combination penalizing images strong in only one branch",
    "Scores clipped at zero before multiplying — negative evidence cannot cancel",
    "Ours: identical machinery, with the caption similarity as a third factor",
], top=Inches(1.9), size=18)

s = new_slide("Backup — full CLIP-L ablation", notes=(
    "Full table from docs/final_ablation_clip_l.csv (macro-mAP, full i-CIR)."))
rows = [("step", "BASIC", "Ours (avg-5)", "Ours (single J)"),
        ("raw (img × text)", "17.95", "25.41", "23.83"),
        ("+ centering", "27.76", "31.87", "31.02"),
        ("+ sim-norm", "27.40", "31.97", "30.28"),
        ("+ Harris", "28.33", "32.82", "31.25"),
        ("+ context", "32.25", "35.76", "34.06"),
        ("+ projection", "32.48", "33.80", "32.58"),
        ("+ query-expansion", "30.28", "32.39", "31.53")]
tbl = s.shapes.add_table(len(rows), 4, Inches(1.2), Inches(1.7), Inches(7.6),
                         Inches(4.4)).table
for i, row in enumerate(rows):
    for j, val in enumerate(row):
        cell = tbl.cell(i, j)
        cell.text = val
        for p in cell.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = Pt(14)
                r.font.bold = (i == 0) or (row[0] == "+ context")

s = new_slide("Backup — reproducing BASIC", notes=(
    "The paper reports 34.35 (CLIP-L full stack); our faithful re-run of the authors' "
    "code gives 32.48. Verified not to be a bug in our pipeline — same code, same "
    "checkpoints; residual gap likely preprocessing/version differences. All comparisons "
    "in the thesis use our reproduced numbers for both methods — apples to apples."))
bullets(s, [
    "i-CIR paper reports BASIC at 34.35 macro-mAP (CLIP-L, full post-processing)",
    "Our reproduction with the authors' own code: 32.48",
    "Same checkpoints and protocol — residual gap traced to environment/preprocessing versions",
    ("All thesis comparisons use reproduced numbers for both BASIC and Ours — same code "
     "path, fair comparison", {"bold": True}),
], top=Inches(1.9), size=18)

s = new_slide("Backup — inference latency", notes=(
    "runs/inference_time/summary.csv — 100 queries, RTX-6000-Ada 48GB, K=5 captions."))
bullets(s, [
    "Per-query online inference: median ≈ 14.75 s (min 10.2, max 21.4) — both backbones alike",
    "Caption generation ≈ 99.7% of the time; embedding the triplet: 22 ms (CLIP-L) / 46 ms (SigLIP2)",
    "Database embeddings are computed offline — search itself is instantaneous",
    "Levers: fewer captions (K), shorter generations, smaller or quantized MLLM, batching",
], top=Inches(1.9), size=18)

s = new_slide("Backup — the five caption instructions", notes=(
    "Tintin example, figures/instruction_captions_compare.tex."))
add_pic(s, IMG["tintin"], Inches(0.68), Inches(1.8), Inches(2.1), Inches(1.8))
txt(s, Inches(0.68), Inches(3.8), Inches(2.1), Inches(0.6), "“as an iconic rooftop sign”",
    size=13, italic=True, align=PP_ALIGN.CENTER)
caps = [("A · adaptive precision", "A character with a beige coat and blue shirt, as an iconic rooftop sign"),
        ("B · constraint-priority", "A character wearing a trench coat, blonde hair, and a blue shirt, is an iconic rooftop sign."),
        ("C · anti-noise contract", "Character in a beige trench coat, blue shirt, with blushing cheeks and short orange hair as an iconic rooftop sign."),
        ("D · slot-fill template", "a cartoon character wearing a trench coat, blushing, with short hair as an iconic rooftop sign."),
        ("E · draft–refine", "Cartoon character in a beige coat and blue shirt appears as an iconic rooftop sign.")]
for i, (tag, captxt) in enumerate(caps):
    c = card(s, Inches(3.1), Inches(1.6 + i * 1.05), Inches(6.3), Inches(0.95))
    tf = c.text_frame; tf.word_wrap = True
    tf.paragraphs[0].text = f"{tag}:  “{captxt}”"
    for r in tf.paragraphs[0].runs:
        r.font.size = Pt(11.5)

prs.save(OUT)
print("saved", OUT, "· slides:", len(prs.slides.__iter__.__self__._sldIdLst))
