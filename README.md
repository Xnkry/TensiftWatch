# TensiftWatch

Notebook-based analysis of dam water reserves and fill rates in the Tensift basin.

## Getting started

Install Conda, then run these commands from the repository root:

```sh
conda env create -f environment.yml
conda activate tensiftwatch
cd notebooks
jupyter lab
```

The environment includes Python 3.12 and the data analysis and plotting
dependencies. Launch Jupyter from `notebooks/` so the notebooks' relative data
paths resolve correctly.

Start with [first_insights.ipynb](notebooks/first_insights.ipynb) for summary
statistics and plots using the included processed data.

### Updating the environment

After pulling changes to `environment.yml`, run these commands from the
repository root to update the existing environment:

```sh
conda env update --name tensiftwatch --file environment.yml --prune
conda activate tensiftwatch
```

The `--prune` option removes dependencies no longer required by the environment
definition. Restart any running notebook kernels to use the updated packages.

## Data and notebooks

- [data/processed/](data/processed/) contains the committed CSV datasets.
  Columns are `date`, `dam`, `capacity_mm3`, `reserve_mm3`, and `fill_rate`.
- [data_cleaning.ipynb](notebooks/data_cleaning.ipynb) prepares August 2026 data
  from a raw Excel workbook.
- [merge_all.ipynb](notebooks/merge_all.ipynb) combines the August, September,
  and October 2026 Excel workbooks.
- [Eda.ipynb](notebooks/Eda.ipynb) explores reserves, average fill rates, and
  correlations.
- [Test_LR.ipynb](notebooks/Test_LR.ipynb) fits linear trends to water reserves.

The cleaning notebooks require source Excel workbooks in `data/raw/`, which is
excluded from Git. Their expected filenames are listed in the notebooks. The
included processed CSVs let you explore the analysis without those workbooks.

### Processed data columns

Each row represents one dam on one date. The CSVs use these columns:

| Column | Meaning | Format or unit |
| --- | --- | --- |
| `date` | Observation date | `YYYY-MM-DD` |
| `dam` | Dam name as recorded in the source | Text |
| `capacity_mm3` | Reservoir capacity | Million cubic metres (Mm³) |
| `reserve_mm3` | Stored water volume | Million cubic metres (Mm³) |
| `fill_rate` | Reservoir fill percentage | Percent, not a 0–1 fraction |

Read `date` with `pd.read_csv(path, parse_dates=["date"])` when plotting time
series or calculating elapsed days.

### Included dataset coverage

| File | Dates (inclusive) | Rows | Dams |
| --- | --- | ---: | ---: |
| `tensift_august_2026.csv` | 2026-08-01 to 2026-08-31 | 155 | 5 |
| `tensift_cleaned.csv` | 2026-08-01 to 2026-10-31 | 460 | 5 |

The combined dataset already includes August; appending the August CSV would
duplicate those observations. These counts describe the currently committed
files and should be updated when the datasets change.

### Rebuilding the processed data

Create `data/raw/` at the repository root and place these source workbooks in it:

- `data_barrages_tensift_aout_2026.xlsx`
- `data_barrages_tensift_sept_2026.xlsx`
- `data_barrages_tensift_oct_2026.xlsx`

Launch Jupyter from `notebooks/` and run `merge_all.ipynb` from top to bottom to
write `data/processed/tensift_cleaned.csv`. To regenerate the separate August
CSV, run `data_cleaning.ipynb`. Both notebooks overwrite their respective output
files; review the resulting CSV changes before committing them.

## Troubleshooting notebooks

- **CSV file not found:** launch Jupyter from `notebooks/`. The data paths are
  relative to the notebook working directory.
- **Excel workbook not found:** the cleaning notebooks need the local files
  listed above. Use `first_insights.ipynb` to explore the committed CSVs without
  rebuilding them.
- **Missing Python package:** activate `tensiftwatch` before starting Jupyter
  and check that the notebook kernel uses that environment. After updating
  dependencies, restart the kernel and run the cells from the top.
- **Variables are undefined or plots look stale:** restart the kernel and run
  all cells in order so results use the current data and code.

## Interpreting the analysis

The [fill rate distribution notebook](notebooks/Fill%20Rate%20Distribution%20-%20Lalla%20Takerkoust.ipynb)
shows the frequency of observed daily fill rates for Lalla Takerkoust. Missing
fill rates are excluded; histogram counts describe observations, not forecasts.

