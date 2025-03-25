"""Data structures that represent a design, a patchwork
of motifs"""

from __future__ import annotations
import re
from typing import Optional, Generator, Tuple, Iterable, Set, Self
from modularmotifs.core.motif import Color, ColorOverflowException, Motif
from modularmotifs.core.rgb_color import RGBAColor
from modularmotifs.core.pixel_grid import PixelGrid


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
    pixel, and the motif(s) that caused that color if the color
    is visible"""

    __col: Color
    __motifs: Set[PlacedMotif]

    def __init__(self, col: Color, motifs: Set[PlacedMotif]):
        self.__col = col
        self.__motifs = motifs if self.__col != Color.INVIS else set()
        if self.__col != Color.INVIS and len(motifs) is None:
            raise ValueError("Visible colors must be caused by motifs!")

    def __add__(self, other: PixelData) -> PixelData:
        new_color = self.__col + other.col()
        new_motifs = self.__motifs.union(other.motifs())
        return PixelData(new_color, new_motifs)

    def __sub__(self, other: PixelData) -> PixelData:
        new_motifs = self.__motifs.difference(other.motifs())
        new_color = self.__col - other.col() if len(new_motifs) == 0 else self.__col
        return PixelData(new_color, new_motifs)

    def __str__(self) -> str:
        return f"PixelData({self.__col}, {self.__motifs})"

    def col(self) -> Color:
        """Getter

        Returns:
            Color: color at this pixel
        """
        return self.__col

    def motifs(self) -> Set[PlacedMotif]:
        """Getter

        Returns:
            Set[PlacedMotif]: Motifs responsible for this color
        """
        return self.__motifs

    def motif(self) -> Optional[PlacedMotif]:
        """Getter

        Returns:
            Optional[PlacedMotif]: None if this is not foreground (black),
            placed motif responsible for the color if foreground
        """
        if self.__col == Color.INVIS:
            return None
        assert len(self.__motifs) == 1
        return next(iter(self.__motifs))


DEFAULT_FORE: RGBAColor = RGBAColor.Fore()
DEFAULT_BACK: RGBAColor = RGBAColor.Back()
DEFAULT_INVIS: RGBAColor = RGBAColor.Invis()


class Design(PixelGrid):
    """Collection of motifs on a canvas"""

    __height: int
    __width: int
    __motifs: set[PlacedMotif]
    __canvas: list[list[PixelData]]

    def __init__(self, height: int, width: int):
        self.__height = height
        self.__width = width
        self.__canvas = [self.__new_row() for _ in range(self.__height)]
        self.__motifs = set()

        self.fore_color: RGBAColor = DEFAULT_FORE
        self.back_color: RGBAColor = DEFAULT_BACK
        self.invis_color: RGBAColor = DEFAULT_INVIS
        pass

    def set_fore_color(self, color: RGBAColor):
        self.fore_color = color
        pass

    def set_back_color(self, color: RGBAColor):
        self.back_color = color
        pass

    def set_invis_color(self, color: RGBAColor):
        self.invis_color = color
        pass

    def __new_row(self) -> list[PixelData]:
        return [Design.default_pixel_data() for _ in range(self.__width)]

    @classmethod
    def default_pixel_data(cls) -> PixelData:
        return PixelData(Color.INVIS, set())

    def motifify(self, x0: int, y0: int, x1: int, y1: int) -> Motif:
        colors = []
        for y in range(y0, y1 + 1):
            colors_row = []
            for x in range(x0, x1 + 1):
                colors_row.append(self.get_color(x, y))
                pass
            colors.append(colors_row)
            pass
        return Motif(colors)

    def add_row(
        self, at_index: int = -1, contents: Optional[list[PixelData]] = None
    ) -> int:
        """Add a row to this design, optionally at the specified index.

        Args:
            at_index (int, optional): The row at which to insert a new row. This
                will shift all rows at_index, at_index+1, etc. to at_index + 1,
                at_index + 2, etc. Defaults to -1 -- which puts it at the end (no shifting)

        Returns:
            int: the index of the row added
        """
        content = contents
        if contents:
            assert (
                len(contents) == self.width()
            ), f"{self.add_row.__qualname__}: given row contents is the wrong length -- expected length {self.width()} but got {len(contents)}"
            pass
        else:
            content = self.__new_row()
            pass

        if at_index == -1 or at_index == self.__height:
            at_index = self.__height
            self.__canvas.append(content)
            pass
        else:
            assert (
                0 <= at_index < self.__height
            ), f"{self.add_row.__qualname__}: Expected index {at_index} to be in [0, {self.__height})"
            self.__canvas.insert(at_index, content)
            pass
        self.__height += 1
        return at_index

    def add_column(
        self, at_index: int = -1, contents: Optional[list[PixelData]] = None
    ) -> int:
        """Add a column to this design, optionally at the specified index.

        Args:
            at_index (int, optional): The column at which to insert a new column. This will shift all columns at indices at_index, at_index+1, etc. to at_index + 1, at_index + 2, etc. Defaults to -1 -- which puts it at the end (no shifting)

        Returns:
            int: the index of the column added
        """
        content = contents
        if contents:
            assert (
                len(contents) == self.height()
            ), f"{self.add_column.__qualname__}: given column contents is the wrong length -- expected length {self.height()} but got {len(contents)}"
            pass
        else:
            content = [Design.default_pixel_data() for i in range(self.__height)]
            pass

        if at_index == -1 or at_index == self.__width:
            at_index = self.__width
            for i in range(self.__height):
                self.__canvas[i].append(content[i])
                pass
            pass
        else:
            assert (
                0 <= at_index < self.__width
            ), f"{self.add_column.__qualname__}: Expected index {at_index} to be in [0, {self.__width})"
            for i in range(self.__height):
                self.__canvas[i].insert(at_index, content[i])
                pass
            pass
        self.__width += 1
        return at_index

    def remove_row(self, at_index: int = -1) -> tuple[int, list[PixelData]]:
        """Remove a row from this design, optionally at the specified index

        Args:
            at_index (int, optional): Remove the row at the given index.
                Defaults to -1 -- the last row will be removed

        Returns:
            list[PixelData]: the row that was removed
        """
        self.__height -= 1
        at_index = self.__height if at_index == -1 else at_index
        return at_index, self.__canvas.pop(at_index)

    def remove_column(self, at_index: int = -1) -> tuple[int, list[PixelData]]:
        """Remove a column from this design, optionally at the specified index

        Args:
            at_index (int, optional): Remove the column at the given index. Defaults to -1 -- the last column

        Returns:
            list[PixelData]: the column that was removed
        """
        col = []
        for i in range(self.__height):
            col.append(self.__canvas[i].pop(at_index))
            pass
        self.__width -= 1
        at_index = self.__width if at_index == -1 else at_index
        return at_index, col

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

    def get_motifs(self, x: int, y: int) -> set[PlacedMotif]:
        return self.__canvas[y][x].motifs()

    def add_motif(self, m: Motif, x: int, y: int) -> PlacedMotif:
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

        Returns:
            PlacedMotif: The motif that has been placed
        """
        if (
            m.height() + y > self.__height
            or m.width() + x > self.__width
            or min(x, y) < 0
        ):
            raise IndexError(
                f"Motif is out of bounds!: {m.height()} x {m.width()} vs ({x}, {y}) and {self.__height}, {self.__width}"
            )

        p = PlacedMotif(x, y, m)
        if p in self.__motifs:
            raise MotifOverlapException
        self.__motifs.add(p)
        successful_pixel_operations: int = 0  # for rollback
        try:
            for iy, row in enumerate(m):
                for ix, col in enumerate(row):
                    self.__canvas[y + iy][x + ix] += PixelData(col, set([p]))
                    successful_pixel_operations += 1
        except ColorOverflowException as exc:
            # roll back!
            self.__motifs.remove(p)
            for iy, row in enumerate(m):
                for ix, col in enumerate(row):
                    if successful_pixel_operations == 0:
                        break
                    self.__canvas[y + iy][x + ix] -= PixelData(col, set([p]))
                    successful_pixel_operations -= 1
            raise MotifOverlapException from exc
        return p

    def remove_motif(self, p: PlacedMotif):
        """Removes a motif from the design

        Args:
            p (PlacedMotif): Motif to be removed
        """
        for iy, row in enumerate(p.motif()):
            for ix, col in enumerate(row):
                self.__canvas[p.y() + iy][p.x() + ix] -= PixelData(col, set([p]))
        self.__motifs.remove(p)

    def row_colors(self, y: int) -> list[Color]:
        return [self.get_color(x, y) for x in range(self.__width)]

    def get_color(self, x: int, y: int) -> Color:
        """Get the color at some point

        Args:
            x (int): x coordinate, from left
            y (int): y coordinate, from top

        Returns:
            Color: Color at that point
        """
        return self.__canvas[y][x].col()

    def get_rgba(self, x: int, y: int) -> RGBAColor:
        """Get the RGBA color at some point.

        Args:
            x (int): x coordinate, from left
            y (int): y coordinate, from top

        Returns:
            RGBAColor: RGBA color at this point
        """
        match self.get_color(x, y):
            case Color.FORE:
                return self.fore_color
            case Color.BACK:
                return self.back_color
            case Color.INVIS:
                return self.invis_color
        raise ValueError("I don't know which color this is!")

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

    def in_range(self, x: int, y: int) -> bool:
        """Whether the given coordinates are inside this design"""
        return 0 <= x < self.__width and 0 <= y < self.__height

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__width}, {self.__height})"

    def __iter__(self) -> Generator[Iterable[Tuple[Color, int, int]], None, None]:
        """Iterate over the design in row-major order
        The inner iterable will give (color, x, y) for each pixel
        """
        for y in range(self.__height):
            yield [(self.get_color(x, y), x, y) for x in range(self.__width)]


class MotifOverlapException(Exception):
    """Raised whenever an added motif conflicts with an
    existing motif at least one pixel"""
