"""Acceptance tests for FUNC-SURFACE-INPUT-001.

The ceiling outline is entered as an ordered sequence of edges, each defined by a length in
meters and the interior angle (degrees) at the corner starting that edge. The first edge sets
the reference direction (heading 0, starting at the origin). ``validate_surface`` reconstructs
the vertices and validates the outline, returning a ``Polygon`` or raising ``SurfaceError``.
"""

import math

import pytest

from ceiling_planner.geometry.surface import (
    Edge,
    Polygon,
    SurfaceError,
    validate_surface,
)


@pytest.mark.req("FUNC-SURFACE-INPUT-001")
def test_accepts_square_and_reconstructs_vertices():
    # Given a 4 m square described as four edges, each a 90 degree corner
    edges = [Edge(4.0, 90.0), Edge(4.0, 90.0), Edge(4.0, 90.0), Edge(4.0, 90.0)]

    # When the outline is validated
    polygon = validate_surface(edges)

    # Then a closed polygon with the four expected corners is returned
    assert isinstance(polygon, Polygon)
    expected = [(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)]
    assert len(polygon.vertices) == len(expected)
    for got, want in zip(polygon.vertices, expected, strict=True):
        assert got == pytest.approx(want)


@pytest.mark.req("FUNC-SURFACE-INPUT-001")
def test_accepts_non_rectangular_l_shape():
    # Given an L-shaped outline (five right corners and one 270 degree reflex corner)
    edges = [
        Edge(4.0, 90.0),
        Edge(2.0, 90.0),
        Edge(2.0, 90.0),
        Edge(2.0, 270.0),
        Edge(2.0, 90.0),
        Edge(4.0, 90.0),
    ]

    # When the outline is validated
    polygon = validate_surface(edges)

    # Then the six vertices of the L are reconstructed and the outline is accepted
    expected = [(0.0, 0.0), (4.0, 0.0), (4.0, 2.0), (2.0, 2.0), (2.0, 4.0), (0.0, 4.0)]
    assert len(polygon.vertices) == len(expected)
    for got, want in zip(polygon.vertices, expected, strict=True):
        assert got == pytest.approx(want)


@pytest.mark.req("FUNC-SURFACE-INPUT-001")
@pytest.mark.parametrize(
    "edges,expected_code",
    [
        (
            [Edge(4.0, 90.0), Edge(4.0, 90.0)],
            "too_few_edges",
        ),
        (
            [Edge(4.0, 90.0), Edge(0.0, 90.0), Edge(4.0, 90.0), Edge(4.0, 90.0)],
            "non_positive_length",
        ),
        (
            [Edge(-1.0, 90.0), Edge(4.0, 90.0), Edge(4.0, 90.0), Edge(4.0, 90.0)],
            "non_positive_length",
        ),
        (
            [Edge(4.0, 0.0), Edge(4.0, 90.0), Edge(4.0, 90.0), Edge(4.0, 90.0)],
            "angle_out_of_range",
        ),
        (
            [Edge(4.0, 360.0), Edge(4.0, 90.0), Edge(4.0, 90.0), Edge(4.0, 90.0)],
            "angle_out_of_range",
        ),
        (
            [Edge(4.0, 90.0), Edge(4.0, 90.0), Edge(3.0, 90.0), Edge(4.0, 90.0)],
            "not_closed",
        ),
        (
            [Edge(4.0, 36.87), Edge(5.0, 36.87), Edge(4.0, 323.13), Edge(5.0, 323.13)],
            "self_intersecting",
        ),
    ],
    ids=[
        "too-few-edges",
        "zero-length",
        "negative-length",
        "angle-zero",
        "angle-360",
        "open-outline",
        "bowtie",
    ],
)
def test_rejects_invalid_outline(edges, expected_code):
    # Given an invalid outline
    # When the outline is validated
    with pytest.raises(SurfaceError) as exc:
        validate_surface(edges)

    # Then the specific violated rule is reported
    assert exc.value.code == expected_code


@pytest.mark.req("FUNC-SURFACE-INPUT-001")
def test_closure_tolerance_is_configurable():
    # Given an outline whose closure gap is 1 cm (a slightly short third edge)
    edges = [Edge(4.0, 90.0), Edge(4.0, 90.0), Edge(3.99, 90.0), Edge(4.0, 90.0)]

    # When validated with a tolerance below the gap it is rejected...
    with pytest.raises(SurfaceError) as exc:
        validate_surface(edges, closure_tolerance_m=0.005)
    assert exc.value.code == "not_closed"

    # ...and accepted when the tolerance covers the gap
    polygon = validate_surface(edges, closure_tolerance_m=0.02)
    assert isinstance(polygon, Polygon)


@pytest.mark.req("FUNC-SURFACE-INPUT-001")
def test_interior_angles_may_be_non_right_angles():
    # Given a rhombus with 60 and 120 degree corners and unit sides
    edges = [Edge(1.0, 120.0), Edge(1.0, 60.0), Edge(1.0, 120.0), Edge(1.0, 60.0)]

    # When the outline is validated
    polygon = validate_surface(edges)

    # Then it is accepted and the second vertex reflects the 60 degree turn
    assert polygon.vertices[0] == pytest.approx((0.0, 0.0))
    assert polygon.vertices[1] == pytest.approx((1.0, 0.0))
    # third vertex: from (1,0) heading turns by 180-60=120 degrees
    expected_v3 = (1.0 + math.cos(math.radians(120.0)), math.sin(math.radians(120.0)))
    assert polygon.vertices[2] == pytest.approx(expected_v3)
