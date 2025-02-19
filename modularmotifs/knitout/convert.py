"""Converts rectangular, 2-colored Designs to Knitout code"""
from modularmotifs.core.motif import Color
from modularmotifs.knitout import knitout
from modularmotifs.core.design import Design

FORE = '1'
BACK = '2'

def convert_knitout(design: Design, path: str) -> None:
    """Converts a complete design to Knitout code

    Args:
        design (Design): complete Design
        path (str): filepath to write Knitout code to
    """
    assert design.complete()
    w = design.width()
    h = design.height()

    carriers = [FORE, BACK] # fore, back

    k = knitout.Writer(' '.join(carriers))

    # cast on with background color
    k.comment("cast on")
    k.ingripper(BACK)
    for i in range(1, w+1, 2):
        k.tuck('+', f'f{i}', BACK)
    reverse_tuck_start = w if w % 2 == 0 else w - 1
    for i in range(reverse_tuck_start, 0, -2):
        k.tuck('-', f'f{i}', BACK)

    # knit the work
    k.comment("knit the work")
    k.ingripper(FORE)
    for j in range(h):
        if j % 2 == 0: # left to right
            for i in range(1, w+1):
                col = design.get_color(i-1, h-j-1)
                carrier = BACK if col == Color.BACK else FORE
                k.knit('+', f'f{i}', carrier)
        else:
            for i in range(w, 0, -1):
                col = design.get_color(i-1, h-j-1)
                carrier = BACK if col == Color.BACK else FORE
                k.knit('-', f'f{i}', carrier)

    #bind off
    k.comment("bind off")
    if h % 2 == 0: # left to right
        for i in range(1, w): # one less than before
            k.xfer(f'f{i}', f'b{i}')
            k.rack(1)
            k.xfer(f'b{i}', f'f{i+1}')
            k.rack(-1)
            k.knit('+', f'f{i+1}', BACK)
    else: # right to left
        for i in range(w, 1, -1): # one less than before
            k.xfer(f'f{i}', f'b{i}')
            k.rack(-1)
            k.xfer(f'b{i}', f'f{i-1}')
            k.rack(1)
            k.knit('+', f'f{i-1}', BACK)

    k.outgripper(FORE)
    k.outgripper(BACK)

    k.write(path)
