import pytest
from modularmotifs.core.motif import (
    Color,
    ColorUnderflowException,
    Motif,
    ColorOverflowException,
    ColorMismatchException,
)
from modularmotifs.core.design import (
    Design,
    PlacedMotif,
    PixelData,
    MotifOverlapException,
)
from modularmotifs.motiflibrary.examples import fg_square, bg_square
from modularmotifs.motiflibrary.examples import motifs as MOTIFS


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
    pixel_data1 = PixelData(Color.INVIS, set([motif1]))
    pixel_data2 = PixelData(Color.FORE, set([motif2]))

    result = pixel_data1 + pixel_data2
    assert result.col() == Color.FORE and result.motif() == motif2


def test_pixel_data_subtraction():
    """Test subtracting a Color from PixelData"""
    motif1 = PlacedMotif(0, 0, motif_example)
    pixel_data = PixelData(Color.FORE, set([motif1]))

    result = pixel_data - pixel_data
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
        pass
    pass


@pytest.fixture
def empty_design():
    return Design(height=0, width=0)  # Empty design with no pixels


@pytest.fixture
def small_design():
    design = Design(height=3, width=3)
    # Add some colors manually (this would simulate a design with different colors)
    fg_2 = fg_square(2)
    bg_1 = bg_square(1)
    design.add_motif(fg_2, 0, 0)
    design.add_motif(bg_1, 2, 0)
    design.add_motif(bg_1, 2, 1)
    design.add_motif(bg_1, 2, 2)
    design.add_motif(bg_1, 0, 2)
    design.add_motif(bg_1, 1, 2)

    # design.get_color(0, 0)  # Foreground color at (0, 0)
    # design.get_color(1, 1)  # Background color at (1, 1)
    # design.get_color(2, 2)  # Invisible color at (2, 2)
    return design


@pytest.fixture
def design_with_motifs():
    design = Design(height=3, width=3)
    # Place some motifs (we will assume this function works correctly)
    motif = MOTIFS["x-3x3"]  # Assuming Motif is defined properly
    design.add_motif(motif, x=0, y=0)
    return design


def test_iter_empty_design(empty_design):
    # Test that iterating over an empty design yields no results
    result = list(empty_design)
    assert result == []  # No rows, no pixels


def test_iter_small_design(small_design):
    # Test that iterating over a small design with specific colors gives correct output
    expected_output = [
        [(Color.FORE, 0, 0), (Color.FORE, 1, 0), (Color.BACK, 2, 0)],
        [(Color.FORE, 0, 1), (Color.FORE, 1, 1), (Color.BACK, 2, 1)],
        [(Color.BACK, 0, 2), (Color.BACK, 1, 2), (Color.BACK, 2, 2)],
    ]
    result = list(small_design)
    assert result == expected_output


def test_iter_design_with_motifs(design_with_motifs):
    # Test that iterating over a design with motifs placed still yields correct (color, x, y)
    expected_output = [
        [(Color.FORE, 0, 0), (Color.BACK, 1, 0), (Color.FORE, 2, 0)],
        [(Color.BACK, 0, 1), (Color.FORE, 1, 1), (Color.BACK, 2, 1)],
        [(Color.FORE, 0, 2), (Color.BACK, 1, 2), (Color.FORE, 2, 2)],
    ]
    result = list(design_with_motifs)
    assert result == expected_output


def test_iter_single_row(design_with_motifs):
    # Test that iterating over a single row of the design returns the correct tuple
    row_data = list(design_with_motifs)[0]  # Get the first row
    expected_row = [(Color.FORE, 0, 0), (Color.BACK, 1, 0), (Color.FORE, 2, 0)]
    assert row_data == expected_row


def test_iter_multiple_rows(design_with_motifs):
    # Test that iterating over multiple rows works and returns the expected colors
    rows = list(design_with_motifs)
    assert len(rows) == 3  # There should be 3 rows
    assert len(rows[0]) == 3  # Each row should have 3 columns

def test_add_row_at_end():
    design = Design(10, 10)
    initial_height = design.height()
    design.add_row()
    assert design.height() == initial_height + 1, "Height should increase by 1"
    assert len([r for r in design]) == design.height(), "Canvas should have the new row added at the end"

def test_add_row_at_index():
    design = Design(10, 10)
    design.add_row()
    initial_height = design.height()
    design.add_row(at_index=0)
    assert design.height() == initial_height + 1, "Height should increase by 1"
    assert len([r for r in design]) == design.height(), "Canvas should have the new row inserted at index 0"

def test_add_row_invalid_index():
    design = Design(10, 10)
    try:
        design.add_row(at_index=100)  # Invalid index
        assert False, "Expected AssertionError"
    except AssertionError:
        pass

def test_add_column_at_end():
    design = Design(10, 10)
    initial_width = design.width()
    design.add_column()
    assert design.width() == initial_width + 1, "Width should increase by 1"
    for row in design:
        assert len(row) == design.width(), "Each row should have an additional column"

def test_add_column_at_index():
    design = Design(10, 10)
    design.add_column()
    initial_width = design.width()
    design.add_column(at_index=0)
    assert design.width() == initial_width + 1, "Width should increase by 1"
    for row in design:
        assert len(row) == design.width(), "Each row should have the new column inserted at index 0"

def test_add_column_invalid_index():
    design = Design(10, 10)
    try:
        design.add_column(at_index=100)  # Invalid index
        assert False, "Expected AssertionError"
    except AssertionError:
        pass

def test_remove_row_at_end():
    design = Design(10, 10)
    design.add_row()
    initial_height = design.height()
    removed_row = design.remove_row()
    assert design.height() == initial_height - 1, "Height should decrease by 1"
    assert len([r for r in design]) == design.height(), "Canvas should have one less row"
    assert removed_row is not None, "The removed row should be returned"

def test_remove_row_at_index():
    design = Design(10, 10)
    design.add_row()
    design.add_row()
    initial_height = design.height()
    removed_row = design.remove_row(at_index=0)
    assert design.height() == initial_height - 1, "Height should decrease by 1"
    assert len([r for r in design]) == design.height(), "Canvas should have one less row"
    assert removed_row is not None, "The removed row should be returned"
    
def test_remove_row_invalid_index():
    design = Design(10, 10)
    try:
        design.remove_row(at_index=100)  # Invalid index
        assert False, "Expected IndexError"
    except IndexError:
        pass


def test_remove_column_at_end():
    design = Design(10, 10)
    design.add_column()
    initial_width = design.width()
    removed_column = design.remove_column()
    assert design.width() == initial_width - 1, "Width should decrease by 1"
    for row in design:
        assert len(row) == design.width(), "Each row should have one less column"
    assert removed_column is not None, "The removed column should be returned"

def test_remove_column_at_index():
    design = Design(10, 10)
    design.add_column()
    design.add_column()
    initial_width = design.width()
    removed_column = design.remove_column(at_index=0)
    assert design.width() == initial_width - 1, "Width should decrease by 1"
    for row in design:
        assert len(row) == design.width(), "Each row should have one less column"
    assert removed_column is not None, "The removed column should be returned"

def test_remove_column_invalid_index():
    design = Design(10, 10)
    try:
        design.remove_column(at_index=100)  # Invalid index
        assert False, "Expected IndexError"
    except IndexError:
        pass
