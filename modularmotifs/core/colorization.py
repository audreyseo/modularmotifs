from modularmotifs.core.design import RGBColor
from modularmotifs.core.design import Design, Color, Motif
from modularmotifs.core.util import rgbcolors_to_image
import abc
from typing import Generator, Tuple, Self, Union
from PIL import Image

class Colorization(abc.ABC):
    """ Class that contains the information for how to colorize a particular design
    """
    # the design that this colorization colorizes
    _d: Design
    # the colors that this colorization uses
    _colors: list[RGBColor]

    def __init__(self, d: Design, colors: list[RGBColor]):
        self._d = d
        self._colors = colors
        pass

    # @abc.abstractmethod
    # def assign_color(self, x: int, y: int) -> Self:
    #     assert (self._d.in_range(x, y)), f"Colorization.assign_color: coordinates ({x}, {y}) out of range of design {d}"
    #     return self

    @abc.abstractmethod
    def get_color(self, x: int, y: int) -> RGBColor:
        assert self._d.in_range(x, y), f"{self.get_color.__qualname__}: coordinates ({x}, {y}) out of range of design {d}"
        pass

    @abc.abstractmethod
    def complete(self) -> bool:
        pass

    @abc.abstractmethod
    def to_image(self) -> Image.Image:
        pass

    pass

class TwoColorsPerRow(Colorization):
    """ Allows assignment of two colors per row for a particular design
    """
    # print(__qualname__)
    # the colors for each row
    _foreground: list[RGBColor]
    _background: list[RGBColor]

    def __init__(self, d: Design, colors: list[RGBColor]):
        super().__init__(d, colors)
        h = d.height()
        # Initialize the foreground and background lists to be length h, one fg/bg color per row
        self._foreground = [ None for _ in range(h) ]
        self._background = [ None for _ in range(h) ]
        pass

    def set_fg(self, row: int, c: Union[int, RGBColor]) -> Self:
        assert 0 <= row < self._d.height(), f"{self.set_fg.__qualname__}: row {row} is out of range of design {d}"
        assert isinstance(c, RGBColor) or 0 <= c < len(self._colors), f"{self.set_fg.__qualname__}: color index {c} is out of range of color list {self._colors}"

        if isinstance(c, int):
            self._foreground[row] = colors[c]
            pass
        else:
            self._foreground[row] = c
        return self

    def set_bg(self, row: int, c: Union[int, RGBColor]) -> Self:
        assert 0 <= row < self._d.height(), f"{self.set_bg.__qualname__}: row {row} is out of range of design {d}"
        assert isinstance(c, RGBColor) or 0 <= c < len(self._colors), f"{self.set_bg.__qualname__}: color index {c} is out of range of color list {self._colors}"

        if isinstance(c, int):
            self._background[row] = colors[c]
            pass
        else:
            self._background[row] = c
            pass
        return self

    def set(self, row: int, fg: Union[int, RGBColor], bg: Union[int, RGBColor]) -> Self:
        return self.set_fg(row, fg).set_bg(row, bg)

    
    def complete(self) -> bool:
        super().complete()
        # need two colors per row
        return len(self._foreground) == self._d.height() and len(self._background) == self._d.height() and all(fg is not None for fg in self._foreground) and all(bg is not None for bg in self._background)

    def get_color(self, x: int, y: int) -> RGBColor:
        super().get_color(x, y)
        
        c = self._d.get_color(x, y)

        assert c != Color.INVIS, f"{self.get_color.__qualname__}: color of design {self._d} at ({x}, {y}) is invisible but should be either foreground or background"
        
        if c == Color.FORE:
            return self._foreground[y]
        elif c == Color.BACK:
            return self._background[y]
        pass

    # def to_image(self) -> Image.Image:
    #     img = Image.new


    def __iter__(self) -> Generator[Tuple[RGBColor, RGBColor], None, None]:
        assert len(self._foreground) == len(self._background), f"{self.__iter__.__qualname__}: foreground and background list lengths should be the same, but they differ: {len(self._foreground)} vs. {len(self._background)}"
        for i in range(len(self._foreground)):
            yield (self._foreground[i], self._background[i])
            pass
        pass

    def to_image(self, square_size=10) -> Image.Image:
        colors = [[self._foreground[y] if c == Color.FORE else self._background[y] for c, x, y in r] for r in self._d]
        return rgbcolors_to_image(colors, square_size=square_size)
        
        # for r in self._d:
        # for c, x, y in r:
        # col = self._foreground[y] if c == Color.FORE else self._background[y]
        # print(col, x, y)
                

        
        # w, h = self._d.width(), self._d.height()
        # img = Image.new("RGB", (w * square_size, h * square_size))
        # pixels = img.load()
        # for y in range(h):
        #     col1 = self._foreground[y]
        #     col2 = self._background[y]
        #     for x in range(w):
        #         # default to the background color
        #         col = col2
        #         if self._d.get_color(x, y) == Color.FORE:
        #             # otherwise, make it the foreground color
        #             col = col1
        #             pass
        #         for i in range(square_size):
        #             for j in range(square_size):
        #                 pixels[x * square_size + i, y * square_size + j] = col.tuple()
        #                 pass
        #             pass
        #         pass
        #     pass
        # return img
                        
            
    pass

        

if __name__ == "__main__":
    twocols = TwoColorsPerRow(Design(1, 1), [])
    twocols.assign_bg(0, 0)
    
