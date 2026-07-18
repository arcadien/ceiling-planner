"""Ceiling outline validation (FUNC-SURFACE-INPUT-001).

An outline is entered as an ordered sequence of :class:`Edge` values. Each edge carries a
length in meters and the interior angle (degrees) at the corner that starts it. The first
edge sets the reference direction (heading 0) and the walk starts at the origin, so only the
shape matters, never the absolute position. :func:`validate_surface` reconstructs the corner
vertices and enforces the outline rules, returning a :class:`Polygon` or raising a
:class:`SurfaceError` whose ``code`` names the violated rule.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

Point = tuple[float, float]

_MIN_EDGES = 3
_ANGLE_MIN = 0.0
_ANGLE_MAX = 360.0
_DEFAULT_CLOSURE_TOLERANCE_M = 0.02


@dataclass(frozen=True)
class Edge:
    """One straight run of the outline: a length and the interior angle at its start corner."""

    length_m: float
    interior_angle_deg: float


@dataclass(frozen=True)
class Polygon:
    """A validated, closed outline described by its corner vertices in reconstruction order."""

    vertices: list[Point]


class SurfaceError(Exception):
    """Raised when an outline violates a validation rule. ``code`` identifies which one."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def validate_surface(
    edges: list[Edge],
    closure_tolerance_m: float = _DEFAULT_CLOSURE_TOLERANCE_M,
) -> Polygon:
    """Validate an edge-sequence outline and return the reconstructed :class:`Polygon`.

    Rules are checked in order and the first violation is raised: ``too_few_edges``,
    ``non_positive_length``, ``angle_out_of_range``, ``not_closed``, ``self_intersecting``.
    """
    if len(edges) < _MIN_EDGES:
        raise SurfaceError("too_few_edges")

    for edge in edges:
        if edge.length_m <= 0:
            raise SurfaceError("non_positive_length")

    for edge in edges:
        if not (_ANGLE_MIN < edge.interior_angle_deg < _ANGLE_MAX):
            raise SurfaceError("angle_out_of_range")

    vertices, closing_point = _reconstruct(edges)

    gap = math.dist(closing_point, vertices[0])
    if gap > closure_tolerance_m:
        raise SurfaceError("not_closed")

    if _is_self_intersecting(vertices):
        raise SurfaceError("self_intersecting")

    return Polygon(vertices)


def _reconstruct(edges: list[Edge]) -> tuple[list[Point], Point]:
    """Walk the edges into corner vertices, returning the vertices and the closing point.

    The first edge keeps heading 0; every later edge turns by ``180 - interior_angle`` at the
    corner that starts it. Vertices are the corner points ``v0..v(N-1)``; the closing point is
    where the last edge lands and should coincide with ``v0``.
    """
    heading_deg = 0.0
    vertices: list[Point] = [(0.0, 0.0)]
    closing_point: Point = vertices[0]

    for i, edge in enumerate(edges):
        if i > 0:
            heading_deg += 180.0 - edge.interior_angle_deg
        heading_rad = math.radians(heading_deg)
        x, y = vertices[-1]
        landing = (
            x + edge.length_m * math.cos(heading_rad),
            y + edge.length_m * math.sin(heading_rad),
        )
        if i < len(edges) - 1:
            vertices.append(landing)
        else:
            closing_point = landing

    return vertices, closing_point


def _is_self_intersecting(vertices: list[Point]) -> bool:
    """True when any pair of non-adjacent closed-polygon edges intersect."""
    n = len(vertices)
    segments = [(vertices[i], vertices[(i + 1) % n]) for i in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            if j == i + 1 or (i == 0 and j == n - 1):
                continue  # adjacent edges share a corner by construction
            if _segments_intersect(*segments[i], *segments[j]):
                return True
    return False


def _orientation(a: Point, b: Point, c: Point) -> int:
    """Sign of the cross product (b - a) x (c - a): +1 ccw, -1 cw, 0 collinear."""
    value = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    if value > 1e-12:
        return 1
    if value < -1e-12:
        return -1
    return 0


def _on_segment(a: Point, b: Point, c: Point) -> bool:
    """True when collinear point ``c`` lies within the bounding box of segment ``a``-``b``."""
    return min(a[0], b[0]) <= c[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= c[1] <= max(
        a[1], b[1]
    )


def _segments_intersect(p1: Point, p2: Point, p3: Point, p4: Point) -> bool:
    """True when segment ``p1``-``p2`` intersects segment ``p3``-``p4``."""
    d1 = _orientation(p3, p4, p1)
    d2 = _orientation(p3, p4, p2)
    d3 = _orientation(p1, p2, p3)
    d4 = _orientation(p1, p2, p4)

    if d1 != d2 and d3 != d4:
        return True

    if d1 == 0 and _on_segment(p3, p4, p1):
        return True
    if d2 == 0 and _on_segment(p3, p4, p2):
        return True
    if d3 == 0 and _on_segment(p1, p2, p3):
        return True
    if d4 == 0 and _on_segment(p1, p2, p4):
        return True

    return False
