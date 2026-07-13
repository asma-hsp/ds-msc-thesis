"""Render slides/presentation_notes.md into a minimal A4 PDF.

Edit presentation_notes.md, then:  python make_notes_pdf.py
Markdown conventions understood:
  '# '  document title (lines after it, until blank, are header meta)
  '## <title> | <budget> | <cum>'  one section per slide
  '> '  callout line (rendered as an indented gray italic note)
  everything else: body paragraphs separated by blank lines
"""
import os
import re
from fpdf import FPDF
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "presentation_notes.md")
OUT = os.path.join(HERE, "presentation_notes.pdf")

RED = (0x9B, 0x00, 0x14)
INK = (0x20, 0x20, 0x20)
MUTED = (0x82, 0x80, 0x7A)

# DejaVu TTFs shipped with matplotlib (cluster has no system TTFs guaranteed)
mpl_fonts = {os.path.basename(f): f for f in font_manager.findSystemFonts()}
def find_font(name):
    for f in font_manager.findSystemFonts():
        if os.path.basename(f) == name:
            return f
    raise FileNotFoundError(name)

pdf = FPDF(format="A4")
pdf.add_font("dejavu", "", find_font("DejaVuSans.ttf"))
pdf.add_font("dejavu", "B", find_font("DejaVuSans-Bold.ttf"))
pdf.add_font("dejavu", "I", find_font("DejaVuSans-Oblique.ttf"))
pdf.set_margins(20, 18, 20)
pdf.set_auto_page_break(True, margin=18)
pdf.add_page()
EPW = pdf.epw  # effective page width

def footer_pages():
    n = pdf.pages_count if hasattr(pdf, "pages_count") else None

with open(SRC) as fh:
    lines = fh.read().splitlines()

i = 0
# --- document title + meta ---
while i < len(lines) and not lines[i].startswith("# "):
    i += 1
title = lines[i][2:].strip()
i += 1
meta = []
while i < len(lines) and lines[i].strip():
    meta.append(lines[i].strip())
    i += 1

pdf.set_font("dejavu", "B", 17)
pdf.set_text_color(*RED)
pdf.multi_cell(EPW, 8, title)
pdf.ln(1)
pdf.set_font("dejavu", "", 9)
pdf.set_text_color(*MUTED)
for m in meta:
    pdf.multi_cell(EPW, 5, m)
pdf.ln(2)
pdf.set_draw_color(*MUTED)
pdf.set_line_width(0.3)
pdf.line(20, pdf.get_y(), 20 + EPW, pdf.get_y())
pdf.ln(4)

# --- sections ---
sec_re = re.compile(r"^## (.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*$")

def flush_para(par, callout=False):
    text = " ".join(par).strip()
    if not text:
        return
    if callout:
        x0 = pdf.get_x()
        y0 = pdf.get_y()
        pdf.set_font("dejavu", "I", 9)
        pdf.set_text_color(*MUTED)
        pdf.set_x(26)
        pdf.multi_cell(EPW - 12, 4.6, text)
        pdf.set_draw_color(*RED)
        pdf.set_line_width(0.6)
        pdf.line(23, y0 + 0.5, 23, pdf.get_y() - 0.5)
        pdf.set_x(x0)
    else:
        pdf.set_font("dejavu", "", 10)
        pdf.set_text_color(*INK)
        pdf.multi_cell(EPW, 5.1, text)
    pdf.ln(1.6)

while i < len(lines):
    line = lines[i]
    if line.strip() == "---":          # horizontal rule
        pdf.ln(2)
        pdf.set_draw_color(*MUTED)
        pdf.set_line_width(0.3)
        pdf.line(20, pdf.get_y(), 20 + EPW, pdf.get_y())
        pdf.ln(3)
        i += 1
        continue
    if line.startswith("# "):          # mid-document part heading
        if pdf.get_y() > 297 - 18 - 40:
            pdf.add_page()
        pdf.ln(2)
        pdf.set_font("dejavu", "B", 14)
        pdf.set_text_color(*RED)
        pdf.multi_cell(EPW, 7, line[2:].strip())
        pdf.ln(2)
        i += 1
        continue
    if line.startswith("## ") and "|" not in line:   # heading without budget | cum
        line = f"{line.rstrip()} | — | —"
    m = sec_re.match(line)
    if m:
        stitle, budget, cum = m.groups()
        # avoid orphan headings near the page bottom
        if pdf.get_y() > 297 - 18 - 30:
            pdf.add_page()
        pdf.ln(2)
        y = pdf.get_y()
        pdf.set_font("dejavu", "B", 12)
        pdf.set_text_color(*RED)
        chip = f"{budget}   ·   {cum}" if budget != "—" else ""
        pdf.cell(EPW - 40, 6.5, stitle)
        pdf.set_font("dejavu", "", 9)
        pdf.set_text_color(*MUTED)
        pdf.cell(40, 6.5, chip, align="R", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1.5)
        i += 1
        continue
    if line.startswith("> "):
        par = []
        while i < len(lines) and lines[i].startswith("> "):
            par.append(lines[i][2:])
            i += 1
        flush_para(par, callout=True)
        continue
    if not line.strip():
        i += 1
        continue
    par = []
    while i < len(lines) and lines[i].strip() and not lines[i].startswith(("## ", "> ")):
        par.append(lines[i])
        i += 1
    flush_para(par)

pdf.output(OUT)
print("wrote", OUT)
