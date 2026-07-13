"""Render the THESIS pipeline figures to PNGs for the slides — the exact same
TikZ sources the thesis uses, no hand-made substitutes.

  figures/pipeline_overview.tex -> slides/assets/pipeline_thesis.png  (our method)
  figures/pipeline_basic.tex    -> slides/assets/pipeline_basic.png   (BASIC baseline:
                                   same layout and styling, caption branch removed)

Needs a LaTeX engine. On the cluster there is none by default; grab tectonic once:

    curl -sL -o /tmp/tect.tar.gz \\
      https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.15.0/tectonic-0.15.0-x86_64-unknown-linux-musl.tar.gz
    tar xzf /tmp/tect.tar.gz -C /tmp

Then:  python slides/make_pipeline_figure.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

import fitz  # pymupdf

REPO = "/extra/ahoseinp/projects/ds-msc-thesis"
TECTONIC = shutil.which("tectonic") or "/tmp/tectonic"
DPI = 300  # standalone page is small, so this stays well within memory

FIGURES = [
    ("figures/pipeline_overview", "pipeline_thesis.png"),
    ("figures/pipeline_basic",    "pipeline_basic.png"),
]

WRAPPER = r"""\documentclass[border=4pt]{standalone}
\usepackage{graphicx}
\usepackage{amsmath,amssymb,bm}
\usepackage{xcolor}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,shapes.geometric,positioning,calc,backgrounds,fit,
                shapes.multipart,decorations.pathreplacing}
\begin{document}
\input{%s}
\end{document}
"""

if not os.path.exists(TECTONIC):
    sys.exit(f"no LaTeX engine at {TECTONIC} — see the docstring")

for src, out_name in FIGURES:
    out = os.path.join(REPO, "slides", "assets", out_name)
    tex = os.path.join(REPO, "_pipe_standalone.tex")
    with open(tex, "w") as fh:
        fh.write(WRAPPER % src)
    try:
        with tempfile.TemporaryDirectory() as td:
            subprocess.run([TECTONIC, "-X", "compile", tex, "--outdir", td],
                           cwd=REPO, check=True)
            pdf = os.path.join(td, "_pipe_standalone.pdf")
            pix = fitz.open(pdf)[0].get_pixmap(dpi=DPI)
            pix.save(out)
            print(f"wrote {out}  ({pix.width}x{pix.height} @ {DPI} dpi)")
    finally:
        if os.path.exists(tex):
            os.remove(tex)
