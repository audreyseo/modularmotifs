""" Utilities """

from modularmotifs.core.motif import Motif, Color
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


