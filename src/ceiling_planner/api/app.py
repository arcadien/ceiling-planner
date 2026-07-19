"""HTTP application exposing the material plan (TECH-API-PLAN-001) and the schema page.

``POST /plan`` composes the geometry validator, the framing calculator, and the plate optimizer
behind one JSON endpoint. Outline-validation failures and invalid parameters are mapped to
HTTP 400 with a machine-readable code.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from ceiling_planner.framing.montants import compute_montants
from ceiling_planner.framing.rails import compute_rails
from ceiling_planner.geometry.surface import (
    Edge,
    SurfaceError,
    edges_from_vertices,
    validate_surface,
)
from ceiling_planner.plates.optimizer import optimize_plates


class EdgeIn(BaseModel):
    length_m: float
    interior_angle_deg: float


class PointsRequest(BaseModel):
    points: list[tuple[float, float]]


class PlanRequest(BaseModel):
    edges: list[EdgeIn]
    closure_tolerance_m: float = 0.02
    montant_spacing_m: float = 0.60
    plate_length_m: float = 2.50
    plate_width_m: float = 1.20
    min_offcut_m: float = 0.30


app = FastAPI(title="ceiling-planner")

_PAGE = Path(__file__).parent / "static" / "index.html"


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    """Serve the self-contained schema page (UI-SCHEMA-001)."""
    return _PAGE.read_text(encoding="utf-8")


@app.post("/edges", response_model=None)
def edges(request: PointsRequest) -> JSONResponse | dict:
    """Derive the editable edge sequence from drawn vertices (FUNC-SURFACE-FROMPOINTS-001)."""
    try:
        derived = edges_from_vertices([(x, y) for x, y in request.points])
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    return {
        "edges": [
            {"length_m": e.length_m, "interior_angle_deg": e.interior_angle_deg} for e in derived
        ]
    }


@app.post("/plan", response_model=None)
def plan(request: PlanRequest) -> JSONResponse | dict:
    """Validate the outline and return the full material plan, or HTTP 400 with a code."""
    edges = [Edge(e.length_m, e.interior_angle_deg) for e in request.edges]
    try:
        polygon = validate_surface(edges, closure_tolerance_m=request.closure_tolerance_m)
        montants = compute_montants(polygon, spacing_m=request.montant_spacing_m)
        rails = compute_rails(polygon)
        plates = optimize_plates(
            polygon,
            plate_length_m=request.plate_length_m,
            plate_width_m=request.plate_width_m,
            min_offcut_m=request.min_offcut_m,
        )
    except SurfaceError as exc:
        return JSONResponse(status_code=400, content={"error": exc.code})
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})

    return {
        "vertices": [[x, y] for x, y in polygon.vertices],
        "montants": [{"offset_m": m.offset_m, "length_m": m.length_m} for m in montants],
        "rails": [{"length_m": r.length_m} for r in rails],
        "plates": {
            "plate_count": plates.plate_count,
            "covered_length_m": plates.covered_length_m,
            "waste_length_m": plates.waste_length_m,
            "pieces": [asdict(p) for p in plates.pieces],
        },
    }
