"""Read and validate TensiftWatch processed CSV files without dependencies."""

import csv
import math
from datetime import date
from pathlib import Path

COLUMNS = ("date", "dam", "capacity_mm3", "reserve_mm3", "fill_rate")


def validate_csv(path):
    """Return observations, raising ValueError for invalid data."""
    with Path(path).open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream, strict=True)
        if reader.fieldnames != list(COLUMNS):
            raise ValueError(f"Expected columns: {', '.join(COLUMNS)}")
        records = [(reader.line_num, row) for row in reader]
    if not records:
        raise ValueError("Dataset contains no observations")
    seen = set()
    for line, row in records:
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"Line {line}: expected {len(COLUMNS)} fields")
        try:
            parsed_date = date.fromisoformat(row["date"])
            if parsed_date.isoformat() != row["date"]:
                raise ValueError
        except ValueError:
            raise ValueError(f"Line {line}: date must be a valid YYYY-MM-DD") from None
        if not row["dam"].strip() or row["dam"] != row["dam"].strip():
            raise ValueError(f"Line {line}: dam must be nonblank without surrounding whitespace")
        for column in COLUMNS[2:]:
            if row[column] == "":
                continue  # Missing measurements are retained by the cleaning notebooks.
            try:
                value = float(row[column])
            except ValueError:
                raise ValueError(f"Line {line}: {column} must be numeric or empty") from None
            if not math.isfinite(value):
                raise ValueError(f"Line {line}: {column} must be finite")
        if row["capacity_mm3"] and float(row["capacity_mm3"]) <= 0:
            raise ValueError(f"Line {line}: capacity_mm3 must be positive when present")
        for column in ("reserve_mm3", "fill_rate"):
            if row[column] and float(row[column]) < 0:
                raise ValueError(f"Line {line}: {column} must be nonnegative")
        key = (row["date"], row["dam"])
        if key in seen:
            raise ValueError(f"Line {line}: duplicate dam/date observation {key}")
        seen.add(key)
    return [row for _, row in records]


def summarize(rows):
    """Summarize validated observations without filling missing measurements."""
    dates = [row["date"] for row in rows]
    return {
        "rows": len(rows),
        "dams": len({row["dam"] for row in rows}),
        "start": min(dates) if dates else None,
        "end": max(dates) if dates else None,
        "missing": {
            column: sum(row[column] == "" for row in rows)
            for column in COLUMNS[2:]
        },
    }


def main(argv=None):
    """Validate one or more CSVs; return a failing status if any are invalid."""
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="Processed CSV files")
    args = parser.parse_args(argv)
    failed = False
    for path in args.paths:
        try:
            result = summarize(validate_csv(path))
        except (OSError, UnicodeError, ValueError, csv.Error) as error:
            print(f"{path}: {error}", file=sys.stderr)
            failed = True
        else:
            print(json.dumps({"path": str(path), **result}, sort_keys=True))
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
