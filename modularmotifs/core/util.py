"""Utilities"""

from modularmotifs.core.motif import Motif, Color
from modularmotifs.core.design import Design, RGBAColor
from typing import Any, Optional, Union
from PIL import Image, ImageDraw
import sys


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


def rectangular_rgbcolors_to_image(
    img: Image.Image,
    w: int,
    h: int,
    lol: list[list[RGBAColor]],
    square_size=1,
    mode="RGB",
    opacity=255,
):
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
                        pixels[x * square_size + i, y * square_size + j] = (
                            color.rgb_tuple()
                        )
                    elif mode == "RGBA":
                        pixels[x * square_size + i, y * square_size + j] = (
                            color.rgba_tuple(opacity=opacity)
                        )
                    pass
                pass
            pass
        pass
    return img


def shape_height(shape: list[tuple[int, int]]):
    ymin = sys.maxsize
    ymax = -sys.maxsize
    for _, y in shape:
        if y < ymin:
            ymin = y
            pass
        if ymax < y:
            ymax = y
            pass
        pass
    # Don't really need absolute value but ehhh just in case...
    return abs(ymax - ymin)


def shape_width(shape: list[tuple[int, int]]):
    xmin = sys.maxsize
    xmax = -sys.maxsize
    for x, _ in shape:
        if x < xmin:
            xmin = x
            pass
        if xmax < x:
            xmax = x
            pass
        pass
    return abs(xmax - xmin)


def list_to_list_of_tuples(shape: list[Any]) -> list[tuple[Any, Any]]:
    assert (
        len(shape) % 2 == 0
    ), f"{list_to_list_of_tuples.__name__}: shape argument has uneven length {len(shape)}"

    points = []
    for i in range(len(shape), step=2):
        points.append((shape[i], shape[i + 1]))
        pass
    return points


def flatten_points(l: list[tuple[Any, Any]]) -> list[Any]:
    flat = []
    for x, y in l:
        flat.append(x)
        flat.append(y)
        pass
    return flat


def normalize_shape(shape: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Normalizes the points in a shape to be non-negative and aligned to the origin (0, 0)

    Args:
        shape (list[tuple[int, int]]): a list of points that describe the outline of the shape.

    Returns:
        list[tuple[int, int]]: a list of points that describe the outline of the shape where the shape is aligned to (0, 0)
    """
    xmin = sys.maxsize
    ymin = sys.maxsize
    for x, y in shape:
        if x < xmin:
            xmin = x
            pass

        if y < ymin:
            ymin = y
            pass
        pass

    return [(x - xmin, y - ymin) for x, y in shape]


def rgbcolors_to_image(
    lol: list[list[RGBAColor]],
    square_size=1,
    mode="RGB",
    opacity=255,
    shape: Union[list[tuple[int, int]], list[int], str] = "rect",
) -> Image.Image:
    """Convert a list of list of RGBAColors to an image

    Arguments
      lol (list[list[RGBAColor]]): a list of lists of RGBAColor objects - i.e., a 2d list representing the colors in the image.
      square_size (int): the default size (in pixels) of the square that represents each color. Defaults to 1
      mode (str): the image mode to use. Currently not implemented! Defaults to "RGB" -- the only option currently supported
      opacity (int): an opacity to override the alpha value. Currently only supported if in RGBA mode. Defaults to 255 (i.e., full opacity or whatever was given by the color originally)
      shape (Union[list[tuple[int, int]], list[int], str]): the shape to use to tile the image. Defaults to "rect" (using squares). If a list, all points will be scaled by square_size -- so shape=[(0, 0), (1, 0), (1, 1), (0, 1)] would give the "same" behavior as shape="rect".

    Returns:
      Image.Image, a PIL.Image.Image object where each "square" has the corresponding color from the input 2d list
    """
    assert (
        lol and lol[0]
    ), f"{rgbcolors_to_image.__qualname__}: 2d list of RGBAColors must be non-empty -- {lol}"
    h = len(lol)
    w = len(lol[0])
    assert all(
        len(r) == w for r in lol
    ), f"{rgbcolors_to_image.__qualname__}: each row must have the same length -- {lol}"
    if mode != "RGB" and mode != "RGBA":
        raise NotImplementedError(
            f"{rgbcolors_to_image.__qualname__}: modes other than RGB are not yet supported (mode: {mode})"
        )
    if shape == "rect":
        img = Image.new(mode, (w * square_size, h * square_size))
        return rectangular_rgbcolors_to_image(
            img, w, h, lol, square_size=square_size, mode=mode, opacity=opacity
        )

    if shape and isinstance(shape[0], int):
        shape = list_to_list_of_tuples(shape)
        pass

    sh = shape_height(shape)
    sw = shape_width(shape)
    # just need to add how much the shape protrudes above and below, and left and right
    total_height = h * square_size + round((sh - 1) * square_size)
    total_width = w * square_size + round((sw - 1) * square_size)

    img = Image.new(mode, (total_width, total_height))
    draw = ImageDraw.Draw(img)

    shape = normalize_shape(shape)

    shape_scaled = [(x * square_size, y * square_size) for x, y in shape]

    for i in range(h):
        y0 = i * square_size
        for j in range(w):
            x0 = j * square_size
            draw.polygon(
                [(x0 + x, y0 + y) for x, y in shape_scaled],
                fill=(
                    lol[i][j].rgba_tuple(opacity=opacity)
                    if mode == "RGBA"
                    else lol[i][j].rgb_tuple()
                ),
                width=0,
            )
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


def design_to_lol(d: Design, mapper=None) -> list[list[int]]:
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


def motif_to_image(
    m: Motif,
    square_size=1,
    mode="RGB",
    opacity=255,
    shape: Union[list[tuple[int, int]], list[int], str] = "rect",
) -> Image.Image:
    return rgbcolors_to_image(
        motif_to_lol(m),
        square_size=square_size,
        mode=mode,
        opacity=opacity,
        shape=shape,
    )


if __name__ == "__main__":
    from modularmotifs.motiflibrary.examples import motifs

    knit = [(0, 0), (0.5, 0.5), (1, 0), (1, 1), (0.5, 1.5), (0, 1)]

    img = motif_to_image(
        motifs["x-3x3"], square_size=20, mode="RGBA", opacity=127, shape=knit
    )
    img.save("knit_test.png")