Monthly summaries retain both year and month. Average fill rates give each
recorded observation equal weight; they are not capacity-weighted basin totals.
Missing observations can therefore change the period represented by an average.

EDA correlations are computed within each dam. Reserve and fill rate describe
related quantities, so their correlation is not evidence of an independent
causal relationship. Linear regression plots describe historical trends in
Mm³/day and should not be treated as validated forecasts. Fits require at least
two distinct observation dates.

## Checking processed data

From the repository root, validate the included CSVs using Python alone:

```sh
python -m src.validate_data data/processed/tensift_august_2026.csv data/processed/tensift_cleaned.csv
```

The command checks the exact column order, row structure, calendar dates,
nonblank dam names without surrounding whitespace, finite numeric measurements,
positive capacities, nonnegative reserves and fill rates, and unique dam/date
pairs within each file. Empty measurement fields are allowed and counted in the
summary. Values above capacity or 100% are retained for investigation, rather
than automatically rejected. The check does not verify source accuracy,
reserve/fill-rate consistency, or uninterrupted daily coverage.

Each valid file produces one JSON line with row and dam counts, date bounds,
and missing-value counts. Errors go to standard error; exit status is 1 if any
file fails and 0 if all files pass. All supplied files are checked even if an
earlier file fails. Validation does not modify the files.

Run the validator's regression tests without installing extra dependencies:

```sh
python -m unittest discover -s tests
```

### Data quality reports

Generate a JSON report without installing additional packages:

```sh
python -m src.data_report data/processed/tensift_cleaned.csv
python -m src.data_report data/processed/tensift_cleaned.csv --dam "Lalla Takerkoust"
```

The report includes overall and per-dam coverage, missing-day counts,
observations exceeding capacity or 100% fill, and monthly measurement counts,
minimums, maximums, and means for each dam. Months include the year. Missing
measurements are excluded from statistics; an entirely missing measurement has
count zero and JSON `null` statistics. Recorded zero values remain included.

Missing days are counted only between each dam's own first and last observation.
This does not detect missing observations outside those bounds or dams absent
from the file. Exceedances are investigation flags, not validation failures or
automatic corrections. Monthly means give equal weight to available observations;
they are not capacity-weighted basin totals or estimates of unobserved days.

Multiple paths produce one JSON line per valid file, without merging datasets.
Errors go to standard error and yield exit status 1; other files are still
processed. `--dam` matches an exact name and fails if it has no observations.
The entire input is validated before filtering. Reports never modify input files.
Redirect standard output to a file if you want to save a report:

```sh
python -m src.data_report data/processed/tensift_cleaned.csv > /tmp/tensift-report.jsonl
```

CSV validation rejects malformed quoting. Row diagnostics identify the physical
line where a record ends, including records containing quoted multiline fields.

### Selecting a reporting period

Date bounds are inclusive and may be used independently or together with an
exact dam name:

```sh
python -m src.data_report data/processed/tensift_cleaned.csv --start 2026-09-01 --end 2026-09-30 --dam "Lalla Takerkoust"
```

The whole file is validated before selecting observations. Reversed bounds are
command-line errors; a selection containing no observations fails for that file.
All report sections describe only the selected observations.

### Additional report sections

| JSON key | Contents |
| --- | --- |
| `gap_intervals` | Inclusive start and end dates and day counts for missing intervals within each dam's observed coverage |
| `completeness_by_dam` | Present and missing measurement counts, plus percentage present among observed rows |
| `latest_by_dam` | Latest observed date and numeric measurements per dam; missing measurements remain `null` |
| `reserve_changes` | Change in Mm³ and average change in Mm³/day between consecutive available reserve measurements |
| `capacity_changes` | Previous and current reported capacities when consecutive available values differ |
| `annual_stats` | Measurement counts, extrema, and means per dam and calendar year |
| `measurements_by_dam` | Measurement statistics over the entire selected period for each dam |

Completeness percentages describe recorded rows, not expected calendar days.
Gap intervals exclude dates outside a dam's observed bounds, including the
edges of a requested date range. Latest dates may differ between dams; missing
latest measurements are not filled from older observations.

Reserve changes skip missing measurements and divide by the actual elapsed
calendar days. They are net storage changes, not estimates of inflow, outflow,
or a daily trajectory between observations. Capacity changes are investigation
flags and may reflect source revisions. Both change sections compare only
observations inside the selected period and never borrow a preceding record
from outside it. Annual and full-period means weight each available observation
equally, including zero, rather than averaging monthly means.
