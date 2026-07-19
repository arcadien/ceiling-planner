"""Acceptance tests for UI-SCHEMA-001.

The application serves a single, self-contained web page at the root path. The page hosts the
canvas schema and talks to the ``/plan`` endpoint; it must not pull scripts or styles from an
external host.
"""

import pytest
from fastapi.testclient import TestClient

from ceiling_planner.api.app import app

client = TestClient(app)


@pytest.mark.req("UI-SCHEMA-001")
def test_root_serves_html_page():
    # When the root path is requested
    response = client.get("/")

    # Then an HTML page is returned
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.req("UI-SCHEMA-001")
def test_page_hosts_the_schema_canvas_and_calls_the_api():
    # Given the served page
    body = client.get("/").text

    # Then it carries the schema canvas and requests a plan from /plan
    assert "<canvas" in body
    assert "/plan" in body


@pytest.mark.req("UI-SCHEMA-001")
def test_page_is_self_contained():
    # Given the served page
    body = client.get("/").text

    # Then it references no external script or stylesheet host
    assert 'src="http' not in body
    assert 'href="http' not in body
    assert "cdn" not in body.lower()
