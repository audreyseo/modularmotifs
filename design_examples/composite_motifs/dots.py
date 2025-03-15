from modularmotifs.core import Design
from modularmotifs.core import CompositeMotif
import modularmotifs.motiflibrary.examples as libexamples

x0 = CompositeMotif(10, 10)



x1, x2 = x0.remove_row(at_index=9)
x3, x4 = x0.remove_row(at_index=8)
x5, x6 = x0.remove_row(at_index=7)
x7, x8 = x0.remove_row(at_index=6)
x9, x10 = x0.remove_row(at_index=5)
x11, x12 = x0.remove_row(at_index=4)
x13, x14 = x0.remove_row(at_index=3)
x15, x16 = x0.remove_row(at_index=2)
x17, x18 = x0.remove_row(at_index=1)
x19, x20 = x0.remove_column(at_index=9)
x21, x22 = x0.remove_column(at_index=8)
x23, x24 = x0.remove_column(at_index=7)
x25, x26 = x0.remove_column(at_index=6)
x27, x28 = x0.remove_column(at_index=5)
x29, x30 = x0.remove_column(at_index=4)
x31, x32 = x0.remove_column(at_index=3)
x33, x34 = x0.remove_column(at_index=2)
x35 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 0, 0)
x36 = x0.add_motif(libexamples.motifs["dot-bg-1x1"], 1, 0)