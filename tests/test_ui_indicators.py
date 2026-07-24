"""Acceptance tests for the indicators and layer toggles of UI-SCHEMA-001.

The page exposes material indicators (total montant length, total rail length, plate count) and
toggles that show or hide the montant and rail overlays on the schema.
"""

import pytest
from fastapi.testclient import TestClient

from ceiling_planner.api.app import app

client = TestClient(app)


@pytest.mark.req("UI-SCHEMA-001")
def test_page_exposes_material_indicators():
    # Given the served page
    body = client.get("/").text

    # Then it carries an indicator element for each material total
    assert 'id="ind-montant"' in body
    assert 'id="ind-rail"' in body
    assert 'id="ind-plates"' in body
    assert 'id="ind-section"' in body


@pytest.mark.req("UI-SCHEMA-001")
def test_page_exposes_layer_toggles():
    # Given the served page
    body = client.get("/").text

    # Then it offers toggles to hide the montant and rail overlays
    assert 'id="toggle-montants"' in body
    assert 'id="toggle-rails"' in body
