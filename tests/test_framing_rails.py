"""Acceptance tests for FUNC-FRAMING-RAILS-001.

Rails are fixed to the walls that carry the montant ends: every outline edge not parallel to
the bearing direction (the first edge, which lies along the x axis after reconstruction). Each
such edge yields one rail equal to its length; edges parallel to the bearing direction carry
no structural rail.
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
def test_square_has_two_rails_on_the_bearing_walls():
    # Given a 4 m square whose first edge runs along x
    # When the rail cut list is computed
    rails = compute_rails(SQUARE)

    # Then only the two vertical walls carry rails, each equal to the wall length
    assert [r.length_m for r in rails] == pytest.approx([4.0, 4.0])


@pytest.mark.req("FUNC-FRAMING-RAILS-001")
def test_rail_length_follows_the_bearing_wall_height():
    # Given a 6 m by 3 m rectangle with the 6 m side entered first
    # When the rail cut list is computed
    rails = compute_rails(WIDE)

    # Then the two rails match the 3 m bearing walls, not the 6 m free edges
    assert [r.length_m for r in rails] == pytest.approx([3.0, 3.0])


@pytest.mark.req("FUNC-FRAMING-RAILS-001")
def test_l_shape_rails_cover_every_non_parallel_edge():
    # Given an L-shaped outline
    # When the rail cut list is computed
    rails = compute_rails(L_SHAPE)

    # Then each of the three non-parallel edges yields a rail
    assert sorted(r.length_m for r in rails) == pytest.approx([2.0, 2.0, 4.0])


@pytest.mark.req("FUNC-FRAMING-RAILS-001")
def test_oblique_edges_still_count_as_bearing_walls():
    # Given a rhombus whose two slanted sides are not parallel to the bearing direction
    # When the rail cut list is computed
    rails = compute_rails(RHOMBUS)

    # Then both slanted unit-length sides carry rails; the two horizontal sides do not
    assert [r.length_m for r in rails] == pytest.approx([1.0, 1.0])


@pytest.mark.req("FUNC-FRAMING-RAILS-001")
def test_rail_is_a_value_object():
    # Given the rails of a square
    rail = compute_rails(SQUARE)[0]

    # Then each rail exposes its length as a Rail value
    assert isinstance(rail, Rail)
    assert rail.length_m == pytest.approx(4.0)
