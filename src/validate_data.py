"""Read and validate TensiftWatch processed CSV files without dependencies."""

import csv
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
    return rows
