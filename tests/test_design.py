import pytest
from core.motif import (
    Color,
    ColorUnderflowException,
    Motif,
    ColorOverflowException,
    ColorMismatchException,
)
from core.design import Design, PlacedMotif, PixelData, MotifOverlapException


@pytest.fixture
def motif_example():
    """Fixture to create a sample motif for testing"""
    bbox = [[Color.FORE, Color.BACK], [Color.BACK, Color.FORE]]
    return Motif(bbox)


@pytest.fixture
def design_example(motif_example):
    """Fixture to create a sample design for testing"""
    design = Design(5, 5)
    design.add_motif(motif_example, 1, 1)
    return design


def test_add_motif(design_example, motif_example):
    """Test adding a motif to the design"""
    design = design_example
    assert design.get_color(1, 1) == Color.FORE
    assert design.get_color(2, 1) == Color.BACK
    assert design.get_color(1, 2) == Color.BACK
    assert design.get_color(2, 2) == Color.FORE


def test_add_motif_out_of_bounds():
    """Test adding a motif out of bounds"""
    bbox = [[Color.FORE, Color.BACK], [Color.BACK, Color.FORE]]
    motif = Motif(bbox)
    design = Design(3, 3)
    with pytest.raises(IndexError):
        design.add_motif(motif, 2, 2)


def test_motif_overlap_exception(design_example, motif_example):
    """Test adding a motif that overlaps an existing one"""
    design = design_example
    bbox = [[Color.FORE, Color.BACK], [Color.BACK, Color.FORE]]
    motif = Motif(bbox)
    with pytest.raises(MotifOverlapException):
        design.add_motif(motif, 1, 1)


def test_remove_motif(design_example, motif_example):
    """Test removing a motif from the design"""
    design = design_example
    p = PlacedMotif(1, 1, motif_example)
    design.remove_motif(p)
    assert design.get_color(1, 1) == Color.INVIS
    assert design.get_color(2, 1) == Color.INVIS
    assert design.get_color(1, 2) == Color.INVIS
    assert design.get_color(2, 2) == Color.INVIS


def test_pixel_data_addition():
    """Test adding two PixelData objects"""
    motif1 = PlacedMotif(0, 0, motif_example)
    motif2 = PlacedMotif(1, 1, motif_example)
    pixel_data1 = PixelData(Color.INVIS, motif1)
    pixel_data2 = PixelData(Color.BACK, motif2)

    result = pixel_data1 + pixel_data2
    assert result.col() == Color.BACK and result.motif() == motif2


def test_pixel_data_subtraction():
    """Test subtracting a Color from PixelData"""
    motif1 = PlacedMotif(0, 0, motif_example)
    pixel_data = PixelData(Color.FORE, motif1)

    result = pixel_data - Color.FORE
    assert result.col() == Color.INVIS


def test_color_addition_exception():
    """Test adding two visible colors raises a ColorOverflowException"""
    with pytest.raises(ColorOverflowException):
        Color.FORE + Color.BACK


def test_color_subtraction_exceptions():
    """Test subtracting a visible color from invisible raises a ColorUnderflowException"""
    with pytest.raises(ColorUnderflowException):
        Color.INVIS - Color.FORE

    """Test subtracting different visible colors raises a ColorMismatchException"""
    with pytest.raises(ColorMismatchException):
        Color.FORE - Color.BACK
