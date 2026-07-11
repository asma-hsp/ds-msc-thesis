"""Build the defense deck on the UniPD template.
Output: slides/defense_slides.pptx. Run make_charts.py and make_slide_assets.py first.
"""
import os
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

REPO = "/extra/ahoseinp/projects/ds-msc-thesis"
FIG = f"{REPO}/figures"
ASSETS = f"{REPO}/slides/assets"
OUT = f"{REPO}/slides/defense_slides.pptx"

INK = RGBColor(0x0B, 0x0B, 0x0B)
MUTED = RGBColor(0x52, 0x51, 0x4E)
RED = RGBColor(0x9B, 0x00, 0x14)
BLUE = RGBColor(0x2A, 0x78, 0xD6)
LIGHT = RGBColor(0xF0, 0xEF, 0xEC)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
ROSE = RGBColor(0xFB, 0xE9, 0xE7)

IMG = {
    "tintin_fig": f"{ASSETS}/icir_tintin.png",
    "inst_cat": f"{ASSETS}/instance_vs_category.png",
    "clip": f"{ASSETS}/clip_schematic.png",
    "stats": f"{ASSETS}/icir_stats_trim.png",
    "basic": f"{ASSETS}/basic_method_trim.png",
    "harris": f"{FIG}/harris_surface.png",
    "success": f"{ASSETS}/qual_success_trim.png",
    "failure": f"{ASSETS}/qual_failure_trim.png",
    "ladder_l": f"{ASSETS}/ladder_clipl.png",
    "ladder_s2": f"{ASSETS}/ladder_siglip2.png",
    "backbones": f"{ASSETS}/backbones.png",
    "ref": f"{ASSETS}/chair_ref_43.jpg",
    "top1": f"{ASSETS}/chair_set_43.jpg",
    "paper_stats": f"{ASSETS}/icir_paper_stats.png",
    "tintin_q": f"{FIG}/caption_example_samples/ref.jpg",
    "eq_pk": f"{ASSETS}/eq_pk.png",
    "eq_ap": f"{ASSETS}/eq_ap.png",
    "eq_map": f"{ASSETS}/eq_map.png",
    "eq_mmap": f"{ASSETS}/eq_mmap.png",
    "eq_centering": f"{ASSETS}/eq_centering.png",
    "eq_minnorm": f"{ASSETS}/eq_minnorm.png",
    "eq_harris": f"{ASSETS}/eq_harris.png",
    "eq_triplet": f"{ASSETS}/eq_triplet.png",
    "eq_problem": f"{ASSETS}/eq_problem.png",
}

prs = Presentation(f"{REPO}/slides/UniPD_template.pptx")
CONTENT_LAYOUT = prs.slide_masters[0].slide_layouts[1]

# ---------------- helpers ----------------
def style_runs(paragraph, size, bold=False, color=INK, italic=False):
    for r in paragraph.runs:
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color

def add_pic(slide, img, left, top, max_w, max_h):
    w, h = Image.open(img).size
    scale = min(max_w / w, max_h / h)
    dw, dh = int(w * scale), int(h * scale)
    return slide.shapes.add_picture(img, int(left + (max_w - dw) / 2),
                                    int(top + (max_h - dh) / 2), dw, dh)

def txt(slide, left, top, w, h, text, size=17, bold=False, color=INK,
        align=PP_ALIGN.LEFT, italic=False, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(left, top, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for i, line in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.alignment = align
        style_runs(p, size, bold, color, italic)
    return box

def clean_placeholders(slide):
    for ph in list(slide.placeholders):
        if ph.placeholder_format.idx != 0:
            ph._element.getparent().remove(ph._element)

def new_slide(title, notes=""):
    slide = prs.slides.add_slide(CONTENT_LAYOUT)
    slide.shapes.title.text = title
    for p in slide.shapes.title.text_frame.paragraphs:
        style_runs(p, 27, bold=False, color=INK)
    clean_placeholders(slide)
    if notes:
        slide.notes_slide.notes_text_frame.text = notes
    # page number bottom-right (title slide is not built via new_slide)
    n = len(prs.slides._sldIdLst)
    txt(slide, Inches(9.25), Inches(7.08), Inches(0.55), Inches(0.32), str(n),
        size=11, color=MUTED, align=PP_ALIGN.RIGHT)
    return slide

def bullets(slide, items, left=Inches(0.68), top=Inches(1.55), w=Inches(8.6),
            size=17, gap=8):
    h = Inches(7.3) - top
    box = slide.shapes.add_textbox(left, top, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        text, opts = item if isinstance(item, tuple) else (item, {})
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if opts.get("indent"):
            p.text = "      –  " + text
        elif opts.get("nobullet"):
            p.text = text
        else:
            p.text = "•  " + text
        p.space_after = Pt(gap)
        style_runs(p, opts.get("size", size), opts.get("bold", False),
                   opts.get("color", INK), opts.get("italic", False))
    return box

def takeaway(slide, text, top):
    bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.68), top,
                                 Inches(8.6), Inches(0.55))
    bar.fill.solid(); bar.fill.fore_color.rgb = LIGHT
    bar.line.fill.background()
    tf = bar.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.12)
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = PP_ALIGN.CENTER
    style_runs(p, 15, bold=True, color=RED)

