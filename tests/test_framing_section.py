"""Acceptance tests for FUNC-FRAMING-SECTION-001.

``select_section`` picks the lightest PRÉGYMÉTAL montant section whose maximum admissible span
(single or doubled/accolés) covers the required free span, or reports that the span exceeds the
catalog.
"""

import pytest
from ceiling_planner.framing.sections import (
    DEFAULT_SECTIONS,
    MontantSection,
    select_section,
)


@pytest.mark.req("FUNC-FRAMING-SECTION-001")
def test_default_catalog_matches_the_siniat_reference():
    # Given the default catalog
    # Then it lists the four PRÉGYMÉTAL sections with their documented spans
    assert [(s.name, s.max_span_single_m, s.max_span_doubled_m) for s in DEFAULT_SECTIONS] == [
        ("M48-35", 2.00, 2.35),
        ("M70-35", 2.55, 3.15),
        ("M90-35", 3.05, 3.80),
        ("M100-50", 3.60, 4.40),
    ]


@pytest.mark.req("FUNC-FRAMING-SECTION-001")
@pytest.mark.parametrize(
    "span,doubled,expected",
    [
        (1.80, False, "M48-35"),
        (2.00, False, "M48-35"),   # boundary is inclusive
        (2.20, False, "M70-35"),
        (2.55, False, "M70-35"),
        (3.05, False, "M90-35"),
        (3.60, False, "M100-50"),
        (2.20, True, "M48-35"),    # doubled raises the M48 span to 2.35
        (2.35, True, "M48-35"),
        (2.40, True, "M70-35"),
        (4.40, True, "M100-50"),
    ],
    ids=[
        "1.80-single", "2.00-single", "2.20-single", "2.55-single", "3.05-single",
        "3.60-single", "2.20-doubled", "2.35-doubled", "2.40-doubled", "4.40-doubled",
    ],
)
def test_selects_lightest_section_that_covers_the_span(span, doubled, expected):
    # Given a required span and doubling choice
    # When the section is selected
    section = select_section(span, doubled=doubled)

    # Then the lightest covering section is returned
    assert section is not None
    assert section.name == expected


@pytest.mark.req("FUNC-FRAMING-SECTION-001")
def test_span_beyond_single_catalog_returns_none():
    # Given a span longer than the strongest single section (3.60 m)
    # When the section is selected for single montants
    # Then no section covers it
    assert select_section(3.70, doubled=False) is None


@pytest.mark.req("FUNC-FRAMING-SECTION-001")
def test_span_beyond_doubled_catalog_returns_none():
    # Given a span longer than the strongest doubled section (4.40 m)
    # When the section is selected for doubled montants
    # Then no section covers it either
    assert select_section(4.50, doubled=True) is None


@pytest.mark.req("FUNC-FRAMING-SECTION-001")
def test_doubling_can_rescue_a_span_single_cannot_cover():
    # Given a 4.0 m span that no single section covers
    assert select_section(4.0, doubled=False) is None

    # When the montants are doubled
    section = select_section(4.0, doubled=True)

    # Then M100-50 accolés covers it
    assert isinstance(section, MontantSection)
    assert section.name == "M100-50"
