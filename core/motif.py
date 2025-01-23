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
        both are visible

        Args:
            c2 (Color): Other color to be added with

        Raises:
            ColorOverlapException: When both colors
            are visible

        Returns:
            Color: new color that represents the visible
            color if one is visible, otherwise invisible
        """
        if self == Color.INVIS:
            return Color(c2)
        if c2 == Color.INVIS:
            return Color(self)
        raise ColorOverlapException


class ColorOverlapException(Exception):
    """Raised whenever two colors are added together
    and neither are invisible"""


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
    except ColorOverlapException:
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


class MotifRow:
    """Row of a motif, glorified list of colors used to prevent
    people from mutating motifs. Asserts that it contains
    at least one color"""

    __data: list[Color]

    def __init__(self, data: list[Color]):
        self.__data = data

    def __iter__(self):
        return iter(self.__data)
