import csv
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from src.validate_data import COLUMNS, main, summarize, validate_csv


class ValidationTests(unittest.TestCase):
    def validate(self, rows=None, header=None):
        if rows is None:
            rows = ["2026-08-01,Lalla Takerkoust,100,25,25"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.csv"
            path.write_text((header or ",".join(COLUMNS)) + "\n" + "\n".join(rows), encoding="utf-8")
            return validate_csv(path)

    def test_invalid_dates(self):
        for value in ("2026-02-30", "20260801", "", "2026-08-01T00:00:00"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "date"):
                self.validate([f"{value},Dam,100,25,25"])

    def test_invalid_names(self):
        for value in ("", " ", " Dam", "Dam "):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "dam"):
                self.validate([f"2026-08-01,{value},100,25,25"])

    def test_invalid_measurements(self):
        for column in range(2, 5):
            for value in ("nan", "inf", "-inf", "unknown"):
                row = ["2026-08-01", "Dam", "100", "25", "25"]
                row[column] = value
                with self.subTest(column=column, value=value), self.assertRaises(ValueError):
                    self.validate([",".join(row)])

    def test_missing_measurements(self):
        self.assertEqual(len(self.validate(["2026-08-01,Dam,,,"])), 1)

    def test_nonpositive_capacity(self):
        for value in ("0", "-10"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "capacity_mm3"):
                self.validate([f"2026-08-01,Dam,{value},25,25"])

    def test_negative_measurements(self):
        for row in ("2026-08-01,Dam,100,-1,25", "2026-08-01,Dam,100,25,-1"):
            with self.subTest(row=row), self.assertRaisesRegex(ValueError, "nonnegative"):
                self.validate([row])

    def test_zero_and_above_capacity_measurements(self):
        self.validate(["2026-08-01,Dam,100,0,0", "2026-08-02,Dam,100,110,110"])

    def test_duplicate_observations(self):
        row = "2026-08-01,Dam,100,25,25"
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.validate([row, row])

    def test_same_date_for_different_dams(self):
        self.validate(["2026-08-01,Dam A,100,25,25", "2026-08-01,Dam B,100,25,25"])

    def test_summary(self):
        rows = self.validate(["2026-08-02,Dam,100,,25", "2026-08-01,Dam,100,25,"])
        result = summarize(rows)
        self.assertEqual((result["rows"], result["dams"]), (2, 1))
        self.assertEqual((result["start"], result["end"]), ("2026-08-01", "2026-08-02"))
        self.assertEqual(result["missing"], {"capacity_mm3": 0, "reserve_mm3": 1, "fill_rate": 1})
        self.assertIsNone(summarize([])["start"])

    def test_cli_continues_after_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "valid.csv"
            path.write_text(",".join(COLUMNS) + "\n2026-08-01,Dam,100,25,25\n")
            output, errors = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                status = main([str(path.with_name("missing.csv")), str(path)])
            self.assertEqual(status, 1)
            self.assertIn("missing.csv", errors.getvalue())
            self.assertEqual(json.loads(output.getvalue())["rows"], 1)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(path)]), 0)

    def test_unclosed_quoted_field(self):
        with self.assertRaises(csv.Error):
            self.validate(['2026-08-01,"Dam,100,25,25'])

    def test_valid_csv(self):
        self.assertEqual(len(self.validate()), 1)

    def test_invalid_structure(self):
        for rows, header in [([], None), (None, "date,dam"), (["2026-08-01,Dam"], None), (["2026-08-01,Dam,100,25,25,extra"], None)]:
            with self.subTest(rows=rows, header=header), self.assertRaises(ValueError):
                self.validate(rows, header)


if __name__ == "__main__":
    unittest.main()
