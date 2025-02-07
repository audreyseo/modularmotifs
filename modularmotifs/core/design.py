"""Data structures that represent a design, a patchwork
of motifs"""

from __future__ import annotations
from typing import Optional, Generator, Tuple, Iterable
from modularmotifs.core.motif import Color, ColorOverflowException, Motif


class PlacedMotif:
    """Glorified immutable struct"""

    __motif: Motif
    __x: int
    __y: int

    def __init__(self, x: int, y: int, motif: Motif):
        self.__x = x
        self.__y = y
        self.__motif = motif

    def motif(self) -> Motif:
        """Getter

        Returns:
            Motif: description of pattern
        """
        return self.__motif

    def x(self) -> int:
        """Getter

        Returns:
            int: x coordinate
        """
        return self.__x

    def y(self) -> int:
        """Getter

        Returns:
            int: y coordinate
        """
        return self.__y

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PlacedMotif):
            return False
        return (
            self.motif() == other.motif()
            and self.x() == other.x()
            and self.y() == other.y()
        )

    def __hash__(self) -> int:
        return hash((self.__motif, self.__x, self.__y))


class PixelData:
    """Data to be associated with a pixel: a color at that
    pixel, and the motif that caused that color if the color
    is visible"""

    __col: Color
    __motif: Optional[PlacedMotif]

    def __init__(self, col: Color, motif: Optional[PlacedMotif]):
        self.__col = col
        self.__motif = motif if col != Color.INVIS else None
        if self.__col != Color.INVIS and self.__motif is None:
            raise ValueError("Visible colors must be caused by motifs!")

    def __add__(self, other: PixelData) -> PixelData:
        new_color = self.__col + other.col()
        new_motif = self.__motif if self.__col != Color.INVIS else other.motif()
        return PixelData(new_color, new_motif)

    def __sub__(self, other: Color) -> PixelData:
        new_color = self.__col - other
        new_motif = None if new_color == Color.INVIS else self.__motif
        return PixelData(new_color, new_motif)

    def __str__(self) -> str:
        return f"PixelData({self.__col}, {self.__motif})"

    def col(self) -> Color:
        """Getter

        Returns:
            Color: color at this pixel
        """
        return self.__col

    def motif(self) -> Optional[PlacedMotif]:
        """Getter

        Returns:
            Optional[PlacedMotif]: None if this is invisible,
            placed motif responsible for the color if visible
        """
        return self.__motif


class RGBColor:
    """Simple RGB [0, 255] triple"""

    def __init__(self, red: int, green: int, blue: int):
        if max(red, green, blue) > 255:
            raise ValueError("RGB coordinates must be less than 255!")
        if min(red, green, blue) < 0:
            raise ValueError("RGB coordinates must be greater than 0!")
        self.__red = red
        self.__blue = blue
        self.__green = green

    def hex(self) -> str:
        """Returns the hex representation
        (e.g., "#3300f2") of the color

        Returns:
            String: hex representation
        """
        return "#" + "".join(
            [
                hex(p).lstrip("0x").zfill(2)
                for p in [self.__red, self.__blue, self.__green]
            ]
        )


DEFAULT_FORE: RGBColor = RGBColor(0, 0, 0)
DEFAULT_BACK: RGBColor = RGBColor(255, 255, 255)
DEFAULT_INVIS: RGBColor = RGBColor(128, 128, 128)


class Design:
    """Collection of motifs on a canvas"""

    __height: int
    __width: int
    __motifs: set[PlacedMotif]
    __canvas: list[list[PixelData]]

    def __init__(self, height: int, width: int):
        self.__height = height
        self.__width = width
        self.__canvas = [
            [PixelData(Color.INVIS, None) for _ in range(self.__width)]
            for _ in range(self.__height)
        ]
        self.__motifs = set()

        self.fore_color: RGBColor = DEFAULT_FORE
        self.back_color: RGBColor = DEFAULT_BACK
        self.invis_color: RGBColor = DEFAULT_INVIS

    def width(self) -> int:
        """Getter

        Returns:
            int: width of the design
        """
        return self.__width

    def height(self) -> int:
        """Getter

        Returns:
            int: height of the design
        """
        return self.__height

    def complete(self) -> bool:
        """Returns True if and only if the design is
        complete (that is, all pixels are visible)

        Returns:
            bool: whether the design is complete
        """
        for row in self.__canvas:
            for px in row:
                if px.col == Color.INVIS:
                    return False
        return True

    def add_motif(self, m: Motif, x: int, y: int):
        """Add a motif to this design. If an error is encountered,
        the design is unchanged

        Args:
            m (Motif): Motif to be added
            x (int): x coordinate, from left
            y (int): y coordinate, from top

        Raises:
            IndexError: Motif would be placed out of bounds
            MotifOverlapException: Motif's visible data overlaps
            an existing motif's
        """
        if (
            m.height() + y > self.__height
            or m.width() + x > self.__width
            or min(x, y) < 0
        ):
            raise IndexError("Motif is out of bounds!")

        p = PlacedMotif(x, y, m)
        if p in self.__motifs:
            raise MotifOverlapException
        self.__motifs.add(p)
        successful_pixel_operations: int = 0  # for rollback
        try:
            for iy, row in enumerate(m):
                for ix, col in enumerate(row):
                    self.__canvas[y + iy][x + ix] += PixelData(col, p)
                    successful_pixel_operations += 1
        except ColorOverflowException as exc:
            # roll back!
            self.__motifs.remove(p)
            for iy, row in enumerate(m):
                for ix, col in enumerate(row):
                    if successful_pixel_operations == 0:
                        break
                    self.__canvas[y + iy][x + ix] -= col
                    successful_pixel_operations -= 1
            raise MotifOverlapException from exc

    def remove_motif(self, p: PlacedMotif):
        """Removes a motif from the design

        Args:
            p (PlacedMotif): Motif to be removed
        """
        for iy, row in enumerate(p.motif()):
            for ix, col in enumerate(row):
                self.__canvas[p.y() + iy][p.x() + ix] -= col
        self.__motifs.remove(p)

    def get_color(self, x: int, y: int) -> Color:
        """Get the color at some point

        Args:
            x (int): x coordinate, from left
            y (int): y coordinate, from top

        Returns:
            Color: Color at that point
        """
        return self.__canvas[y][x].col()

    def get_rgb(self, x: int, y: int) -> RGBColor:
        """Get the RGB color at some point.

        Args:
            x (int): x coordinate, from left
            y (int): y coordinate, from top

        Returns:
            RGBColor: RGB color at this point
        """
        match self.get_color(x, y):
            case Color.FORE:
                return self.fore_color
            case Color.BACK:
                return self.back_color
            case Color.INVIS:
                return self.invis_color

    def get_motif(self, x: int, y: int) -> Optional[PlacedMotif]:
        """Get the placed motif responsible for the color
        at some point if that color is visible

        Args:
            x (int): x coordinate, from left
            y (int): y coordinate, from top

        Returns:
            Optional[PlacedMotif]: None when the color is invisible,
            otherwise the responsible placed motif
        """
        return self.__canvas[y][x].motif()

    def __iter__(self) -> Generator[Iterable[Tuple[Color, int, int]], None, None]:
        """Iterate over the design in row-major order
        The inner iterable will give (color, x, y) for each pixel
        """
        for y in range(self.__height):
            yield [(self.get_color(x, y), x, y) for x in range(self.__width)]

        
        


class MotifOverlapException(Exception):
    """Raised whenever an added motif conflicts with an
    existing motif at least one pixel"""
