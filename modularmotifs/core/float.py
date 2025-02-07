"""Data structure to capture the essence of a float

Possibly over-engineering here...
"""
from modularmotifs.core.motif import Color
from typing import Tuple

class FloatStrand:
    """Floats are horizontal lengths of yarn that occur because of color changes in stranded colorwork knitting
    """
    # Length of the float
    __length: int
    # the x coordinate of where the float begins. The next stitch using this color is at __start + __length + 1 -- note that this is inclusize
    __start: int
    # The row where the float occurred
    __rownum: int
    # Color
    __color: Color

    def __init__(self, start: int, length: int, row: int = -1, color: Color = None):
        """Create an instance of a FloatStrand

        Args
        ====

        start: int -- the left x coordinate of this float (i.e., the last stitch knit with this color)
        
        length: int -- the number of stitches in between that were knit in the other color. The right x coordinate of this float (i.e., the next stitch knit with this color) should be at start + length + 1

        row: int, optional -- the row where this float occurs

        color: Color, optional -- the color of this float. If provided, this color should not be 'invisible'
        """
        assert color is None or color != Color.INVIS, f"FloatStrand: color {color} should be None or not 'invisible'"
        self.__length = length
        self.__start = start
        self.__rownum = row
        self.__color = color
        pass

    def has_row(self) -> bool:
        return self.__rownum and self.__rownum != -1

    def get_row(self) -> int:
        return self.__rownum

    def has_color(self) -> bool:
        return self.__color is not None

    def get_color(self) -> Color:
        return self.__color

    def __len__(self) -> int:
        return self.__length

    def x_left(self) -> int:
        return self.__start

    def x_right(self) -> int:
        return self.__start + self.__length + 1

    def xs(self) -> Tuple[int, int]:
        return self.x_left(), self.x_right()

    
    

    
    
