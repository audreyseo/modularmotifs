"""Tests generated with ChatGPT. I put motif.py into ChatGPT and
asked it to generate tests for the module. I tested the tests
by running them and inspecting the failed ones. It found some bugs,
and also made some bad testcases. I fixed the bugs and testcases.
It helped us because now we can have more trustworthy code and focus
on writing new code rather than debugging old code"""

import pytest
from core.motif import Color, ColorOverlapException, empty, Motif, MotifRow


def test_color_addition():
    assert (Color.FORE + Color.INVIS) == Color.FORE
    assert (Color.INVIS + Color.BACK) == Color.BACK
    assert (Color.INVIS + Color.INVIS) == Color.INVIS

    with pytest.raises(ColorOverlapException):
        _ = Color.FORE + Color.BACK


def test_empty_function():
    assert empty([]) is True
    assert empty([Color.INVIS, Color.INVIS]) is True
    assert empty([Color.INVIS, Color.FORE]) is False
    assert empty([Color.FORE, Color.BACK]) is False


def test_motif_valid_construction():
    bbox = [
        [Color.FORE, Color.FORE, Color.INVIS],
        [Color.INVIS, Color.BACK, Color.BACK],
    ]
    motif = Motif(bbox)
    assert motif.height() == 2
    assert motif.width() == 3


def test_motif_invalid_construction():
    with pytest.raises(ValueError, match="Motifs must have positive height!"):
        Motif([])

    with pytest.raises(ValueError, match="Motifs must have positive width!"):
        Motif([[]])

    with pytest.raises(
        ValueError, match="Motifs must have rectangular bounding boxes!"
    ):
        Motif([[Color.INVIS, Color.FORE], [Color.INVIS]])

    with pytest.raises(ValueError, match="Motif starts with an empty column!"):
        Motif(
            [
                [Color.INVIS, Color.FORE],
                [Color.INVIS, Color.BACK],
            ]
        )

    with pytest.raises(ValueError, match="Motif ends with an empty column!"):
        Motif(
            [
                [Color.FORE, Color.INVIS],
                [Color.BACK, Color.INVIS],
            ]
        )

    with pytest.raises(ValueError, match="Motif starts with an empty row!"):
        Motif(
            [
                [Color.INVIS, Color.INVIS],
                [Color.BACK, Color.FORE],
            ]
        )

    with pytest.raises(ValueError, match="Motif ends with an empty row!"):
        Motif(
            [
                [Color.BACK, Color.FORE],
                [Color.INVIS, Color.INVIS],
            ]
        )


def test_motif_iteration():
    bbox = [
        [Color.FORE, Color.INVIS],
        [Color.INVIS, Color.BACK],
    ]
    motif = Motif(bbox)
    rows = list(iter(motif))
    assert len(rows) == 2
    assert isinstance(rows[0], MotifRow)


def test_motif_row_iteration():
    row = MotifRow([Color.FORE, Color.BACK])
    colors = list(iter(row))
    assert colors == [Color.FORE, Color.BACK]