def card(slide, left, top, w, h, text=None, fill=WHITE, line=MUTED, size=13,
         bold=False, color=INK, italic=False, align=PP_ALIGN.CENTER):
    c = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, w, h)
    c.fill.solid(); c.fill.fore_color.rgb = fill
    if line is None:
        c.line.fill.background()
    else:
        c.line.color.rgb = line
        c.line.width = Pt(1)
    if text is not None:
        tf = c.text_frame
        tf.word_wrap = True
        for i, ln in enumerate(text.split("\n")):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = ln
            p.alignment = align
            style_runs(p, size, bold, color, italic)
    return c

def arrow(slide, left, top, w, h=Inches(0.42)):
    a = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, left, top, w, h)
    a.fill.solid(); a.fill.fore_color.rgb = RED
    a.line.fill.background()
    return a

def table(slide, rows, left, top, width, row_h=0.42, size=14,
          highlight_rows=(), col0_left=True):
    n, m = len(rows), len(rows[0])
    tbl = slide.shapes.add_table(n, m, left, top, width,
                                 Inches(row_h * n)).table
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = tbl.cell(i, j)
            cell.text = str(val)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            for p in cell.text_frame.paragraphs:
                p.alignment = (PP_ALIGN.LEFT if (j == 0 and col0_left)
                               else PP_ALIGN.CENTER)
                style_runs(p, size, bold=(i == 0 or i in highlight_rows),
                           color=WHITE if i == 0 else INK)
    return tbl

# =========================================================
# 1 — title
# =========================================================
s = prs.slides[0]
s.shapes.title.text = ("Imagining the Target:\nZero-Shot Instance-Level Composed "
                       "Image Retrieval with MLLM-Generated Captions")
for p in s.shapes.title.text_frame.paragraphs:
    style_runs(p, 26, bold=False, color=INK)
for ph in s.placeholders:
    if ph.placeholder_format.idx == 1:
        ph.text = ("Asma Hoseinpour Siouki\nMSc Data Science — University of Padova\n"
                   "Supervisor: Prof. Lamberto Ballan · Co-supervisor: Prof. Marco Fiorucci\n"
                   "July 2026")
        for p in ph.text_frame.paragraphs:
            style_runs(p, 15, color=INK)
s.notes_slide.notes_text_frame.text = (
    "0:20 — Hook: retrieving one specific object from 752k images, when the query "
    "is an image plus a textual modification — with no training at all.")
sldIdLst = prs.slides._sldIdLst
prs.part.drop_rel(sldIdLst[1].rId)
sldIdLst.remove(sldIdLst[1])

# =========================================================
# 2 — Composed Image Retrieval
# =========================================================
s = new_slide("Composed Image Retrieval (CIR)", notes=(
    "1:00 — Good morning everyone, and thank you for being here. Imagine that you see "
    "a chair online that you really like, but you would like to find a dining set that "
    "includes that same chair design together with a table. To express exactly what "
    "you are looking for, you need to combine both elements: the image identifies the "
    "chair, and the text describes the context in which you want to find it. This is "
    "an example of composed image retrieval — the task of my thesis. The query "
    "consists of a QUERY IMAGE and a QUERY TEXT; the goal is to retrieve images that "
    "preserve the identity of the object in the query image while satisfying the "
    "modification described by the query text."))
