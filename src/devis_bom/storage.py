"""SQLite-backed persistence for BOM lines and price captures.

Covers BOM-FUNC-LINES-001 and BOM-FUNC-PRICES-001.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from devis_bom.models import BomLine, PriceCapture

_SCHEMA = """
CREATE TABLE IF NOT EXISTS bom_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT NOT NULL,
    designation TEXT NOT NULL,
    quantity REAL NOT NULL,
    unit TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS price_captures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    line_id INTEGER NOT NULL REFERENCES bom_lines(id) ON DELETE CASCADE,
    store TEXT NOT NULL,
    price REAL NOT NULL,
    currency TEXT NOT NULL,
    url TEXT NOT NULL,
    captured_at TEXT NOT NULL
);
"""


class BomRepository:
    """Owns the SQLite connection and maps rows to domain dataclasses."""

    def __init__(self, db_path: str | Path = "devis_bom.db") -> None:
        self._connection = sqlite3.connect(db_path, check_same_thread=False)
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.executescript(_SCHEMA)
        self._connection.commit()

    def add_line(self, reference: str, designation: str, quantity: float, unit: str) -> BomLine:
        cursor = self._connection.execute(
            "INSERT INTO bom_lines (reference, designation, quantity, unit) VALUES (?, ?, ?, ?)",
            (reference, designation, quantity, unit),
        )
        self._connection.commit()
        return BomLine(cursor.lastrowid, reference, designation, quantity, unit)

    def list_lines(self) -> list[BomLine]:
        rows = self._connection.execute(
            "SELECT id, reference, designation, quantity, unit FROM bom_lines ORDER BY id"
        ).fetchall()
        return [BomLine(*row) for row in rows]

    def get_line(self, line_id: int) -> BomLine | None:
        row = self._connection.execute(
            "SELECT id, reference, designation, quantity, unit FROM bom_lines WHERE id = ?",
            (line_id,),
        ).fetchone()
        return BomLine(*row) if row else None

    def get_line_by_reference(self, reference: str) -> BomLine | None:
        row = self._connection.execute(
            "SELECT id, reference, designation, quantity, unit FROM bom_lines "
            "WHERE lower(trim(reference)) = lower(trim(?))",
            (reference,),
        ).fetchone()
        return BomLine(*row) if row else None

    def delete_line(self, line_id: int) -> bool:
        cursor = self._connection.execute("DELETE FROM bom_lines WHERE id = ?", (line_id,))
        self._connection.commit()
        return cursor.rowcount > 0

    def add_capture(
        self, line_id: int, store: str, price: float, currency: str, url: str, captured_at: str
    ) -> PriceCapture:
        cursor = self._connection.execute(
            "INSERT INTO price_captures (line_id, store, price, currency, url, captured_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (line_id, store, price, currency, url, captured_at),
        )
        self._connection.commit()
        return PriceCapture(cursor.lastrowid, line_id, store, price, currency, url, captured_at)

    def list_captures(self, line_id: int) -> list[PriceCapture]:
        rows = self._connection.execute(
            "SELECT id, line_id, store, price, currency, url, captured_at FROM price_captures "
            "WHERE line_id = ? ORDER BY price ASC",
            (line_id,),
        ).fetchall()
        return [PriceCapture(*row) for row in rows]
