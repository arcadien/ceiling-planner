"""Acceptance tests for FUNC-FRAMING-ENTRETOISE-001.

An entretoise (cross-brace) is placed along every interior plate butt joint — a boundary shared
by two contiguous plate pieces within a strip — so the otherwise-unsupported plate edges are
carried. Boundaries at the outline (walls) and gaps between disjoint pieces get none.
"""

import pytest
from ceiling_planner.framing.entretoises import Entretoise, compute_entretoises

from ceiling_planner.geometry.surface import Polygon
from ceiling_planner.plates.optimizer import PlatePiece, optimize_plates


def rectangle(width: float, height: float) -> Polygon:
    return Polygon([(0.0, 0.0), (width, 0.0), (width, height), (0.0, height)])


@pytest.mark.req("FUNC-FRAMING-ENTRETOISE-001")
def test_single_plate_has_no_butt_joint():
    # Given a strip covered by a single plate (2.5 m by 1.20 m)
    plan = optimize_plates(rectangle(2.5, 1.20))

    # When entretoises are computed
    entretoises = compute_entretoises(plan.pieces)

    # Then there is no interior butt joint, so no entretoise
    assert entretoises == []


@pytest.mark.req("FUNC-FRAMING-ENTRETOISE-001")
def test_butt_joints_get_one_entretoise_each():
    # Given a 6.0 m by 1.20 m strip cut into three plates (seams at 2.5 and 5.0)
    plan = optimize_plates(rectangle(6.0, 1.20))

    # When entretoises are computed
    entretoises = compute_entretoises(plan.pieces)

    # Then each interior seam carries an entretoise spanning the strip band
    assert [round(e.x_m, 6) for e in entretoises] == pytest.approx([2.5, 5.0])
    assert all(e.length_m == pytest.approx(1.20) for e in entretoises)
    assert all((e.y_min_m, e.y_max_m) == pytest.approx((0.0, 1.20)) for e in entretoises)


@pytest.mark.req("FUNC-FRAMING-ENTRETOISE-001")
def test_wall_boundaries_are_not_butt_joints():
    # Given an exact two-plate fit (one interior seam at 2.5, walls at 0 and 5)
    plan = optimize_plates(rectangle(5.0, 1.20))

    # When entretoises are computed
    entretoises = compute_entretoises(plan.pieces)

    # Then only the interior seam gets an entretoise, not the walls
    assert [round(e.x_m, 6) for e in entretoises] == pytest.approx([2.5])


@pytest.mark.req("FUNC-FRAMING-ENTRETOISE-001")
def test_gap_between_disjoint_pieces_yields_no_entretoise():
    # Given two pieces in the same strip separated by a gap (disjoint room parts)
    pieces = [
        PlatePiece(0, 0.0, 1.2, 0.0, 2.0, "cut"),
        PlatePiece(0, 0.0, 1.2, 3.0, 5.0, "cut"),
    ]

    # When entretoises are computed
    entretoises = compute_entretoises(pieces)

    # Then the gap (a wall on each side) yields no entretoise
    assert entretoises == []


@pytest.mark.req("FUNC-FRAMING-ENTRETOISE-001")
def test_entretoise_is_a_value_object():
    # Given a butt joint
    entretoise = compute_entretoises(optimize_plates(rectangle(5.0, 1.20)).pieces)[0]

    # Then it exposes its position, band and length as an Entretoise value
    assert isinstance(entretoise, Entretoise)
    assert entretoise.x_m == pytest.approx(2.5)
    assert entretoise.length_m == pytest.approx(1.20)
