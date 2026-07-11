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
    "ref": f"{ASSETS}/chair_ref.jpg",
    "top1": f"{ASSETS}/chair_set.jpg",
    "tintin_q": f"{FIG}/caption_example_samples/ref.jpg",
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
    "1:00 — Running example: you have seen a chair you like and want the same chair, "
    "but as a set around a table. Query = the chair image + 'placed around a table'; "
    "target = that exact chair, arranged as a dining set. The two modalities are "
    "complementary: the image fixes WHAT (this specific chair), the text specifies the "
    "TRANSFORMATION (as a set around a table). Applications: product search, archive "
    "exploration, digital asset management."))
Y, BH = Inches(1.75), Inches(2.15)
add_pic(s, IMG["ref"], Inches(0.68), Y, Inches(2.3), BH)
txt(s, Inches(3.05), Y, Inches(0.4), BH, "+", size=32, bold=True,
    align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
card(s, Inches(3.5), Inches(2.35), Inches(2.0), Inches(1.0),
     text="“placed around\na table”", size=14, italic=True, color=BLUE)
arrow(s, Inches(5.65), Inches(2.6), Inches(0.65))
add_pic(s, IMG["top1"], Inches(6.5), Y, Inches(2.3), BH)
txt(s, Inches(0.68), Inches(3.95), Inches(2.3), Inches(0.35), "reference image",
    size=12, color=MUTED, align=PP_ALIGN.CENTER)
txt(s, Inches(3.5), Inches(3.45), Inches(2.0), Inches(0.35), "modification text",
    size=12, color=MUTED, align=PP_ALIGN.CENTER)
txt(s, Inches(6.5), Inches(3.95), Inches(2.3), Inches(0.35), "target image",
    size=12, color=MUTED, align=PP_ALIGN.CENTER)
bullets(s, [
    "The query is a pair: a reference image and a modification text — “this, but changed as described”",
    "The two modalities are complementary: the image fixes the subject, the text specifies its transformation",
    "Neither modality alone can express the information need — composition is essential",
], top=Inches(4.55), size=16, gap=6)
takeaway(s, "Retrieval conditioned jointly on visual content and a textual modification.",
         Inches(6.45))

# =========================================================
# 3 — Instance-level CIR
# =========================================================
s = new_slide("From categories to instances", notes=(
    "0:50 — Same query, two regimes. Category-level: any chair around a table "
    "satisfies the query — all four results count. Instance-level: only THIS chair "
    "counts; the three other chair sets are hard negatives. Identity must be preserved "
    "under the modification. Category-level methods have no mechanism for this."))
add_pic(s, IMG["inst_cat"], Inches(0.55), Inches(1.5), Inches(8.9), Inches(3.85))
bullets(s, [
    ("Category-level CIR:  any instance of the class satisfies the query", {}),
    ("Instance-level CIR:  the retrieved object must preserve the identity of the "
     "reference — under changes of medium, material, viewpoint, and context",
     {"bold": True}),
], top=Inches(5.45), size=16, gap=6)

# =========================================================
# 4 — the i-CIR benchmark
# =========================================================
s = new_slide("The i-CIR benchmark — query structure", notes=(
    "1:20 — Walk the tintin instance: 1 reference image, 5 modification texts = 5 "
    "composed queries. Each query has MULTIPLE ground truths (3–14 here, green "
    "badges). Hard negatives are curated per instance (5,128 for tintin): statues of "
    "other characters, other rooftop signs, other cartoon t-shirts — designed so that "
    "single-modality shortcuts fail. Psomas et al., 2025."))
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
    "0:40 — 1,883 queries over 202 instances (median 6 per instance), searched among "
    "752,092 database images. Histograms: queries per instance, positives per query, "
    "pool sizes. Needle-in-a-haystack regime: positives are a vanishing fraction of "
    "the database."))
add_pic(s, IMG["stats"], Inches(0.55), Inches(1.5), Inches(8.9), Inches(3.8))
stats = [("202", "object instances"), ("1,883", "composed queries"),
         ("6", "median queries / instance"), ("752,092", "database images")]
for i, (num, lab) in enumerate(stats):
    c = card(s, Inches(0.55 + i * 2.28), Inches(5.55), Inches(2.08), Inches(1.0),
             text=num, size=22, bold=True, color=RED)
    p2 = c.text_frame.add_paragraph()
    p2.text = lab
    p2.alignment = PP_ALIGN.CENTER
    style_runs(p2, 12, color=MUTED)

