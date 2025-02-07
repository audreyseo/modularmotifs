import pytest
from modularmotifs.ui.util.selection import Selection
from typing import List, Tuple

# Tests generated by chatgpt

@pytest.fixture
def empty_selection():
    return Selection()

@pytest.fixture
def sample_selection():
    return Selection([(3, 3), (1, 2), (2, 1)])

def test_empty_initialization(empty_selection):
    # Test if an empty selection initializes correctly
    assert len(empty_selection.selected_cells) == 0
    assert list(empty_selection) == []

def test_initialization_with_selected_cells():
    # Test if initialization with selected cells works
    selected_cells = [(1, 1), (2, 2)]
    selection = Selection(selected_cells)
    assert len(selection.selected_cells) == 2
    assert list(selection) == [(1, 1), (2, 2)]

def test_add_method():
    # Test the add method
    selection = Selection()
    selection.add(1, 1)
    selection.add(2, 2)
    selection.add(3, 3)
    assert len(selection.selected_cells) == 3
    assert list(selection) == [(1, 1), (2, 2), (3, 3)]

def test_add_duplicate():
    # Test that duplicates are not added
    selection = Selection([(1, 1), (2, 2)])
    selection.add(1, 1)  # Adding a duplicate
    selection.add(3, 3)
    assert len(selection.selected_cells) == 3
    assert list(selection) == [(1, 1), (2, 2), (3, 3)]

def test_row_major_order(sample_selection):
    # Test that cells are sorted in row-major order
    assert list(sample_selection) == [(2, 1), (1, 2), (3, 3)]

def test_iterator(sample_selection):
    # Test the iterator
    iter_cells = list(sample_selection)
    assert iter_cells == [(2, 1), (1, 2), (3, 3)]

def test_repr(sample_selection):
    # Test the string representation -- it will give the row-major order which looks weird
    assert repr(sample_selection) == "Selection([(2, 1),(1, 2),(3, 3)])"

def test_add_empty():
    # Test adding an element to an empty selection
    selection = Selection()
    selection.add(5, 5)
    assert len(selection.selected_cells) == 1
    assert list(selection) == [(5, 5)]

def test_repr_empty(empty_selection):
    # Test the string representation for an empty selection
    assert repr(empty_selection) == "Selection([])"

def test_multiple_adds():
    # Test adding multiple cells and checking if the list is correctly sorted
    selection = Selection([(3, 3)])
    selection.add(1, 1).add(2, 2).add(0, 0)
    assert list(selection) == [(0, 0), (1, 1), (2, 2), (3, 3)]

def test_edge_case_out_of_bounds():
    # This would be a hypothetical test if selection cells were to be restricted to grid bounds
    # For now, it's just a placeholder since this class doesn't restrict bounds.
    selection = Selection([(0, 0), (4, 5)])
    assert list(selection) == [(0, 0), (4, 5)]
