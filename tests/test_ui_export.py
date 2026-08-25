"""Acceptance tests for UI-EXPORT-001.

The page offers PNG and SVG export controls for the current plan schema.
"""

import pytest
from fastapi.testclient import TestClient

from ceiling_planner.api.app import app

client = TestClient(app)


@pytest.mark.req("UI-EXPORT-001")
def test_page_offers_png_and_svg_export():
    # Given the served page
    body = client.get("/").text

    # Then it exposes PNG and SVG export controls
    assert 'id="export-png"' in body
    assert 'id="export-svg"' in body