Y, BH = Inches(1.75), Inches(2.15)
add_pic(s, IMG["ref"], Inches(0.68), Y, Inches(2.5), BH)
txt(s, Inches(3.2), Y, Inches(0.4), BH, "+", size=32, bold=True,
    align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
card(s, Inches(3.6), Inches(2.35), Inches(2.0), Inches(1.0),
     text="“placed around\na table”", size=14, italic=True, color=BLUE)
arrow(s, Inches(5.7), Inches(2.6), Inches(0.6))
add_pic(s, IMG["top1"], Inches(6.4), Y, Inches(2.5), BH)
txt(s, Inches(0.68), Inches(3.95), Inches(2.5), Inches(0.35), "query image",
    size=12, color=MUTED, align=PP_ALIGN.CENTER)
txt(s, Inches(3.6), Inches(3.45), Inches(2.0), Inches(0.35), "query text",
    size=12, color=MUTED, align=PP_ALIGN.CENTER)
txt(s, Inches(6.4), Inches(3.95), Inches(2.5), Inches(0.35), "target image",
    size=12, color=MUTED, align=PP_ALIGN.CENTER)
bullets(s, [
    "The query consists of a query image and a query text",
    ("Goal: retrieve images that preserve the identity of the object in the query "
     "image while satisfying the modification described by the query text", {"bold": True}),
    "Neither element alone can express the information need — both must be combined",
], top=Inches(4.55), size=16, gap=6)
takeaway(s, "Search with a picture and a sentence at the same time.", Inches(6.45))

# =========================================================
# 3 — Instance-level CIR
# =========================================================
s = new_slide("From categories to instances", notes=(
    "0:50 — Unlike category-level retrieval, where any object from the correct class "
    "may be accepted, instance-level retrieval requires the exact same object shown in "
    "the query image. Why this is more challenging: candidates from the same category "
    "look almost identical, so the system must separate one specific object from "
    "thousands of lookalikes — and at the same time still recognise it when the "
    "modification changes its appearance. Category-level methods have no mechanism "
    "for this identity constraint."))
add_pic(s, IMG["inst_cat"], Inches(0.55), Inches(1.5), Inches(8.9), Inches(3.85))
bullets(s, [
    ("Category-level CIR:  any object from the correct class may be accepted", {}),
    ("Instance-level CIR:  the retrieved object must be the exact same object shown "
     "in the query image", {"bold": True}),
    ("Harder: same-class candidates are near-lookalikes, yet the true object must "
     "still be recognised under the modification", {}),
], top=Inches(5.4), size=16, gap=5)

# =========================================================
# 4 — the i-CIR benchmark
# =========================================================
s = new_slide("The i-CIR benchmark — query structure", notes=(
    "1:20 — For our experiments, we use the i-CIR benchmark. Each instance has "
    "several composed queries, and each query may have multiple correct target "
    "images. The dataset also includes hard negatives that were selected specifically "
    "for each instance. These images are designed to confuse the retrieval system, "
    "because they may match either the image or the text, but not both correctly. "
    "(Walk one column: statue of another character; a rooftop without the sign; "
    "another cartoon on a t-shirt.) Psomas et al., 2025."))
add_pic(s, IMG["tintin_fig"], Inches(0.55), Inches(1.5), Inches(8.9), Inches(4.3))
bullets(s, [
    ("Each instance contributes several composed queries; every query has multiple "
     "ground-truth targets", {}),
    ("Curated hard negatives satisfy one modality but not both — single-modality "
     "shortcuts fail by design", {}),
], top=Inches(5.95), size=15, gap=5)

# =========================================================
# 5 — statistics
# =========================================================
s = new_slide("The i-CIR benchmark — scale", notes=(
    "0:40 — The scale: a database of 752,092 images, 202 object instances, 1,883 "
    "composed queries — median 6 per instance. Histograms as in the i-CIR paper "
    "(recomputed from the dataset): image queries, text queries and hard negatives "
    "per instance; positives per composed query. Needle-in-a-haystack regime: the "
    "positives are a vanishing fraction of the database."))
stats = [("752,092", "database images"), ("202", "object instances"),
         ("1,883", "composed queries"), ("6", "median queries / instance")]
for i, (num, lab) in enumerate(stats):
    c = card(s, Inches(0.55 + i * 2.28), Inches(1.7), Inches(2.08), Inches(1.0),
             text=num, size=22, bold=True, color=RED)
    p2 = c.text_frame.add_paragraph()
    p2.text = lab
    p2.alignment = PP_ALIGN.CENTER
    style_runs(p2, 12, color=MUTED)
add_pic(s, IMG["paper_stats"], Inches(0.55), Inches(3.1), Inches(8.9), Inches(2.4))
txt(s, Inches(0.55), Inches(5.7), Inches(8.9), Inches(0.4),
    "distributions recomputed from the benchmark, following Psomas et al. (2025), Fig. 2",
    size=11, color=MUTED, align=PP_ALIGN.CENTER)

# =========================================================
# 6 — problem formulation
# =========================================================
s = new_slide("Problem formulation — a zero-shot setting", notes=(
    "1:00 — To summarize the task: we are given a query image and a query text, and "
    "we want to retrieve database images that are relevant to both. The system "
    "assigns a score to every image in the database and ranks them from the most to "
    "the least relevant. In this thesis we adopt a zero-shot setting: we do not train "
    "or fine-tune any model on the i-CIR dataset. This choice is important because "
    "supervised composed image retrieval requires labelled triplets — a query image, "
    "a query text, and a target image. At the instance level, collecting these "
    "annotations for every new object would be expensive and difficult to scale. By "
    "using frozen pre-trained models, the system can be applied directly to "
    "previously unseen object instances."))
add_pic(s, IMG["eq_problem"], Inches(0.9), Inches(1.65), Inches(8.2), Inches(0.85))
bullets(s, [
    ("Every database image receives a relevance score; the database is ranked from "
     "most to least relevant", {}),
    ("Zero-shot setting: no model is trained or fine-tuned on i-CIR", {"bold": True}),
    ("Why: supervised CIR needs labelled triplets (query image, query text, target) — "
     "at the instance level this cannot scale to new objects", {}),
    ("Frozen pre-trained models apply directly to previously unseen instances", {}),
], top=Inches(2.85), size=17, gap=10)

# =========================================================
# 7 — evaluation
# =========================================================
s = new_slide("Evaluation metric", notes=(
    "1:00 — The system returns a ranked list. Precision@k: the fraction of the top-k "
    "results that are correct. Average precision: precision at each rank where a "
    "correct image appears, averaged — high when the correct images sit at the top. "
    "mAP averages over all 1,883 queries; macro-mAP first averages within each "
    "instance, so every one of the 202 objects counts equally — the primary metric."))
pos = {0, 2, 5}
for i in range(8):
    card(s, Inches(0.75 + i * 0.72), Inches(1.55), Inches(0.6), Inches(0.6),
         text="✓" if i in pos else "",
         fill=RGBColor(0x0C, 0xA3, 0x0C) if i in pos else LIGHT,
         line=None, size=18, bold=True, color=WHITE)
txt(s, Inches(6.7), Inches(1.62), Inches(2.7), Inches(0.5),
    "ranked list (green = correct)", size=12, color=MUTED)
mrows = [
    ("eq_pk", "Precision@k", "fraction of the top-k results that are correct"),
    ("eq_ap", "Average Precision", "precision at each correct result's rank, averaged"),
    ("eq_map", "mAP", "mean over all queries"),
    ("eq_mmap", "macro-mAP", "per-instance average first — the primary metric"),
]
y = Inches(2.45)
for eq, name, desc in mrows:
    b = txt(s, Inches(0.75), y + Inches(0.06), Inches(3.15), Inches(0.95),
            name, size=14, bold=True, color=INK)
    p2 = b.text_frame.add_paragraph()
    p2.text = desc
    style_runs(p2, 11.5, color=MUTED)
    add_pic(s, IMG[eq], Inches(4.05), y, Inches(5.3), Inches(0.92))
    y += Inches(1.08)

# =========================================================
# 8 — VLMs / CLIP
# =========================================================
s = new_slide("Vision–language models: a shared embedding space", notes=(
    "1:20 — The building block. CLIP: two encoders — one for images, one for text — "
    "trained on 400 million image–caption pairs so that an image and a text with the "
    "same meaning land on nearby points in one shared vector space. Consequence: the "
    "relevance between any image and any sentence is just the cosine similarity of "
    "two vectors. SigLIP is a newer model of the same family, trained with an "
    "improved (sigmoid) objective — it appears later as an alternative backbone. "
    "Both are used frozen. This is the slide the non-CV committee must retain."))
add_pic(s, IMG["clip"], Inches(0.55), Inches(1.5), Inches(8.9), Inches(3.5))
bullets(s, [
    ("CLIP: two encoders trained on 400M image–caption pairs, mapping images and "
     "sentences into one shared vector space (Radford et al., 2021)", {}),
    ("Relevance between any image and any sentence = cosine similarity of their "
     "vectors", {"bold": True}),
    ("SigLIP / SigLIP2: same dual-encoder family, newer sigmoid training objective — "
     "used later as an alternative backbone", {}),
    ("Both used frozen; baseline backbone: CLIP ViT-L/14", {}),
], top=Inches(5.1), size=15, gap=5)

# =========================================================
# 9 — BASIC
# =========================================================
s = new_slide("The BASIC method (Psomas et al., 2025)", notes=(
    "1:20 — The benchmark's zero-shot reference method, our baseline. Two unimodal "
    "branches score every database image independently: visual similarity to the "
    "query image; textual similarity to the query text. Branch-specific "
    "post-processing (walk the figure at high level), then multiplicative fusion — a "
    "soft conjunction, which is what composed queries demand."))
add_pic(s, IMG["basic"], Inches(0.55), Inches(1.5), Inches(8.9), Inches(3.55))
bullets(s, [
    ("Image branch  sᵛ(x): visual similarity between database image and the query image", {}),
    ("Text branch  sᵗ(x): similarity between database image and the query text", {}),
    ("Multiplicative fusion  sᵛ · sᵗ  — a soft logical AND: both conditions must "
     "hold simultaneously", {"bold": True}),
], top=Inches(5.15), size=15, gap=5)

# =========================================================
# 10 — score normalisation & Harris
# =========================================================
s = new_slide("Score normalisation and the Harris criterion", notes=(
    "1:00 — Raw branch scores live on different scales; min-normalisation (s_min "
    "estimated once, offline) rescales each, negative residuals clamped to zero. "
    "Fusion adds a Harris-inspired penalty: candidates strong in ONE modality only — "
    "exactly the benchmark's curated negatives — are suppressed, analogous to the "
    "corner detector penalising single-direction responses. λ fixed across all "
    "experiments."))
txt(s, Inches(0.68), Inches(1.5), Inches(4.8), Inches(0.7),
    "1.  Per-branch min-normalisation, negative residuals clamped:",
    size=15, bold=True)
add_pic(s, IMG["eq_minnorm"], Inches(0.8), Inches(2.25), Inches(4.3), Inches(0.8))
txt(s, Inches(0.68), Inches(3.25), Inches(4.8), Inches(0.7),
    "2.  Harris-inspired fusion — a product with a single-modality penalty:",
    size=15, bold=True)
add_pic(s, IMG["eq_harris"], Inches(0.8), Inches(4.05), Inches(4.3), Inches(0.85))
add_pic(s, IMG["harris"], Inches(5.35), Inches(1.7), Inches(4.15), Inches(3.4))
bullets(s, [
    ("The penalty suppresses candidates that excel in one modality but are mediocre "
     "in the other — precisely the benchmark's designed negatives", {}),
], top=Inches(5.35), size=15, gap=4)

# =========================================================
# 11 — hinge
# =========================================================
s = new_slide("The structural limitation — and the proposal", notes=(
    "1:20 — THE slide of the talk; slow down. Both branches are strictly unimodal: no "
    "component ever reads image and text jointly, so compositional semantics are "
    "inaccessible — 'as a painting' vs 'next to a painting' produce identical branch "
    "scores. Proposal: a multimodal LLM reads the composed query and generates a "
    "caption of the imagined target; embedded with the same frozen text encoder, it "
    "becomes a third multiplicative branch. This is the thesis title in one line."))
txt(s, Inches(0.68), Inches(1.5), Inches(8.6), Inches(0.75),
    "In BASIC, no component ever reads the query image and the query text together.",
    size=18, bold=True, color=RED)
bullets(s, [
    ("Both branches are unimodal, so the composition “this object” × “this "
     "transformation” is never modelled — “as a painting” and “next to a painting” "
     "demand different targets, yet each branch sees only its half of the query", {}),
], top=Inches(2.3), size=15, gap=5)
# proposal motif — one aligned row
MY, MH = Inches(3.85), Inches(1.5)
add_pic(s, IMG["ref"], Inches(0.68), MY, Inches(1.5), MH)
card(s, Inches(2.28), MY + Inches(0.2), Inches(1.6), Inches(1.1),
     text="“placed around\na table”", size=12, italic=True, color=BLUE)
arrow(s, Inches(3.98), MY + Inches(0.54), Inches(0.5))
card(s, Inches(4.58), MY + Inches(0.2), Inches(1.5), Inches(1.1), fill=ROSE,
     text="multimodal\nLLM", size=13, bold=True)
arrow(s, Inches(6.18), MY + Inches(0.54), Inches(0.5))
card(s, Inches(6.78), MY, Inches(2.55), MH,
     text="“White metallic chair with scrolled armrests placed around a table.”",
     size=11.5, italic=True, align=PP_ALIGN.LEFT)
txt(s, Inches(0.68), MY + MH + Inches(0.08), Inches(3.2), Inches(0.35),
    "query image  +  query text", size=12, color=MUTED, align=PP_ALIGN.CENTER)
txt(s, Inches(6.78), MY + MH + Inches(0.08), Inches(2.55), Inches(0.35),
    "caption of the imagined target", size=12, color=MUTED,
    align=PP_ALIGN.CENTER)
txt(s, Inches(2.3), Inches(6.2), Inches(2.2), Inches(0.5),
    "third scoring branch:", size=14, bold=True, color=INK)
add_pic(s, IMG["eq_triplet"], Inches(4.55), Inches(6.1), Inches(3.0), Inches(0.7))

# =========================================================
# 12 — caption generation
# =========================================================
s = new_slide("Target-caption generation", notes=(
    "1:10 — Captioner: InternVL 3.5 (8B), frozen; conditioned on the query image and "
    "the query text; instructed to describe the target. Five instruction strategies "
    "yield five diverse captions per query (two shown, for our chair example). "
    "Caption embedded by the SAME frozen text encoder — zero-shot preserved, nothing "
    "trained."))
bullets(s, [
    ("Captioner: InternVL 3.5 (8B), frozen — conditioned on the query image and the "
     "query text", {}),
    ("The instruction matters: five prompting strategies produce five diverse "
     "captions per query", {}),
    ("adaptive precision · constraint-priority · anti-noise contract · slot-fill "
     "template · draft–refine", {"indent": True, "size": 14, "color": MUTED}),
    ("The caption is embedded by the same frozen text encoder and scored like any "
     "text — the pipeline remains fully zero-shot", {"bold": True}),
], top=Inches(1.55), size=16, gap=7)
add_pic(s, IMG["ref"], Inches(0.68), Inches(4.2), Inches(1.6), Inches(1.35))
card(s, Inches(0.68), Inches(5.7), Inches(1.6), Inches(0.8),
     text="“placed around\na table”", size=11, italic=True, color=BLUE)
for i, (tag, cap) in enumerate([
        ("draft–refine", "“White metallic chair with scrolled armrests placed "
                         "around a table.”"),
        ("constraint-priority", "“A white metal chair with scrolled armrests and "
                                "vertical back bars, placed around a table.”")]):
    c = card(s, Inches(2.6), Inches(4.2 + i * 1.15), Inches(6.7), Inches(1.02),
             text=f"{tag}:", size=11, bold=True, color=RED, align=PP_ALIGN.LEFT)
    p2 = c.text_frame.add_paragraph()
    p2.text = cap
    style_runs(p2, 11.5, italic=True, color=INK)
txt(s, Inches(2.6), Inches(6.55), Inches(6.7), Inches(0.4),
    "… three further strategies on the backup slide", size=11, color=MUTED)

# =========================================================
# 13 — effect of captions
# =========================================================
s = new_slide("Effect of the caption branch", notes=(
    "0:50 — CLIP ViT-L/14, raw similarity products, before any post-processing "
    "(runs/final_experiments/ablation_clip_l, product rung; micro-mAP from per-query "
    "files). One caption: +5.9 macro. Averaging five: +7.5 — and no prompt selection "
    "on the evaluation set."))
table(s, [
    ("configuration", "macro-mAP", "mAP (micro)"),
    ("img × txt   (BASIC baseline, no caption)", "17.95", "21.85"),
    ("img × txt × caption   (single, draft–refine)", "23.83", "29.46"),
    ("img × txt × caption   (5 captions, averaged)", "25.41", "30.79"),
], Inches(1.0), Inches(1.7), Inches(8.0), row_h=0.55, size=15,
      highlight_rows={3})
txt(s, Inches(1.0), Inches(4.1), Inches(8.0), Inches(0.4),
    "CLIP ViT-L/14 · raw similarity product · no post-processing",
    size=12, color=MUTED, align=PP_ALIGN.CENTER)
bullets(s, [
    ("A single generated caption adds +5.9 macro-mAP (+33% relative) — the largest "
     "single contribution in this work", {}),
    ("Averaging the five instruction variants outperforms any individual prompt and "
     "requires no prompt selection", {}),
], top=Inches(4.7), size=16, gap=7)
takeaway(s, "The joint image–text reading that BASIC lacks is worth +7.5 macro-mAP on its own.",
         Inches(6.2))

# =========================================================
# 14 — centering
# =========================================================
s = new_slide("Post-processing I — centering", notes=(
    "1:00 — VLM embeddings are anisotropic: a large shared component (generic "
    "visual/linguistic statistics) inflates ALL similarities. Centering subtracts a "
    "precomputed corpus mean and re-normalises; computed once offline, zero query-time "
    "cost. Numbers: runs/final_experiments/ablation_clip_l and siglip2_ladder run "
    "summaries — same provenance as every other slide. Honest nuance: with the caption "
    "branch the gain shrinks (CLIP-L +6.5) and on SigLIP2 vanishes at this rung "
    "(−0.6, recovered later in the ladder): the caption already supplies part of the "
    "distinctive signal centering is meant to isolate."))
add_pic(s, IMG["eq_centering"], Inches(0.85), Inches(1.65), Inches(3.4), Inches(0.95))
bullets(s, [
    ("VLM embedding spaces are anisotropic: a shared, uninformative component "
     "inflates every similarity score", {}),
    ("Subtracting a precomputed mean μ isolates the distinctive part of each "
     "embedding — computed once, no query-time cost", {}),
], left=Inches(4.55), top=Inches(1.55), w=Inches(4.85), size=14, gap=6)
table(s, [
    ("pipeline", "raw", "+ centering", "Δ"),
    ("img × txt — CLIP-L", "17.95", "27.76", "+9.8"),
    ("img × txt × caption — CLIP-L", "25.41", "31.87", "+6.5"),
    ("img × txt — SigLIP2", "38.12", "49.96", "+11.8"),
    ("img × txt × caption — SigLIP2", "56.09", "55.51", "−0.6"),
], Inches(1.0), Inches(3.35), Inches(8.0), row_h=0.48, size=13)
txt(s, Inches(1.0), Inches(5.9), Inches(8.0), Inches(0.35),
    "macro-mAP · caption = 5-caption average", size=12, color=MUTED,
    align=PP_ALIGN.CENTER)
txt(s, Inches(0.85), Inches(6.3), Inches(8.3), Inches(0.75),
    "Large gains for the duplet; smaller with the caption branch — the caption "
    "already supplies part of the distinctive signal.", size=14, italic=True,
    color=MUTED, align=PP_ALIGN.CENTER)

# =========================================================
# =========================================================
# 15 — contextualization
# =========================================================
s = new_slide("Post-processing II — text contextualization", notes=(
    "0:50 — Bare fragments ('during sunset') are out-of-distribution for a text "
    "encoder trained on full captions. BASIC wraps the modification in object nouns "
    "drawn from a corpus, embeds all phrases, centers and averages them. Largest "
    "post-processing gain, on every backbone; numbers are the +Harris → +context "
    "rung of the ladder."))
bullets(s, [
    ("The text encoder is trained on full captions; terse fragments such as "
     "“during sunset” are out-of-distribution", {}),
    ("Contextualization wraps the modification in object nouns (“dog during sunset”, "
     "“sunset dog”, …), embeds all variants, and averages them", {}),
    ("The single largest post-processing gain — on every backbone", {"bold": True}),
], top=Inches(1.55), size=16, gap=7)
table(s, [
    ("pipeline", "before (+ Harris)", "after (+ context)", "Δ"),
    ("img × txt — CLIP-L", "28.33", "32.25", "+3.9"),
    ("img × txt × caption — CLIP-L", "32.82", "35.76", "+2.9"),
    ("img × txt — SigLIP2", "47.64", "57.69", "+10.1"),
    ("img × txt × caption — SigLIP2", "55.87", "61.98", "+6.1"),
], Inches(1.0), Inches(3.8), Inches(8.0), row_h=0.48, size=13)
txt(s, Inches(1.0), Inches(6.3), Inches(8.0), Inches(0.35),
    "macro-mAP · caption = 5-caption average", size=12, color=MUTED,
    align=PP_ALIGN.CENTER)

# =========================================================
# 16 — full ladder CLIP-L
# =========================================================
s = new_slide("The full post-processing ladder (CLIP-L)", notes=(
    "1:00 — All rungs cumulatively, both pipelines (docs/final_ablation_clip_l.csv). "
    "Projection and query expansion were tuned for raw CLIP features: with the "
    "caption branch present they consistently reduce performance (for BASIC alone "
    "+proj is marginally above +context, 32.48 vs 32.25). The proposed pipeline "
    "therefore stops at contextualization — selective adoption is itself a finding."))
add_pic(s, IMG["ladder_l"], Inches(0.55), Inches(1.55), Inches(8.9), Inches(4.4))
takeaway(s, "Adopt what stacks, drop what doesn't: the pipeline ends at + context.",
         Inches(6.2))

# =========================================================
# 17 — backbones
# =========================================================
s = new_slide("Backbone study — does the caption branch transfer?", notes=(
    "0:50 — Same pipeline, four frozen dual encoders, raw products "
    "(docs/backbone_recall.csv). The caption branch improves every backbone; SigLIP-L "
    "doubles (21→43). SigLIP2 (sigmoid contrastive loss, improved recipe) is the "
    "strongest base model. One sentence on SigLIP: same dual-encoder family, newer "
    "training objective."))
add_pic(s, IMG["backbones"], Inches(0.55), Inches(1.55), Inches(8.9), Inches(4.4))
takeaway(s, "Backbone-agnostic: the caption branch improves every dual encoder tested.",
         Inches(6.2))

# =========================================================
# 18 — final results
# =========================================================
s = new_slide("Final results — SigLIP2", notes=(
    "1:10 — Best backbone, full ladder (runs/caption_backbone_instancepool/"
    "siglip2_ladder/summary_ladder.csv). Same qualitative shape: peak at +context, "
    "proj/QE detrimental. Headline: 61.98 macro-mAP zero-shot vs 57.69 for BASIC at "
    "its own best rung (+4.3) — and vs 38.1 for the raw product. Reproduction-gap "
    "question → backup."))
add_pic(s, IMG["ladder_s2"], Inches(0.55), Inches(1.55), Inches(8.9), Inches(4.4))
takeaway(s, "61.98 macro-mAP, fully zero-shot — +4.3 over BASIC's best configuration.",
         Inches(6.2))

# =========================================================
# 18b — the best overall system
# =========================================================
s = new_slide("Our best overall system", notes=(
    "0:40 — One slide, one recipe: SigLIP2 backbone + InternVL captions (five "
    "instruction strategies, averaged) + centering and contextualization, nothing "
    "after. 61.98 macro-mAP / 62.07 micro-mAP, all components frozen. +4.3 over the "
    "strongest BASIC configuration and +23.9 over the raw img × txt product on the "
    "same backbone."))
recipe = [("backbone", "SigLIP2\n(frozen dual encoder)"),
          ("caption branch", "InternVL 8B\n5 captions, averaged"),
          ("post-processing", "centering\n+ contextualization")]
for i, (lab, val) in enumerate(recipe):
    c = card(s, Inches(0.75 + i * 2.95), Inches(1.75), Inches(2.7), Inches(1.45),
             text=lab, size=12, color=MUTED)
    for ln in val.split("\n"):
        p2 = c.text_frame.add_paragraph()
        p2.text = ln
        p2.alignment = PP_ALIGN.CENTER
        style_runs(p2, 15, bold=True, color=INK)
    if i < 2:
        txt(s, Inches(3.42 + i * 2.95), Inches(2.2), Inches(0.4), Inches(0.5),
            "+", size=24, bold=True, color=RED, align=PP_ALIGN.CENTER)
big = card(s, Inches(2.3), Inches(3.7), Inches(5.4), Inches(1.7), fill=ROSE,
           line=None, text="61.98", size=48, bold=True, color=RED)
p2 = big.text_frame.add_paragraph()
p2.text = "macro-mAP · fully zero-shot"
p2.alignment = PP_ALIGN.CENTER
style_runs(p2, 14, color=MUTED)
bullets(s, [
    ("+4.3 over the strongest BASIC configuration (57.69) — after all of its "
     "post-processing", {}),
    ("+23.9 over the raw img × txt product on the same backbone (38.12)", {}),
], top=Inches(5.75), size=16, gap=6)

# =========================================================
# 19 — qualitative success
# =========================================================
s = new_slide("Qualitative — where the caption wins", notes=(
    "0:45 (flex) — Pink pencil case, 'without sticky paper notes but filled with pens "
    "and markers'. Image-only similarity retrieves lookalikes; the caption resolves "
    "the NEGATION and the required content, placing both ground truths at the top "
    "(AP 15 → 42 → 100)."))
add_pic(s, IMG["success"], Inches(0.55), Inches(1.5), Inches(8.9), Inches(5.55))

# =========================================================
# 20 — qualitative failure
# =========================================================
s = new_slide("Qualitative — characteristic failure", notes=(
    "0:45 (flex) — Mask of Agamemnon, 'as a painting'. The target is an abstract "
    "painting, visually remote from the query image; every pipeline returns real masks. "
    "When the modification demands a drastic domain shift, the visual branch "
    "dominates the product. Honest diagnosis — sets up future work."))
add_pic(s, IMG["failure"], Inches(0.55), Inches(1.5), Inches(8.9), Inches(4.65))
takeaway(s, "Failure mode: under drastic domain shifts, visual identity overpowers the modification.",
         Inches(6.35))

# =========================================================
# 21 — limitations & future work
# =========================================================
s = new_slide("Limitations and future work", notes=(
    "0:40 — Latency: caption generation ≈ 15 s/query, 99.7% of online inference "
    "(Appendix C). Fusion: fixed product cannot re-weight branches per query. Prompt "
    "sensitivity: averaging mitigates, does not remove. Future: distilled/quantised "
    "captioners; query-adaptive fusion; category-level transfer."))
bullets(s, [
    ("Inference cost — caption generation dominates (≈ 15 s per query, 99.7% of "
     "online latency); ranking itself is instantaneous", {}),
    ("Fusion rigidity — the fixed product cannot down-weight the visual branch when "
     "the modification demands a domain shift", {}),
    ("Prompt sensitivity — five-caption averaging mitigates but does not remove "
     "dependence on instruction design", {}),
    ("Future work", {"bold": True}),
    ("distilled or quantised captioners for interactive latency", {"indent": True, "size": 15}),
    ("query-adaptive fusion in place of the fixed product", {"indent": True, "size": 15}),
    ("transfer of the caption branch to category-level CIR benchmarks", {"indent": True, "size": 15}),
], top=Inches(1.7), size=17, gap=9)

# =========================================================
# 22 — conclusions
# =========================================================
s = new_slide("Conclusions", notes=(
    "0:40 — Three contributions, mirroring the narrative: (1) zero-shot instance-level "
    "CIR is viable at 752k scale; (2) MLLM target captions supply the missing joint "
    "image–text reading — largest single gain, transfers across all four backbones; "
    "(3) 61.98 macro-mAP with disciplined post-processing, +4.3 over BASIC's best. "
    "Thank the committee."))
bullets(s, [
    ("A frozen, fully zero-shot pipeline retrieves specific object instances among "
     "752,092 images from an image + a sentence", {}),
    ("MLLM-generated target captions supply the joint image–text reading that "
     "dual-encoder pipelines structurally lack — the largest single gain "
     "(+7.5 macro-mAP on CLIP-L), consistent across all four backbones", {"bold": True}),
    ("With centering and contextualization — and dropping the steps that stop "
     "helping — the system reaches 61.98 macro-mAP, +4.3 over the strongest BASIC "
     "configuration", {}),
], top=Inches(1.7), size=17, gap=10)

# =========================================================
# thank-you slide (full-bleed red)
# =========================================================
s = new_slide("")
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width,
                        prs.slide_height)
