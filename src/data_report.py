"""Describe validated reservoir observations without modifying source data."""

from collections import defaultdict
from datetime import date
from statistics import mean

from .validate_data import COLUMNS, summarize, validate_csv


def coverage_by_dam(rows):
    """Return deterministic coverage summaries for each observed dam."""
    groups = defaultdict(list)
    for row in rows:
        groups[row["dam"]].append(row)
    return {dam: summarize(group) for dam, group in sorted(groups.items())}


def gaps_by_dam(rows):
    """Count absent days only between each dam's first and last observations."""
    groups = defaultdict(set)
    for row in rows:
        groups[row["dam"]].add(date.fromisoformat(row["date"]))
    return {
        dam: (max(days) - min(days)).days + 1 - len(days)
        for dam, days in sorted(groups.items())
    }


def measurement_stats(rows):
    """Describe available measurements; missing values never become zero."""
    result = {}
    for column in COLUMNS[2:]:
        values = [float(row[column]) for row in rows if row[column] != ""]
        result[column] = {
            "count": len(values),
            "min": min(values) if values else None,
            "max": max(values) if values else None,
            "mean": mean(values) if values else None,
        }
    return result
