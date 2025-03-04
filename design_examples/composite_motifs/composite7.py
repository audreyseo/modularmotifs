from modularmotifs.core import Design
from modularmotifs.core import CompositeMotif
import modularmotifs.motiflibrary.examples as libexamples

x0 = CompositeMotif(10, 10)



x1 = x0.add_motif(libexamples.motifs["plus-3x3"], 1, 0)
x2 = x0.add_motif(libexamples.motifs["plus-3x3"], 4, 3)
x3 = x0.add_motif(libexamples.motifs["plus-3x3"], 1, 7)