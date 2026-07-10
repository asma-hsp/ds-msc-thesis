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
    axt.text(0.5, 0.5, label, ha="center", va="center", fontsize=13.5,
             color=BLUE, family="monospace")

    axp = fig.add_subplot(gs[1, c])
    axp.imshow(letterbox(f"{TINTIN_DB}/{qdir}/{pos}"))
    axp.set_xticks([]); axp.set_yticks([])
    for sp in axp.spines.values():
        sp.set_edgecolor("#cccccc"); sp.set_linewidth(0.8)
    axp.text(0.985, 0.03, f"1 of {npos}", transform=axp.transAxes, ha="right",
             va="bottom", fontsize=10, color="white",
             bbox=dict(boxstyle="round,pad=0.25", fc=GREEN, ec="none", alpha=0.9))

    axn = fig.add_subplot(gs[2, c])
    axn.imshow(letterbox(f"{TINTIN_DB}/hn/tintin_hn{hn}.jpg"))
    axn.set_xticks([]); axn.set_yticks([])
    for sp in axn.spines.values():
        sp.set_edgecolor("#cccccc"); sp.set_linewidth(0.8)

fig.text(0.585, 0.395, "composed positives", ha="center", fontsize=17,
         family="serif", color=INK)
fig.text(0.685, 0.395, "(each query has 3–14 ground truths)", ha="left",
         fontsize=12.5, family="serif", color=GRAY)
fig.text(0.585, 0.012, "hard negatives", ha="center", fontsize=17,
         family="serif", color=INK)
fig.text(0.665, 0.012, "(from the instance's pool of 5,128 curated distractors)",
         ha="left", fontsize=12.5, family="serif", color=GRAY)
fig.savefig(f"{OUT}/icir_tintin.png", facecolor="white")
plt.close(fig)

# ------------------------------------------------------------------
# 2. category-level vs instance-level
# ------------------------------------------------------------------
results = [f"{TINTIN_DB}/on_a_t-shirt/tintin_on_a_t-shirt_pos03.jpg",
           f"{TINTIN_DB}/hn/tintin_hn4311.jpg",
           f"{TINTIN_DB}/hn/tintin_hn4295.jpg"]
rows = [
    ("Category-level", "“a cartoon character\non a t-shirt”", [True, True, True]),
    ("Instance-level", "“this character\non a t-shirt”", [True, False, False]),
]
fig = plt.figure(figsize=(11.5, 5.6), dpi=200)
gs = fig.add_gridspec(2, 5, width_ratios=[1, 1.15, 1, 1, 1], hspace=0.42,
                      wspace=0.12, left=0.01, right=0.99, top=0.90, bottom=0.03)
for r, (mode, qtext, oks) in enumerate(rows):
    axq = fig.add_subplot(gs[r, 0])
    axq.imshow(letterbox(f"{DATA}/query/tintin/tintin_image_query1.jpg"))
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
# 3. CLIP dual-encoder contrastive schematic
# ------------------------------------------------------------------
imgs = [f"{DATA}/query/tintin/tintin_image_query1.jpg",
        "/extra/ahoseinp/projects/ds-msc-thesis/figures/pipeline_samples/ref.jpg",
        "/extra/ahoseinp/projects/ds-msc-thesis/figures/pipeline_samples/db3.jpg"]
texts = ["“a comic-book character\nwith a white dog”",
         "“an ancient Greek temple\non a cliff”",
         "“…”"]
texts_short = ["“a comic character\nwith a white dog”",
               "“a Greek temple\non a cliff”", "“ … ”"]
fig, ax = plt.subplots(figsize=(11.5, 5.4), dpi=200)
ax.set_xlim(0, 11.5); ax.set_ylim(0, 5.4); ax.axis("off")

def rbox(x, y, w, h, label, fc="#f0efec", fontsize=13, tc=INK, bold=True):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", fc=fc,
                       ec=MUTED, lw=1.1)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
            fontsize=fontsize, color=tc, fontweight="bold" if bold else "normal")

# top pipeline: images -> image encoder
for i, im in enumerate(imgs):
    thumb = letterbox(im)
    x0 = 0.3 + i * 1.35
    ax.imshow(thumb, extent=(x0, x0 + 1.2, 3.55, 4.45), aspect="auto", zorder=3)
ax.annotate("", xy=(5.05, 4.0), xytext=(4.45, 4.0),
            arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.6))
rbox(5.1, 3.55, 1.75, 0.9, "image\nencoder")
# bottom pipeline: texts -> text encoder
for i, t in enumerate(texts_short):
    x0 = 1.0 + i * 1.65
    ax.text(x0, 1.0, t, ha="center", va="center", fontsize=8.5, color=BLUE,
            family="monospace",
            bbox=dict(boxstyle="round,pad=0.32", fc="white", ec=BLUE, lw=1.1))
ax.annotate("", xy=(5.05, 1.0), xytext=(4.45, 1.0),
            arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.6))
rbox(5.1, 0.55, 1.75, 0.9, "text\nencoder")
# similarity matrix (right, vertically centered)
mx, my, cell = 8.3, 1.35, 0.85
for i in range(3):
    for j in range(3):
        fc = "#9B0014" if i == j else "#f0efec"
        b = FancyBboxPatch((mx + j * cell, my + (2 - i) * cell), cell * 0.9,
                           cell * 0.9, boxstyle="round,pad=0.02", fc=fc,
                           ec="white", lw=1.5)
        ax.add_patch(b)
ax.annotate("", xy=(mx - 0.12, my + 2.45), xytext=(6.9, 4.0),
            arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.6))
ax.annotate("", xy=(mx - 0.12, my + 0.2), xytext=(6.9, 1.0),
            arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.6))
ax.text(6.95, 3.35, "one vector\nper image", fontsize=9.5, color=GRAY,
        ha="left", va="center")
ax.text(6.95, 1.75, "one vector\nper text", fontsize=9.5, color=GRAY,
        ha="left", va="center")
ax.text(mx + 1.28, my - 0.35,
        "cosine-similarity matrix:\nmatching pairs (diagonal) pulled together,\n"
        "all other pairs pushed apart",
        ha="center", va="top", fontsize=10.5, color=MUTED)
ax.text(mx + 1.28, my + 2.95, "contrastive pre-training\n(400M image–text pairs)",
        ha="center", va="bottom", fontsize=12, color=INK, fontweight="bold")
fig.savefig(f"{OUT}/clip_schematic.png", facecolor="white",
            bbox_inches="tight")
plt.close(fig)

# ------------------------------------------------------------------
# 4. formula renders
# ------------------------------------------------------------------
EQS = {
    "eq_ap": r"$\mathrm{AP}(q) \;=\; \sum_{i \geq 1}\,(r_i - r_{i-1})\;\frac{p_i + p_{i-1}}{2}$",
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
