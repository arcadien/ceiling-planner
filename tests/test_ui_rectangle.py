"""Acceptance tests for UI-RECT-001.

The page offers a rectangle shortcut: width and height inputs plus a button that fills the edge
list with the four right-angle edges of that rectangle.
"""

import pytest
from fastapi.testclient import TestClient

from ceiling_planner.api.app import app

client = TestClient(app)


@pytest.mark.req("UI-RECT-001")
def test_page_offers_a_rectangle_shortcut():
    # Given the served page
    body = client.get("/").text

    # Then it exposes width/height inputs and an apply control for a rectangle
    assert 'id="rect-width"' in body
    assert 'id="rect-height"' in body
    assert 'id="rect-apply"' in body
