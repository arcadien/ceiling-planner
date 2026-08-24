"""Bearing-axis selection for the montants (FUNC-FRAMING-ORIENT-001).

Montants span between two bearing walls; their length is the outline extent in the bearing
direction. To keep montants short (better load capacity), the bearing axis is the shorter of the
bounding-box dimensions. The rest of the framing assumes a horizontal bearing (montants along x),
so a wide outline is transposed (x and y swapped) before framing and mapped back for display.
"""

from __future__ import annotations

from ceiling_planner.geometry.surface import Polygon


def bearing_axis(polygon: Polygon) -> str:
    """Return the montant axis: ``"x"`` when x is the shorter (or equal) extent, else ``"y"``."""
    xs = [x for x, _ in polygon.vertices]
    ys = [y for _, y in polygon.vertices]
    x_extent = max(xs) - min(xs)
    y_extent = max(ys) - min(ys)
    return "y" if x_extent > y_extent else "x"


def transposed(polygon: Polygon) -> Polygon:
    """Return ``polygon`` with x and y swapped (a y-bearing outline computes as x-bearing)."""
    return Polygon([(y, x) for x, y in polygon.vertices])


__all__ = ["bearing_axis", "transposed"]
