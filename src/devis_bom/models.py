"""Domain types for the BOM and its captured store prices.

Covers BOM-FUNC-LINES-001 (lines) and BOM-FUNC-PRICES-001 (price captures).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BomLine:
    id: int
    reference: str
    designation: str
    quantity: float
    unit: str = "pcs"


@dataclass(frozen=True)
class PriceCapture:
    id: int
    line_id: int
    store: str
    price: float
    currency: str
    url: str
    captured_at: str
