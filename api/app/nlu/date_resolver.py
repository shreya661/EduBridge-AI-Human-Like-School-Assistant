"""Deterministic date resolution utility for natural language expressions."""

from datetime import date, timedelta
from typing import Optional
import re


def resolve_date_expression(
    expr: Optional[str],
    reference_date: Optional[date] = None
) -> Optional[date]:
    """
    Resolve natural language date expressions deterministically.
    Never lets the LLM invent or calculate dates.
    """
    if not expr:
        return None
    
    ref = reference_date or date.today()
    cleaned = expr.strip().lower()

    if cleaned in {"today", "current", "now"}:
        return ref
    elif cleaned in {"yesterday", "prev day", "previous day"}:
        return ref - timedelta(days=1)
    elif cleaned in {"tomorrow", "next day"}:
        return ref + timedelta(days=1)

    # Standard ISO format: YYYY-MM-DD
    iso_match = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", cleaned)
    if iso_match:
        try:
            year, month, day = map(int, iso_match.groups())
            return date(year, month, day)
        except ValueError:
            return None

    # Common format: DD/MM/YYYY or DD-MM-YYYY
    dmy_match = re.match(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{4})$", cleaned)
    if dmy_match:
        try:
            day, month, year = map(int, dmy_match.groups())
            return date(year, month, day)
        except ValueError:
            return None

    # Day of week (e.g. "monday", "last friday")
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for idx, day_name in enumerate(days):
        if day_name in cleaned:
            current_weekday = ref.weekday()
            delta = (current_weekday - idx) % 7
            if delta == 0 and "last" in cleaned:
                delta = 7
            return ref - timedelta(days=delta)

    return None
