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
RED = RGBColor(0x9B, 0x00, 0x13)
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
    "pipeline": f"{ASSETS}/pipeline_overview.png",
    "clip_siglip": f"{ASSETS}/clip_vs_siglip.png",
    "qual_success": f"{ASSETS}/qual_tintin_success_q1782.png",
    "qual_failure": f"{ASSETS}/qual_tintin_failure_q1779.png",
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
        style_runs(p, 25, bold=True, color=WHITE)   # red banner -> white title
    clean_placeholders(slide)
    if notes:
        slide.notes_slide.notes_text_frame.text = notes
    n = len(prs.slides._sldIdLst)
    txt(slide, Inches(8.9), Inches(6.94), Inches(0.75), Inches(0.32), str(n),
        size=12, bold=True, color=WHITE, align=PP_ALIGN.RIGHT)   # white on footer band
    return slide

def bullets(slide, items, left=Inches(0.68), top=Inches(1.55), w=Inches(8.6),
            size=17, gap=8):
    h = Inches(6.75) - top
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
    "Good morning everyone, and thank you for being here.")
sldIdLst = prs.slides._sldIdLst
prs.part.drop_rel(sldIdLst[1].rId)
sldIdLst.remove(sldIdLst[1])

# =========================================================
# 2 — Composed Image Retrieval
# =========================================================
s = new_slide("Composed Image Retrieval", notes=(
    "Imagine that you see a chair online that you really like, but you would like to "
    "find a dining set that includes that same chair design together with a table.\n\n"
    "Searching only with the IMAGE of the chair would mainly return the same chair or "
    "other visually similar chairs. It would not understand that you are looking for "
    "it as part of a dining set.\n\n"
    "On the other hand, searching only for 'a dining table and chairs' would return "
    "many different sets, but probably not the specific chair you selected.\n\n"
    "To express exactly what you are looking for, you need to combine both elements: "
    "the image identifies the chair, while the text describes the context in which you "
    "want to find it.\n\n"
    "This is an example of composed image retrieval, the task I worked on in my "
    "thesis. The query consists of a reference image and a textual modification. The "
    "goal is to retrieve images that preserve the information provided by the "
    "reference image while also satisfying the modification described by the text."))
