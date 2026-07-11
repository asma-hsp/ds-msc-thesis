"""Render a chooser sheet: query image + modification text + one target,
for ~24 committee-relatable candidates. Numbered so the user can pick.
"""
import os
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA = "/extra/ahoseinp/projects/thesis_cir/data/icir"
OUT = "/tmp/claude-21121/-extra-ahoseinp-projects-thesis-cir/b23825ed-e377-4287-a66c-a0c9c2039154/scratchpad"

# (id, instance, modification_text, subfolder, group)
CANDS = [
    # --- Italian landmarks: instantly relatable to a Padova committee ---
    ("leaning_tower_of_pisa", "with a person pretending to hold it up", "with_a_person_pretending_to_hold_it_up", "Italy"),
    ("leaning_tower_of_pisa", "as vivid pop art", "as_vivid_pop_art", "Italy"),
    ("colosseum", "as a digital illustration with a Christmas tree in front", "as_a_digital_illustration_with_a_Christmas_tree_in_front", "Italy"),
    ("pantheon_rome", "as a painting", "as_a_painting", "Italy"),
    ("ponte_vecchio_florence", "at night", "at_night", "Italy"),
    ("piazza_san_marco_venice", "as a photo reflecting on water", "as_a_photo_reflecting_on_water", "Italy"),
    ("portofino_italy", "as a painting", "as_a_painting", "Italy"),
    ("matera_italy", "during sunset", "during_sunset", "Italy"),
    ("alberobello_italy", "as a pen sketch", "as_a_pen_sketch", "Italy"),
    # --- world landmarks with human / evocative modifications ---
    ("taj_mahal", "with a man proposing to a woman in front", "with_a_man_proposing_to_a_woman_in_front", "World"),
    ("golden_gate_bridge", "with fog", "with_fog", "World"),
    ("mount_fuji_japan", "as japanese art", "as_japanese_art", "World"),
    ("machu_pichu", "with fog", "with_fog", "World"),
    # --- iconic products (business / economics / engineer) ---
    ("chanel_nr_5", "as a painting", "as_a_painting", "Product"),
    ("converse_all_star_red_high_top", "with yellow shoelaces", "with_yellow_shoelaces", "Product"),
    ("ferrari_f40", "with snow", "with_snow", "Product"),
    ("delorean_dmc_12", "as a miniature", "as_a_miniature", "Product"),
    ("vespa_946", "with a person sitting on", "with_a_person_sitting_on", "Product"),
    ("tesla_cybertruck", "as a lego", "as_a_lego", "Product"),
    ("nintendo_game_boy", "along with the tetris game cartridge", "along_with_the_tetris_game_cartridge", "Product"),
    ("corona_beer_bottle", "held in hand on a beach", "held_in_hand_on_a_beach", "Product"),
    # --- design / engineering / science icons ---
    ("eames_lounge_chair", "in a vintage magazine page", "in_a_vintage_magazine_page", "Design"),
    ("saturn_v_space_rocket", "during liftoff", "during_liftoff", "Design"),
    ("air_france_concorde", "with a crowd in front", "with_a_crowd_in_front", "Design"),
    ("canon_ae-1_programm", "with a film around", "with_a_film_around", "Design"),
    ("mask_of_agamemnon", "as a painting", "as_a_painting", "Design"),
]

def first_img(d):
    for f in sorted(os.listdir(d)):
        if f.lower().endswith((".jpg", ".jpeg", ".png")):
            return os.path.join(d, f)
    return None

def letterbox(path, size):
    im = Image.open(path).convert("RGB")
    im.thumbnail((size, size))
    canvas = Image.new("RGB", (size, size), (255, 255, 255))
    canvas.paste(im, ((size - im.width) // 2, (size - im.height) // 2))
    return canvas

rows = []
for inst, mod, sub, group in CANDS:
    qdir = f"{DATA}/query/{inst}"
    tdir = f"{DATA}/database/{inst}/{sub}"
    q = first_img(qdir)
    t = first_img(tdir) if os.path.isdir(tdir) else None
    if q is None or t is None:
        print("MISSING", inst, sub, os.path.isdir(tdir))
        continue
    rows.append((inst, mod, group, q, t))

n = len(rows)
cols = 2
rws = (n + cols - 1) // cols
TH = 140
cellw, cellh = TH * 2 + 90, TH + 96
sheet = Image.new("RGB", (cellw * cols, cellh * rws + 40), (250, 250, 248))
d = ImageDraw.Draw(sheet)
try:
    fbold = ImageFont.truetype("/extra/ahoseinp/conda_envs/thesis-cir/lib/python3.10/site-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSans-Bold.ttf", 18)
    freg = ImageFont.truetype("/extra/ahoseinp/conda_envs/thesis-cir/lib/python3.10/site-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSans.ttf", 15)
    fsm = ImageFont.truetype("/extra/ahoseinp/conda_envs/thesis-cir/lib/python3.10/site-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSans.ttf", 12)
except Exception:
    fbold = freg = fsm = ImageFont.load_default()

GROUP_C = {"Italy": (0x1a, 0x7a, 0x1a), "World": (0x2a, 0x78, 0xd6),
           "Product": (0x9B, 0x00, 0x14), "Design": (0xb8, 0x6a, 0x00)}

for i, (inst, mod, group, q, t) in enumerate(rows):
    r, c = divmod(i, cols)
    x0, y0 = c * cellw + 20, r * cellh + 30
    # number + instance name + group
    d.text((x0, y0), f"{i+1}.", font=fbold, fill=(20, 20, 20))
    d.text((x0 + 34, y0 + 1), inst.replace("_", " "), font=fbold, fill=(20, 20, 20))
    d.text((x0 + 34, y0 + 23), group, font=fsm, fill=GROUP_C.get(group, (100, 100, 100)))
    # full modification text on its own line
    d.text((x0, y0 + 44), "“" + mod + "”", font=freg, fill=(0x2a, 0x78, 0xd6))
    # query image  →  target image
    iy = y0 + 72
    sheet.paste(letterbox(q, TH), (x0, iy))
    d.text((x0 + TH + 12, iy + TH // 2 - 12), "→", font=fbold, fill=(0x9B, 0x00, 0x14))
    sheet.paste(letterbox(t, TH), (x0 + TH + 44, iy))

sheet.save(f"{OUT}/candidates_sheet.png")
print("wrote sheet with", n, "candidates")
