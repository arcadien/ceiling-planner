"""HTTP application exposing the BOM, price-capture, and summary API, and the management page.

Independent from ``ceiling_planner``'s API (see BOM-TECH-API-001). CORS is opened to any origin
so the companion browser extension, running under a ``chrome-extension://`` origin, can call the
API directly — an accepted tradeoff for a tool run locally for a single user.
"""

from __future__ import annotations

import os
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from devis_bom.service import DevisBomError, DevisBomService, LineWithPrices
from devis_bom.storage import BomRepository

_PAGE = Path(__file__).parent / "static" / "index.html"

_ERROR_STATUS = {
    "unknown_reference": 404,
    "unknown_line": 404,
}


class LineIn(BaseModel):
    reference: str
    designation: str
    quantity: float
    unit: str = "pcs"


class PriceIn(BaseModel):
    reference: str
    store: str
    price: float
    url: str = ""
    currency: str = "EUR"


def _line_json(line_with_prices: LineWithPrices) -> dict:
    best = line_with_prices.best_capture
    return {
        "line": asdict(line_with_prices.line),
        "captures": [asdict(c) for c in line_with_prices.captures],
        "best_capture": asdict(best) if best else None,
    }


def create_app(db_path: str | None = None) -> FastAPI:
    """Build the app with its own repository, so tests can point it at a throwaway database."""
    app = FastAPI(title="devis-bom")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    resolved_path = db_path or os.environ.get("DEVIS_BOM_DB_PATH", "devis_bom.db")
    service = DevisBomService(BomRepository(resolved_path))

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        """Serve the self-contained BOM management page (BOM-UI-PAGE-001)."""
        return _PAGE.read_text(encoding="utf-8")

    @app.get("/api/lines")
    def list_lines() -> list[dict]:
        return [_line_json(lp) for lp in service.list_lines_with_prices()]

    @app.post("/api/lines", response_model=None)
    def add_line(request: LineIn) -> JSONResponse | dict:
        try:
            line = service.add_line(
                request.reference, request.designation, request.quantity, request.unit
            )
        except DevisBomError as exc:
            return JSONResponse(status_code=400, content={"error": exc.code})
        return asdict(line)

    @app.delete("/api/lines/{line_id}", response_model=None)
    def delete_line(line_id: int) -> JSONResponse | dict:
        try:
            service.delete_line(line_id)
        except DevisBomError as exc:
            return JSONResponse(
                status_code=_ERROR_STATUS.get(exc.code, 400), content={"error": exc.code}
            )
        return {"deleted": line_id}

    @app.post("/api/prices", response_model=None)
    def add_price(request: PriceIn) -> JSONResponse | dict:
        try:
            capture = service.record_price(
                request.reference, request.store, request.price, request.url, request.currency
            )
        except DevisBomError as exc:
            return JSONResponse(
                status_code=_ERROR_STATUS.get(exc.code, 400), content={"error": exc.code}
            )
        return asdict(capture)

    @app.get("/api/summary")
    def summary() -> dict:
        result = service.summary()
        return {
            "estimated_total": result.estimated_total,
            "currency": result.currency,
            "priced_line_ids": result.priced_line_ids,
            "gaps": [asdict(line) for line in result.gaps],
        }

    return app


app = create_app()