bg.fill.solid(); bg.fill.fore_color.rgb = RED
bg.line.fill.background()
tf = bg.text_frame
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
p = tf.paragraphs[0]
p.text = "Thank you!"
p.alignment = PP_ALIGN.CENTER
style_runs(p, 54, bold=True, color=WHITE)
s.notes_slide.notes_text_frame.text = "Thank the committee; open for questions."

# =========================================================
# backups
# =========================================================
s = new_slide("Backup — full CLIP-L ablation", notes=(
    "Paper: Psomas et al.; Reproduced: our re-run of the released code; last column: "
    "our caption pipeline (5-caption average)."))
table(s, [
    ("configuration", "paper", "reproduced", "× caption (avg-5)"),
    ("img × txt product", "17.48", "17.95", "25.41"),
    ("+ centering", "28.33", "27.76", "31.87"),
    ("+ sim-normalisation", "—", "27.40", "31.97"),
    ("+ Harris criterion", "—", "28.33", "32.82"),
    ("+ contextualization", "33.48", "32.25", "35.76"),
    ("+ projection", "34.35", "32.48", "33.80"),
    ("+ query expansion", "—", "30.28", "32.39"),
], Inches(1.0), Inches(1.7), Inches(8.0), row_h=0.52, size=14,
      highlight_rows={5})