# =========================================================
# 6 — problem formulation
# =========================================================
s = new_slide("Problem formulation — a zero-shot setting", notes=(
    "1:00 — Formalise: rank the whole database by a scoring function conditioned on "
    "the composed query. Why zero-shot: (i) no training triplets exist at instance "
    "level; (ii) supervised fusion models inherit their training distribution — each "
    "new instance would need new data; (iii) zero-shot generalises immediately. "
    "Verbally place related work: supervised combiner networks (CIRR/FashionIQ) and "
    "zero-shot textual-inversion methods (Pic2Word, SEARLE) address category-level "
    "CIR — that literature motivates but does not solve the instance-level setting."))
add_pic(s, IMG["eq_problem"], Inches(0.9), Inches(1.6), Inches(8.2), Inches(0.85))
bullets(s, [
    ("Open-set retrieval: rank the entire database by a scoring function "
     "s(x | Iᵧ, tᵧ) — no candidate shortlist, no per-instance classifier", {}),
    ("Supervision is neither available nor scalable: labelled (image, text, target) "
     "triplets do not exist for these instances, and every newly added object would "
     "require new annotation", {}),
    ("Zero-shot constraint adopted throughout: frozen pre-trained models only — no "
     "learned parameters, no fine-tuning", {"bold": True}),
    ("Prior CIR work — supervised combiner networks and zero-shot textual "
     "inversion — targets the category regime; neither preserves instance "
     "identity for unseen objects", {}),
], top=Inches(2.7), size=16, gap=9)

# =========================================================
# 7 — evaluation
# =========================================================
s = new_slide("Evaluation protocol", notes=(
    "1:00 — AP integrates the precision–recall curve of one ranked list; mAP averages "
    "over queries; macro-mAP averages per instance first, so query-rich instances do "
    "not dominate — the benchmark's primary metric."))
pos = {0, 2, 5}
for i in range(8):
    card(s, Inches(0.75 + i * 0.72), Inches(1.55), Inches(0.6), Inches(0.6),
         text="✓" if i in pos else "",
         fill=RGBColor(0x0C, 0xA3, 0x0C) if i in pos else LIGHT,
         line=None, size=18, bold=True, color=WHITE)
txt(s, Inches(6.7), Inches(1.62), Inches(2.7), Inches(0.5),
    "ranked list (green = ground truth)", size=12, color=MUTED)
rows = [("eq_ap", "Average precision — the area under one query's precision–recall curve"),
        ("eq_map", "mAP — every query weighted equally"),
        ("eq_mmap", "macro-mAP — every instance weighted equally; the primary metric")]
y = Inches(2.45)
for eq, lab in rows:
    add_pic(s, IMG[eq], Inches(0.75), y, Inches(4.5), Inches(0.95))
    txt(s, Inches(5.5), y + Inches(0.18), Inches(3.9), Inches(0.85), lab,
        size=14, color=INK)
    y += Inches(1.15)

# =========================================================
# 8 — VLMs / CLIP
# =========================================================
s = new_slide("Vision–language models: a shared embedding space", notes=(
    "1:20 — Dual-encoder architecture, contrastively pre-trained on 400M pairs: "
    "matching image–caption pairs are pulled together in a common vector space. "
    "Consequence: image–text relevance reduces to cosine similarity of two "
    "embeddings. Baseline backbone: CLIP ViT-L/14, frozen. This is the slide the "
    "non-CV committee must retain."))
add_pic(s, IMG["clip"], Inches(0.55), Inches(1.5), Inches(8.9), Inches(3.5))
bullets(s, [
    "Dual encoder: images and sentences are mapped into one common vector space",
    "Contrastive pre-training on 400M web image–caption pairs (CLIP; Radford et al., 2021)",
    ("Cross-modal relevance = cosine similarity of two embeddings — computable for "
     "any image against any sentence", {"bold": True}),
    "Baseline backbone in this work: CLIP ViT-L/14, frozen",
], top=Inches(5.15), size=15, gap=5)

# =========================================================
# 9 — BASIC
# =========================================================
s = new_slide("The BASIC method (Psomas et al., 2025)", notes=(
    "1:20 — The benchmark's zero-shot reference method, our baseline. Two unimodal "
    "branches score every database image independently: visual similarity to the "
    "reference; textual similarity to the modification. Branch-specific "
    "post-processing (walk the figure at high level), then multiplicative fusion — a "
    "soft conjunction, which is what composed queries demand."))
