"""Business logic composing the repository into BOM, price capture, and summary operations.

Covers BOM-FUNC-LINES-001, BOM-FUNC-PRICES-001, and BOM-FUNC-SUMMARY-001.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from devis_bom.models import BomLine, PriceCapture
from devis_bom.storage import BomRepository


class DevisBomError(Exception):
    """Raised when an operation violates a domain rule. ``code`` identifies which one."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class LineWithPrices:
    line: BomLine
    captures: list[PriceCapture]

    @property
    def best_capture(self) -> PriceCapture | None:
        return self.captures[0] if self.captures else None


@dataclass(frozen=True)
class Summary:
    estimated_total: float
    currency: str
    priced_line_ids: list[int]
    gaps: list[BomLine]


class DevisBomService:
    """Domain operations for the BOM, on top of a :class:`BomRepository`."""

    def __init__(self, repository: BomRepository) -> None:
        self._repository = repository

    def add_line(
        self, reference: str, designation: str, quantity: float, unit: str = "pcs"
    ) -> BomLine:
        reference = reference.strip()
        designation = designation.strip()
        if not reference:
            raise DevisBomError("empty_reference")
        if not designation:
            raise DevisBomError("empty_designation")
        if quantity <= 0:
            raise DevisBomError("non_positive_quantity")
        if self._repository.get_line_by_reference(reference) is not None:
            raise DevisBomError("duplicate_reference")
        return self._repository.add_line(reference, designation, quantity, unit.strip() or "pcs")

    def delete_line(self, line_id: int) -> None:
        if not self._repository.delete_line(line_id):
            raise DevisBomError("unknown_line")

    def record_price(
        self, reference: str, store: str, price: float, url: str, currency: str = "EUR"
    ) -> PriceCapture:
        store = store.strip()
        if not store:
            raise DevisBomError("empty_store")
        if price <= 0:
            raise DevisBomError("non_positive_price")
        line = self._repository.get_line_by_reference(reference)
        if line is None:
            raise DevisBomError("unknown_reference")
        captured_at = datetime.now(UTC).isoformat()
        return self._repository.add_capture(
            line.id, store, price, currency.strip() or "EUR", url.strip(), captured_at
        )

    def list_lines_with_prices(self) -> list[LineWithPrices]:
        return [
            LineWithPrices(line, self._repository.list_captures(line.id))
            for line in self._repository.list_lines()
        ]

    def summary(self) -> Summary:
        lines = self.list_lines_with_prices()
        priced = [lp for lp in lines if lp.best_capture is not None]
        gaps = [lp.line for lp in lines if lp.best_capture is None]
        total = sum(lp.line.quantity * lp.best_capture.price for lp in priced)
        currency = priced[0].best_capture.currency if priced else "EUR"
        return Summary(
            estimated_total=total,
            currency=currency,
            priced_line_ids=[lp.line.id for lp in priced],
            gaps=gaps,
        )
