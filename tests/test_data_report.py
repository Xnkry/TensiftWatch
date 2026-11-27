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

    def test_stats_exclude_missing_and_include_zero(self):
        rows = [observation(reserve=""), observation(reserve="0"), observation(reserve="30")]
        self.assertEqual(report.measurement_stats(rows)["reserve_mm3"],
                         {"count": 2, "min": 0, "max": 30, "mean": 15})
        self.assertIsNone(report.measurement_stats([])["fill_rate"]["mean"])

    def test_exceedances_preserve_observations(self):
        row = observation(reserve="110", fill="110")
        self.assertEqual(report.exceedances([row])[0]["reasons"],
                         ["reserve_above_capacity", "fill_above_100"])
        self.assertEqual(row["reserve_mm3"], "110")
        self.assertEqual(report.exceedances([observation(reserve="100", fill="100")]), [])
        self.assertEqual(report.exceedances([observation(capacity="", fill="")]), [])
