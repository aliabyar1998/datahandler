# datahandler

Lightweight pandas utilities for cleaning messy DataFrames and generating quick data profiles — no dependencies beyond `pandas` and `numpy`.

It gives you three things:

- **`df.clean`** — a chainable pandas accessor for step-by-step cleaning (`df.clean.colnames().trim().na().df`)
- **`clean(df)`** — a one-shot function that runs a sensible default cleaning pipeline
- **`profile(df)`** — a one-shot column-by-column data profile (missing %, uniqueness, min/max, top values, etc.)

Built and hardened specifically against messy, real-world data: duplicate column names, mixed-type columns, unhashable cell values (lists/dicts), empty DataFrames, negative-number column names, and more. See [Known limitations](#known-limitations) for the one remaining edge case that's cosmetic rather than functional.

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

`clean(df)` will, in order:

1. Drop fully-empty rows **and** columns
2. Fix up column names: stringify, lowercase, snake_case, preserve the sign on negative-number names, and de-duplicate any resulting collisions
3. Trim leading/trailing whitespace on string columns (non-string values are left alone)
4. Replace only truly blank (`""`) strings with `NaN` — `"na"`, `"n/a"`, `"none"`, and `"missing"` are left untouched as real string values
5. Drop duplicate rows (safe even if some cells contain lists/dicts)

Note: unlike earlier drafts of this pipeline, `clean()` does **not** touch datetime normalization and does **not** treat `"na"`/`"n/a"`/`"none"`/`"missing"` as missing-value placeholders — only literal blank strings are nulled.

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

Works for numeric, datetime, categorical (including numeric-coded categorical), duplicate-named, and mixed-type columns — including columns containing unhashable values like lists or dicts.

## API reference

### `df.clean` accessor methods

All methods below mutate the accessor's internal DataFrame and return `self`, so they can be chained. Access `.df` at the end of a chain to retrieve the resulting `pandas.DataFrame`.

| Method | Description |
|---|---|
| `.colnames()` | Convert column names to `snake_case`; preserves the sign on negative-number names (e.g. `-3` → `neg_3`); de-duplicates any resulting name collisions |
| `.dropempty()` | Drop rows and columns that are entirely empty |
| `.dropdup()` | Drop duplicate rows; falls back to a hashable-proxy comparison if any column holds unhashable values (lists/dicts) |
| `.na()` | Replace blank (`""`) strings with `NaN` in string/object columns |
| `.trim()` | Strip leading/trailing whitespace from string values only — non-string values (numbers, booleans, lists, dicts, `NaN`/`None`) are left untouched |
| `.lower()` | Lowercase string values only; non-string values are left untouched |
| `.upper()` | Uppercase string values only; non-string values are left untouched |
| `.title()` | Title-case string values only, e.g. `"john smith"` → `"John Smith"`; non-string values are left untouched |
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

## Design notes / hardening against messy data

This library has been deliberately stress-tested against pathological input, and the following behaviors are intentional:

- **Duplicate column names** don't crash `profile()`. Columns are accessed positionally (`iloc`), and stats are kept in an ordered list rather than a name-keyed dict, so two columns named the same thing each get their own correct stats instead of one silently overwriting the other.
- **Mixed-type object columns** (e.g. a column that's mostly strings but has a stray number, boolean, `None`, list, or dict mixed in) are handled safely by `trim()`/`lower()`/`upper()`/`title()`. Only actual string values are transformed; everything else passes through unchanged instead of being silently converted to `NaN`.
- **Unhashable cell values** (lists, dicts, sets) don't crash `dropdup()`, `profile()`, or `clean()`. A repr-based hashable proxy is used internally for comparison/counting only — the real values in the output are untouched.
- **Negative-number column names** keep their sign. A column literally named `-3` becomes `neg_3`, not `3` — the naive regex cleanup would otherwise silently drop the minus sign and risk colliding with an unrelated column named `3`.
- **A completely empty, default-constructed `DataFrame()`** doesn't crash `clean()` or `.colnames()`. (Its default column index is an empty `int64` `RangeIndex`, which pandas' `.map(str)` leaves untouched when there's nothing to map — `.astype(str)` is applied afterward to force the conversion.)
- **Column-name deduplication** never produces a fresh collision. The dedup logic tracks every name assigned so far (not just counts of original duplicates), so e.g. columns `["Col", "COL", "col_2"]` correctly resolve to `["col", "col_3", "col_2"]` instead of two columns both ending up named `col_2`.

## Known limitations

- **Symbol-only column names collapse to an unclear name.** A column named purely with symbols (e.g. `"###"` or `"!!!"`) reduces to an empty string after the snake_case cleanup regex. The dedup logic correctly prevents a silent collision between two such columns, but the second one ends up named `_2` rather than something more descriptive like `unnamed_2`. This is cosmetic — no data is lost or miscounted — but the resulting column name is not very readable. Rename such columns manually if this comes up.
- Floating-point columns with values near the limits of `float64` (e.g. ~`1e308`) can produce `inf` for `Sum`/`Mean` in `profile()` due to standard floating-point overflow — this is inherent numeric behavior, not a library bug.
- `profile()`'s numeric-vs-categorical detection treats boolean columns as numeric (standard pandas behavior), so `Min`/`Max`/`Sum` for a boolean column will show as `False`/`True`/count-of-`True` rather than `---`.

## Requirements

- Python 3.8+
- pandas
- numpy

## License

Apache
