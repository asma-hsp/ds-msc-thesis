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
from matplotlib.patches import FancyBboxPatch, Circle
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
fig, ax = plt.subplots(figsize=(11.0, 4.6), dpi=200)
ax.set_xlim(0, 11.0); ax.set_ylim(0, 4.6); ax.axis("off")

def rbox(x, y, w, h, label, fc="#f0efec", fontsize=13, tc=INK, bold=True):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", fc=fc,
                       ec=MUTED, lw=1.1)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
            fontsize=fontsize, color=tc, fontweight="bold" if bold else "normal")

# top: one image -> image encoder
thumb = letterbox(CHAIR_Q)
ax.imshow(thumb, extent=(0.5, 2.3, 2.75, 4.1), aspect="auto", zorder=3)
ax.annotate("", xy=(3.35, 3.42), xytext=(2.45, 3.42),
            arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.6))
rbox(3.4, 2.97, 1.8, 0.9, "image\nencoder")
# bottom: one text -> text encoder
ax.text(1.4, 1.05, CHAIR_CAP, ha="center", va="center", fontsize=11,
        color=BLUE, family="monospace",
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=BLUE, lw=1.2))
ax.annotate("", xy=(3.35, 1.05), xytext=(2.55, 1.05),
            arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.6))
rbox(3.4, 0.6, 1.8, 0.9, "text\nencoder")
# shared embedding space
space = plt.matplotlib.patches.Ellipse((8.3, 2.3), 4.4, 3.6,
                                       fc="#fafaf8", ec=MUTED, lw=1.3)
ax.add_patch(space)
ax.text(8.3, 3.75, "shared embedding space", ha="center", fontsize=13,
        color=INK, fontweight="bold")
ax.annotate("", xy=(7.15, 2.85), xytext=(5.25, 3.42),
            arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.6))
ax.annotate("", xy=(7.35, 1.85), xytext=(5.25, 1.05),
            arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.6))
ax.text(6.05, 3.45, "one vector", fontsize=9.5, color=GRAY, ha="left", va="bottom")
ax.text(6.05, 1.15, "one vector", fontsize=9.5, color=GRAY, ha="left", va="top")
for (x, y, col) in [(7.55, 2.75, "#2a78d6"), (7.95, 2.05, "#9B0014")]:
    dot = plt.matplotlib.patches.Circle((x, y), 0.13, fc=col, ec="none")
    ax.add_patch(dot)
ax.plot([7.55, 7.95], [2.75, 2.05], color=GRAY, lw=1.2, ls="--")
ax.text(9.15, 2.35, "similar meaning\n= nearby points\n(cosine similarity)",
        fontsize=11.5, color=INK, ha="center", va="center")
fig.savefig(f"{OUT}/clip_schematic.png", facecolor="white", bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------------------------
# 4. formula renders
# ------------------------------------------------------------------
EQS = {
    "eq_pk": r"$\mathrm{P@}k \;=\; \frac{\mathrm{correct\ results\ in\ top-}k}{k}$",
    "eq_ap": r"$\mathrm{AP} \;=\; \frac{1}{R}\,\sum_{k}\ \mathrm{P@}k \cdot \mathrm{rel}(k)$",
    "eq_map": r"$\mathrm{mAP} \;=\; \frac{1}{|Q|}\sum_{q \in Q}\mathrm{AP}(q)$",
    "eq_mmap": r"$\mathrm{macro}\;\mathrm{mAP} \;=\; \frac{1}{|\mathcal{I}|}\sum_{I \in \mathcal{I}}\;\frac{1}{|Q_I|}\sum_{q \in Q_I}\mathrm{AP}(q)$",
    "eq_centering": r"$\tilde{e}(x) \;=\; \frac{e(x)-\mu}{\Vert\, e(x)-\mu \,\Vert}$",
    "eq_minnorm": r"$\tilde{s} \;=\; \frac{s - s_{\min}}{|\,s_{\min}\,|}\,,\qquad \tilde{s} \leftarrow \max(\tilde{s},\, 0)$",
    "eq_harris": r"$\tilde{s}^{\,f} \;=\; \tilde{s}^{\,v}\,\tilde{s}^{\,t} \;-\; \lambda\,\left(\tilde{s}^{\,v} + \tilde{s}^{\,t}\right)^{2}$",
    "eq_triplet": r"$\tilde{s}^{\,f} \;=\; \tilde{s}^{\,v}\cdot\tilde{s}^{\,t}\cdot\tilde{s}^{\,c}$",
    "eq_problem": r"$q=(I_q,\,t_q)\ \longrightarrow\ \mathrm{rank\ every}\ x \in \mathcal{X}\ \mathrm{by}\ s(x \mid I_q,\,t_q),\quad |\mathcal{X}| = 752{,}092$",
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

img_q = defaultdict(set)
txt_q = defaultdict(set)
with open(f"{DATA}/query_files.csv") as fh:
    for path, text, inst in csv.reader(fh):
        img_q[inst].add(path)
        txt_q[inst].add(text)
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
    ("(a) image queries / instance", sorted(len(v) for v in img_q.values()),
     np.arange(0.5, 26.5, 1)),
    ("(b) text queries / instance", sorted(len(v) for v in txt_q.values()),
     np.arange(0.5, 6.5, 1)),
    ("(c) hard negatives / instance", sorted(hn_counts), 20),
    ("(d) positives / composed query",
     [min(v, 30) for v in pos_per_query.values()], np.arange(0.5, 31.5, 1)),
]
fig, axes = plt.subplots(1, 4, figsize=(13.2, 3.1), dpi=200)
for i, (ax, (title, vals, bins)) in enumerate(zip(axes, panels)):
    med = statistics.median(vals)
    ax.hist(vals, bins=bins, color=BLUE, edgecolor="white", linewidth=0.6)
    ax.axvline(med, color=ORANGE, lw=2)
    ax.text(0.97, 0.92, f"median {med:g}", transform=ax.transAxes, ha="right",
            fontsize=10.5, color=ORANGE, style="italic")
    if i == 3:
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