Y, BH = Inches(1.7), Inches(2.0)
add_pic(s, IMG["ref"], Inches(0.68), Y, Inches(2.5), BH)
txt(s, Inches(3.2), Y, Inches(0.4), BH, "+", size=30, bold=True,
    align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
card(s, Inches(3.6), Inches(2.25), Inches(2.0), Inches(0.9),
     text="“placed around\na table”", size=13, italic=True, color=BLUE)
arrow(s, Inches(5.7), Inches(2.5), Inches(0.6))
add_pic(s, IMG["top1"], Inches(6.4), Y, Inches(2.5), BH)
txt(s, Inches(0.68), Inches(3.75), Inches(2.5), Inches(0.35), "reference image",
    size=12, color=MUTED, align=PP_ALIGN.CENTER)
txt(s, Inches(3.6), Inches(3.25), Inches(2.0), Inches(0.35), "modification text",
    size=12, color=MUTED, align=PP_ALIGN.CENTER)
txt(s, Inches(6.4), Inches(3.75), Inches(2.5), Inches(0.35), "target image",
    size=12, color=MUTED, align=PP_ALIGN.CENTER)
bullets(s, [
    ("Image only  →  the same chair, or visually similar chairs — but not as a dining set", {}),
    ("Text only  →  many dining sets — but not your specific chair", {}),
    ("Both together: the image identifies the object, the text describes the context "
     "in which you want to find it", {"bold": True}),
], top=Inches(4.35), size=16, gap=7)
takeaway(s, "Retrieve images that preserve the reference object and satisfy the modification.",
         Inches(6.15))

# =========================================================
# 3 — instance-level
# =========================================================
s = new_slide("Instance-level composed retrieval", notes=(
    "My thesis focuses specifically on the INSTANCE-LEVEL version of this task.\n\n"
    "In category-level composed image retrieval, any object belonging to the correct "
    "class may satisfy the query. For example, if the query asks for a chair around a "
    "dining table, any suitable chair design might be considered correct.\n\n"
    "In instance-level retrieval, this is not enough. The system must retrieve the "
    "exact same chair shown in the reference image, while also satisfying the textual "
    "modification.\n\n"
    "Therefore, the main challenge is to preserve the identity of a specific object "
    "even when its context, appearance, viewpoint, or visual domain changes."))
add_pic(s, IMG["inst_cat"], Inches(0.55), Inches(1.45), Inches(8.9), Inches(3.9))
bullets(s, [
    ("Category-level:  any object of the correct class may satisfy the query", {}),
    ("Instance-level:  the system must retrieve the exact same object shown in the "
     "reference image, while also satisfying the modification", {"bold": True}),
    ("The challenge: preserve the identity of a specific object even when its context, "
     "appearance, viewpoint, or visual domain changes", {}),
], top=Inches(5.4), size=15, gap=5)

# =========================================================
# 4 — i-CIR query structure (tintin)
# =========================================================
s = new_slide("The i-CIR benchmark", notes=(
    "For our experiments, we use the i-CIR benchmark, which was specifically designed "
    "for instance-level composed image retrieval.\n\n"
    "Each object instance is associated with several composed queries, and every "
    "composed query consists of a reference image and a modification text.\n\n"
    "Each query may also have multiple correct target images — several database images "
    "can correctly depict the same object under the requested modification.\n\n"
    "In addition, each instance has its own database containing carefully curated hard "
    "negatives. These are designed to confuse the retrieval system: some are visually "
    "similar to the reference image but fail to satisfy the modification; others "
    "satisfy the modification but depict a different object instance; some appear to "
    "match both parts partially while still being incorrect.\n\n"
    "This prevents the system from succeeding by relying only on the image or only on "
    "the text."))
add_pic(s, IMG["tintin_fig"], Inches(0.55), Inches(1.45), Inches(8.9), Inches(4.4))
bullets(s, [
    ("Each instance → several composed queries; each query → possibly several correct "
     "targets", {}),
    ("Curated hard negatives per instance: right object / wrong modification, or right "
     "modification / wrong object — succeeding on one modality alone is not enough", {}),
], top=Inches(6.0), size=14, gap=4)

# =========================================================
# 5 — i-CIR scale
# =========================================================
s = new_slide("The i-CIR benchmark — scale", notes=(
    "The scale: a database of 752,092 images, 202 object instances, 1,883 composed "
    "queries, with a median of 6 queries per instance. The histograms show the "
    "distributions — image and text queries per instance, hard negatives per instance, "
    "and positives per composed query."))
stats = [("752,092", "database images"), ("202", "object instances"),
         ("1,883", "composed queries"), ("6", "median queries / instance")]
for i, (num, lab) in enumerate(stats):
    c = card(s, Inches(0.55 + i * 2.28), Inches(1.6), Inches(2.08), Inches(0.95),
             text=num, size=21, bold=True, color=RED)
    p2 = c.text_frame.add_paragraph()
    p2.text = lab
    p2.alignment = PP_ALIGN.CENTER
    style_runs(p2, 11.5, color=MUTED)
add_pic(s, IMG["paper_stats"], Inches(0.55), Inches(2.95), Inches(8.9), Inches(2.6))
txt(s, Inches(0.55), Inches(5.75), Inches(8.9), Inches(0.4),
    "distributions recomputed from the benchmark (cf. Psomas et al., 2025, Fig. 2)",
    size=11, color=MUTED, align=PP_ALIGN.CENTER)

# =========================================================
# 6 — problem formulation / zero-shot
# =========================================================
s = new_slide("Problem formulation — a zero-shot setting", notes=(
    "To summarize the task, we are given a reference image and a modification text, "
    "and we want to retrieve database images that are relevant to both.\n\n"
    "The system assigns a score to every image in the database and ranks the images "
    "from the most relevant to the least relevant.\n\n"
    "In this thesis we adopt a zero-shot setting: we do not train or fine-tune any "
    "model on the i-CIR dataset.\n\n"
    "This choice is important because supervised composed image retrieval requires "
    "labelled triplets consisting of a reference image, a modification text, and a "
    "correct target image. At the instance level, collecting these annotations for "
    "every new object would be expensive and difficult to scale — every newly "
    "introduced object instance could require additional labelled training data.\n\n"
    "Instead, by using frozen pre-trained models, the retrieval system can be applied "
    "directly to previously unseen object instances without additional training."))
add_pic(s, IMG["eq_problem"], Inches(0.9), Inches(1.6), Inches(8.2), Inches(0.8))
bullets(s, [
    ("The system scores every database image and ranks them from most to least "
     "relevant", {}),
    ("Zero-shot: we do not train or fine-tune any model on i-CIR", {"bold": True}),
    ("Supervised CIR needs labelled triplets (reference image, modification text, "
     "target image) — at the instance level, every new object would require new "
     "annotation", {}),
    ("Frozen pre-trained models apply directly to previously unseen object instances", {}),
], top=Inches(2.7), size=16, gap=9)

# =========================================================
# 7 — evaluation metric
# =========================================================
s = new_slide("Evaluation metric", notes=(
    "Since this is a retrieval task, the system assigns a relevance score to every "
    "image in the database. We sort the images by this score, from most to least "
    "relevant. The evaluation checks WHERE the correct target images appear in this "
    "ranked list.\n\n"
    "For a single query we use Average Precision (AP). AP gives a high score when the "
    "correct images appear near the top of the ranking; if they appear much lower, the "
    "score decreases.\n\n"
    "We then compute mean Average Precision (mAP) by averaging AP across all queries.\n\n"
    "However, the number of queries is not the same for every object instance. If we "
    "averaged directly over all queries, instances with more queries would have a "
    "larger influence on the result.\n\n"
    "For this reason our main metric is macro-mAP: we first average the query scores "
    "within each object instance, and then average across all instances — so every "
    "instance contributes equally, regardless of how many queries it has."))
pos = {0, 2, 5}
for i in range(8):
    card(s, Inches(0.75 + i * 0.72), Inches(1.5), Inches(0.6), Inches(0.6),
         text="✓" if i in pos else "",
         fill=RGBColor(0x0C, 0xA3, 0x0C) if i in pos else LIGHT,
         line=None, size=18, bold=True, color=WHITE)
txt(s, Inches(6.7), Inches(1.57), Inches(2.7), Inches(0.5),
    "ranked list (green = correct)", size=12, color=MUTED)
mrows = [
    ("eq_pk", "Precision@k", "fraction of the top-k results that are correct"),
    ("eq_ap", "Average Precision", "high when correct images appear near the top"),
    ("eq_map", "mAP", "AP averaged over all queries"),
    ("eq_mmap", "macro-mAP", "average within each instance, then across instances"),
]
y = Inches(2.35)
for eq, name, desc in mrows:
    b = txt(s, Inches(0.75), y + Inches(0.05), Inches(3.15), Inches(0.9),
            name, size=14, bold=True, color=INK)
    p2 = b.text_frame.add_paragraph()
    p2.text = desc
    style_runs(p2, 11, color=MUTED)
    add_pic(s, IMG[eq], Inches(4.05), y, Inches(5.3), Inches(0.86))
    y += Inches(0.98)
takeaway(s, "Main metric: macro-mAP — every instance contributes equally.", Inches(6.2))

# =========================================================
# 8 — vision-language models
# =========================================================
s = new_slide("Vision–language models: CLIP and SigLIP", notes=(
    "The main technical challenge is combining the information from the reference "
    "image and the modification text. To represent both modalities we use frozen, "
    "pre-trained vision–language models: CLIP and SigLIP.\n\n"
    "These models use a dual-encoder (two-tower) architecture. One encoder processes "
    "images, the other processes text, and both map their inputs into the SAME "
    "embedding space. Because the representations share this space, we can measure "
    "semantic similarity with cosine similarity: an image gets a high score when its "
    "embedding is close to the embedding of the corresponding text.\n\n"
    "The models are used completely frozen — we only extract embeddings; we never "
    "update or fine-tune their parameters.\n\n"
    "CLIP and SigLIP follow the same dual-encoder principle but differ in TRAINING. "
    "CLIP uses a batch-level contrastive objective based on a softmax: for each image, "
    "the matching text must be distinguished from the other texts in the batch, and "
    "vice versa. SigLIP instead uses a pairwise sigmoid loss: each image–text pair is "
    "treated independently as matching or non-matching. This avoids the global softmax "
    "normalization and scales better to large batches.\n\n"
    "We compare these frozen backbones to test whether our method depends on one "
    "particular vision–language model."))
add_pic(s, IMG["clip"], Inches(0.55), Inches(1.45), Inches(5.2), Inches(2.9))
add_pic(s, IMG["clip_siglip"], Inches(5.85), Inches(1.55), Inches(3.6), Inches(2.7))
bullets(s, [
    ("Dual-encoder (two-tower): one image encoder, one text encoder, both mapping into "
     "the same embedding space → similarity = cosine similarity", {}),
    ("Used completely frozen: we only extract embeddings, never update parameters", {"bold": True}),
    ("CLIP compares all image–text pairs within a batch using a softmax-based "
     "contrastive objective; SigLIP classifies each pair independently with a sigmoid "
     "loss — no global softmax, scales better to large batches", {}),
], top=Inches(4.5), size=14, gap=5)

# =========================================================
# 9 — BASIC
# =========================================================
s = new_slide("The baseline: BASIC", notes=(
    "The baseline for our work is BASIC, the zero-shot method introduced together with "
    "the i-CIR benchmark.\n\n"
    "BASIC processes the two parts of the composed query SEPARATELY. The reference "
    "image is encoded by the visual encoder and the modification text by the text "
    "encoder. The database images are also encoded in advance by the visual encoder.\n\n"
    "For every database image, BASIC computes two similarity scores. The first is the "
    "VISUAL similarity — how similar the database image is to the reference image. The "
    "second is the TEXTUAL similarity — how well the database image matches the "
    "modification text. Both are computed as dot products between the corresponding "
    "embeddings.\n\n"
    "The two scores are then MULTIPLIED. This multiplicative fusion acts like a soft "
    "logical AND: a database image receives a high final score only if it matches both "
    "the reference image and the textual modification.\n\n"
    "The method also includes additional processing steps — centering, score "
    "normalization, contextualization — which I will discuss later."))
add_pic(s, IMG["basic"], Inches(0.55), Inches(1.45), Inches(8.9), Inches(3.4))
bullets(s, [
    ("The two parts of the query are processed separately, each by its own encoder", {}),
    ("For every database image: visual similarity sᵛ to the reference image, and "
     "textual similarity sᵗ to the modification text (dot products of embeddings)", {}),
    ("The two scores are multiplied — a soft logical AND: a high final score requires "
     "matching BOTH the reference image and the modification", {"bold": True}),
    ("Additional steps — centering, score normalisation, contextualisation — come later", {}),
], top=Inches(4.95), size=14, gap=4)

# =========================================================
# 10 — limitation + our idea
# =========================================================
s = new_slide("Limitation of the baseline — our proposal", notes=(
    "The main limitation of the baseline is that the reference image and the "
    "modification text are NEVER PROCESSED JOINTLY. The image branch only sees the "
    "reference image, the text branch only sees the modification. As a result, the "
    "model does not explicitly represent the complete composed query.\n\n"
    "To address this, we introduce a THIRD scoring branch based on a generated target "
    "caption.\n\n"
    "We provide both the reference image and the modification text simultaneously to a "
    "multimodal large language model. We ask the model to imagine that the requested "
    "modification has been applied to the object in the reference image, and to "
    "describe the resulting target image.\n\n"
    "For example, in the chair query the model receives the image of the specific "
    "chair together with the text 'placed around a table', and generates a caption "
    "such as: 'White metallic chair with scrolled armrests placed around a table.'\n\n"
    "This caption contains information from BOTH parts of the query: the visual "
    "identity of the chair and the context specified by the text.\n\n"
    "We encode the generated caption with the same frozen text encoder and compute its "
    "similarity with every database image. The final score therefore combines three "
    "signals: similarity to the reference image, to the modification text, and to the "
    "generated target caption."))
txt(s, Inches(0.68), Inches(1.45), Inches(8.6), Inches(0.7),
    "In BASIC, the reference image and the modification text are never processed jointly.",
    size=18, bold=True, color=RED)
bullets(s, [
    ("Each branch sees only half of the query, so the complete composed query is never "
     "explicitly represented", {}),
], top=Inches(2.2), size=15, gap=4)
MY, MH = Inches(3.05), Inches(1.45)
add_pic(s, IMG["ref"], Inches(0.68), MY, Inches(1.45), MH)
card(s, Inches(2.23), MY + Inches(0.2), Inches(1.55), Inches(1.05),
     text="“placed around\na table”", size=11, italic=True, color=BLUE)
arrow(s, Inches(3.88), MY + Inches(0.5), Inches(0.45))
card(s, Inches(4.43), MY + Inches(0.15), Inches(1.6), Inches(1.15), fill=ROSE,
     text="multimodal\nLLM", size=13, bold=True)
arrow(s, Inches(6.13), MY + Inches(0.5), Inches(0.45))
card(s, Inches(6.68), MY, Inches(2.6), MH,
     text="“White metallic chair with scrolled armrests placed around a table.”",
     size=11, italic=True, align=PP_ALIGN.LEFT)
txt(s, Inches(0.68), MY + MH + Inches(0.05), Inches(3.1), Inches(0.35),
    "both parts of the query, together", size=11, color=MUTED, align=PP_ALIGN.CENTER)
txt(s, Inches(6.68), MY + MH + Inches(0.05), Inches(2.6), Inches(0.35),
    "generated target caption", size=11, color=RED, align=PP_ALIGN.CENTER)
txt(s, Inches(0.68), Inches(5.5), Inches(3.0), Inches(0.4),
    "a third scoring branch:", size=14, bold=True, color=INK)
add_pic(s, IMG["eq_triplet"], Inches(3.5), Inches(5.4), Inches(3.1), Inches(0.65))
takeaway(s, "The caption carries both the visual identity and the requested context.",
         Inches(6.15))

# =========================================================
# 11 — the MLLM
# =========================================================
s = new_slide("The captioner: InternVL 3.5-8B", notes=(
    "For target-caption generation we use the frozen 8-billion-parameter version of "
    "InternVL 3.5.\n\n"
    "We selected this model because it is an open-source multimodal large language "
    "model that can jointly process images and text.\n\n"
    "It also provides a practical balance between performance and computational cost. "
    "Although it is much smaller than many larger multimodal models, it achieves "
    "competitive results across a range of vision–language benchmarks.\n\n"
    "Most importantly, we use it WITHOUT any fine-tuning. It only receives the "
    "reference image, the modification text, and our instruction to describe the "
    "expected target image."))
bullets(s, [
    ("Open-source multimodal LLM that can jointly process an image and a text — "
     "exactly what the caption branch requires", {}),
    ("8B parameters: a practical balance of quality and cost — far smaller than "
     "frontier multimodal models, yet competitive across vision–language benchmarks", {"bold": True}),
    ("Used entirely without fine-tuning: it receives only the reference image, the "
     "modification text, and our instruction", {}),
], top=Inches(1.5), size=16, gap=8)
arch = [("vision encoder", "InternViT"),
        ("projector", "MLP"),
        ("language model", "Qwen3-8B")]
for i, (lab, val) in enumerate(arch):
    c = card(s, Inches(0.75 + i * 2.95), Inches(4.0), Inches(2.7), Inches(1.1),
             text=lab, size=11.5, color=MUTED)
    p2 = c.text_frame.add_paragraph()
    p2.text = val
    p2.alignment = PP_ALIGN.CENTER
    style_runs(p2, 15, bold=True, color=INK)
    if i < 2:
        txt(s, Inches(3.42 + i * 2.95), Inches(4.35), Inches(0.4), Inches(0.4),
            "→", size=20, bold=True, color=RED, align=PP_ALIGN.CENTER)
takeaway(s, "Frozen, open-source, 8B parameters — no fine-tuning anywhere in the pipeline.",
         Inches(5.4))

# =========================================================
# 12 — prompt design
# =========================================================
s = new_slide("Designing the instruction", notes=(
    "An important part of the caption-generation stage is the INSTRUCTION given to the "
    "multimodal model.\n\n"
    "The quality of the generated caption depends strongly on how the task is "
    "formulated. For this reason I carried out an extensive prompt-design process and "
    "tested more than twenty different instructions.\n\n"
    "I varied several elements: the level of detail requested, the use of examples, the "
    "order of the constraints, and restrictions intended to prevent the model from "
    "introducing irrelevant information.\n\n"
    "Based on these experiments I selected five complementary prompting strategies. "
    "Each encourages the model to describe the imagined target from a slightly "
    "different perspective, and together they produce a diverse set of candidate "
    "captions."))
bullets(s, [
    ("The caption quality depends strongly on how the task is formulated", {}),
    ("Extensive prompt design: more than 20 instructions tested, varying the level of "
     "detail, the use of examples, the order of constraints, and restrictions against "
     "irrelevant information", {}),
    ("Five complementary strategies selected — each describes the imagined target from "
     "a different perspective, together producing a diverse set of captions", {"bold": True}),
], top=Inches(1.5), size=16, gap=8)
strategies = ["adaptive\nprecision", "constraint\npriority", "anti-noise\ncontract",
              "slot-fill\ntemplate", "draft–refine"]
for i, name in enumerate(strategies):
    card(s, Inches(0.7 + i * 1.76), Inches(4.15), Inches(1.6), Inches(0.95),
         text=name, size=11.5, bold=True, color=INK, fill=ROSE, line=None)
txt(s, Inches(0.7), Inches(5.25), Inches(8.6), Inches(0.4),
    "the five prompting strategies — their captions are averaged (avg-5)",
    size=12, color=MUTED, align=PP_ALIGN.CENTER)
takeaway(s, "Prompt design is part of the method, not an afterthought.", Inches(5.8))

# =========================================================
# 13 — effect of the caption branch
# =========================================================
s = new_slide("Effect of the caption branch", notes=(
    "Adding a single generated caption improves macro-mAP by about 5.9 points, from "
    "17.95 to 23.83. This suggests the caption captures useful compositional "
    "information not fully represented by the image and text branches separately.\n\n"
    "Using MULTIPLE captions improves the result further. We generate five captions "
    "with different prompting strategies, average their embeddings, and use the "
    "resulting representation for retrieval. This reduces the influence of "
    "prompt-specific wording or irrelevant details and emphasizes information that is "
    "consistent across the captions.\n\n"
    "With this five-caption average, macro-mAP reaches 25.41 — an improvement of about "
    "7.5 points over the original image–text baseline.\n\n"
    "(All results from here use CLIP ViT-L/14 as the backbone unless stated otherwise.)"))
table(s, [
    ("", "img × txt", "img × txt × caption\n(single)", "img × txt × caption\n(avg-5)"),
    ("macro-mAP", "17.95", "23.83", "25.41"),
    ("gain", "—", "+5.9", "+7.5"),
], Inches(0.9), Inches(2.0), Inches(8.2), row_h=0.72, size=15, highlight_rows={1})
txt(s, Inches(0.9), Inches(4.3), Inches(8.2), Inches(0.4),
    "CLIP ViT-L/14 · raw similarity product · no post-processing",
    size=12, color=MUTED, align=PP_ALIGN.CENTER)
bullets(s, [
    ("A single caption already adds +5.9 macro-mAP — compositional information the two "
     "branches miss on their own", {}),
    ("Averaging five captions reduces prompt-specific wording and keeps what is "
     "consistent across them: +7.5 in total", {"bold": True}),
], top=Inches(4.85), size=15, gap=6)
txt(s, Inches(0.68), Inches(6.35), Inches(8.6), Inches(0.35),
    "From here on: CLIP ViT-L/14 as the vision–language backbone, unless stated otherwise.",
    size=12, italic=True, color=RED, align=PP_ALIGN.CENTER)

# =========================================================
# 14 — pipeline overview
# =========================================================
s = new_slide("The pipeline", notes=(
    "To summarize the pipeline so far: each composed query contains a reference image "
    "and a modification text. We also generate a caption describing the imagined "
    "target image.\n\n"
    "These three components — the reference image, the original text, and the generated "
    "caption — are encoded using frozen, pre-trained vision–language models and mapped "
    "into a shared embedding space.\n\n"
    "For every database image we compute three similarity scores: its similarity to the "
    "reference image, to the modification text, and to the generated caption.\n\n"
    "We first normalize these scores so they are on comparable scales. We then combine "
    "them multiplicatively and apply the Harris-inspired penalty, which reduces the "
    "score of candidates that match only one or two branches strongly while performing "
    "poorly on the others.\n\n"
    "I will now discuss two additional processing techniques that further improve "
    "retrieval performance."))
add_pic(s, IMG["pipeline"], Inches(0.4), Inches(1.5), Inches(9.2), Inches(4.5))
takeaway(s, "Three branches, one shared embedding space, all components frozen.",
         Inches(6.2))

# =========================================================
# 15 — score fusion
# =========================================================
s = new_slide("Combining the three scores", notes=(
    "Before combining the visual, textual, and caption scores, we first apply min-based "
    "normalization so that the three branches are on comparable scales. Any negative "
    "residual values are then clamped to zero, meaning they provide no positive "
    "evidence for the candidate image.\n\n"
    "The normalized scores are combined MULTIPLICATIVELY, because the final result "
    "should perform well across all branches at the same time.\n\n"
    "We also use a Harris-inspired penalty. The idea comes from the Harris corner "
    "detector, where a strong response in only one direction is not sufficient. "
    "Similarly, a candidate should not receive a high score just because it matches one "
    "branch very well while matching the others poorly.\n\n"
    "For example, an image may contain the exact chair but not show it around a table, "
    "or it may show chairs around a table but not the specific chair from the reference "
    "image. The Harris term penalizes this imbalance, and it is combined with a "
    "hyperparameter lambda.\n\n"
    "As a result, the final score favors candidates that receive consistently high "
    "scores from the image, text, and caption branches."))
txt(s, Inches(0.68), Inches(1.45), Inches(4.7), Inches(0.6),
    "1.  Min-normalisation, negative residuals clamped to zero:", size=14, bold=True)
add_pic(s, IMG["eq_minnorm"], Inches(0.8), Inches(2.05), Inches(4.3), Inches(0.75))
txt(s, Inches(0.68), Inches(3.0), Inches(4.7), Inches(0.6),
    "2.  Multiply, with a Harris-inspired penalty (λ):", size=14, bold=True)
add_pic(s, IMG["eq_harris"], Inches(0.8), Inches(3.6), Inches(4.3), Inches(0.8))
add_pic(s, IMG["harris"], Inches(5.4), Inches(1.6), Inches(4.0), Inches(3.2))
bullets(s, [
    ("The Harris corner detector idea: a strong response in only ONE direction is not "
     "enough", {}),
    ("An image may show the exact chair but not around a table — or chairs around a "
     "table but not the right chair. The penalty suppresses this imbalance", {}),
    ("λ is a hyperparameter, fixed across all experiments", {}),
], top=Inches(4.85), size=14, gap=4)

# =========================================================
# 16 — centering
# =========================================================
s = new_slide("Post-processing I — centering", notes=(
    "Vision–language embedding spaces often contain a large common component shared by "
    "many embeddings. This component may represent generic visual or linguistic "
    "patterns rather than the distinctive information required for retrieval.\n\n"
    "To reduce this effect, we compute a mean embedding for each modality using a "
    "separate corpus. We subtract this mean from the corresponding embeddings and then "
    "normalize them again.\n\n"
    "The average image feature reflects general visual patterns, while the average text "
    "feature captures common linguistic patterns. Subtracting them helps isolate "
    "semantic content from distributional bias.\n\n"
    "Important caveat: this should NOT be understood as literally removing 'the sky' "
    "from every image. Instead, it removes DIRECTIONS in the embedding space that are "
    "common across many samples — generic visual composition, background patterns, or "
    "broad dataset biases."))
bullets(s, [
    ("Embedding spaces contain a large common component: generic visual or linguistic "
     "patterns rather than distinctive, retrieval-relevant information", {}),
    ("We compute a mean embedding per modality on a separate corpus, subtract it, and "
     "re-normalise:", {}),
], top=Inches(1.5), size=16, gap=8)
add_pic(s, IMG["eq_centering"], Inches(1.0), Inches(3.1), Inches(8.0), Inches(0.9))
bullets(s, [
    ("The mean image feature captures general visual patterns; the mean text feature, "
     "common linguistic patterns — subtracting them isolates semantic content from "
     "distributional bias", {}),
    ("Not literally removing “the sky” from every image: it removes DIRECTIONS in the "
     "embedding space that are common across many samples", {"bold": True}),
], top=Inches(4.25), size=15, gap=6)
takeaway(s, "Remove what is common to everything, keep what is distinctive.", Inches(6.2))

# =========================================================
# 17 — contextualization
# =========================================================
s = new_slide("Post-processing II — text contextualisation", notes=(
    "CLIP is trained primarily on natural-language captions and full sentences. As a "
    "result, single-word text queries (e.g. 'sculpture') or sentence fragments (e.g. "
    "'during sunset') are OUT-OF-DISTRIBUTION input and may produce text features that "
    "are not well aligned with image features.\n\n"
    "To address this, we introduce a contextualisation step that enriches such textual "
    "queries with additional terms. We generate multiple caption-like queries by "
    "combining the raw text query with elements from a subject corpus — adding a random "
    "set of terms before (e.g. 'dog during the sunset') and after (e.g. 'sculpture "
    "dog') the text query.\n\n"
    "These composed phrases are embedded with the text encoder, centered, and averaged. "
    "This yields a more robust textual feature that better reflects how the model "
    "interprets concepts in natural language."))
bullets(s, [
    ("The text encoder is trained on full captions; a bare fragment such as “during "
     "sunset” is out-of-distribution and produces poorly aligned features", {}),
    ("Contextualisation enriches the query with terms from a subject corpus — placed "
     "before and after the modification:", {}),
], top=Inches(1.5), size=16, gap=7)
for i, (raw, ctx) in enumerate([("“during sunset”", "“dog during the sunset”"),
                                ("“sculpture”", "“sculpture dog”")]):
    card(s, Inches(1.15), Inches(3.15 + i * 0.85), Inches(2.6), Inches(0.65),
         text=raw, size=12.5, italic=True, color=BLUE)
    txt(s, Inches(3.85), Inches(3.22 + i * 0.85), Inches(0.5), Inches(0.5), "→",
        size=16, bold=True, color=RED, align=PP_ALIGN.CENTER)
    card(s, Inches(4.45), Inches(3.15 + i * 0.85), Inches(3.7), Inches(0.65),
         text=ctx, size=12.5, italic=True, color=INK)
bullets(s, [
    ("The composed phrases are embedded, centered, and averaged — giving a more robust "
     "textual feature that matches how the encoder sees natural language", {"bold": True}),
], top=Inches(5.0), size=15, gap=5)
takeaway(s, "Speak to the text encoder in the kind of language it was trained on.",
         Inches(6.2))

# =========================================================
# 18 — the ladder
# =========================================================
s = new_slide("Adding the steps on top of each other", notes=(
    "Here we add each post-processing step cumulatively, for the baseline (blue) and "
    "for our caption pipeline (red), on CLIP ViT-L/14.\n\n"
    "The caption pipeline stays above the baseline along the entire ladder. Centering "
    "gives a large jump for the baseline; contextualisation gives the largest single "
    "post-processing gain.\n\n"
    "Two further BASIC steps — the contrastive projection and query expansion — are "
    "omitted: they do not help on this benchmark once the caption branch is present."))
add_pic(s, IMG["ladder_l"], Inches(0.55), Inches(1.5), Inches(8.9), Inches(4.5))
takeaway(s, "The caption pipeline stays ahead at every step of the ladder.", Inches(6.2))

# =========================================================
# 19 — backbones
# =========================================================
s = new_slide("Vision–language backbones", notes=(
    "We evaluate the pipeline with four frozen backbones spanning two model families "
    "and two capacity levels — both to measure how much the choice of backbone matters, "
    "and to report numbers comparable to the i-CIR baseline.\n\n"
    "CLIP ViT-L/14 is the backbone most commonly reported in the zero-shot CIR "
    "literature, which makes our numbers directly comparable. CLIP ViT-H/14 is the "
    "higher-capacity variant and the strongest CLIP model on the duplet baseline.\n\n"
    "SigLIP replaces the softmax contrastive loss with the pairwise sigmoid loss. We use "
    "SigLIP ViT-L/16 at 256px and the more recent, higher-capacity SigLIP2 g/16 at "
    "384px, which is the best-aligned encoder of the four."))
table(s, [
    ("backbone", "family", "embedding dim", "role"),
    ("CLIP ViT-L/14", "CLIP", "768", "paper-comparable"),
    ("CLIP ViT-H/14", "CLIP", "1024", "strongest CLIP on the duplet"),
    ("SigLIP ViT-L/16-256", "SigLIP", "1024", "sigmoid-loss family"),
    ("SigLIP2 g/16-384", "SigLIP", "1536", "best overall"),
], Inches(0.7), Inches(2.1), Inches(8.6), row_h=0.62, size=14, highlight_rows={4})
bullets(s, [
    ("Two families (softmax-contrastive vs sigmoid) × two capacity levels — to test "
     "whether the method depends on one particular model", {}),
], top=Inches(5.35), size=15, gap=5)

# =========================================================
# 20 — backbone results
# =========================================================
s = new_slide("The caption branch across backbones", notes=(
    "The same pipeline, on all four frozen backbones, at the raw product rung.\n\n"
    "The caption branch improves EVERY backbone. The largest jump is on SigLIP-L, where "
    "macro-mAP roughly doubles, from 21.1 to 43.3. SigLIP2 is the strongest base model.\n\n"
    "This shows the contribution does not depend on one particular vision–language "
    "model."))
add_pic(s, IMG["backbones"], Inches(0.55), Inches(1.5), Inches(8.9), Inches(4.5))
takeaway(s, "The caption branch helps every backbone — it is not a CLIP-specific trick.",
         Inches(6.2))

# =========================================================
# 21 — final results
# =========================================================
s = new_slide("Final results — SigLIP2", notes=(
    "The best backbone, with the full ladder. The shape is the same as on CLIP-L: the "
    "caption pipeline stays above the baseline throughout, and contextualisation gives "
    "the final jump.\n\n"
    "Our best configuration reaches 61.98 macro-mAP, against 57.69 for BASIC at the "
    "same rung — and against 38.1 for the plain image × text product."))
add_pic(s, IMG["ladder_s2"], Inches(0.55), Inches(1.5), Inches(8.9), Inches(4.5))
takeaway(s, "61.98 macro-mAP, fully zero-shot — +4.3 over BASIC.", Inches(6.2))

# =========================================================
# 22 — best overall system
# =========================================================
s = new_slide("Our best overall system", notes=(
    "One slide, one recipe: the SigLIP2 backbone, the caption branch with five averaged "
    "captions, and post-processing through centering and contextualisation. Every "
    "component frozen.\n\n"
    "61.98 macro-mAP and 62.07 micro-mAP. Beyond mAP: the correct target is ranked "
    "first for 71.1% of queries, and appears in the top-10 for 94.9% of queries. "
    "Recall@100 is 93.8%.\n\n"
    "That high recall is what motivates reranking as future work: the correct images "
    "are almost always retrieved — the remaining error is mostly in their ORDER."))
recipe = [("backbone", "SigLIP2 g/16-384"), ("caption branch", "InternVL 3.5-8B\navg-5"),
          ("post-processing", "centering\n+ contextualisation")]
for i, (lab, val) in enumerate(recipe):
    c = card(s, Inches(0.75 + i * 2.95), Inches(1.6), Inches(2.7), Inches(1.3),
             text=lab, size=11.5, color=MUTED)
    for ln in val.split("\n"):
        p2 = c.text_frame.add_paragraph()
        p2.text = ln
        p2.alignment = PP_ALIGN.CENTER
        style_runs(p2, 13.5, bold=True, color=INK)
    if i < 2:
        txt(s, Inches(3.42 + i * 2.95), Inches(2.0), Inches(0.4), Inches(0.5),
            "+", size=22, bold=True, color=RED, align=PP_ALIGN.CENTER)
metrics = [("61.98", "macro-mAP"), ("62.07", "mAP"), ("71.1%", "Hit@1"),
           ("94.9%", "Hit@10"), ("93.8%", "Recall@100")]
for i, (num, lab) in enumerate(metrics):
    hero = (i == 0)
    c = card(s, Inches(0.62 + i * 1.79), Inches(3.35), Inches(1.62), Inches(1.15),
             text=num, size=20 if hero else 17, bold=True,
             color=RED if hero else INK, fill=ROSE if hero else LIGHT, line=None)
    p2 = c.text_frame.add_paragraph()
    p2.text = lab
    p2.alignment = PP_ALIGN.CENTER
    style_runs(p2, 11, color=MUTED)
bullets(s, [
    ("+4.3 macro-mAP over the strongest BASIC configuration (57.69)", {}),
    ("The correct target reaches the top-10 for 94.9% of queries — most of the "
     "remaining error is in the ORDER of already-retrieved candidates", {"bold": True}),
], top=Inches(4.75), size=15, gap=6)

# =========================================================
# 23 — qualitative success
# =========================================================
s = new_slide("Qualitative example — success", notes=(
    "Tintin, 'as an iconic rooftop sign'. The plain image × text product already gets "
    "89% AP, but it mixes in generic Tintin drawings. Adding the caption — 'Cartoon "
    "character in a beige coat and blue shirt appears as an iconic rooftop sign' — "
    "pushes the true rooftop-sign photographs to the top: 98% AP.\n\n"
    "The caption resolves what the modification actually asks for."))
add_pic(s, IMG["qual_success"], Inches(0.4), Inches(1.5), Inches(9.2), Inches(5.0))

# =========================================================
# 24 — qualitative failure
# =========================================================
s = new_slide("Qualitative example — failure", notes=(
    "The same instance, 'as a human size statue'. Here the caption branch does NOT "
    "help: the generated caption describes the character, but the visual branch keeps "
    "pulling in drawings and figurines rather than life-size statues.\n\n"
    "This is the characteristic failure mode: when the modification demands a drastic "
    "change of visual domain, the image branch dominates the product and the caption is "
    "not enough to overcome it."))
add_pic(s, IMG["qual_failure"], Inches(0.4), Inches(1.5), Inches(9.2), Inches(5.0))

# =========================================================
# 25 — limitations & future work
# =========================================================
s = new_slide("Limitations and future work", notes=(
    "Limitations. The main cost is caption generation — about 15 seconds per query, "
    "which dominates online inference. The results also depend on prompt design: "
    "averaging five captions mitigates this, but does not remove it. And the fixed, "
    "unweighted product cannot adapt when one branch should matter more.\n\n"
    "Future work. A stronger or more efficient captioner — or a single high-quality "
    "caption that matches avg-5 without five generations — would cut the main compute "
    "cost. The fixed product could be replaced by a learned or weighted fusion of the "
    "three similarities, relaxing the zero-shot constraint in exchange for accuracy.\n\n"
    "Because recall is already high — the correct instance lands in the top-ranked "
    "shortlist for the large majority of queries — a second-stage RERANKER that "
    "reorders this shortlist is a promising direction: most of the remaining error is "
    "in the ordering of candidates that are already retrieved. A text-conditioned "
    "reranker that reorders by similarity to the target caption, rather than to the "
    "reference image, is a natural candidate, since it keeps the modification in the "
    "loop at the reranking stage.\n\n"
    "Finally, the caption-as-third-modality idea is benchmark-agnostic and could be "
    "evaluated beyond i-CIR, on category-level CIR benchmarks and other instance-level "
    "retrieval settings."))
txt(s, Inches(0.68), Inches(1.45), Inches(8.6), Inches(0.4), "Limitations",
    size=16, bold=True, color=RED)
bullets(s, [
    ("Compute — caption generation dominates online inference (≈ 15 s per query)", {}),
    ("Prompt sensitivity — results depend on instruction design; avg-5 mitigates but "
     "does not remove it", {}),
    ("The fixed, unweighted product cannot re-weight the branches per query", {}),
], top=Inches(1.9), size=14.5, gap=4)
txt(s, Inches(0.68), Inches(3.7), Inches(8.6), Inches(0.4), "Future work",
    size=16, bold=True, color=RED)
bullets(s, [
    ("A stronger or more efficient captioner — or a single caption matching avg-5 "
     "without five generations — would cut the main compute cost", {}),
    ("A learned or weighted fusion of the three similarities, relaxing the zero-shot "
     "constraint in exchange for accuracy", {}),
    ("Second-stage reranking: recall is already high (Hit@10 = 94.9%), so most of the "
     "remaining error is in the ORDER of candidates that are already retrieved — a "
     "text-conditioned reranker keeps the modification in the loop", {"bold": True}),
    ("The caption-as-third-modality idea is benchmark-agnostic: category-level CIR and "
     "other instance-level retrieval settings", {}),
], top=Inches(4.15), size=14.5, gap=4)

# =========================================================
# 26 — conclusions
# =========================================================
s = new_slide("Conclusions", notes=(
    "Four conclusions.\n\n"
    "First: the caption is the single most effective component. Adding the target "
    "caption improves every backbone on the full dataset, and in the component ablation "
    "it is the largest single contributor — larger than feature centering and far "
    "larger than the remaining BASIC preprocessing.\n\n"
    "Second: a simple caption can replace elaborate preprocessing. A plain image × text "
    "baseline plus the caption reaches the level of the fully tuned BASIC pipeline, and "
    "with a strong backbone exceeds it. The textual signal is better supplied by an "
    "explicit target description than by contextualising the bare modification phrase.\n\n"
    "Third: centering and the caption are complementary — their gains add up, and the "
    "best configuration combines both.\n\n"
    "Fourth: SigLIP2 is the strongest backbone for the pipeline, reaching the "
    "thesis-best 61.98 macro-mAP, even though CLIP-H is stronger on the bare duplet "
    "baseline — the backbone must be judged WITHIN the full pipeline."))
bullets(s, [
    ("The caption is the single most effective component — it improves every backbone, "
     "and is the largest single contributor in the ablation: larger than centering, far "
     "larger than the rest of the BASIC preprocessing", {"bold": True}),
    ("A simple caption can replace elaborate preprocessing — plain img × txt plus the "
     "caption reaches the fully tuned BASIC pipeline, and with a strong backbone "
     "exceeds it", {}),
    ("Centering and the caption are complementary — their gains add up; the best "
     "configuration combines both", {}),
    ("SigLIP2 is the strongest backbone for the pipeline (61.98 macro-mAP) even though "
     "CLIP-H is stronger on the bare duplet — a backbone must be judged within the "
     "full pipeline", {}),
], top=Inches(1.6), size=15, gap=10)

# =========================================================
# 27 — thank you (full-bleed red)
# =========================================================
s = new_slide("")
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
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
    "Every rung of the ladder, for the three pipelines. macro-mAP, full i-CIR, "
    "CLIP ViT-L/14."))
