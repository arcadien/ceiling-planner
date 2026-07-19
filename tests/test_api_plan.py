"""Acceptance tests for TECH-API-PLAN-001.

``POST /plan`` accepts an outline as edges (length + interior angle) plus optional parameters
and returns the reconstructed vertices, montant and rail cut lists, and the plate layout. A
failed outline validation or an invalid parameter returns HTTP 400 with a code.
"""

import pytest
from fastapi.testclient import TestClient

from ceiling_planner.api.app import app

client = TestClient(app)

SQUARE_EDGES = [{"length_m": 4.0, "interior_angle_deg": 90.0} for _ in range(4)]


@pytest.mark.req("TECH-API-PLAN-001")
def test_plan_returns_full_material_plan_for_valid_outline():
    # Given a valid square outline
    # When a plan is requested
    response = client.post("/plan", json={"edges": SQUARE_EDGES})

    # Then every section of the material plan is present
    assert response.status_code == 200
    data = response.json()
    expected_vertices = [[0.0, 0.0], [4.0, 0.0], [4.0, 4.0], [0.0, 4.0]]
    assert len(data["vertices"]) == len(expected_vertices)
    for got, want in zip(data["vertices"], expected_vertices, strict=True):
        assert got == pytest.approx(want)
    assert len(data["montants"]) >= 1
    assert len(data["rails"]) == 2
    assert data["plates"]["plate_count"] >= 1
    assert data["plates"]["pieces"][0]["kind"] in {"full", "cut", "reused"}


@pytest.mark.req("TECH-API-PLAN-001")
def test_optional_parameters_are_honored():
    # Given a plan requested with a coarse montant spacing
    response = client.post(
        "/plan", json={"edges": SQUARE_EDGES, "montant_spacing_m": 4.0}
    )

    # Then the montants follow that spacing (offsets 0 and 4 only)
    assert response.status_code == 200
    offsets = [m["offset_m"] for m in response.json()["montants"]]
    assert offsets == pytest.approx([0.0, 4.0])


@pytest.mark.req("TECH-API-PLAN-001")
def test_invalid_outline_returns_400_with_code():
    # Given an outline with too few edges
    response = client.post(
        "/plan", json={"edges": [{"length_m": 4.0, "interior_angle_deg": 90.0}] * 2}
    )

    # Then the validation code is reported with HTTP 400
    assert response.status_code == 400
    assert response.json()["error"] == "too_few_edges"


@pytest.mark.req("TECH-API-PLAN-001")
def test_invalid_parameter_returns_400():
    # Given a valid outline but a non-positive montant spacing
    response = client.post(
        "/plan", json={"edges": SQUARE_EDGES, "montant_spacing_m": 0.0}
    )

    # Then the request is rejected with HTTP 400
    assert response.status_code == 400
    assert "error" in response.json()
