import tempfile
import unittest
from pathlib import Path

from src.validate_data import COLUMNS, validate_csv


class ValidationTests(unittest.TestCase):
    def validate(self, rows=None, header=None):
        if rows is None:
            rows = ["2026-08-01,Lalla Takerkoust,100,25,25"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.csv"
            path.write_text((header or ",".join(COLUMNS)) + "\n" + "\n".join(rows), encoding="utf-8")
            return validate_csv(path)

    def test_valid_csv(self):
        self.assertEqual(len(self.validate()), 1)

    def test_invalid_structure(self):
        for rows, header in [([], None), (None, "date,dam"), (["2026-08-01,Dam"], None), (["2026-08-01,Dam,100,25,25,extra"], None)]:
            with self.subTest(rows=rows, header=header), self.assertRaises(ValueError):
                self.validate(rows, header)


if __name__ == "__main__":
    unittest.main()
