"""Acceptance tests for FUNC-FRAMING-MONTANTS-001.

Montants run parallel to the first edge (the bearing direction, i.e. the x axis after
outline reconstruction). ``compute_montants`` places them at the given spacing across the
perpendicular extent, plus one flush to each extremity, and returns a cut list. A concave
outline yields several montant pieces at the positions where the cross-section is split.
"""

import pytest

from ceiling_planner.framing.montants import Montant, compute_montants
from ceiling_planner.geometry.surface import Polygon

SQUARE = Polygon([(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)])
L_SHAPE = Polygon([(0.0, 0.0), (4.0, 0.0), (4.0, 2.0), (2.0, 2.0), (2.0, 4.0), (0.0, 4.0)])
U_SHAPE = Polygon(
    [
        (0.0, 0.0),
        (4.0, 0.0),
        (4.0, 4.0),
        (3.0, 4.0),
        (3.0, 2.0),
        (1.0, 2.0),
        (1.0, 4.0),
        (0.0, 4.0),
    ]
)


@pytest.mark.req("FUNC-FRAMING-MONTANTS-001")
def test_square_yields_uniform_montants():
    # Given a 4 m square and a 1 m spacing
    # When the montant cut list is computed
    montants = compute_montants(SQUARE, spacing_m=1.0)

    # Then one montant sits at each meter plus the far wall, all spanning the full width
    assert [m.offset_m for m in montants] == pytest.approx([0.0, 1.0, 2.0, 3.0, 4.0])
    assert [m.length_m for m in montants] == pytest.approx([4.0, 4.0, 4.0, 4.0, 4.0])


@pytest.mark.req("FUNC-FRAMING-MONTANTS-001")
def test_l_shape_montants_have_varying_lengths():
    # Given an L-shaped outline (narrower above the reflex corner) and a 1 m spacing
    # When the montant cut list is computed
    montants = compute_montants(L_SHAPE, spacing_m=1.0)

    # Then montants past the reflex corner are shorter, proving non-rectangular support
    assert [m.offset_m for m in montants] == pytest.approx([0.0, 1.0, 2.0, 3.0, 4.0])
    assert [m.length_m for m in montants] == pytest.approx([4.0, 4.0, 2.0, 2.0, 2.0])


@pytest.mark.req("FUNC-FRAMING-MONTANTS-001")
def test_concave_outline_splits_montants_into_pieces():
    # Given a U-shaped outline whose upper half has a central notch
    # When the montant cut list is computed at 1 m spacing
    montants = compute_montants(U_SHAPE, spacing_m=1.0)

    # Then the notched rows produce two pieces each (eight pieces total)
    assert len(montants) == 8
    assert sorted(m.length_m for m in montants) == pytest.approx(
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 4.0, 4.0]
    )


@pytest.mark.req("FUNC-FRAMING-MONTANTS-001")
def test_default_spacing_is_60_cm():
    # Given a 4 m square and the default spacing
    # When the montant cut list is computed without an explicit spacing
    montants = compute_montants(SQUARE)

    # Then montants sit every 0.60 m plus the far wall
    assert [m.offset_m for m in montants] == pytest.approx(
        [0.0, 0.6, 1.2, 1.8, 2.4, 3.0, 3.6, 4.0]
    )
    assert all(m.length_m == pytest.approx(4.0) for m in montants)


@pytest.mark.req("FUNC-FRAMING-MONTANTS-001")
@pytest.mark.parametrize("bad_spacing", [0.0, -0.5], ids=["zero", "negative"])
def test_non_positive_spacing_is_rejected(bad_spacing):
    # Given a valid outline but a non-positive spacing
    # When the montant cut list is computed
    with pytest.raises(ValueError):
        compute_montants(SQUARE, spacing_m=bad_spacing)


