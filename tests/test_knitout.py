"""Tests the knitout conversion"""
from modularmotifs.core.design import Design
from modularmotifs.core.motif import Motif
from modularmotifs.motiflibrary.examples import motifs
from modularmotifs.knitout.convert import convert_knitout

def tile_motif(motif: Motif, w: int, h: int) -> Design:
    """Creates a design by tiling a motif

    Args:
        motif (Motif): motif to be tiled
        w (int): Number of motifs width-wise
        h (int): Number of motifs height-wise

    Returns:
        Design: Tiled motifs
    """
    d = Design(motif.width() * w, motif.height() * h)
    for x in range(w):
        for y in range(h):
            d.add_motif(motif, x*motif.width(), y*motif.height())
    return d


def test_basic_convert():
    """Makes sure basic conversion doesn't crash"""
    d = tile_motif(motifs["plus-3x3"], 3, 3)
    convert_knitout(d, "basic_convert.k")
