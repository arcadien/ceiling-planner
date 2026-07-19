"""Acceptance tests for UI-DRAW-001.

The schema page offers a draw mode: the user sketches the outline on the canvas, and the
points are converted to editable edges through the ``/edges`` endpoint.
"""

import pytest
from fastapi.testclient import TestClient

from ceiling_planner.api.app import app

client = TestClient(app)


@pytest.mark.req("UI-DRAW-001")
def test_page_offers_a_draw_control():
    # Given the served page
    body = client.get("/").text

    # Then it exposes a draw control
    assert 'id="draw"' in body


@pytest.mark.req("UI-DRAW-001")
def test_page_sends_drawn_points_to_the_edges_endpoint():
    # Given the served page
    body = client.get("/").text

    # Then its script posts the sketch to /edges
    assert "/edges" in body
