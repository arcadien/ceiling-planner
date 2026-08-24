"""Acceptance tests for FUNC-FRAMING-ORIENT-001.

The montants run in the shortest dimension. ``bearing_axis`` returns the axis they run along and
``transposed`` swaps x and y so framing computed with a horizontal bearing maps to that axis.
"""

import pytest

from ceiling_planner.framing.orientation import bearing_axis, transposed
from ceiling_planner.geometry.surface import Polygon


def rectangle(width: float, height: float) -> Polygon:
    return Polygon([(0.0, 0.0), (width, 0.0), (width, height), (0.0, height)])


@pytest.mark.req("FUNC-FRAMING-ORIENT-001")
def test_tall_room_keeps_bearing_on_x():
    # Given a room taller than wide (x-extent < y-extent)
    # Then montants already run along x (the shorter dimension)
    assert bearing_axis(rectangle(3.0, 6.0)) == "x"


@pytest.mark.req("FUNC-FRAMING-ORIENT-001")
def test_wide_room_moves_bearing_to_y():
    # Given a corridor wider than tall (x-extent > y-extent)
    # Then montants run along y (across the shorter width)
    assert bearing_axis(rectangle(6.0, 3.0)) == "y"


@pytest.mark.req("FUNC-FRAMING-ORIENT-001")
def test_square_defaults_to_x():
    # Given equal extents
    # Then the bearing defaults to x
    assert bearing_axis(rectangle(4.0, 4.0)) == "x"


@pytest.mark.req("FUNC-FRAMING-ORIENT-001")
def test_transposed_swaps_coordinates():
    # Given an L-shaped outline
    poly = Polygon([(0.0, 0.0), (4.0, 0.0), (4.0, 2.0), (2.0, 2.0), (2.0, 4.0), (0.0, 4.0)])

    # When it is transposed
    swapped = transposed(poly)

    # Then every vertex has x and y exchanged
    assert swapped.vertices == [(y, x) for (x, y) in poly.vertices]


@pytest.mark.req("FUNC-FRAMING-ORIENT-001")
def test_transposing_a_wide_room_makes_it_bearing_x():
    # Given a wide room whose bearing should be y
    wide = rectangle(6.0, 3.0)

    # When transposed, the bearing axis of the result is x (framing computes horizontally)
    assert bearing_axis(transposed(wide)) == "x"
