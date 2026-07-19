"""Acceptance tests for FUNC-PLATE-OPTIM-001.

Plates (default 2.50 m by 1.20 m) cover the outline in strips one plate-width wide along the
bearing direction. Within each strip, plates are consumed end to end to fill the run length;
the offcut from a cut plate is reused to start the next run when it is long enough, otherwise
it is waste. ``optimize_plates`` reports the plate count, covered length, and wasted length.
"""

import pytest
from ceiling_planner.plates.optimizer import PlatePlan, optimize_plates

from ceiling_planner.geometry.surface import Polygon


def rectangle(width: float, height: float) -> Polygon:
    return Polygon([(0.0, 0.0), (width, 0.0), (width, height), (0.0, height)])


@pytest.mark.req("FUNC-PLATE-OPTIM-001")
def test_exact_fit_single_strip_has_no_waste():
    # Given a 5.0 m by 1.20 m strip covered by 2.50 m plates
    # When the plate plan is computed
    plan = optimize_plates(rectangle(5.0, 1.20))

    # Then exactly two plates cover it with no waste
    assert plan.plate_count == 2
    assert plan.covered_length_m == pytest.approx(5.0)
    assert plan.waste_length_m == pytest.approx(0.0)


@pytest.mark.req("FUNC-PLATE-OPTIM-001")
def test_two_exact_strips_stack_without_waste():
    # Given a 5.0 m by 2.40 m area (two full plate-width strips)
    # When the plate plan is computed
    plan = optimize_plates(rectangle(5.0, 2.40))

    # Then four plates cover both strips with no waste
    assert plan.plate_count == 4
    assert plan.covered_length_m == pytest.approx(10.0)
    assert plan.waste_length_m == pytest.approx(0.0)


@pytest.mark.req("FUNC-PLATE-OPTIM-001")
def test_partial_last_plate_leaves_waste():
    # Given a 6.0 m by 1.20 m strip that needs three plates (2.5 + 2.5 + 1.0)
    # When the plate plan is computed
    plan = optimize_plates(rectangle(6.0, 1.20))

    # Then three plates are needed and 1.5 m of plate is wasted
    assert plan.plate_count == 3
    assert plan.covered_length_m == pytest.approx(6.0)
    assert plan.waste_length_m == pytest.approx(1.5)


@pytest.mark.req("FUNC-PLATE-OPTIM-001")
def test_offcut_reuse_across_strips_saves_a_plate():
    # Given a 6.0 m by 2.40 m area: two strips of 6.0 m each
    # When the plate plan is computed with offcut reuse
    plan = optimize_plates(rectangle(6.0, 2.40))

    # Then reusing the 1.5 m offcut drops the total from six plates to five
    assert plan.plate_count == 5
    assert plan.covered_length_m == pytest.approx(12.0)
    assert plan.waste_length_m == pytest.approx(0.5)


@pytest.mark.req("FUNC-PLATE-OPTIM-001")
def test_short_offcut_below_threshold_is_not_reused():
    # Given two 2.3 m strips whose 0.2 m offcuts fall below the 0.30 m reuse threshold
    # When the plate plan is computed
    plan = optimize_plates(rectangle(2.3, 2.40), min_offcut_m=0.30)

    # Then each strip consumes its own plate and the short offcuts are wasted
    assert plan.plate_count == 2
    assert plan.covered_length_m == pytest.approx(4.6)
    assert plan.waste_length_m == pytest.approx(0.4)


@pytest.mark.req("FUNC-PLATE-OPTIM-001")
@pytest.mark.parametrize(
    "kwargs",
    [
        {"plate_length_m": 0.0},
        {"plate_width_m": -1.2},
        {"min_offcut_m": -0.1},
    ],
    ids=["zero-length", "negative-width", "negative-offcut"],
)
def test_non_positive_dimensions_are_rejected(kwargs):
    # Given an invalid plate dimension
    # When the plate plan is computed
    with pytest.raises(ValueError):
        optimize_plates(rectangle(5.0, 1.20), **kwargs)


@pytest.mark.req("FUNC-PLATE-OPTIM-001")
def test_result_is_a_plate_plan_value():
    # Given a simple exact-fit outline
    plan = optimize_plates(rectangle(2.5, 1.20))

    # Then the result is a PlatePlan exposing the purchase count
    assert isinstance(plan, PlatePlan)
    assert plan.plate_count == 1
    assert plan.waste_length_m == pytest.approx(0.0)