txt(s, Inches(1.0), Inches(5.95), Inches(8.0), Inches(0.4),
    "macro-mAP · full i-CIR · CLIP ViT-L/14", size=12, color=MUTED,
    align=PP_ALIGN.CENTER)

s = new_slide("Backup — reproducing BASIC", notes="Reproduction-gap details.")
bullets(s, [
    "Paper's best (CLIP-L, + projection): 34.35 macro-mAP; our re-run of the released code: 32.48",
    "Contextualization draws fresh object nouns per query — small run-to-run variance",
    ("Residual gap concentrated in the image branch: features re-extracted in a newer "
     "software stack (image decoding/resizing differ across library versions; database "
     "re-download quality)", {}),
    ("Both methods are evaluated in the same environment — relative comparisons are "
     "unaffected", {"bold": True}),
], top=Inches(1.8), size=16, gap=9)

s = new_slide("Backup — online inference latency", notes=(
    "runs/inference_time/summary.csv — 100 queries, RTX-6000-Ada 48 GB, K=5 captions."))
bullets(s, [
    "Per-query online inference: median ≈ 14.75 s (min 10.2, max 21.4), backbone-independent",
    "Caption generation ≈ 99.7% of latency; triplet embedding: 22 ms (CLIP-L) / 46 ms (SigLIP2)",
    "Database embeddings are precomputed offline; ranking itself is instantaneous",
    "Levers: fewer captions K, shorter generations, smaller / quantised MLLM, batched decoding",
], top=Inches(1.8), size=16, gap=9)

