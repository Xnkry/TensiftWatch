"""Read and validate TensiftWatch processed CSV files without dependencies."""

import csv
import math
from datetime import date
from pathlib import Path

COLUMNS = ("date", "dam", "capacity_mm3", "reserve_mm3", "fill_rate")


def validate_csv(path):
    """Return observations, raising ValueError for invalid data."""
    with Path(path).open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != list(COLUMNS):
            raise ValueError(f"Expected columns: {', '.join(COLUMNS)}")
        rows = list(reader)
    if not rows:
        raise ValueError("Dataset contains no observations")
    for line, row in enumerate(rows, start=2):
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
    return rows
