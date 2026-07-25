# datahandler

A lightweight Python toolkit for cleaning and profiling Pandas DataFrames. It ships as a Pandas DataFrame accessor (`df.clean`) plus a small set of standalone helper functions, aimed at speeding up routine data-preprocessing and exploratory data analysis (EDA) tasks.

## Features

- **Column name standardisation** — convert messy headers to consistent `snake_case`, with automatic de-duplication.
- **Missing-data handling** — drop empty rows/columns, replace placeholder strings (e.g. `"N/A"`, `"none"`, `"missing"`) with `NaN`.
- **Row cleanup** — drop duplicate rows.
- **String cleanup** — trim whitespace, normalise case (`lower()` / `upper()`).
- **Datetime normalisation** — strip time components from `datetime64` columns.
- **Category cleanup** — drop unused categories from categorical columns.
- **DataFrame profiling** — a one-call summary of types, missing values, uniqueness, and per-column statistics (numeric, datetime, and categorical), formatted for quick inspection.
- **One-step cleaning** — a convenience function that runs a sensible default cleaning pipeline in a single call.

## Requirements

- Python 3.8+
- pandas
- numpy

## Installation

This project is currently distributed via GitHub. Clone the repository and import it directly from your project, or copy `datahandler.py` into your codebase:

```bash
git clone https://github.com/ironking63/datahandler.git
```

```python
import sys
sys.path.append("path/to/datahandler")

import datahandler
```

## Quick Start

### Using the `.clean` accessor

Importing `datahandler` registers a `clean` accessor on every Pandas DataFrame. Each method returns a **new DataFrame** rather than mutating in place, so you can reassign or continue processing it.

```python
import pandas as pd
import datahandler

df = pd.read_csv("data.csv")

df = df.clean.colnames()    # standardise column names
df = df.clean.dropempty()   # drop fully empty rows/columns
df = df.clean.dropdup()     # drop duplicate rows
df = df.clean.na(["N/A", "none", "missing"])  # replace placeholders with NaN
df = df.clean.trim()        # strip whitespace from string columns
df = df.clean.lower()       # lowercase string columns
df = df.clean.dtnormal()    # normalise datetime columns
df = df.clean.rmcats()      # drop unused categories
```

**Note on chaining:** because each method returns a plain `DataFrame` (not the accessor), a single chained expression must re-invoke `.clean` between steps:

```python
df = (
    df.clean.colnames()
      .clean.dropempty()
      .clean.dropdup()
      .clean.na(["N/A", "none", "missing"])
      .clean.trim()
      .clean.lower()
      .clean.dtnormal()
      .clean.rmcats()
)
```

You can also preview intermediate results without breaking a chain using `.show(n)`, which prints the first `n` rows and returns the DataFrame unchanged:

```python
df = df.clean.colnames().clean.show(5).clean.dropempty()
```

### One-step cleaning

For a quick default clean without composing individual steps:

```python
df = datahandler.clean(df)
```

This applies, in order: placeholder-to-`NaN` replacement (on string columns), removal of fully empty rows, removal of duplicate rows, column-name standardisation (with duplicate-name handling), and datetime normalisation.

### Profiling a DataFrame

```python
profile_df = datahandler.profile(df)
print(profile_df)
```

`profile()` returns a transposed summary DataFrame — one column per field in the original data — reporting, per column:

| Row | Description |
|---|---|
| `Type` | pandas dtype |
| `Uniqueness` | whether all values are unique |
| `Total` | non-null count and percentage |
| `Missing` | null count and percentage |
| `Unique` | distinct-value count and percentage |
| `Empty string` | count of empty strings (text columns only) |
| `Neg \| Zero \| Pos` | counts of negative, zero, and positive values (numeric columns only) |
| `Min` / `Max` | minimum/maximum value (numeric columns, or date for datetime columns) |
| `Mean` / `Sum` | numeric only |
| `Top 10 Count` | the 10 most frequent values with counts and percentages |

The DataFrame's total row count and approximate memory usage (in KB) are attached to the result's index/column names for quick reference when printed.

## API Reference

### `df.clean` accessor (`DataFrameCleaner`)

| Method | Description |
|---|---|
| `colnames()` | Standardise column names to `snake_case`; de-duplicates repeated names. |
| `dropempty()` | Drop rows and columns that are entirely empty (`NaN`). |
| `dropdup()` | Drop duplicate rows. |
| `na(patterns=None)` | Replace given placeholder strings (regex-matched, across all columns) with `NaN`. Defaults to `["n/a", ""]`. |
| `trim()` | Strip leading/trailing whitespace from string/object columns. |
| `lower()` | Lowercase all string/object columns. |
| `upper()` | Uppercase all string/object columns. |
| `show(n=5)` | Print the first `n` rows without breaking the chain; returns the DataFrame unchanged. |
| `dtnormal()` | Normalise `datetime64[ns]` columns to midnight (date-only). |
| `rmcats()` | Remove unused categories from categorical columns. |

### Standalone functions

| Function | Description |
|---|---|
| `profile(df)` | Returns a transposed summary DataFrame profiling every column (see table above). |
| `clean(df)` | Applies a fixed default cleaning pipeline and returns a new, cleaned DataFrame. |
| `rmcats(df)` | Removes unused categories from categorical columns. **Modifies `df` in place and returns `None`** — this differs from the accessor's `.rmcats()`, which returns a cleaned copy. |

## Known Limitations

- Chained calls on the `.clean` accessor require re-referencing `.clean` between method calls (see Quick Start note above), since methods return plain DataFrames rather than the accessor itself.
- `na()` on the accessor operates across the whole DataFrame, while the standalone `clean()` function restricts placeholder replacement to string/object columns — the two are not identical.
- The standalone `rmcats()` function mutates its input and returns `None`; prefer `df.clean.rmcats()` if you want a returned copy.

## License

Add your chosen license here (e.g. MIT).

## Contributing

Issues and pull requests are welcome via the GitHub repository.
