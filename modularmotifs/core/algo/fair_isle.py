""" Fair isle is a style of stranded colorwork knitting.

https://en.wikipedia.org/wiki/Fair_Isle_(technique)
"""

from modularmotifs.core import Design, Color, Motif, Colorization, TwoColorsPerRow
from modularmotifs.core.design import RGBColor
import random

def rowizable(d: Design) -> bool:
    """ Traditional fair isle sweaters and the like are usually arranged in rows of motifs, though this isn't necessarily always true. Eventually I want this algorithm to be able to make smarter decisions, but for now, something that just tries to colorize is fine.
    """
    return False


def fair_isle_colorization(d: Design, colors: list[RGBColor], max_colors_per_row: int = 2, random_seed: int = None) -> Colorization:
    """Colorizes a given design in fair isle-style with some colors

    Args:
        d (Design): the design to colorize
        colors (list[RGBColor]): the colors to colorize the design with
        max_colors_per_row (int): the number of colors to use per row, at maximum. Defaults to 2. Currently this argument does nothing.
        random_seed (int): the random seed to use, if any. To be used for testing.

    Returns:
        list[list[RGBColor]]: a list giving the colors to use for the [foreground, background] for each row. If more than two colors per row are permitted, then the return type would likely need to change (because more information would be needed to determine where to place the third color)
    """

    if random_seed is not None:
        random.seed(a=random_seed)
        pass

    assignments = TwoColorsPerRow(d, colors)

    for i in range(d.height()):
        cols = d.row_colors(i)
        if len(cols) == 1:
            # It doesn't matter which
            c = random.choice(colors)
            assignments.set(i, c, c)
            pass
        elif len(cols) > 1:
            twocolors = random.sample(colors, 2)
            assignments.set(i, twocolors[0], twocolors[1])
            pass
        pass
    return assignments
    
    

    # simplest form: for any given row, 
