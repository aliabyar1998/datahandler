# datahandler

Lightweight pandas utilities for cleaning messy DataFrames and generating quick data profiles — no extra dependencies beyond `pandas` and `numpy`.

It gives you three things:

- **`df.clean`** — a chainable pandas accessor for step-by-step cleaning (`df.clean.colnames().trim().na().df`)
- **`clean(df)`** — a one-shot function that runs a sensible default cleaning pipeline
- **`profile(df)`** — a one-shot column-by-column data profile (missing %, uniqueness, min/max, top values, etc.)

## Installation

This is a single-file module — no package install required. Drop `datahandler.py` into your project and import it:

```bash
pip install pandas numpy
```

```python
import datahandler as dh
```

## Quick start

### Chainable cleaning accessor

Importing the module registers a `.clean` accessor on every pandas `DataFrame`:

```python
import pandas as pd
import datahandler as dh  # registers df.clean

df = pd.DataFrame({
    "Full Name": ["  John Smith", "JANE DOE", "n/a", None],
    "City": ["new york", "LOS ANGELES", "", "chicago"],
})

clean_df = (
    df.clean
      .colnames()     # -> snake_case column names
      .dropempty()    # drop fully-empty rows/columns
      .dropdup()      # drop duplicate rows
      .na()           # blank strings -> NaN
      .trim()         # strip whitespace
      .title()        # Title Case all string columns
      .dtnormal()     # normalize datetime columns to midnight
      .rmcats()       # drop unused categorical categories
      .df             # unwrap back to a plain DataFrame
)
```

> **Note:** because every accessor method returns the accessor itself (for chaining), you must finish the chain with `.df` to get a real `pandas.DataFrame` back.

### One-shot cleaning function

If you just want sensible defaults without composing a chain:

```python
clean_df = dh.clean(df)
```

`clean(df)` will:
- snake_case all column names
- treat blank/placeholder strings (`""`, `"na"`, `"n/a"`, `"none"`, `"missing"` — case-insensitive) as missing
- drop fully-empty rows
- drop duplicate rows
- de-duplicate any resulting column-name collisions
- normalize datetime columns to midnight

### Data profiling

```python
dh.profile(df)
```

Returns a transposed summary DataFrame — one column per original column — with:

| Row | Description |
|---|---|
| `Type` | pandas dtype |
| `Uniqueness` | whether all values are unique |
| `Total` | non-null count and % |
| `Missing` | null count and % |
| `Unique` | distinct value count and % |
| `Empty string` | count of empty-string values (non-numeric columns) |
| `Neg / Zero / Pos` | sign breakdown (numeric columns) |
| `Min` / `Max` / `Mean` / `Sum` | numeric or datetime summary stats |
| `Top 10 Count` | the 10 most frequent values with counts and percentages |

Works for numeric, datetime, and categorical (including numeric-coded categorical) columns.

## API reference

### `df.clean` accessor methods

All methods below mutate the accessor's internal DataFrame and return `self`, so they can be chained. Access `.df` at the end of a chain to retrieve the resulting `pandas.DataFrame`.

| Method | Description |
|---|---|
| `.colnames()` | Convert column names to `snake_case`; de-duplicates any resulting name collisions |
| `.dropempty()` | Drop rows and columns that are entirely empty |
| `.dropdup()` | Drop duplicate rows |
| `.na()` | Replace blank (`""`) strings with `NaN` in string/object columns |
| `.trim()` | Strip leading/trailing whitespace from string columns |
| `.lower()` | Lowercase all string columns |
| `.upper()` | Uppercase all string columns |
| `.title()` | Title-case all string columns, e.g. `"john smith"` → `"John Smith"` |
| `.show(n=5)` | Print a preview of the first `n` rows without breaking the chain |
| `.dtnormal()` | Normalize all `datetime64[ns]` columns to midnight |
| `.rmcats()` | Remove unused categories from `category` dtype columns |
| `.df` | *(property)* Unwrap the accessor and return the underlying `DataFrame` |

`.lower()`, `.upper()`, and `.title()` are alternative capitalization steps — use at most one per chain.

### Module-level functions

| Function | Description |
|---|---|
| `clean(df)` | Run the default one-shot cleaning pipeline described above |
| `profile(df)` | Generate the column-by-column profile summary described above |
| `rmcats(df)` | Return a copy of `df` with unused categories removed from all `category` columns |

## Requirements

- Python 3.8+
- pandas
- numpy

