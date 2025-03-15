""" Utilities """

from modularmotifs.core.motif import Motif, Color
from modularmotifs.core.design import Design, RGBAColor
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


def rgbcolors_to_image(lol: list[list[RGBAColor]], square_size=1, mode="RGB", opacity=255) -> Image.Image:
    """Convert a list of list of RGBAColors to an image

    Arguments
      lol (list[list[RGBAColor]]): a list of lists of RGBAColor objects - i.e., a 2d list representing the colors in the image.
      square_size (int): the default size (in pixels) of the square that represents each color. Defaults to 1
      mode (str): the image mode to use. Currently not implemented! Defaults to "RGB" -- the only option currently supported

    Returns:
      Image.Image, a PIL.Image.Image object where each "square" has the corresponding color from the input 2d list
    """
    assert lol and lol[0], f"{rgbcolors_to_image.__qualname__}: 2d list of RGBAColors must be non-empty -- {lol}"
    h = len(lol)
    w = len(lol[0])
    assert all(len(r) == w for r in lol), f"{rgbcolors_to_image.__qualname__}: each row must have the same length -- {lol}"
    if mode != "RGB" and mode != "RGBA":
        raise NotImplementedError(f"{rgbcolors_to_image.__qualname__}: modes other than RGB are not yet supported (mode: {mode})")
    img = Image.new(mode, (w * square_size, h * square_size))
    pixels = img.load()
    if square_size == 1:
        for y in range(h):
            for x in range(w):
                if mode == "RGB":
                    pixels[x, y] = lol[y][x].rgb_tuple()
                elif mode == "RGBA":
                    pixels[x, y] = lol[y][x].rgba_tuple(opacity=opacity)
                pass
            pass
        return img
    
    for y in range(h):
        for x in range(w):
            color = lol[y][x]
            for i in range(square_size):
                for j in range(square_size):
                    if mode == "RGB":
                        pixels[x * square_size + i, y * square_size + j] = color.rgb_tuple()
                    elif mode == "RGBA":
                        pixels[x * square_size + i, y * square_size + j] = color.rgba_tuple(opacity=opacity)
                    pass
                pass
            pass
        pass
    return img
            

def design2png(design: Design, square_size: int = 10) -> Image.Image:
    color_grid = []
    for y in range(design.height()):
        row = []
        for x in range(design.width()):
            row.append(design.get_rgb(x, y))
        color_grid.append(row)
    img = rgbcolors_to_image(color_grid, square_size=square_size)
    return img

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

def motif_to_lol(m: Motif) -> list[list[RGBAColor]]:
    lol = []
    for i in range(m.height()):
        newrow = []
        for j in range(m.width()):
            newrow.append(m.get_rgba(j, i))
            pass
        lol.append(newrow)
        pass
    return lol