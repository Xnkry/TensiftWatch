"""Describe validated reservoir observations without modifying source data."""

from collections import defaultdict
from datetime import date

from .validate_data import COLUMNS, summarize, validate_csv


def coverage_by_dam(rows):
    """Return deterministic coverage summaries for each observed dam."""
    groups = defaultdict(list)
    for row in rows:
        groups[row["dam"]].append(row)
    return {dam: summarize(group) for dam, group in sorted(groups.items())}
