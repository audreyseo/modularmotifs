"""This module is the base-est
module; it defines colors which make up
motifs"""

from __future__ import annotations
from enum import Enum
from typing import Iterable


class Color(Enum):
    """Colors are either foreground (black?),
    background (white?), or invisible (to help everything
    have a square bounding box despite not being square).

    They can be added together as long as at least one is
    invisible, otherwise it raises a custom exception"""

    FORE = 1
    BACK = 2
    INVIS = 3

    def __add__(self, c2: Color):
        """Adds two colors, raising an exception if
        both are visible but not both background

        Args:
            c2 (Color): Other color to be added with

        Raises:
            ColorOverlapException: When both colors
            are visible and not both background

        Returns:
            Color: new color that represents the visible
            color if one is visible, background if both
            are background, otherwise invisible
        """
        if self == Color.INVIS:
            return Color(c2)
        if c2 == Color.INVIS:
            return Color(self)
        if self == Color.BACK and c2 == Color.BACK:
            return Color(self)
        raise ColorOverflowException

    def __sub__(self, c2: Color) -> Color:
        """Subtracts c2 from self

        Args:
            c2 (Color): Color to subtract

        Raises:
            ColorUnderflowException: Subtract a visible color from invisible
            ColorMismatchException: Subtract different visible colors

        Returns:
            Color: difference
        """
        if self == Color.INVIS and c2 != Color.INVIS:
            raise ColorUnderflowException
        if c2 == Color.INVIS:
            # identity
            return Color(self)
        # know that c2 is visible and self is visible
        if self == c2:
            # successful subtraction
            return Color.INVIS
        raise ColorMismatchException

    def __str__(self) -> str:
        if self == Color.INVIS:
            return "invis"
        if self == Color.BACK:
            return "back"
        if self == Color.FORE:
            return "fore"
        # panic!
        raise ColorMismatchException


class ColorOverflowException(Exception):
    """Raised whenever two colors are added together
    and neither are invisible"""


class ColorUnderflowException(Exception):
    """Raised whenever a visible color is subtracted
    from an invisible one"""


class ColorMismatchException(Exception):
    """Raised whenever a visible color is subtracted
    from a different visible one"""


def empty(lst: Iterable[Color]) -> bool:
    """Decides whether the list of colors is empty
    (all invisible)

    Args:
        lst (Iterable[Color]): iterable container of colors

    Returns:
        bool: True when all colors are invisible
    """
    try:
        return sum(lst, Color.INVIS) == Color.INVIS
    except ColorOverflowException:
        return False


class Motif:
    """A motif is an immutable rectangle of Color.
    There's no restriction that the visible Colors are
    connected, but we'd expect them to be.

    Motifs are iterable using extended for loops; they
    are iterated in row-major order (left to right, then
    top to bottom)
    """

    __width: int
    __height: int
    __data: list[list[Color]]

    def __init__(self, bbox: list[list[Color]]):
        """Constructs a new Motif.

        Args:
            bbox (list[list[Color]]): Rectangular bounding
            box for the motif, describing its values. Must
            have positive area. Additionally, must not
            start or end with an empty column or row

        Raises:
            ValueError: Nonpositive, nonrectangular, or
            nonminimal bounding box
        """
        self.__height = len(bbox)
        if self.__height <= 0:
            raise ValueError("Motifs must have positive height!")

        self.__width = len(bbox[0])
        if self.__width <= 0:
            raise ValueError("Motifs must have positive width!")
        for row in bbox[1:]:
            if len(row) != self.__width:
                raise ValueError("Motifs must have rectangular bounding boxes!")

        self.__data = [MotifRow(row) for row in bbox]

        # check columns
        if empty([row[0] for row in bbox]):
            raise ValueError("Motif starts with an empty column!")
        if empty([row[-1] for row in bbox]):
            raise ValueError("Motif ends with an empty column!")

        # check rows
        if empty(self.__data[0]):
            raise ValueError("Motif starts with an empty row!")
        if empty(self.__data[-1]):
            raise ValueError("Motif ends with an empty row!")

    def height(self) -> int:
        """Height of the bounding box for this motif (number of rows)

        Returns:
            int
        """
        return self.__height

    def width(self) -> int:
        """Height of the bounding box for this motif (number of columns)

        Returns:
            int
        """
        return self.__width

    def __iter__(self):
        return iter(self.__data)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Motif):
            return False
        return list(iter(self)) == list(iter(other))

    def __hash__(self) -> int:
        return hash(tuple(self.__data))

    def __repr__(self) -> str:
        return f"Motif({self.__data})"


class MotifRow:
    """Row of a motif, glorified list of colors used to prevent
    people from mutating motifs. Asserts that it contains
    at least one color"""

    __data: list[Color]

    def __init__(self, data: list[Color]):
        self.__data = data

    def __iter__(self):
        return iter(self.__data)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MotifRow):
            return False
        return list(iter(self)) == list(iter(other))

    def __hash__(self) -> int:
        return hash(tuple(self.__data))

    def __repr__(self) -> str:
        return f"MotifRow({list(map(str, self.__data))})"
