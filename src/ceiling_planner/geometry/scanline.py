"""Shared scan-line helper over a validated :class:`Polygon`.

A single primitive underlies both the montant cut list and the plate optimizer: the interior
extents where a horizontal line crosses the outline. Montants run parallel to the first edge
(the x axis after reconstruction), so a scan line at height ``y`` yields the bearing-direction
spans of the outline at that position.
"""

from __future__ import annotations

from ceiling_planner.geometry.surface import Polygon


def interior_spans(polygon: Polygon, y: float) -> list[float]:
    """Lengths of the interior intervals where the horizontal line at ``y`` crosses the outline.

    Uses the even-odd scan-line rule: each non-horizontal edge is counted when
    ``y_low <= y < y_high``, crossings are sorted along x and paired into interior intervals.
    """
    vertices = polygon.vertices
    n = len(vertices)
    crossings: list[float] = []

    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        if y1 == y2:
            continue  # horizontal edge contributes no crossing
        y_low, y_high = (y1, y2) if y1 < y2 else (y2, y1)
        if y_low <= y < y_high:
            t = (y - y1) / (y2 - y1)
            crossings.append(x1 + t * (x2 - x1))

    crossings.sort()
    return [crossings[i + 1] - crossings[i] for i in range(0, len(crossings) - 1, 2)]


__all__ = ["interior_spans"]