add_pic(s, IMG["basic"], Inches(0.55), Inches(1.5), Inches(8.9), Inches(3.55))
bullets(s, [
    ("Image branch  sᵛ(x): visual similarity between database image and the reference", {}),
    ("Text branch  sᵗ(x): similarity between database image and the modification text", {}),
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
    "In BASIC, no component ever reads the reference image and the modification text together.",
    size=18, bold=True, color=RED)
bullets(s, [
    ("Both branches are unimodal, so the composition “this object” × “this "
     "transformation” is never modelled — “as a painting” and “next to a painting” "
     "demand different targets, yet each branch sees only its half of the query", {}),
], top=Inches(2.3), size=15, gap=5)
add_pic(s, IMG["tintin_q"], Inches(0.68), Inches(3.7), Inches(1.55), Inches(1.3))
card(s, Inches(0.68), Inches(5.15), Inches(1.55), Inches(0.85),
     text="“as an iconic\nrooftop sign”", size=11, italic=True, color=BLUE)
arrow(s, Inches(2.4), Inches(4.45), Inches(0.5))
card(s, Inches(3.05), Inches(4.2), Inches(1.85), Inches(1.0), fill=ROSE,
     text="multimodal LLM\n(reads both)", size=13, bold=True)
arrow(s, Inches(5.05), Inches(4.45), Inches(0.5))
card(s, Inches(5.7), Inches(4.05), Inches(3.6), Inches(1.3),
     text="“Cartoon character in a beige coat and blue shirt appears as an "
          "iconic rooftop sign.”", size=12, italic=True, align=PP_ALIGN.LEFT)
txt(s, Inches(5.7), Inches(5.4), Inches(3.6), Inches(0.4),
    "a caption of the imagined target", size=12, color=MUTED,
    align=PP_ALIGN.CENTER)
txt(s, Inches(0.68), Inches(6.15), Inches(2.2), Inches(0.5),
    "third branch:", size=14, bold=True, color=INK)
add_pic(s, IMG["eq_triplet"], Inches(2.6), Inches(6.05), Inches(3.2), Inches(0.7))

# =========================================================
# 12 — caption generation
# =========================================================
s = new_slide("Target-caption generation", notes=(
    "1:10 — Captioner: InternVL 3.5 (8B), frozen; conditioned on reference image + "
    "modification; instructed to describe the target. Five instruction strategies "
    "yield five diverse captions per query. Caption embedded by the SAME frozen text "
    "encoder — zero-shot preserved, nothing trained."))
bullets(s, [
    ("Captioner: InternVL 3.5 (8B), frozen — conditioned on the reference image and "
     "the modification text", {}),
    ("The instruction matters: five prompting strategies produce five diverse "
     "captions per query", {}),
    ("adaptive precision · constraint-priority · anti-noise contract · slot-fill "
     "template · draft–refine", {"indent": True, "size": 14, "color": MUTED}),
    ("The caption is embedded by the same frozen text encoder and scored like any "
     "text — the pipeline remains fully zero-shot", {"bold": True}),
], top=Inches(1.55), size=16, gap=7)
add_pic(s, IMG["tintin_q"], Inches(0.68), Inches(4.2), Inches(1.6), Inches(1.35))
card(s, Inches(0.68), Inches(5.7), Inches(1.6), Inches(0.8),
     text="“as an iconic\nrooftop sign”", size=11, italic=True, color=BLUE)
for i, (tag, cap) in enumerate([
        ("draft–refine", "“Cartoon character in a beige coat and blue shirt appears "
                         "as an iconic rooftop sign.”"),
        ("constraint-priority", "“A character wearing a trench coat, blonde hair, and "
                                "a blue shirt, is an iconic rooftop sign.”")]):
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
    "painting, visually remote from the reference; every pipeline returns real masks. "
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
txt(s, Inches(0.68), Inches(5.5), Inches(8.6), Inches(0.7), "Thank you.",
    size=30, bold=True, color=RED, align=PP_ALIGN.CENTER)

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

s = new_slide("Backup — the five caption instructions", notes="Tintin example, all five.")
add_pic(s, IMG["tintin_q"], Inches(0.68), Inches(1.7), Inches(2.0), Inches(1.7))
txt(s, Inches(0.68), Inches(3.55), Inches(2.0), Inches(0.6),
    "“as an iconic rooftop sign”", size=12, italic=True, color=BLUE,
    align=PP_ALIGN.CENTER)
caps = [("A · adaptive precision", "A character with a beige coat and blue shirt, as an iconic rooftop sign"),
        ("B · constraint-priority", "A character wearing a trench coat, blonde hair, and a blue shirt, is an iconic rooftop sign."),
        ("C · anti-noise contract", "Character in a beige trench coat, blue shirt, with blushing cheeks and short orange hair as an iconic rooftop sign."),
        ("D · slot-fill template", "a cartoon character wearing a trench coat, blushing, with short hair as an iconic rooftop sign."),
        ("E · draft–refine", "Cartoon character in a beige coat and blue shirt appears as an iconic rooftop sign.")]
for i, (tag, cap) in enumerate(caps):
    card(s, Inches(3.0), Inches(1.6 + i * 1.05), Inches(6.4), Inches(0.95),
         text=f"{tag}:  “{cap}”", size=11, align=PP_ALIGN.LEFT)

prs.save(OUT)
print("saved", OUT, "slides:", len(prs.slides._sldIdLst))
