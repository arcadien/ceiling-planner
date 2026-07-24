"""Montant section selection from the required span (FUNC-FRAMING-SECTION-001).

For a self-supporting ceiling the montant section is chosen from the free span between the two
bearing walls. The catalog below holds the PRÉGYMÉTAL sections with their maximum admissible
span, single and doubled back-to-back (accolés), per the Siniat reference (DTU 25.41). The
catalog is ordered from lightest to strongest so the first section that covers the span wins.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MontantSection:
    """A montant section with its maximum admissible span, single and doubled (accolés)."""

    name: str
    max_span_single_m: float
    max_span_doubled_m: float

    def max_span_m(self, doubled: bool) -> float:
        """Maximum admissible span for this section given the doubling choice."""
        return self.max_span_doubled_m if doubled else self.max_span_single_m


# PRÉGYMÉTAL sections, lightest to strongest (Siniat / DTU 25.41 reference).
DEFAULT_SECTIONS: list[MontantSection] = [
    MontantSection("M48-35", 2.00, 2.35),
    MontantSection("M70-35", 2.55, 3.15),
    MontantSection("M90-35", 3.05, 3.80),
    MontantSection("M100-50", 3.60, 4.40),
]


def select_section(
    span_m: float,
    doubled: bool = False,
    catalog: list[MontantSection] = DEFAULT_SECTIONS,
) -> MontantSection | None:
    """Return the lightest section whose admissible span covers ``span_m``, else ``None``.

    ``None`` means the span exceeds every catalog section (an intermediate support or a
    longer-span system is required).
    """
    for section in catalog:
        if section.max_span_m(doubled) >= span_m:
            return section
    return None


__all__ = ["DEFAULT_SECTIONS", "MontantSection", "select_section"]