s = new_slide("Backup — the five caption instructions",
              notes="Chair example, all five (InternVL, INSTR F–J).")
add_pic(s, IMG["ref"], Inches(0.68), Inches(1.7), Inches(2.0), Inches(1.7))
txt(s, Inches(0.68), Inches(3.55), Inches(2.0), Inches(0.6),
    "“placed around a table”", size=12, italic=True, color=BLUE,
    align=PP_ALIGN.CENTER)
caps = [("adaptive precision", "A metallic chair with ornate details, placed around a table."),
        ("constraint-priority", "A white metal chair with scrolled armrests and vertical back bars, placed around a table."),
        ("anti-noise contract", "White metal chair with scrolled armrests and vertical back bars placed around a table."),
        ("slot-fill template", "a white metal chair with ornate back, scrolled armrests, and four legs placed around a table."),
        ("draft–refine", "White metallic chair with scrolled armrests placed around a table.")]
for i, (tag, cap) in enumerate(caps):
    card(s, Inches(3.0), Inches(1.6 + i * 1.05), Inches(6.4), Inches(0.95),
         text=f"{tag}:  “{cap}”", size=11, align=PP_ALIGN.LEFT)

prs.save(OUT)
print("saved", OUT, "slides:", len(prs.slides._sldIdLst))
