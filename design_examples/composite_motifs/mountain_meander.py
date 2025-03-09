# already imported
from modularmotifs.core import Design
from modularmotifs.core import CompositeMotif
import modularmotifs.motiflibrary.examples as libexamples

x0 = CompositeMotif(10, 10)



x1, x2 = x0.remove_column(at_index=9)
x3, x4 = x0.remove_column(at_index=8)
x5, x6 = x0.remove_column(at_index=7)
x7, x8 = x0.remove_column(at_index=6)
x9, x10 = x0.remove_column(at_index=5)
x11, x12 = x0.remove_column(at_index=4)
x13, x14 = x0.remove_row(at_index=9)
x15, x16 = x0.remove_row(at_index=8)
x17, x18 = x0.remove_row(at_index=7)
x19, x20 = x0.remove_row(at_index=6)
x21, x22 = x0.remove_row(at_index=5)
x23 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 0, 1)
x24 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 1, 0)
x25 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 2, 1)
x26 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 3, 2)
x27 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 1, 2)
x28 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 0, 3)
x29 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 2, 3)
x30 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 3, 4)