"""Acceptance tests for BOM-FUNC-LINES-001, BOM-FUNC-PRICES-001, BOM-FUNC-SUMMARY-001.

Covers adding/removing BOM lines, matching a captured price to a line by reference, and
summarizing the cheapest price per line into an estimated total with reported gaps.
"""

import pytest

from devis_bom.service import DevisBomError, DevisBomService
from devis_bom.storage import BomRepository


@pytest.fixture
def service(tmp_path):
    return DevisBomService(BomRepository(tmp_path / "test.db"))


@pytest.mark.req("BOM-FUNC-LINES-001")
def test_add_line_then_lists_it(service):
    # Given no lines yet
    # When a line is added
    line = service.add_line("LEG-411600", "Disjoncteur 16A", 3, "pcs")

    # Then it appears in the listing
    lines = service.list_lines_with_prices()
    assert [lp.line.reference for lp in lines] == ["LEG-411600"]
    assert line.quantity == 3


@pytest.mark.req("BOM-FUNC-LINES-001")
def test_add_line_rejects_duplicate_reference_case_and_space_insensitive(service):
    # Given a line already exists
    service.add_line("LEG-411600", "Disjoncteur 16A", 1)

    # When another line is added with the same reference, differently cased and padded
    # Then it is rejected
    with pytest.raises(DevisBomError) as exc:
        service.add_line("  leg-411600 ", "Autre désignation", 2)
    assert exc.value.code == "duplicate_reference"


@pytest.mark.req("BOM-FUNC-LINES-001")
def test_add_line_rejects_non_positive_quantity(service):
    with pytest.raises(DevisBomError) as exc:
        service.add_line("REF-1", "Item", 0)
    assert exc.value.code == "non_positive_quantity"


@pytest.mark.req("BOM-FUNC-LINES-001")
def test_delete_line_removes_it(service):
    # Given a line
    line = service.add_line("REF-1", "Item", 1)

    # When it is deleted
    service.delete_line(line.id)

    # Then it no longer appears
    assert service.list_lines_with_prices() == []


@pytest.mark.req("BOM-FUNC-LINES-001")
def test_delete_unknown_line_raises(service):
    with pytest.raises(DevisBomError) as exc:
        service.delete_line(999)
    assert exc.value.code == "unknown_line"


@pytest.mark.req("BOM-FUNC-PRICES-001")
def test_record_price_matches_line_by_trimmed_case_insensitive_reference(service):
    # Given a BOM line
    service.add_line("LEG-411600", "Disjoncteur 16A", 1)

    # When a price is captured with a differently-cased, padded reference
    capture = service.record_price(" leg-411600 ", "Rexel", 12.5, "https://rexel.example/p")

    # Then it is attached to that line
    lines = service.list_lines_with_prices()
    assert lines[0].captures == [capture]


@pytest.mark.req("BOM-FUNC-PRICES-001")
def test_record_price_rejects_unknown_reference(service):
    with pytest.raises(DevisBomError) as exc:
        service.record_price("UNKNOWN", "Rexel", 10, "https://rexel.example")
    assert exc.value.code == "unknown_reference"


@pytest.mark.req("BOM-FUNC-PRICES-001")
def test_record_price_rejects_non_positive_price(service):
    service.add_line("REF-1", "Item", 1)
    with pytest.raises(DevisBomError) as exc:
        service.record_price("REF-1", "Rexel", 0, "https://rexel.example")
    assert exc.value.code == "non_positive_price"


@pytest.mark.req("BOM-FUNC-PRICES-001")
def test_record_price_keeps_every_capture_instead_of_overwriting(service):
    service.add_line("REF-1", "Item", 1)
    service.record_price("REF-1", "Rexel", 10.0, "https://rexel.example")
    service.record_price("REF-1", "Manomano", 8.0, "https://manomano.example")

    lines = service.list_lines_with_prices()
    assert len(lines[0].captures) == 2


@pytest.mark.req("BOM-FUNC-SUMMARY-001")
def test_summary_sums_quantity_times_cheapest_price_and_reports_gaps(service):
    # Given two lines, one with two price captures and one with none
    service.add_line("REF-1", "Item 1", 2)
    service.add_line("REF-2", "Item 2", 1)
    service.record_price("REF-1", "Rexel", 10.0, "https://rexel.example")
    service.record_price("REF-1", "Manomano", 8.0, "https://manomano.example")

    # When the summary is computed
    summary = service.summary()

    # Then the total uses the cheapest price and REF-2 is reported as a gap
    assert summary.estimated_total == pytest.approx(16.0)
    assert [g.reference for g in summary.gaps] == ["REF-2"]


@pytest.mark.req("BOM-FUNC-SUMMARY-001")
def test_summary_reports_full_gap_when_no_capture_exists(service):
    service.add_line("REF-1", "Item 1", 1)

    summary = service.summary()

    assert summary.estimated_total == 0
    assert [g.reference for g in summary.gaps] == ["REF-1"]