table(s, [
    ("step", "img × txt", "× caption (single)", "× caption (avg-5)"),
    ("raw product", "17.95", "23.83", "25.41"),
    ("+ centering", "27.76", "31.02", "31.87"),
    ("+ sim-normalisation", "27.40", "30.28", "31.97"),
    ("+ Harris criterion", "28.33", "31.25", "32.82"),
    ("+ contextualisation", "32.25", "34.06", "35.76"),
    ("+ projection", "32.48", "32.58", "33.80"),
    ("+ query expansion", "30.28", "31.53", "32.39"),
], Inches(1.0), Inches(1.75), Inches(8.0), row_h=0.5, size=13.5,
      highlight_rows={5})
txt(s, Inches(1.0), Inches(5.5), Inches(8.0), Inches(0.4),
    "macro-mAP · full i-CIR · CLIP ViT-L/14 · the pipeline stops at contextualisation",
    size=12, color=MUTED, align=PP_ALIGN.CENTER)

s = new_slide("Backup — reproducing BASIC", notes=(
    "If asked about the paper's number: the i-CIR paper reports 34.35 for BASIC "
    "(CLIP-L, full stack). Our re-run of the released code gives 32.48. The gap is "
    "concentrated in the image branch and is consistent with re-extracting features in "
    "a newer software stack. Both methods are evaluated in the same environment, so the "
    "comparisons are unaffected."))
