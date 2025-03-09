from modularmotifs.core import Design
import modularmotifs.motiflibrary.examples as libexamples

x0 = Design(10, 10)



x1 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 3, 2)
x2 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 3, 6)
x3 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 9, 3)
x4 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 7, 6)
x5 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 6, 3)
x6 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 3, 3)
x7 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 2, 4)
x8 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 0, 8)
x9 = x0.add_motif(libexamples.motifs["dot-fg-1x1"], 0, 9)