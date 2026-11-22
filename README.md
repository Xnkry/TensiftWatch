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
