"""Acceptance tests for FUNC-FRAMING-RAILS-001.

Rails follow the whole perimeter: every outline edge carries one rail equal to its length, so
the rails sit flush against every wall.
"""

import math

import pytest

from ceiling_planner.framing.rails import Rail, compute_rails
from ceiling_planner.geometry.surface import Polygon

SQUARE = Polygon([(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)])
WIDE = Polygon([(0.0, 0.0), (6.0, 0.0), (6.0, 3.0), (0.0, 3.0)])
L_SHAPE = Polygon([(0.0, 0.0), (4.0, 0.0), (4.0, 2.0), (2.0, 2.0), (2.0, 4.0), (0.0, 4.0)])
RHOMBUS = Polygon(
    [
        (0.0, 0.0),
        (1.0, 0.0),
        (1.0 + math.cos(math.radians(120.0)), math.sin(math.radians(120.0))),
        (math.cos(math.radians(120.0)), math.sin(math.radians(120.0))),
    ]
)


@pytest.mark.req("FUNC-FRAMING-RAILS-001")
def test_square_has_a_rail_on_every_wall():
    # Given a 4 m square
    # When the rail cut list is computed
    rails = compute_rails(SQUARE)

    # Then all four walls carry a 4 m rail
    assert [r.length_m for r in rails] == pytest.approx([4.0, 4.0, 4.0, 4.0])


@pytest.mark.req("FUNC-FRAMING-RAILS-001")
def test_rectangle_rails_follow_all_four_sides():
    # Given a 6 m by 3 m rectangle with the 6 m side entered first
    # When the rail cut list is computed
    rails = compute_rails(WIDE)

    # Then rails follow the full perimeter, in outline order
    assert [r.length_m for r in rails] == pytest.approx([6.0, 3.0, 6.0, 3.0])


@pytest.mark.req("FUNC-FRAMING-RAILS-001")
def test_l_shape_rails_cover_every_edge():
    # Given an L-shaped outline
    # When the rail cut list is computed
    rails = compute_rails(L_SHAPE)

    # Then each of the six edges yields a rail
    assert sorted(r.length_m for r in rails) == pytest.approx([2.0, 2.0, 2.0, 2.0, 4.0, 4.0])


@pytest.mark.req("FUNC-FRAMING-RAILS-001")
def test_oblique_edges_also_carry_rails():
    # Given a rhombus with unit-length sides
    # When the rail cut list is computed
    rails = compute_rails(RHOMBUS)

    # Then every side, slanted or horizontal, carries a rail
    assert [r.length_m for r in rails] == pytest.approx([1.0, 1.0, 1.0, 1.0])


@pytest.mark.req("FUNC-FRAMING-RAILS-001")
def test_rail_is_a_value_object():
    # Given the rails of a square
    rail = compute_rails(SQUARE)[0]

    # Then each rail exposes its length as a Rail value
    assert isinstance(rail, Rail)
    assert rail.length_m == pytest.approx(4.0)
