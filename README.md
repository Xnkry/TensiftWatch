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
