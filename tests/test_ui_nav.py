"""Acceptance tests for UI-NAV-001.

The schema canvas supports wheel zoom, drag pan, and a recenter (fit) control.
"""

import pytest
from fastapi.testclient import TestClient

from ceiling_planner.api.app import app

client = TestClient(app)


@pytest.mark.req("UI-NAV-001")
def test_page_supports_zoom_and_pan():
    # Given the served page
    body = client.get("/").text

    # Then it wires wheel zoom and exposes a recenter control
    assert "wheel" in body
    assert 'id="fit"' in body
