import contextlib
import io
import json
import tempfile
from pathlib import Path
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

    def test_monthly_stats_separate_years_and_dams(self):
        rows = [observation("2027-08-01"), observation("2026-08-02", reserve=""),
                observation("2026-08-01"), observation(dam="Other")]
        result = report.monthly_stats(rows)
        self.assertEqual([(item["dam"], item["month"], item["rows"]) for item in result],
                         [("Dam", "2026-08", 2), ("Dam", "2027-08", 1), ("Other", "2026-08", 1)])
        self.assertEqual(result[0]["measurements"]["reserve_mm3"]["count"], 1)

    def test_cli_reports_valid_files_after_invalid_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.csv"
            path.write_text(",".join(report.COLUMNS) + "\n2026-08-01,Dam,100,25,25\n")
            output, errors = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                status = report.main([str(path.with_name("absent.csv")), str(path)])
            self.assertEqual(status, 1)
            self.assertIn("absent.csv", errors.getvalue())
            self.assertEqual(json.loads(output.getvalue())["summary"]["rows"], 1)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(report.main([str(path)]), 0)

    def test_cli_dam_filter_and_unknown_name(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.csv"
            path.write_text(",".join(report.COLUMNS) +
                            "\n2026-08-01,Dam,100,25,25\n2026-08-01,Other,100,50,50\n")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(report.main([str(path), "--dam", "Other"]), 0)
            self.assertEqual(list(json.loads(output.getvalue())["coverage_by_dam"]), ["Other"])
            with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(report.main([str(path), "--dam", "Unknown"]), 1)
                with path.open("a") as stream:
                    stream.write("invalid,Dam,100,25,25\n")
                self.assertEqual(report.main([str(path), "--dam", "Other"]), 1)

    def test_cli_date_bounds(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.csv"
            path.write_text(",".join(report.COLUMNS) +
                            "\n2026-08-01,Dam,100,25,25\n2026-08-02,Dam,100,50,50\n")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(report.main([str(path), "--start", "2026-08-02",
                                              "--end", "2026-08-02"]), 0)
            self.assertEqual(json.loads(output.getvalue())["summary"]["rows"], 1)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(report.main([str(path), "--end", "2026-07-31"]), 1)
                with self.assertRaises(SystemExit):
                    report.main([str(path), "--start", "2026-08-02", "--end", "2026-08-01"])
