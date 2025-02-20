""" Fair isle is a style of stranded colorwork knitting.

https://en.wikipedia.org/wiki/Fair_Isle_(technique)
"""

from modularmotifs.core import Design, Color, Motif, Colorization, TwoColorsPerRow
from modularmotifs.core.design import RGBColor
import random


def rowizable(d: Design) -> bool:
    """Traditional fair isle sweaters and the like are usually arranged in rows of motifs, though this isn't necessarily always true. Eventually I want this algorithm to be able to make smarter decisions, but for now, something that just tries to colorize is fine."""
    return False


def fair_isle_colorization(
    d: Design,
    colors: list[RGBColor],
    max_colors_per_row: int = 2,
    random_seed: int = None,
) -> Colorization:
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
        cols = set(d.row_colors(i))
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
    return assignments    # simplest form: for any given row,

if __name__ == "__main__":
    # do some very basic testing out of stuff...
    from modularmotifs.motiflibrary.examples import motifs
    from modularmotifs.core.util import design_to_lol

    d = Design(height=11, width=11)
    d.add_motif(motifs["plus-3x3"], 0, 0)
    d.add_motif(motifs["x-3x3"], 4, 0)
    d.add_motif(motifs["plus-3x3"], 8, 0)
    d.add_motif(motifs["x-3x3"], 0, 4)
    d.add_motif(motifs["plus-3x3"], 4, 4)
    d.add_motif(motifs["x-3x3"], 8, 4)
    d.add_motif(motifs["plus-3x3"], 0, 8)
    d.add_motif(motifs["x-3x3"], 4, 8)
    d.add_motif(motifs["plus-3x3"], 8, 8)

    for r in d:
        for (col, x, y) in r:
            print(x, y, col)
            pass
        pass

    lol = design_to_lol(d, mapper={1: 0, 2: 1, 3: 1})

    for r in lol:
        print(" ".join(list(map(str, r))))
        pass

    colors = [RGBColor.from_hex("#320E3B"),
              RGBColor.from_hex("#E56399"),
              RGBColor.from_hex("#7F96FF"),
              RGBColor.from_hex("#A6CFD5"),
              RGBColor.from_hex("#DBFCFF")]

    colorized = fair_isle_colorization(d, colors, random_seed=1)
    img = colorized.to_image(square_size=30)
    img.save("example3.png")
    


