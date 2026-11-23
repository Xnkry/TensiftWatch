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
