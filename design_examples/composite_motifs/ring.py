from modularmotifs.core import Design
from modularmotifs.core import CompositeMotif
import modularmotifs.motiflibrary.examples as libexamples

x0 = CompositeMotif(10, 10)



x1 = x0.add_column()
x2 = x0.add_column()
x3 = x0.add_column()
x4 = x0.add_column()
x5 = x0.add_row()
x6 = x0.add_row()
x7 = x0.add_row()
x8 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 0, 4)
x9 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 1, 4)
x10 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 1, 5)
x11 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 0, 5)
x12 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 2, 2)
x13 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 2, 3)
x14 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 3, 3)
x15 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 3, 2)
x16 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 4, 0)
x17 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 4, 1)
x18 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 5, 1)
x19 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 5, 0)
x20 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 7, 0)
x21 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 7, 1)
x22 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 8, 1)
x23 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 8, 0)
x24 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 9, 2)
x25 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 9, 3)
x26 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 10, 3)
x27 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 10, 2)
x28 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 11, 4)
x29 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 11, 5)
x30 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 12, 5)
x31 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 12, 4)
x32, x33 = x0.remove_column(at_index=13)
x34 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 0, 7)
x35 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 1, 7)
x36 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 1, 8)
x37 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 0, 8)
x38 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 2, 9)
x39 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 3, 9)
x40 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 3, 10)
x41 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 2, 10)
x42 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 4, 11)
x43 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 4, 12)
x44 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 5, 12)
x45 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 5, 11)
x46 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 7, 11)
x47 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 7, 12)
x48 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 8, 12)
x49 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 8, 11)
x50 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 9, 10)
x51 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 9, 9)
x52 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 10, 9)
x53 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 10, 10)
x54 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 11, 8)
x55 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 11, 7)
x56 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 12, 7)
x57 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 12, 8)
x58 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 6, 5)
x59 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 5, 6)
x60 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 6, 7)
x61 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 7, 6)