table(s, [
    ("BASIC, CLIP ViT-L/14", "macro-mAP"),
    ("reported in the i-CIR paper", "34.35"),
    ("our reproduction (released code)", "32.48"),
], Inches(2.2), Inches(1.9), Inches(5.6), row_h=0.6, size=15)
bullets(s, [
    ("The gap is concentrated in the IMAGE branch — features re-extracted in a newer "
     "software stack (image decoding / resizing differ across library versions)", {}),
    ("Contextualisation also draws fresh object nouns per query — small run-to-run "
     "variance", {}),
    ("Both BASIC and our method are evaluated in the SAME environment, so all relative "
     "comparisons in this thesis are unaffected", {"bold": True}),
], top=Inches(4.1), size=15, gap=7)

s = new_slide("Backup — inference latency", notes=(
    "100 queries, RTX-6000-Ada 48 GB, five captions per query. Caption generation is "
    "≈99.7% of the online cost; the retrieval itself is negligible. Database embeddings "
    "are precomputed offline."))
table(s, [
    ("stage", "CLIP-L", "SigLIP2"),
    ("caption generation (5 captions)", "≈ 14.7 s", "≈ 14.7 s"),
    ("embedding the query triplet", "22 ms", "46 ms"),
    ("total, per query (median)", "14.75 s", "14.75 s"),
], Inches(1.4), Inches(1.9), Inches(7.2), row_h=0.58, size=14, highlight_rows={3})
bullets(s, [
    ("Caption generation is ≈ 99.7% of online inference — the backbone choice does not "
     "change latency", {"bold": True}),
    ("Database embeddings are precomputed offline; ranking itself is instantaneous", {}),
    ("Levers: fewer captions, shorter generations, a smaller or quantised MLLM", {}),
], top=Inches(4.5), size=15, gap=6)

