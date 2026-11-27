import unittest

from src import data_report as report


def observation(day="2026-08-01", dam="Dam", capacity="100", reserve="25", fill="25"):
    return dict(zip(report.COLUMNS, (day, dam, capacity, reserve, fill)))


class ReportTests(unittest.TestCase):
    def test_coverage(self):
        result = report.coverage_by_dam([observation(dam="Z"), observation(dam="A")])
        self.assertEqual(list(result), ["A", "Z"])
        self.assertEqual(result["A"]["rows"], 1)
        self.assertEqual(report.coverage_by_dam([]), {})

    def test_gaps_across_months(self):
        rows = [observation("2026-09-02"), observation("2026-08-31"), observation(dam="Other")]
        self.assertEqual(report.gaps_by_dam(rows), {"Dam": 1, "Other": 0})
        self.assertEqual(report.gaps_by_dam([]), {})
