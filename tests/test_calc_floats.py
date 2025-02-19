from modularmotifs.core import Design, Color
from modularmotifs.core.float import FloatStrand
from modularmotifs.ui.util.selection import Selection
from typing import Iterable, Dict
from modularmotifs.core.algo import calculate_float_lengths
from modularmotifs.motiflibrary.examples import int_lol_to_motif

import pytest
from typing import Dict

# Generated with chatgpt


# Fixtures for creating designs, selection, and other dependencies
@pytest.fixture
def empty_design():
    design = Design(height=3, width=3)
    return design


@pytest.fixture
def simple_design():
    # Create a simple 3x3 design with alternating colors
    design = Design(height=3, width=3)
    dumb = int_lol_to_motif([[1, 2, 1], [1, 2, 1], [2, 1, 2]])
    design.add_motif(dumb, 0, 0)
    # design.get_color(0, 0)  # Foreground color at (0, 0)
    # design.get_color(1, 0)  # Background color at (1, 0)
    # design.get_color(2, 0)  # Foreground color at (2, 0)
    # design.get_color(0, 1)  # Foreground color at (0, 1)
    # design.get_color(1, 1)  # Background color at (1, 1)
    # design.get_color(2, 1)  # Foreground color at (2, 1)
    # design.get_color(0, 2)  # Background color at (0, 2)
    # design.get_color(1, 2)  # Foreground color at (1, 2)
    # design.get_color(2, 2)  # Background color at (2, 2)
    return design


@pytest.fixture
def design_with_invisible():
    # Create a 3x3 design where some pixels are invisible (INVIS color)
    design = Design(height=3, width=3)
    dumb_with_invisible = int_lol_to_motif([[1, 2, 3], [1, 2, 3], [3, 3, 2]])
    design.add_motif(dumb_with_invisible, 0, 0)
    # design.get_color(0, 0)  # Foreground color at (0, 0)
    # design.get_color(1, 0)  # Background color at (1, 0)
    # design.get_color(2, 0)  # Invis color at (2, 0)
    # design.get_color(0, 1)  # Foreground color at (0, 1)
    # design.get_color(1, 1)  # Background color at (1, 1)
    # design.get_color(2, 1)  # Invis color at (2, 1)
    # design.get_color(0, 2)  # Invis color at (0, 2)
    # design.get_color(1, 2)  # Invis color at (1, 2)
    # design.get_color(2, 2)  # Background color at (2, 2)
    return design


@pytest.fixture
def selection():
    # Mocking the Selection, assuming it stores some selected cells
    return Selection([(0, 0), (1, 1), (2, 2)])


# The tests


def test_calculate_float_lengths_empty_design(empty_design):
    # An empty design is full of invisible stuff
    with pytest.raises(AssertionError):
        result = calculate_float_lengths(empty_design)
        # assert result == [], "For an empty design, there should be no floats."


def test_calculate_float_lengths_simple_design(simple_design):
    # Assuming alternating colors, there should be one float from (0,0) to (2,0) (length 1)
    result = calculate_float_lengths(simple_design)
    num = 9
    assert len(result) == num, f"Expected {num} float strands, got {len(result)}"

    # Check the first float length
    assert len(result[0]) == 1, f"Expected float length of 1, got {len(result[0])}"

    # Check the second float length
    assert len(result[1]) == 1, f"Expected float length of 1, got {len(result[1])}"


def test_calculate_float_lengths_with_invisible(design_with_invisible):
    # Test behavior with invisible pixels being treated as background
    result = calculate_float_lengths(design_with_invisible, treat_invisible_as_bg=True)
    num = 5
    assert (
        len(result) == num
    ), f"Expected {num} float strands, got {len(result)}: {result}"

    # print(result)
    # assert False
    # Validate float lengths for each strand
    assert (
        len(result[0]) == 1
    ), f"Expected float length of 2, got {len(result[0])}"  # (0, 0) -> (1, 0)
    assert (
        len(result[1]) == 2
    ), f"Expected float length of 2, got {len(result[1])}"  # (0, 1) -> (1, 1)
    assert (
        len(result[2]) == 1
    ), f"Expected float length of 1, got {len(result[2])}"  # (1, 2) -> (2, 2)
    pass


@pytest.mark.skip(reason="The selection feature is not yet implemented")
def test_calculate_float_lengths_with_selection(design_with_invisible, selection):
    # I doubt that this test is correct
    result = calculate_float_lengths(
        design_with_invisible, selection=selection, treat_invisible_as_bg=True
    )
    assert (
        len(result) == 1
    ), f"Expected 1 float strand based on the selection, got {len(result)}: {result}"
    # Check the length of the float
    assert len(result[0]) == 1, f"Expected float length of 1, got {len(result[0])}"


def test_calculate_float_lengths_with_min_float_length(design_with_invisible):
    result = calculate_float_lengths(
        design_with_invisible, min_float_length=2, treat_invisible_as_bg=True
    )
    # Expect only floats with length >= 2
    num = 3
    assert (
        len(result) == num
    ), f"Expected {num} float strands with min length 2, got {len(result)}: {result}"

    # Ensure the floats have the correct minimum length
    assert all(
        len(f) >= 2 for f in result
    ), "Not all floats meet the minimum length condition."


def test_calculate_float_lengths_incomplete_design(design_with_invisible):
    # Incomplete design should raise an assertion error when `treat_invisible_as_bg=False`
    with pytest.raises(AssertionError):
        calculate_float_lengths(design_with_invisible, treat_invisible_as_bg=False)
