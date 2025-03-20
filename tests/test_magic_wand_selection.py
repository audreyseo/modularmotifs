import pytest

from modularmotifs.motiflibrary.examples import motifs

from modularmotifs.core.design import Design
from modularmotifs.ui.util.magic_wand_selection import magic_wand_select

@pytest.fixture
def design_example():
    d = Design(9, 9)
    """
101000000
010000000
101000000
000101000
000010000
000101000
000000000
000000000
000000000
"""
    
    d.add_motif(motifs["x-3x3"], 0, 0)
    d.add_motif(motifs["x-3x3"], 3, 3)
    return d
@pytest.fixture
def empty_design():
    d = Design(0, 0)
    return d

@pytest.fixture
def blank_design():
    d = Design(3, 3)
    return d

@pytest.fixture
def noncontiguous_design():
    d = Design(9, 9)
    d.add_motif(motifs["x-3x3"], 0, 0)
    d.add_motif(motifs["x-3x3"], 6, 6)
    return d

import pytest

def test_basic_selection(design_example):
    start = (0, 0)  # Starting from the first red pixel
    
    result = magic_wand_select(design_example, *start)
    
    expected_result = set([
        (0, 0),
        (2, 0),
        (1, 1),
        (0, 2),
        (2, 2),
        (3, 3),
        (5, 3),
        (4, 4),
        (3, 5),
        (5, 5)
    ])
    
    assert result == expected_result
    
    result1 = magic_wand_select(design_example, *(1, 1))
    assert result1 == expected_result
    
    result2 = magic_wand_select(design_example, 5, 5)
    assert result2 == expected_result
    
    result3 = magic_wand_select(design_example, 3, 5)
    assert result3 == expected_result
    

def test_edge_case_empty_image(empty_design):
    start = (0, 0)
    try:
        result = magic_wand_select(empty_design, *start)
        assert False
    except:
        assert True

def test_full_image_replacement(blank_design):
    start = (1, 1)  # Start from the center
    assert blank_design.in_range(1, 1), f"Not in range"
    
    result = magic_wand_select(blank_design, *start)
    
    expected_result = set([
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 1),
        (1, 2),
        (2, 0),
        (2, 1),
        (2, 2)
    ])
    
    assert result == expected_result

def test_out_of_bounds(design_example):
    start = (10, 10)  # Start point out of bounds
    
    result = magic_wand_select(design_example, *start, )
    
    assert result == set([])

def test_non_contiguous_selection(noncontiguous_design):
    start = (0, 0)
    
    result = magic_wand_select(noncontiguous_design, *start)
    
    expected_result = set([
        (0, 0),
        (2, 0),
        (1, 1),
        (0, 2),
        (2, 2)
    ])
    
    assert result == expected_result
    
    result1 = magic_wand_select(noncontiguous_design, 8, 8)
    expected_result = set([
        (6, 6),
        (8, 6),
        (7, 7),
        (6, 8),
        (8, 8)
    ])
