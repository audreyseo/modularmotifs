# Try to use every single language feature in every way imaginable
from modularmotifs.core import Design
import modularmotifs.motiflibrary.examples as libexamples
from modularmotifs.core import Motif, Color

x0 = Design(10, 10)

x1 = x0.add_motif(libexamples.motifs["plus-3x3"], 1, 1)
x2 = x0.add_motif(libexamples.motifs["plus-3x3"], 6, 5)
x3 = x0.add_motif(libexamples.motifs["x-3x3"], 2, 5)
x4 = x0.add_row(at_index=-1)
y = [0, 1.0, 2]
x5 = x0.add_row()
x6 = x0.add_column()
x7 = x0.add_column()
x8 = x0.add_column()
x9 = x0.add_column()
x10 = x0.add_motif(libexamples.motifs["plus-3x3"], 10, 1)
x11 = x0.add_motif(libexamples.motifs["plus-3x3"], 10, 8)
x12 = x0.add_motif(libexamples.motifs["plus-3x3"], 2, 9)
removed_index, col = x0.remove_column()
x13 = x0.add_column(at_index=removed_index, contents=col)
removed_index, col = x0.remove_column()
x14 = x0.add_column(contents=col)
removed3, row = x0.remove_row(at_index=3)
x15 = x0.add_row(at_index=removed3, contents=row)
removed4, row1 = x0.remove_row(at_index=removed3)
x16 = x0.add_row(contents=row1)
# Checkerboard motif
m = Motif([[Color.FORE, Color.BACK], [Color.BACK, Color.FORE]])