s = new_slide("Backup — the five instructions", notes=(
    "The five prompting strategies on the tintin example, 'as an iconic rooftop sign'."))
add_pic(s, IMG["tintin_q"], Inches(0.68), Inches(1.7), Inches(2.0), Inches(1.7))
txt(s, Inches(0.68), Inches(3.55), Inches(2.0), Inches(0.6),
    "“as an iconic rooftop sign”", size=12, italic=True, color=BLUE,
    align=PP_ALIGN.CENTER)
caps = [("adaptive precision", "A character with a beige coat and blue shirt, as an iconic rooftop sign"),
        ("constraint-priority", "A character wearing a trench coat, blonde hair, and a blue shirt, is an iconic rooftop sign."),
        ("anti-noise contract", "Character in a beige trench coat, blue shirt, with blushing cheeks and short orange hair as an iconic rooftop sign."),
        ("slot-fill template", "a cartoon character wearing a trench coat, blushing, with short hair as an iconic rooftop sign."),
        ("draft–refine", "Cartoon character in a beige coat and blue shirt appears as an iconic rooftop sign.")]
for i, (tag, cap) in enumerate(caps):
    card(s, Inches(3.0), Inches(1.6 + i * 1.0), Inches(6.4), Inches(0.9),
         text=f"{tag}:  “{cap}”", size=10.5, align=PP_ALIGN.LEFT)

prs.save(OUT)
print("saved", OUT, "slides:", len(prs.slides._sldIdLst))
