"""Data structures that represent a design, a patchwork
of motifs"""

from __future__ import annotations
from typing import Optional
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
            m.height() + y >= self.__height
            or m.width() + x >= self.__width
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
                    self.__canvas[y + iy][x + ix] -= PixelData(col, p)
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


class MotifOverlapException(Exception):
    """Raised whenever an added motif conflicts with an
    existing motif at least one pixel"""
