from modularmotifs.core import Design, Color
from modularmotifs.core.float import FloatStrand
from modularmotifs.ui.util.selection import Selection
from typing import Iterable, Dict


def calculate_float_lengths(
    d: Design,
    treat_invisible_as_bg: bool = False,
    selection: Selection = None,
    min_float_length: int = 1,
    in_the_round: bool = False,
) -> list[FloatStrand]:
    """ """

    if not treat_invisible_as_bg:
        assert d.complete(), f"calculate_float_lengths: design {d} is not complete"

    def opposite_color(c: Color) -> Color:
        if c == Color.FORE:
            return Color.BACK
        if c == Color.BACK:
            return Color.FORE

        assert (
            treat_invisible_as_bg
        ), f"calculate_float_lengths: color should not be invisible"
        return Color.FORE

    floats: list[FloatStrand] = []

    for row in d:
        lastcolor = None
        lastx = -1

        for c, x, y in row:
            opp_color = opposite_color(c)
            if lastcolor is None:
                # print(c, opp_color)
                lastcolor = opp_color
                pass
            elif lastcolor == opposite_color(opp_color):  # double negation essentially
                # we must have switched colors
                length = x - lastx - 1
                if length >= min_float_length:
                    # print(lastx, length, y, lastcolor)
                    floats.append(FloatStrand(lastx, length, row=y, color=lastcolor))
                lastx = x - 1
                lastcolor = opp_color
                pass
            else:
                # lastcolor is still the opposite of the current color
                continue
            pass
        if lastcolor and (not in_the_round or lastx != -1):
            # essentially, was the other color used at all?
            # actually, this is faulty -- you'll need to bring the other yarn over if you need it. you can only do this if you're knitting in the round
            # TODO: FIX
            floats.append(
                FloatStrand(lastx, d.width() - lastx - 1, row=y, color=lastcolor)
            )
            pass
        pass
    return floats
