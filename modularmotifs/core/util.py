""" Utilities """

from modularmotifs.core.motif import Motif, Color
from modularmotifs.core.design import Design
from typing import Optional
from PIL import Image


# ====================================================
# Motif PNG conversion
# black is foreground white is background
# ====================================================
def png2motif(png_path: str) -> Motif:
    img = Image.open(png_path).convert("1")  # Force binary color
    pixels = img.load()
    bbox: list[list[Color]] = []
    for x in range(img.size[1]):
        row: list[Color] = []
        for y in range(img.size[0]):
            if pixels[y, x] == 0:
                row.append(Color.FORE)
            elif pixels[y, x] == 255:
                row.append(Color.BACK)
            else:
                raise ValueError
        bbox.append(row)
    return Motif(bbox)


def motif2png(motif: Motif) -> Image.Image:
    w, h = motif.width(), motif.height()
    img = Image.new("1", (w, h))
    pixels = img.load()
    for x, row in enumerate(motif):
        for y, color in enumerate(row):
            if color == Color.FORE:
                pixels[y, x] = 0
            elif color == Color.BACK:
                pixels[y, x] = 255
            elif color == Color.INVIS:
                pixels[y, x] = 255  # set invis to white, can change alpha later
            else:
                raise ValueError
    return img


def design_to_lol(d: Design, mapper = None) -> list[list[int]]:
    lol = []
    for i in range(d.height()):
        newrow = []
        for j in range(d.width()):
            val = d.get_color(j, i).value
            if mapper is not None and val in mapper:
                newrow.append(mapper[val])
                pass
            else:
                newrow.append(val)
                pass
            pass
        lol.append(newrow)
        pass
    return lol
