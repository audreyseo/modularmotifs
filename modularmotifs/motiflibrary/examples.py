from modularmotifs.core.motif import Color, Motif

def int_to_color(i: int) -> Color:
    assert (i == 1 or i == 2 or i == 3), f"int_to_color: {i} must be one of 1 (foreground), 2 (background), or 3 (invisible)"

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



motifs = {
    "plus-3x3": int_lol_to_color_lol([[2, 1, 2],
                                  [1, 1, 1],
                                  [2, 1, 2]]),
    "x-3x3": int_lol_to_color_lol([[1, 2, 1],
                                   [2, 1, 2],
                                   [1, 2, 1]]),
    "crosshair-3x3": int_lol_to_color_lol([[2, 1, 2],
                                           [1, 2, 1],
                                           [2, 1, 2]]),
    "triangle1-5x9": int_lol_to_color_lol([[3, 3, 3, 3, 1, 3, 3, 3, 3],
                                           [3, 3, 3, 1, 1, 1, 3, 3, 3],
                                           [3, 3, 1, 1, 3, 1, 1, 3, 3],
                                           [3, 1, 1, 3, 1, 3, 1, 1, 3],
                                           [1, 1, 1, 1, 1, 1, 1, 1, 1]])

}
