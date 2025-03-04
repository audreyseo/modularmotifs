from modularmotifs.core.motif import Color, Motif
from modularmotifs.core.design import PlacedMotif, PixelData, Design

class CompositeMotif(Design, Motif):
    """A class that represents a composite motif, which is really just a Design under the hood
    """
    def __init__(self, height: int, width: int):
        # calls Design's constructor
        super(CompositeMotif, self).__init__(height, width)
        pass
    pass

if __name__ == "__main__":
    cm = CompositeMotif(10, 10)
    print(cm)
    