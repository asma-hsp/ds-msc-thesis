"""Render the THESIS pipeline figure (figures/pipeline_overview.tex) to a PNG
for the slides — no hand-made substitute, the exact same TikZ source the thesis uses.

Needs a LaTeX engine. On the cluster there is none by default; grab tectonic once:

    curl -sL -o /tmp/tect.tar.gz \\
      https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.15.0/tectonic-0.15.0-x86_64-unknown-linux-musl.tar.gz
    tar xzf /tmp/tect.tar.gz -C /tmp

Then:  python slides/make_pipeline_figure.py
Output: slides/assets/pipeline_thesis.png
"""
import os
import shutil
import subprocess
import sys
import tempfile

import fitz  # pymupdf

REPO = "/extra/ahoseinp/projects/ds-msc-thesis"
OUT = f"{REPO}/slides/assets/pipeline_thesis.png"
TECTONIC = shutil.which("tectonic") or "/tmp/tectonic"
DPI = 170  # 300 dpi OOMs on the login node

WRAPPER = r"""\documentclass[border=4pt]{standalone}
\usepackage{graphicx}
\usepackage{amsmath,amssymb,bm}
\usepackage{xcolor}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,shapes.geometric,positioning,calc,backgrounds,fit,
                shapes.multipart,decorations.pathreplacing}
\begin{document}
\input{figures/pipeline_overview}
\end{document}
"""

if not os.path.exists(TECTONIC):
    sys.exit(f"no LaTeX engine at {TECTONIC} — see the docstring")

tex = os.path.join(REPO, "_pipe_standalone.tex")
with open(tex, "w") as fh:
    fh.write(WRAPPER)

with tempfile.TemporaryDirectory() as td:
    subprocess.run([TECTONIC, "-X", "compile", tex, "--outdir", td],
                   cwd=REPO, check=True)
    pdf = os.path.join(td, "_pipe_standalone.pdf")
    fitz.open(pdf)[0].get_pixmap(dpi=DPI).save(OUT)

os.remove(tex)
print("wrote", OUT)
