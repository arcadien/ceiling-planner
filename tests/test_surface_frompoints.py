"""Acceptance tests for FUNC-SURFACE-FROMPOINTS-001.

``edges_from_vertices`` turns an ordered list of outline vertices into the edge sequence
(length + interior angle) consumed by ``validate_surface``. Clockwise input is normalized to
counter-clockwise, and the derived sequence round-trips back to the same shape.
"""

import pytest
from fastapi.testclient import TestClient

from ceiling_planner.api.app import app
from ceiling_planner.geometry.surface import edges_from_vertices, validate_surface

client = TestClient(app)

SQUARE = [(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)]
L_SHAPE = [(0.0, 0.0), (4.0, 0.0), (4.0, 2.0), (2.0, 2.0), (2.0, 4.0), (0.0, 4.0)]


@pytest.mark.req("FUNC-SURFACE-FROMPOINTS-001")
def test_square_vertices_derive_four_right_angle_edges():
    # Given the four corners of a square
    # When the edge sequence is derived
    edges = edges_from_vertices(SQUARE)

    # Then every edge is 4 m long with a 90 degree corner
    assert [(e.length_m, e.interior_angle_deg) for e in edges] == pytest.approx(
        [(4.0, 90.0), (4.0, 90.0), (4.0, 90.0), (4.0, 90.0)]
    )


@pytest.mark.req("FUNC-SURFACE-FROMPOINTS-001")
def test_reflex_corner_is_derived_for_l_shape():
    # Given the six corners of an L-shape
    # When the edge sequence is derived
    edges = edges_from_vertices(L_SHAPE)

    # Then the reflex corner comes out as 270 degrees
    assert [round(e.interior_angle_deg, 3) for e in edges] == [90.0, 90.0, 90.0, 270.0, 90.0, 90.0]
    assert [round(e.length_m, 3) for e in edges] == [4.0, 2.0, 2.0, 2.0, 2.0, 4.0]


@pytest.mark.req("FUNC-SURFACE-FROMPOINTS-001")
def test_clockwise_input_is_normalized_to_convex_angles():
    # Given a square traced clockwise
    clockwise = list(reversed(SQUARE))

    # When the edge sequence is derived
    edges = edges_from_vertices(clockwise)

    # Then corners are still 90 degrees, not 270
    assert all(e.interior_angle_deg == pytest.approx(90.0) for e in edges)


@pytest.mark.req("FUNC-SURFACE-FROMPOINTS-001")
def test_derived_edges_round_trip_through_validation():
    # Given the derived edges of an L-shape
    edges = edges_from_vertices(L_SHAPE)

    # When they are validated
    polygon = validate_surface(edges)

    # Then the reconstructed shape matches the original vertices
    assert len(polygon.vertices) == len(L_SHAPE)
    for got, want in zip(polygon.vertices, L_SHAPE, strict=True):
        assert got == pytest.approx(want)


@pytest.mark.req("FUNC-SURFACE-FROMPOINTS-001")
def test_fewer_than_three_vertices_is_rejected():
    # Given only two vertices
    # When the edge sequence is derived
    with pytest.raises(ValueError):
        edges_from_vertices([(0.0, 0.0), (1.0, 0.0)])


@pytest.mark.req("FUNC-SURFACE-FROMPOINTS-001")
def test_edges_endpoint_returns_derived_edges():
    # Given a square drawn as points
    response = client.post("/edges", json={"points": [list(p) for p in SQUARE]})

    # Then the endpoint returns the four derived edges
    assert response.status_code == 200
    edges = response.json()["edges"]
    assert len(edges) == 4
    assert edges[0]["length_m"] == pytest.approx(4.0)
    assert edges[0]["interior_angle_deg"] == pytest.approx(90.0)


@pytest.mark.req("FUNC-SURFACE-FROMPOINTS-001")
def test_edges_endpoint_rejects_too_few_points():
    # Given fewer than three points
    response = client.post("/edges", json={"points": [[0.0, 0.0], [1.0, 0.0]]})

    # Then the request is rejected with HTTP 400
    assert response.status_code == 400
    assert "error" in response.json()
