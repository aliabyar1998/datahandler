# datahandler

Lightweight pandas utilities for cleaning messy DataFrames and generating quick data profiles — no dependencies beyond `pandas` and `numpy`.

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

> **Note:** every accessor method returns the accessor itself (for chaining), so finish the chain with `.df` to get a real `pandas.DataFrame` back.

### One-shot cleaning function

If you just want sensible defaults without composing a chain:

```python
clean_df = dh.clean(df)
```

`clean(df)` runs, in order:

1. Drop fully-empty rows **and** columns
2. Fix up column names: stringify, lowercase, snake_case, preserve the sign on negative-number names, and de-duplicate any resulting collisions
3. Trim leading/trailing whitespace on string columns (non-string values are left alone)
4. Replace only truly blank (`""`) strings with `NaN` — `"na"`, `"n/a"`, `"none"`, and `"missing"` are left untouched as real string values
5. Drop duplicate rows

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

Works across numeric, datetime, and categorical (including numeric-coded categorical) columns.

## Features & abilities

- **Chainable API** via the `.clean` accessor, or a one-shot `clean()` function for the common default pipeline
- **Column name normalization** to `snake_case`, with sign preserved on negative-number names (e.g. a column named `-3` becomes `neg_3`, not `3`)
- **Safe deduplication of column names**, so cleanup never silently produces two columns with the same name
- **Whitespace trimming and case conversion** (`lower`, `upper`, `title`) that only transform actual string values — numbers, booleans, and other non-string values in a column are left as-is
- **Blank-string handling**: `na()` and `clean()` null out only truly empty strings, never numeric-adjacent tokens like `"na"`/`"none"`/`"missing"` unless you ask for that explicitly
- **Duplicate-row removal** that works even when a column holds unhashable values like lists or dicts
- **Datetime normalization** (`dtnormal()`) and **unused-category cleanup** (`rmcats()`) as standalone chain steps
- **`profile()`** works correctly across duplicate-named columns, mixed-type columns, and columns containing unhashable values (lists/dicts), producing a full per-column diagnostic table
- Works safely on edge cases like a completely empty DataFrame

## API reference

### `df.clean` accessor methods

All methods below mutate the accessor's internal DataFrame and return `self`, so they can be chained. Access `.df` at the end of a chain to retrieve the resulting `pandas.DataFrame`.

| Method | Description |
|---|---|
| `.colnames()` | Convert column names to `snake_case`; preserves the sign on negative-number names; de-duplicates any resulting name collisions |
| `.dropempty()` | Drop rows and columns that are entirely empty |
| `.dropdup()` | Drop duplicate rows |
| `.na()` | Replace blank (`""`) strings with `NaN` in string/object columns |
| `.trim()` | Strip leading/trailing whitespace from string values only |
| `.lower()` | Lowercase string values only |
| `.upper()` | Uppercase string values only |
| `.title()` | Title-case string values only, e.g. `"john smith"` → `"John Smith"` |
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

## Limitations

- **Symbol-only column names produce unclear names.** A column named purely with symbols (e.g. `"###"` or `"!!!"`) reduces to an empty string after the `snake_case` cleanup, and if a second such column exists it ends up named `_2` rather than something more descriptive. No data is lost or miscounted, but the resulting name isn't very readable — rename such columns manually if this comes up.
- Floating-point columns with values near the limits of `float64` (e.g. ~`1e308`) can produce `inf` for `Sum`/`Mean` in `profile()` due to standard floating-point overflow.
- `profile()`'s numeric-vs-categorical detection treats boolean columns as numeric (standard pandas behavior), so `Min`/`Max`/`Sum` for a boolean column will show as `False`/`True`/count-of-`True` rather than `---`.

## Requirements

- Python 3.8+
- pandas
- numpy

## License

Apache 2.0
