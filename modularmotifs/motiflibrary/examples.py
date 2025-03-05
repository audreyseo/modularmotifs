from modularmotifs.core.motif import Color, Motif
from modularmotifs.core.util import png2motif
from pathlib import Path
PATH = Path(__file__).parent.absolute()

def int_to_color(i: int) -> Color:
    assert (
        i == 1 or i == 2 or i == 3
    ), f"int_to_color: {i} must be one of 1 (foreground), 2 (background), or 3 (invisible)"

    if i == 1:
        return Color.FORE
    elif i == 2:
        return Color.BACK
    return Color.INVIS


def int_list_to_color_list(ints: list[int]) -> list[Color]:
    return list(map(int_to_color, ints))


def int_lol_to_color_lol(intss: list[list[int]]) -> list[list[Color]]:
    """Turn an int list of lists (lol) to a color list-of-lists"""
    return list(map(int_list_to_color_list, intss))


def int_lol_to_motif(intss: list[list[int]]) -> Motif:
    """Turn an int list of lists (lol) to a Motif"""
    return Motif(int_lol_to_color_lol(intss))

# 1 = foreground
# 2 = background
# 3 = invisible
motifs = {
    "plus-3x3": int_lol_to_motif([[2, 1, 2], [1, 1, 1], [2, 1, 2]]),
    "x-3x3": int_lol_to_motif([[1, 2, 1], [2, 1, 2], [1, 2, 1]]),
    "crosshair-3x3": int_lol_to_motif([[2, 1, 2], [1, 2, 1], [2, 1, 2]]),
    "triangle1-5x9": int_lol_to_motif(
        [
            [3, 3, 3, 3, 1, 3, 3, 3, 3],
            [3, 3, 3, 1, 1, 1, 3, 3, 3],
            [3, 3, 1, 1, 3, 1, 1, 3, 3],
            [3, 1, 1, 3, 1, 3, 1, 1, 3],
            [1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
    ),
    "meander-8x7": int_lol_to_motif(
        [
            [1, 1, 1, 1, 2, 1, 1],
            [1, 1, 1, 2, 1, 1, 1],
            [1, 1, 2, 1, 1, 1, 1],
            [1, 2, 2, 1, 1, 1, 1],
            [1, 1, 2, 1, 1, 1, 1],
            [1, 1, 1, 2, 1, 1, 1],
            [1, 1, 1, 1, 2, 1, 1],
            [1, 1, 1, 1, 1, 2, 1]
        ]
    ),
    "flower-8x7": int_lol_to_motif(
        [
            [2, 2, 2, 1, 2, 2, 2],
            [2, 2, 1, 1, 1, 2, 2],
            [2, 1, 1, 1, 1, 1, 2],
            [2, 1, 1, 2, 1, 1, 2],
            [2, 1, 1, 1, 1, 1, 2],
            [2, 2, 1, 1, 1, 2, 2],
            [2, 2, 2, 1, 2, 2, 2],
            [2, 2, 2, 1, 2, 2, 2]
        ]
    ),
    "vine-12x7": int_lol_to_motif(
        [
            [2, 2, 1, 2, 2, 2, 2],
            [2, 1, 2, 2, 1, 2, 2],
            [2, 1, 2, 1, 1, 1, 2],
            [2, 1, 2, 2, 1, 2, 2],
            [2, 2, 1, 2, 2, 2, 2],
            [2, 2, 2, 1, 2, 2, 2],
            [2, 2, 2, 2, 1, 2, 2],
            [2, 2, 1, 2, 2, 1, 2],
            [2, 1, 1, 1, 2, 1, 2],
            [2, 2, 1, 2, 2, 1, 2],
            [2, 2, 2, 2, 1, 2, 2],
            [2, 2, 2, 1, 2, 2, 2]
        ]
    ),
    "diag-5x10": int_lol_to_motif(
        [
            [2, 1, 1, 1, 1, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 1, 2, 2, 2, 1, 2],
            [1, 1, 2, 1, 1, 2, 2, 1, 2, 2],
            [1, 1, 1, 2, 1, 2, 1, 2, 2, 2],
            [1, 1, 1, 1, 2, 1, 2, 2, 2, 2]
        ]
    ),
    "square-in-diamond-4x8": int_lol_to_motif(
        [
            [2, 2, 2, 1, 2, 1, 2, 1],
            [2, 2, 2, 1, 1, 2, 1, 1],
            [2, 2, 2, 1, 2, 1, 2, 1],
            [1, 1, 1, 2, 1, 1, 1, 2]
        ]
    ),
    "diamonds-6x6": int_lol_to_motif(
        [
            [2, 1, 2, 2, 2, 1],
            [2, 2, 1, 2, 1, 2],
            [2, 2, 2, 1, 2, 2],
            [2, 2, 1, 2, 1, 2],
            [2, 1, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2]
        ]
    ),
    "leaves-7x6": int_lol_to_motif(
        [
            [2, 2, 2, 1, 1, 1],
            [2, 2, 1, 1, 1, 2],
            [2, 1, 1, 1, 2, 2],
            [1, 2, 2, 2, 1, 1],
            [2, 1, 1, 1, 2, 2],
            [2, 2, 1, 1, 1, 2],
            [2, 2, 2, 1, 1, 1]
        ]
    ),
    "rose-9x12": int_lol_to_motif(
        [
            [2, 2, 2, 1, 2, 1, 1, 1, 2, 2, 2, 2],
            [2, 2, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2],
            [2, 1, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2],
            [2, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 2],
            [2, 1, 1, 2, 1, 1, 2, 2, 1, 1, 2, 2],
            [2, 1, 1, 1, 2, 2, 1, 2, 1, 1, 2, 2],
            [2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 2],
            [2, 2, 1, 1, 1, 1, 2, 2, 1, 2, 2, 2],
            [2, 2, 2, 1, 1, 2, 1, 1, 2, 2, 2, 2]
        ]
    ),
    "wave-12x8": int_lol_to_motif(
        [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [2, 2, 2, 2, 2, 2, 2, 2],
            [2] * 8,
            [2] + [1] * 7,
            [2, 1] + [2] * 5 + [1],
            [2, 1, 2, 1, 1, 1, 2, 1],
            [2, 1, 2, 1, 2, 1, 1, 1],
            [2, 1, 2, 1] + [2] * 4,
            [1, 1, 2] + [1] * 5,
            [2] * 8,
            [2] * 8,
            [1] * 8
        ]
    ),
    "wave-6x7": int_lol_to_motif(
        [
            [2, 2, 1, 1, 1, 2, 2],
            [2, 1, 2, 2, 2, 1, 2],
            [2, 1, 2, 1, 2, 2, 1],
            [2, 2, 1, 2, 1, 2, 1],
            [1, 2, 2, 2, 1, 2, 2],
            [2, 1, 1, 1, 2, 2, 2]
        ]
    ),
    "crown-8x16": int_lol_to_motif(
        [
            [2] * 7 + [1] + [2] * 8,
            [2, 2, 1, 1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 2, 2, 2],
            [2, 1, 2, 2, 2, 1, 2, 1, 2, 1, 2, 2, 2, 1, 2, 2],
            [1, 2, 2, 2, 1, 2, 2, 2, 2, 2, 1, 2, 2, 2, 1, 2],
            [2, 1, 2, 1, 2, 1, 2, 2, 2, 1, 2, 1, 2, 1, 2, 2],
            [2, 2] + [1] * 11 + [2, 2, 2],
            [2, 2, 1] + [2, 1] * 5 + [2, 2, 2],
            [2, 2] + [1] * 11 + [2, 2, 2]
        ]
    ),
    "crown-8x14": int_lol_to_motif(
        [
            [2] * 6 + [1] + [2] * 7,
            [2, 1, 1, 2, 2, 1, 2, 1, 2, 2, 1, 1, 2, 2],
            [1, 2, 2, 1, 2, 1, 2, 1, 2, 1, 2, 2, 1, 2],
            [1, 1, 2, 2, 1, 2, 2, 2, 1, 2, 2, 1, 1, 2],
            [2, 1, 1, 2, 2, 2, 1, 2, 2, 2, 1, 1, 2, 2],
            [2, 2] + [1] * 9 + [2, 2, 2],
            [2] * 3 + [1] * 3 + [2] + [1] * 3 + [2] * 4,
            [2] * 4 + [1] * 5 + [2] * 5
        ]
    )
}

bird_motifs = {str(png) : png2motif(str(png)) for png in (PATH / "bird").glob("*.png")}

def fg_square(w: int) -> Motif:
    """Return a w x w motif where every color is the foreground color"""
    lol = [[1] * w] * w
    return int_lol_to_motif(lol)


def bg_square(w: int) -> Motif:
    """Return a w x w motif where every color is the background color"""
    lol = [[2] * w] * w
    return int_lol_to_motif(lol)


# if __name__ == "__main__":
#     print(fg_square(1))
