"""This module is the base-est
module; it defines colors which make up
motifs"""

from __future__ import annotations
from enum import Enum
from typing import Iterable, Dict


class Color(Enum):
    """Defines foreground, background, and invisible colors."""
    FORE = 1
    BACK = 2
    INVIS = 3

    def __add__(self, c2: Color):
        """Adds two colors, raising an exception if both are visible."""
        if self == Color.INVIS:
            return Color(c2)
        if c2 == Color.INVIS:
            return Color(self)
        raise ColorOverflowException

    def __sub__(self, c2: Color) -> Color:
        """Subtracts c2 from self."""
        if self == Color.INVIS and c2 != Color.INVIS:
            raise ColorUnderflowException
        if c2 == Color.INVIS:
            return Color(self)
        if self == c2:
            return Color.INVIS
        raise ColorMismatchException


class ColorOverflowException(Exception):
    """Raised when two visible colors are added."""


class ColorUnderflowException(Exception):
    """Raised when a visible color is subtracted from an invisible one."""


class ColorMismatchException(Exception):
    """Raised when subtracting different visible colors."""


def empty(lst: Iterable[Color]) -> bool:
    """Checks if a list of colors is entirely invisible."""
    try:
        return sum(lst, Color.INVIS) == Color.INVIS
    except ColorOverflowException:
        return False


class Motif:
    """Represents an immutable motif as a grid of colors."""

    def __init__(self, bbox: list[list[Color]]):
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

        if empty([row[0] for row in bbox]) or empty([row[-1] for row in bbox]):
            raise ValueError("Motif has empty border columns!")
        if empty(self.__data[0]) or empty(self.__data[-1]):
            raise ValueError("Motif has empty border rows!")

    def height(self) -> int:
        return self.__height

    def width(self) -> int:
        return self.__width

    def __iter__(self):
        return iter(self.__data)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Motif) and list(iter(self)) == list(iter(other))

    def __hash__(self) -> int:
        return hash(tuple(self.__data))


class MotifRow:
    """Immutable row of a motif."""
    def __init__(self, data: list[Color]):
        self.__data = data

    def __iter__(self):
        return iter(self.__data)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MotifRow) and list(iter(self)) == list(iter(other))

    def __hash__(self) -> int:
        return hash(tuple(self.__data))


# Motif Library
MOTIFS: Dict[str, Motif] = {
    "plus-3x3": Motif([
        [Color.BACK, Color.FORE, Color.BACK],
        [Color.FORE, Color.FORE, Color.FORE],
        [Color.BACK, Color.FORE, Color.BACK]
    ]),
    "x-3x3": Motif([
        [Color.FORE, Color.BACK, Color.FORE],
        [Color.BACK, Color.FORE, Color.BACK],
        [Color.FORE, Color.BACK, Color.FORE]
    ]),
    "crosshair-3x3": Motif([
        [Color.BACK, Color.FORE, Color.BACK],
        [Color.FORE, Color.BACK, Color.FORE],
        [Color.BACK, Color.FORE, Color.BACK]
    ])
}
