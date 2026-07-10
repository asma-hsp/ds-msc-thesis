"""Charts for the defense deck. Light surface (white slides).
Palette: BASIC = blue #2a78d6 (dataviz reference slot 1), Ours = UniPD red #9B0014
(brand accent; identity also carried by direct labels + legend, never color alone).
Chrome: muted ink axes, hairline grid, primary ink labels.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

OUT = "/extra/ahoseinp/projects/ds-msc-thesis/slides/assets"
import os
os.makedirs(OUT, exist_ok=True)

INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
BASIC_C = "#2a78d6"
OURS_C = "#9B0014"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "text.color": INK,
    "axes.edgecolor": BASELINE,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.linewidth": 0.8,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

def clean_axes(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)

RUNGS = ["raw\n(img × text)", "+ centering", "+ sim-norm", "+ Harris", "+ context",
         "+ projection", "+ query-exp."]

def ladder_chart(basic, ours, fname, peak_idx=4, ylim=None, headline=None):
    fig, ax = plt.subplots(figsize=(8.6, 4.1), dpi=200)
    clean_axes(ax)
    x = range(len(RUNGS))
    # shaded 'dropped' region after +context
    ax.axvspan(peak_idx + 0.35, len(RUNGS) - 0.6, color="#f0efec", zorder=0)
    ax.text(peak_idx + 1.5, ylim[1] - 1.2, "hurt performance\n→ dropped",
            ha="center", va="top", fontsize=10.5, color=MUTED, style="italic")
    ax.plot(x, basic, "-o", color=BASIC_C, linewidth=2, markersize=7, label="BASIC")
    ax.plot(x, ours, "-o", color=OURS_C, linewidth=2, markersize=7,
            label="Ours: img × txt × caption (avg-5)")
    # direct labels: first and peak points of each series
    for series, color, dy in ((basic, BASIC_C, -2.6), (ours, OURS_C, 1.4)):
        for i in (0, peak_idx):
            ax.annotate(f"{series[i]:.1f}", (i, series[i]),
                        textcoords="offset points", xytext=(0, 14 if dy > 0 else -20),
                        ha="center", fontsize=11.5, fontweight="bold", color=color)
    if headline:
        ax.annotate(headline, (peak_idx, ours[peak_idx]),
                    textcoords="offset points", xytext=(0, 30), ha="center",
                    fontsize=12, fontweight="bold", color=OURS_C)
    ax.set_xticks(list(x))
    ax.set_xticklabels(RUNGS, fontsize=10.5, color=INK)
    ax.set_ylabel("macro-mAP", fontsize=11)
    if ylim:
        ax.set_ylim(*ylim)
    ax.legend(loc="lower center", frameon=False, fontsize=11)
    fig.tight_layout()
    fig.savefig(f"{OUT}/{fname}", facecolor="white")
    plt.close(fig)

# CLIP-L ladder — docs/final_ablation_clip_l.csv (BASIC vs Ours avg-5)
ladder_chart(
    basic=[17.95, 27.76, 27.40, 28.33, 32.25, 32.48, 30.28],
    ours=[25.41, 31.87, 31.97, 32.82, 35.76, 33.80, 32.39],
    fname="ladder_clipl.png", ylim=(14, 41),
)

# SigLIP2 ladder — runs/caption_backbone_instancepool/siglip2_ladder/summary_ladder.csv
ladder_chart(
    basic=[38.12, 49.96, 45.49, 47.64, 57.69, 52.67, 49.56],
    ours=[56.09, 55.51, 53.70, 55.87, 61.98, 59.02, 57.29],
    fname="ladder_siglip2.png", ylim=(34, 70),
)

# Backbone comparison — docs/backbone_recall.csv (macro-mAP, raw scores, no post-proc)
backbones = ["CLIP-L", "CLIP-H", "SigLIP-L", "SigLIP2"]
basic = [17.95, 41.10, 21.10, 38.11]
ours = [25.41, 47.05, 43.33, 56.09]
fig, ax = plt.subplots(figsize=(8.6, 4.1), dpi=200)
clean_axes(ax)
w = 0.34
xs = range(len(backbones))
b1 = ax.bar([i - w / 2 for i in xs], basic, width=w - 0.03, color=BASIC_C, label="img × txt")
b2 = ax.bar([i + w / 2 for i in xs], ours, width=w - 0.03, color=OURS_C,
            label="Ours: img × txt × caption (avg-5)")
for bars, color in ((b1, BASIC_C), (b2, OURS_C)):
    for r in bars:
        ax.annotate(f"{r.get_height():.1f}", (r.get_x() + r.get_width() / 2, r.get_height()),
                    textcoords="offset points", xytext=(0, 4), ha="center",
                    fontsize=11.5, fontweight="bold", color=color)
ax.set_xticks(list(xs))
ax.set_xticklabels(backbones, fontsize=12, color=INK)
ax.set_ylabel("macro-mAP", fontsize=11)
ax.set_ylim(0, 64)
ax.legend(loc="upper left", frameon=False, fontsize=11)
fig.tight_layout()
fig.savefig(f"{OUT}/backbones.png", facecolor="white")
plt.close(fig)
print("charts written to", OUT)
