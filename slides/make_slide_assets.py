"""Figure assets for the defense deck (beyond the result charts in make_charts.py).

Produces in slides/assets/:
  icir_tintin.png          the i-CIR sample figure rebuilt for the tintin instance
  instance_vs_category.png category- vs instance-level comparison panel
  clip_schematic.png       dual-encoder contrastive schematic
  eq_*.png                 formula renders (mathtext)
Needs the i-CIR data on the cluster (thesis_cir/data/icir).
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Arc
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets")
DATA = "/extra/ahoseinp/projects/thesis_cir/data/icir"
TINTIN_DB = f"{DATA}/database/tintin"
os.makedirs(OUT, exist_ok=True)

INK = "#0b0b0b"
MUTED = "#52514e"
BLUE = "#2a78d6"
ORANGE = "#e8871e"
GREEN = "#1a7a1a"
GRAY = "#898781"
RED = "#9B0014"

def letterbox(path, aspect=4 / 3, pad_color=(255, 255, 255)):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    if w / h > aspect:
        W, H = w, int(round(w / aspect))
    else:
        W, H = int(round(h * aspect)), h
    canvas = Image.new("RGB", (W, H), pad_color)
    canvas.paste(im, ((W - w) // 2, (H - h) // 2))
    return canvas

# ------------------------------------------------------------------
# 1. i-CIR tintin sample figure (same layout family as icir_dataset)
# ------------------------------------------------------------------
queries = [
    ("as a human\nsize statue", "as_a_human_size_statue",
     "tintin_as_a_human_size_statue_pos04.jpg", "4159", 11),
    ("as an action\nfigure", "as_an_action_figure",
     "tintin_as_an_action_figure_pos04.jpg", "0040", 14),
    ("as an iconic\nrooftop sign", "as_an_iconic_rooftop_sign",
     "tintin_as_an_iconic_rooftop_sign_pos02.jpg", "1014", 10),
    ("on a billboard\nad", "on_a_billboard_ad",
     "tintin_on_a_billboard_ad_pos1.jpg", "0002", 3),
    ("on a t-shirt", "on_a_t-shirt",
     "tintin_on_a_t-shirt_pos03.jpg", "4311", 14),
]
fig = plt.figure(figsize=(15.2, 6.4), dpi=200)
gs = fig.add_gridspec(3, 6, height_ratios=[0.55, 1, 1], hspace=0.32, wspace=0.10,
                      left=0.01, right=0.99, top=0.99, bottom=0.075)

# query image spanning rows 1-2 in column 0
axq = fig.add_subplot(gs[1:, 0])
axq.imshow(letterbox(f"{DATA}/query/tintin/tintin_image_query1.jpg"))
axq.set_xticks([]); axq.set_yticks([])
for sp in axq.spines.values():
    sp.set_edgecolor(ORANGE); sp.set_linewidth(3.5)
axq.set_title("image query", y=-0.16, fontsize=17, color=ORANGE, family="serif")

for c, (label, qdir, pos, hn, npos) in enumerate(queries, start=1):
    axt = fig.add_subplot(gs[0, c])
    axt.set_xticks([]); axt.set_yticks([])
    for sp in axt.spines.values():
        sp.set_edgecolor(BLUE); sp.set_linewidth(2.2)
    axt.text(0.5, 0.5, label, ha="center", va="center", fontsize=16.5,
             color=BLUE, family="monospace")

    axp = fig.add_subplot(gs[1, c])
    axp.imshow(letterbox(f"{TINTIN_DB}/{qdir}/{pos}"))
    axp.set_xticks([]); axp.set_yticks([])
    for sp in axp.spines.values():
        sp.set_edgecolor("#cccccc"); sp.set_linewidth(0.8)

    axn = fig.add_subplot(gs[2, c])
    axn.imshow(letterbox(f"{TINTIN_DB}/hn/tintin_hn{hn}.jpg"))
    axn.set_xticks([]); axn.set_yticks([])
    for sp in axn.spines.values():
        sp.set_edgecolor("#cccccc"); sp.set_linewidth(0.8)

fig.text(0.585, 0.395, "composed positives", ha="center", fontsize=18,
         family="serif", color=INK)
fig.text(0.585, 0.012, "hard negatives", ha="center", fontsize=18,
         family="serif", color=INK)
fig.savefig(f"{OUT}/icir_tintin.png", facecolor="white")
plt.close(fig)

# ------------------------------------------------------------------
# 2. category-level vs instance-level  (ornate metal chair)
# ------------------------------------------------------------------
CHAIR_DB = f"{DATA}/database/ornate_metal_chair"
CHAIR_Q = f"{DATA}/query/ornate_metal_chair/ornate_metal_chair_image_query1.jpg"
results = [f"{CHAIR_DB}/placed_around_a_table/ornate_metal_chair_placed_around_a_table_pos1.jpg",
           f"{CHAIR_DB}/hn/ornate_metal_chair_hn2116.jpg",
           f"{CHAIR_DB}/hn/ornate_metal_chair_hn2117.jpg",
           f"{CHAIR_DB}/hn/ornate_metal_chair_hn2120.jpg"]
rows = [
    ("Category-level", "“a chair placed\naround a table”", [True, True, True, True]),
    ("Instance-level", "“this chair placed\naround a table”", [True, False, False, False]),
]
fig = plt.figure(figsize=(12.5, 5.6), dpi=200)
gs = fig.add_gridspec(2, 6, width_ratios=[1, 1.15, 1, 1, 1, 1], hspace=0.42,
                      wspace=0.12, left=0.01, right=0.99, top=0.90, bottom=0.03)
for r, (mode, qtext, oks) in enumerate(rows):
    axq = fig.add_subplot(gs[r, 0])
    axq.imshow(letterbox(CHAIR_Q))
    axq.set_xticks([]); axq.set_yticks([])
    for sp in axq.spines.values():
        sp.set_edgecolor(ORANGE); sp.set_linewidth(2.5)
    axt = fig.add_subplot(gs[r, 1])
    axt.axis("off")
    axt.text(0.5, 0.62, qtext, ha="center", va="center", fontsize=12.5,
             color=BLUE, family="monospace")
    axt.annotate("", xy=(0.98, 0.25), xytext=(0.06, 0.25),
                 arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6))
    axt.set_title(mode, fontsize=15, family="serif", color=INK, y=0.94,
                  fontweight="bold")
    for c, (img, ok) in enumerate(zip(results, oks), start=2):
        ax = fig.add_subplot(gs[r, c])
        ax.imshow(letterbox(img))
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_edgecolor(GREEN if ok else RED)
            sp.set_linewidth(2.6)
        ax.text(0.97, 0.97, "✓" if ok else "✗", transform=ax.transAxes,
                ha="right", va="top", fontsize=20, fontweight="bold",
                color="white",
                bbox=dict(boxstyle="circle,pad=0.18",
                          fc=GREEN if ok else RED, ec="none"))
fig.savefig(f"{OUT}/instance_vs_category.png", facecolor="white")
plt.close(fig)

# ------------------------------------------------------------------
# 3. CLIP dual-encoder schematic (single pair, chair example)
# ------------------------------------------------------------------
CHAIR_CAP = "\u201ca white ornate\nmetal chair\u201d"
C_IMG, C_TXT = "#2a78d6", "#9B0014"
fig, ax = plt.subplots(figsize=(11.0, 4.6), dpi=200)
ax.set_xlim(0, 11.0); ax.set_ylim(0, 4.6); ax.axis("off")

def rbox(x, y, w, h, label, fc="#f0efec", fontsize=13, tc=INK, bold=True, ec=MUTED):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", fc=fc,
                       ec=ec, lw=1.3)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
            fontsize=fontsize, color=tc, fontweight="bold" if bold else "normal")

# top row: image -> image encoder -> image vector
thumb = letterbox(CHAIR_Q)
ax.imshow(thumb, extent=(0.35, 2.05, 2.85, 4.15), aspect="auto", zorder=3)
ax.annotate("", xy=(3.05, 3.5), xytext=(2.2, 3.5),
            arrowprops=dict(arrowstyle="-|>", color=GRAY, lw=1.8))
rbox(3.1, 3.05, 1.9, 0.9, "image\nencoder", ec=C_IMG)
ax.annotate("", xy=(6.05, 3.5), xytext=(5.1, 3.5),
            arrowprops=dict(arrowstyle="-|>", color=C_IMG, lw=1.8))
rbox(6.1, 3.15, 1.5, 0.7, "image\nvector", fc="white", ec=C_IMG, tc=C_IMG, fontsize=11)

# bottom row: text -> text encoder -> text vector
ax.text(1.2, 1.05, CHAIR_CAP, ha="center", va="center", fontsize=11,
        color=BLUE, family="monospace",
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=BLUE, lw=1.2))
ax.annotate("", xy=(3.05, 1.05), xytext=(2.3, 1.05),
            arrowprops=dict(arrowstyle="-|>", color=GRAY, lw=1.8))
rbox(3.1, 0.6, 1.9, 0.9, "text\nencoder", ec=C_TXT)
ax.annotate("", xy=(6.05, 1.05), xytext=(5.1, 1.05),
            arrowprops=dict(arrowstyle="-|>", color=C_TXT, lw=1.8))
rbox(6.1, 0.7, 1.5, 0.7, "text\nvector", fc="white", ec=C_TXT, tc=C_TXT, fontsize=11)

# both vectors land in ONE shared embedding space (drawn as a circle), where the
# angle between them IS the similarity
space = Circle((9.25, 2.3), 1.42, fc="#f4f6fb", ec=MUTED, lw=1.4, ls=(0, (5, 3)),
               zorder=1)
ax.add_patch(space)
ax.text(9.25, 3.92, "shared embedding space", fontsize=11.5, color=INK,
        ha="center", va="center", fontweight="bold")
ax.annotate("", xy=(8.35, 2.95), xytext=(7.65, 3.3),
            arrowprops=dict(arrowstyle="-|>", color=C_IMG, lw=1.8))
ax.annotate("", xy=(8.35, 1.62), xytext=(7.65, 1.15),
            arrowprops=dict(arrowstyle="-|>", color=C_TXT, lw=1.8))
# the two embedded vectors inside the space, with the angle between them
ax.annotate("", xy=(9.95, 3.05), xytext=(9.25, 2.3),
            arrowprops=dict(arrowstyle="-|>", color=C_IMG, lw=2.4), zorder=4)
ax.annotate("", xy=(10.25, 2.25), xytext=(9.25, 2.3),
            arrowprops=dict(arrowstyle="-|>", color=C_TXT, lw=2.4), zorder=4)
ax.add_patch(Arc((9.25, 2.3), 1.05, 1.05, theta1=-3, theta2=47,
                 color=MUTED, lw=1.3, zorder=4))
ax.text(9.62, 2.02, "θ", fontsize=12, color=MUTED, ha="center", va="center",
        style="italic", zorder=5)
ax.text(9.25, 0.42, "cos θ  =  similarity", fontsize=11.5, color=INK,
        ha="center", va="center", fontweight="bold", zorder=5,
        bbox=dict(boxstyle="round,pad=0.3", fc="#f7e9ea", ec=C_TXT, lw=1.2))
fig.savefig(f"{OUT}/clip_schematic.png", facecolor="white", bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------------------------
# 4. formula renders
# ------------------------------------------------------------------
EQS = {
    # NB: matplotlib mathtext has no \textrm — hyphens go inside \mathrm{}
    "eq_pk": r"$\mathrm{P@}k \;=\; \frac{\mathrm{correct\ results\ in\ top-}k}{k}$",
    "eq_ap": r"$\mathrm{AP@}k \;=\; \frac{1}{R}\,\sum_{j=1}^{k}\ \mathrm{P@}j \cdot \mathrm{rel}(j)$",
    "eq_map": r"$\mathrm{mAP@}k \;=\; \frac{1}{|Q|}\sum_{q \in Q}\mathrm{AP@}k(q)$",
    "eq_mmap": r"$\mathrm{macro\ mAP@}k \;=\; \frac{1}{|\mathcal{I}|}\sum_{I \in \mathcal{I}}\;\frac{1}{|Q_I|}\sum_{q \in Q_I}\mathrm{AP@}k(q)$",
    "eq_centering": r"$\bar{q}^{\,v} = \phi^{v}(q^{v}) - \mu^{v}\,,\qquad \bar{q}^{\,t} = \phi^{t}(q^{t}) - \mu^{t}$",
    "eq_minnorm": r"$\tilde{s} \;=\; \frac{s - s_{\min}}{|\,s_{\min}\,|}\,,\qquad \tilde{s} \leftarrow \max(\tilde{s},\, 0)$",
    "eq_harris": r"$\tilde{s}^{\,f} \;=\; \tilde{s}^{\,v}\,\tilde{s}^{\,t} \;-\; \lambda\,\left(\tilde{s}^{\,v} + \tilde{s}^{\,t}\right)^{2}$",
    "eq_triplet": r"$\tilde{s}^{\,f} \;=\; \tilde{s}^{\,v}\cdot\tilde{s}^{\,t}\cdot\tilde{s}^{\,c}$",
    "eq_problem": r"$q=(I_q,\,t_q)\ \longrightarrow\ \mathrm{rank\ every}\ x \in \mathcal{X}\ \mathrm{by}\ s(x \mid I_q,\,t_q)$",
}
for name, eq in EQS.items():
    fig = plt.figure(figsize=(8, 1.2), dpi=300)
    fig.text(0.5, 0.5, eq, ha="center", va="center", fontsize=17, color=INK)
    fig.savefig(f"{OUT}/{name}.png", facecolor="white", bbox_inches="tight",
                pad_inches=0.06)
    plt.close(fig)

print("assets written to", OUT)

# ------------------------------------------------------------------
# 5. paper-style i-CIR statistics (recomputed from the dataset),
#    matching the paper's Fig. 2: (a) image queries, (b) text queries,
#    (c) hard negatives per instance; (d) positives per composed query
# ------------------------------------------------------------------
import csv
from collections import defaultdict

# composed queries per instance: each row of query_files.csv IS one composed query
cq_per_inst = defaultdict(int)
with open(f"{DATA}/query_files.csv") as fh:
    for path, text, inst in csv.reader(fh):
        cq_per_inst[inst] += 1
pos_per_query = defaultdict(int)
with open(f"{DATA}/database_files.csv") as fh:
    for path, text, inst in csv.reader(fh):
        if "/hn/" not in path:
            pos_per_query[(inst, text)] += 1
hn_counts = []
for inst in sorted(os.listdir(f"{DATA}/database")):
    hnd = f"{DATA}/database/{inst}/hn"
    if os.path.isdir(hnd):
        hn_counts.append(len(os.listdir(hnd)))

import numpy as np
import statistics
panels = [
    ("(a) hard negatives / instance", sorted(hn_counts), 20),
    ("(b) positives / composed query",
     [min(v, 30) for v in pos_per_query.values()], np.arange(0.5, 31.5, 1)),
    ("(c) composed queries / instance", sorted(cq_per_inst.values()),
     np.arange(0.5, 26.5, 1)),
]
fig, axes = plt.subplots(1, 3, figsize=(11.4, 3.2), dpi=200)
for i, (ax, (title, vals, bins)) in enumerate(zip(axes, panels)):
    med = statistics.median(vals)
    ax.hist(vals, bins=bins, color=BLUE, edgecolor="white", linewidth=0.6)
    ax.axvline(med, color=ORANGE, lw=2)
    ax.text(0.97, 0.92, f"median {med:g}", transform=ax.transAxes, ha="right",
            fontsize=10.5, color=ORANGE, style="italic")
    if i == 1:
        ax.text(0.97, 0.78, "long tail to 127", transform=ax.transAxes,
                ha="right", fontsize=9.5, color=GRAY, style="italic")
    ax.set_title(title, fontsize=12.5, color=INK, loc="left")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color="#e1e0d9", lw=0.7)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, labelsize=9.5, colors=GRAY)
fig.tight_layout()
fig.savefig(f"{OUT}/icir_paper_stats.png", facecolor="white")
plt.close(fig)

# ------------------------------------------------------------------
# 6. slide-2 chair images letterboxed to identical 4:3 boxes
# ------------------------------------------------------------------
letterbox(f"{OUT}/chair_ref.jpg").save(f"{OUT}/chair_ref_43.jpg", quality=92)
letterbox(f"{OUT}/chair_set.jpg").save(f"{OUT}/chair_set_43.jpg", quality=92)
print("stats + chair 4:3 done")

# ------------------------------------------------------------------
# 7. pipeline overview (slide-native version of thesis Fig. 5.1)
# ------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(14.0, 5.8), dpi=200)
ax.set_xlim(0, 14.0); ax.set_ylim(0, 5.8); ax.axis("off")

def pbox(x, y, w, h, label, fc="#f0efec", fs=11, tc=INK, bold=True, ec=MUTED):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                                fc=fc, ec=ec, lw=1.1))
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fs,
            color=tc, fontweight="bold" if bold else "normal")

def ar(x0, y0, x1, y1, color=GRAY, ls="-", rad=0.0):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="->", color=color, lw=1.3, ls=ls,
                                connectionstyle=f"arc3,rad={rad}"))

LANE = {"v": 4.65, "t": 3.0, "c": 1.15}

# --- inputs
ax.imshow(letterbox(CHAIR_Q), extent=(0.15, 1.35, LANE["v"] - 0.45, LANE["v"] + 0.5),
          aspect="auto", zorder=3)
ax.text(0.75, LANE["v"] - 0.68, "query image", ha="center", fontsize=9.5, color=ORANGE)
ax.text(0.75, LANE["t"], "“placed around\na table”", ha="center", va="center",
        fontsize=9.5, color=BLUE, family="monospace",
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=BLUE, lw=1.0))
ax.text(0.75, LANE["t"] - 0.62, "query text", ha="center", fontsize=9.5, color=BLUE)

# --- caption branch: the MLLM reads BOTH parts of the query
pbox(2.0, LANE["c"] - 0.45, 1.35, 0.9, "MLLM\n(InternVL)", fc="#fbe9e7", ec=RED, fs=10)
ar(1.4, LANE["v"] - 0.45, 2.0, LANE["c"] + 0.3, color=RED, rad=-0.28)
ar(1.4, LANE["t"] - 0.3, 2.0, LANE["c"] + 0.1, color=RED, rad=-0.18)
ar(3.4, LANE["c"], 3.85, LANE["c"], color=RED)
ax.text(5.05, LANE["c"], "“White metallic chair\nwith scrolled armrests\nplaced around a table.”",
        ha="center", va="center", fontsize=8.5, color=INK, style="italic",
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=RED, lw=1.0))
ax.text(5.05, LANE["c"] - 0.85, "generated target caption", ha="center", fontsize=8.5,
        color=RED)

# --- encoders
for k, lab in (("v", "image\nencoder"), ("t", "text\nencoder"), ("c", "text\nencoder")):
    pbox(6.6, LANE[k] - 0.4, 1.4, 0.8, lab, fs=10)
ar(1.45, LANE["v"], 6.55, LANE["v"])
ar(1.45, LANE["t"], 6.55, LANE["t"])
ar(6.25, LANE["c"], 6.55, LANE["c"])

# --- centering
for k in LANE:
    pbox(8.4, LANE[k] - 0.32, 0.85, 0.64, "\u2212 \u03bc", fs=11, fc="#eef3fb", ec=BLUE)
    ax.text(8.83, LANE[k] - 0.52, "centering", ha="center", fontsize=7.5, color=BLUE)
    ar(8.05, LANE[k], 8.37, LANE[k])

# --- database feeds every dot product
ax.text(9.85, 5.62, "database (752,092 images)", ha="center", fontsize=9, color=MUTED)
pbox(9.05, 5.05, 1.6, 0.45, "image encoder  \u2212 \u03bc", fc="#eef3fb", ec=BLUE,
     fs=8, bold=False)
for k in LANE:
    ax.text(9.85, LANE[k], "\u2299", ha="center", va="center", fontsize=15, color=INK)
    ar(9.3, LANE[k], 9.68, LANE[k])
    ar(9.85, 5.0, 9.85, LANE[k] + 0.25, color=BLUE, ls=":")
for k, lab in (("v", "s\u1d5b"), ("t", "s\u1d57"), ("c", "s\u1d9c")):
    ax.text(10.5, LANE[k], lab, ha="center", va="center", fontsize=13, color=INK,
            fontweight="bold")
    ar(10.05, LANE[k], 10.3, LANE[k])
    ar(10.72, LANE[k], 11.05, LANE[k])

# --- fusion
pbox(11.1, 1.6, 2.05, 3.55,
     "min-normalise\n+ clamp\n\n\u00d7   \u00d7\n\nHarris penalty\n(\u03bb)",
     fs=10, fc="#fbe9e7", ec=RED)
ax.text(12.12, 1.2, "final score", ha="center", fontsize=10.5, color=RED, fontweight="bold")
ax.text(12.12, 0.75, "\u2192  ranked list", ha="center", fontsize=10, color=INK)
ax.text(12.12, 0.28, "all components frozen", ha="center", fontsize=8.5, color=MUTED,
        style="italic")
fig.savefig(f"{OUT}/pipeline_overview.png", facecolor="white", bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------------------------
# 8. CLIP vs SigLIP objective schematic
# ------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(10.0, 3.5), dpi=200)
for ax, (name, sub) in zip(axes, [
        ("CLIP", "softmax over the batch:\neach image competes against all texts"),
        ("SigLIP", "independent sigmoid per pair:\nmatch / no-match, no batch competition")]):
    ax.set_xlim(-0.6, 4); ax.set_ylim(-1.35, 4); ax.axis("off")
    for i in range(4):
        for j in range(4):
            on = (i == j)
            fc = RED if on else "#f0efec"
            ax.add_patch(FancyBboxPatch((j, 3 - i), 0.88, 0.88,
                                        boxstyle="round,pad=0.02", fc=fc,
                                        ec="white", lw=1.4))
    if name == "CLIP":
        ax.add_patch(plt.Rectangle((-0.08, 2.92), 4.04, 1.04, fill=False,
                                   ec=BLUE, lw=2.2))
        ax.text(4.05, 3.44, "softmax\nover row", fontsize=9, color=BLUE,
                va="center", ha="left")
    else:
        for (i, j) in [(0, 0), (1, 2)]:
            ax.add_patch(plt.Rectangle((j - 0.06, 3 - i - 0.06), 1.0, 1.0,
                                       fill=False, ec=BLUE, lw=2.2))
        ax.text(1.7, 4.0, "each cell scored on its own", fontsize=9, color=BLUE,
                ha="center")
    ax.text(1.94, -0.55, name, ha="center", fontsize=15, fontweight="bold", color=INK)
    ax.text(1.94, -1.15, sub, ha="center", fontsize=9.5, color=MUTED)
fig.savefig(f"{OUT}/clip_vs_siglip.png", facecolor="white", bbox_inches="tight")
plt.close(fig)
print("pipeline + clip/siglip done")