@pytest.mark.req("FUNC-FRAMING-MONTANTS-001")
def test_montant_is_a_value_object():
    # Given a computed montant
    montant = compute_montants(SQUARE, spacing_m=2.0)[0]

    # Then it exposes its offset and length as a Montant value
    assert isinstance(montant, Montant)
    assert montant.offset_m == pytest.approx(0.0)
    assert montant.length_m == pytest.approx(4.0)
    assert montant.doubled is False


@pytest.mark.req("FUNC-FRAMING-MONTANTS-001")
def test_montant_carries_its_span_endpoints():
    # Given the montants of the concave U-shape at a position with two pieces
    montants = compute_montants(U_SHAPE, spacing_m=1.0)

    # Then each montant is a segment whose endpoints bound its length
    for m in montants:
        assert m.x_end_m - m.x_start_m == pytest.approx(m.length_m)

    # And the notched row at offset 3.0 yields the two interior intervals [0,1] and [3,4]
    notched = sorted((m.x_start_m, m.x_end_m) for m in montants if m.offset_m == pytest.approx(3.0))
    assert notched == pytest.approx([(0.0, 1.0), (3.0, 4.0)])


@pytest.mark.req("FUNC-FRAMING-MONTANTS-001")
def test_forced_offsets_add_montants_at_plate_joints():
    # Given forced offsets (plate butt joints) that miss the 1 m entraxe grid
    montants = compute_montants(SQUARE, spacing_m=1.0, forced_offsets=[1.2, 2.4, 3.6])

    # Then montants are forced at those joints as well as the entraxe grid
    offsets = sorted(round(m.offset_m, 6) for m in montants)
    assert offsets == pytest.approx([0.0, 1.0, 1.2, 2.0, 2.4, 3.0, 3.6, 4.0])


@pytest.mark.req("FUNC-FRAMING-MONTANTS-001")
def test_joint_montants_can_be_doubled():
    # Given joint doubling enabled
    montants = compute_montants(
        SQUARE, spacing_m=1.0, forced_offsets=[1.2, 2.4, 3.6], double_joints=True
    )

    # Then only the forced joint montants are marked doubled
    doubled = sorted(round(m.offset_m, 6) for m in montants if m.doubled)
    plain = sorted(round(m.offset_m, 6) for m in montants if not m.doubled)
    assert doubled == pytest.approx([1.2, 2.4, 3.6])
    assert plain == pytest.approx([0.0, 1.0, 2.0, 3.0, 4.0])


@pytest.mark.req("FUNC-FRAMING-MONTANTS-001")
def test_forced_joint_wins_over_a_too_close_entraxe_montant():
    # Given a forced joint 0.05 m from an entraxe montant (below the 0.10 m clearance)
    montants = compute_montants(SQUARE, spacing_m=1.0, forced_offsets=[1.05])

    # Then the entraxe montant at 1.0 is dropped and the joint at 1.05 is kept
    offsets = sorted(round(m.offset_m, 3) for m in montants)
    assert offsets == pytest.approx([0.0, 1.05, 2.0, 3.0, 4.0])


@pytest.mark.req("FUNC-FRAMING-MONTANTS-001")
def test_montants_never_sit_closer_than_the_clearance():
    # Given a dense set of forced joints near the entraxe grid
    montants = compute_montants(SQUARE, spacing_m=0.6, forced_offsets=[1.25, 2.5, 3.75])

    # Then no two montants are closer than the 0.10 m clearance
    offsets = sorted(m.offset_m for m in montants)
    gaps = [offsets[i + 1] - offsets[i] for i in range(len(offsets) - 1)]
    assert min(gaps) >= 0.10 - 1e-9


@pytest.mark.req("FUNC-FRAMING-MONTANTS-001")
def test_no_forced_offsets_keeps_plain_entraxe_grid():
    # Given no forced offsets
    montants = compute_montants(SQUARE, spacing_m=1.0)

    # Then only the entraxe grid and extremities are placed, none doubled
    offsets = [round(m.offset_m, 6) for m in montants]
    assert offsets == pytest.approx([0.0, 1.0, 2.0, 3.0, 4.0])
    assert not any(m.doubled for m in montants)
