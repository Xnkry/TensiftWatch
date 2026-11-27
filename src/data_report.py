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


def exceedances(rows):
    """Flag values for investigation without rejecting or correcting them."""
    findings = []
    for row in sorted(rows, key=lambda row: (row["date"], row["dam"])):
        reasons = []
        if row["capacity_mm3"] and row["reserve_mm3"]:
            if float(row["reserve_mm3"]) > float(row["capacity_mm3"]):
                reasons.append("reserve_above_capacity")
        if row["fill_rate"] and float(row["fill_rate"]) > 100:
            reasons.append("fill_above_100")
        if reasons:
            findings.append({"date": row["date"], "dam": row["dam"], "reasons": reasons})
    return findings


def monthly_stats(rows):
    """Group measurement summaries by dam and calendar year-month."""
    groups = defaultdict(list)
    for row in rows:
        groups[(row["dam"], row["date"][:7])].append(row)
    return [
        {"dam": dam, "month": month, "rows": len(group), "measurements": measurement_stats(group)}
        for (dam, month), group in sorted(groups.items())
    ]


def build_report(rows):
    """Build a JSON-compatible report from validated observations."""
    return {
        "summary": summarize(rows),
        "coverage_by_dam": coverage_by_dam(rows),
        "missing_days_by_dam": gaps_by_dam(rows),
        "exceedances": exceedances(rows),
        "monthly": monthly_stats(rows),
    }


def main(argv=None):
    """Print one JSON report per valid input; continue after input errors."""
    import argparse
    import csv
    import json
    import sys
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="Processed CSV files")
    args = parser.parse_args(argv)
    failed = False
    for path in args.paths:
        try:
            rows = validate_csv(path)
            result = build_report(rows)
        except (OSError, UnicodeError, ValueError, csv.Error) as error:
            print(f"{path}: {error}", file=sys.stderr)
            failed = True
        else:
            print(json.dumps({"path": str(path), **result}, sort_keys=True, allow_nan=False))
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
