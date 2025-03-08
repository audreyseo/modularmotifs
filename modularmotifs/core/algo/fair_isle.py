""" Fair isle is a style of stranded colorwork knitting.

https://en.wikipedia.org/wiki/Fair_Isle_(technique)
"""

import numpy as np
from modularmotifs.core import Design, Color, Motif, Colorization, TwoColorsPerRow
from modularmotifs.core.colorization import Change, PrettierTwoColorRows
from modularmotifs.core.design import RGBAColor
import random


def rowizable(d: Design) -> bool:
    """Traditional fair isle sweaters and the like are usually arranged in rows of motifs, though this isn't necessarily always true. Eventually I want this algorithm to be able to make smarter decisions, but for now, something that just tries to colorize is fine."""
    return False


def fair_isle_colorization(
    d: Design,
    colors: list[RGBAColor],
    max_colors_per_row: int = 2,
    random_seed: int = None,
) -> Colorization:
    """Colorizes a given design in fair isle-style with some colors

    Args:
        d (Design): the design to colorize
        colors (list[RGBAColor]): the colors to colorize the design with
        max_colors_per_row (int): the number of colors to use per row, at maximum. Defaults to 2. Currently this argument does nothing.
        random_seed (int): the random seed to use, if any. To be used for testing.

    Returns:
        list[list[RGBAColor]]: a list giving the colors to use for the [foreground, background] for each row. If more than two colors per row are permitted, then the return type would likely need to change (because more information would be needed to determine where to place the third color)
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

def fair_isle_colorization_new(p: PrettierTwoColorRows, random_seed: int = None):
    
    if random_seed is not None:
        np.random.seed(seed=random_seed)
        pass
    
    rng = np.random.default_rng()
    
    def choice(a: np.ndarray) -> int:
        return int(rng.choice(a, size=1, replace=False))
    
    colors = p._colors
    ncolors = np.arange(len(colors))
    
    sample = rng.choice(ncolors, size=2, replace=False)
    
    p.set(0, *[int(s) for s in sample])
    
    for i in range(1, p.height()):
        change = p.get_change(i)
        match change.perms.to_str():
            case "SAME":
                p.set(i, *p.last(i))
            case "CHANGE_FG":
                lastbg = p.last_bg(i)
                p.set(i, choice(ncolors[ncolors != lastbg]), p.last_bg(i))
            case "CHANGE_BG":
                lastfg = p.last_fg(i)
                p.set(i, lastfg, choice(ncolors[ncolors != lastfg]))
            case "CHANGE_EITHER":
                # xor
                lastfg, lastbg = p.last(i)
                c = choice(ncolors[(ncolors != lastbg) & (ncolors != lastfg)])
                if random.randint(0, 1) == 0:
                    # fg
                    p.set(i, c, p.last_bg(i))
                else:
                    p.set(i, p.last_fg(i), c)
            case "CHANGE_OR":
                # inclusive or
                r = random.randint(0, 2)
                lastfg, lastbg = p.last(i)
                subset = ncolors[(ncolors != lastfg) & (ncolors != lastbg)]
                if r == 0 or r == 1:
                    c = choice(subset)
                    if r == 0:
                        p.set(i, c, p.last_bg(i))
                    else:
                        p.set(i, p.last_fg(i), c)
                else:
                    p.set(i, *[int(k) for k in rng.choice(subset, size=2, replace=False)])
                    pass
            case "CHANGE_BOTH":
                fg, bg = p.last(i)
                lastfg, lastbg = p.last(i)
                subset = ncolors[(ncolors != lastfg) & (ncolors != lastbg)]
                p.set(i, *[int(k) for k in rng.choice(subset, size=2, replace=False)])
                    
def generate_changes(d: Design) -> list[Change]:
    row_motifs = set()
    changes = []
    for row in d:
        current_motifs = set()
        for _, x, y in row:
            current_motifs = current_motifs.union(d.get_motifs(x, y))
            pass
        if row_motifs != current_motifs:
            row_motifs = current_motifs
            changes.append(Change.from_ints(y, 5, 1))
            pass
        else:
            changes.append(Change.from_ints(y, 1, 1))
            pass
        pass
    return changes
        

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

    colors = [RGBAColor.from_hex("#320E3B"),
              RGBAColor.from_hex("#E56399"),
              RGBAColor.from_hex("#7F96FF"),
              RGBAColor.from_hex("#A6CFD5"),
              RGBAColor.from_hex("#DBFCFF")]

    seed = 1

    colorized = fair_isle_colorization(d, colors, random_seed=seed)
    img = colorized.to_image(square_size=30)
    img.save(f"example{seed}.png")
    


