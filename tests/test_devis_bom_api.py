"""Acceptance tests for BOM-TECH-API-001 and BOM-UI-PAGE-001.

Exercises the HTTP surface over the domain logic already covered by
``test_devis_bom_service.py``: status codes, error codes, and JSON shapes.
"""

import pytest
from fastapi.testclient import TestClient

from devis_bom.api.app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(str(tmp_path / "test.db"))
    return TestClient(app)


@pytest.mark.req("BOM-TECH-API-001")
def test_add_and_list_line(client):
    response = client.post(
        "/api/lines", json={"reference": "REF-1", "designation": "Item", "quantity": 2}
    )
    assert response.status_code == 200

    response = client.get("/api/lines")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["line"]["reference"] == "REF-1"
    assert data[0]["best_capture"] is None


@pytest.mark.req("BOM-TECH-API-001")
def test_add_line_with_duplicate_reference_returns_400(client):
    client.post("/api/lines", json={"reference": "REF-1", "designation": "Item", "quantity": 1})

    response = client.post(
        "/api/lines", json={"reference": "REF-1", "designation": "Item 2", "quantity": 1}
    )

    assert response.status_code == 400
    assert response.json()["error"] == "duplicate_reference"


@pytest.mark.req("BOM-TECH-API-001")
def test_capture_price_for_unknown_reference_returns_404(client):
    response = client.post(
        "/api/prices", json={"reference": "UNKNOWN", "store": "Rexel", "price": 10}
    )

    assert response.status_code == 404
    assert response.json()["error"] == "unknown_reference"


@pytest.mark.req("BOM-TECH-API-001")
def test_capture_price_then_summary_reflects_it(client):
    client.post("/api/lines", json={"reference": "REF-1", "designation": "Item", "quantity": 3})

    response = client.post(
        "/api/prices",
        json={"reference": "REF-1", "store": "Rexel", "price": 5.0, "url": "https://rexel.example"},
    )
    assert response.status_code == 200

    response = client.get("/api/summary")
    assert response.status_code == 200
    summary = response.json()
    assert summary["estimated_total"] == pytest.approx(15.0)
    assert summary["gaps"] == []


@pytest.mark.req("BOM-TECH-API-001")
def test_delete_line_removes_it(client):
    response = client.post(
        "/api/lines", json={"reference": "REF-1", "designation": "Item", "quantity": 1}
    )
    line_id = response.json()["id"]

    response = client.delete(f"/api/lines/{line_id}")
    assert response.status_code == 200

    response = client.get("/api/lines")
    assert response.json() == []


@pytest.mark.req("BOM-TECH-API-001")
def test_delete_unknown_line_returns_404(client):
    response = client.delete("/api/lines/999")

    assert response.status_code == 404
    assert response.json()["error"] == "unknown_line"


@pytest.mark.req("BOM-UI-PAGE-001")
def test_index_serves_the_bom_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "devis-bom" in response.text
