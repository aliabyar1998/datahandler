import pandas as pd
import numpy as np
import re


@pd.api.extensions.register_dataframe_accessor("clean")
class DataFrameCleaner:
    """
    A lightweight pandas DataFrame cleaner accessor.
    Usage:
        df = (
            df.clean
              .colnames()
              .dropempty()
              .dropdup()
              .na(["N/A", "none", "missing"])
              .trim()
              .lower()
              .show()
              .dtnormal()
              .rmcats()
        )
    """

    def __init__(self, pandas_obj):
        self._df = pandas_obj

    # -----------------------------------
    # Clean column names
    # -----------------------------------
    def colnames(self):
        """Convert column names to snake_case."""
        df = self._df.copy()
        df.columns = df.columns.map(str)
        df.columns = df.columns.str.strip().str.lower().str.replace(r"\W+","_",regex=True).str.replace(r"_+","_",regex=True).str.strip("_")
        if df.columns.duplicated().any():
            new_cols = []
            counts = {}
            for col in df.columns:
                counts[col] = counts.get(col, 0) + 1
                new_name = f"{col}_{counts[col]}" if counts[col] > 1 else col
                new_cols.append(new_name)
            df.columns = new_cols
        return df

    # -----------------------------------
    # Remove empty rows/columns
    # -----------------------------------
    def dropempty(self):
        """Remove completely empty rows and columns."""
        df = self._df.dropna(how="all").dropna(axis=1, how="all")
        return df

    # -----------------------------------
    # Drop duplicate rows
    # -----------------------------------
    def dropdup(self):
        """Drop duplicate rows."""
        df = self._df.drop_duplicates()
        return df

    # -----------------------------------
    # Replace certain placeholder strings with NaN
    # -----------------------------------
    def na(self, patterns=None):
        """Replace given placeholder strings with NaN."""
        if patterns is None:
            patterns = ["n/a" , ""]
        df = self._df.replace(patterns, np.nan, regex=True)
        return df

    # -----------------------------------
    # Trim leading/trailing spaces in all string cells
    # -----------------------------------
    def trim(self):
        """Trim whitespace in all string columns."""
        df = self._df.copy()
        obj_cols = df.select_dtypes(include=["object", "string"]).columns
        df[obj_cols] = df[obj_cols].apply(lambda s: s.str.strip())
        return df

    # -----------------------------------
    # Optional: lowercase all string columns
    # -----------------------------------
    def lower(self):
        """Convert all string columns to lowercase."""
        df = self._df.copy()
        obj_cols = df.select_dtypes(include=["object", "string"]).columns
        for col in obj_cols:
            df[col] = df[col].str.lower()
        return df
    
    # -----------------------------------
    # Optional: uppercase all string columns
    # -----------------------------------
    def upper(self):
        """Convert all string columns to uppercase."""
        df = self._df.copy()
        obj_cols = df.select_dtypes(include=["object", "string"]).columns
        for col in obj_cols:
            df[col] = df[col].str.upper()
        return df

    # -----------------------------------
    # Chain-friendly print preview
    # -----------------------------------
    def show(self, n=5):
        """Preview the top n rows without breaking the chain."""
        print(self._df.head(n))
        return self._df
    

    def dtnormal(self):
        df = self._df.copy()
        for col in df.select_dtypes(include=['datetime64[ns]']).columns:
            df[col] = df[col].dt.normalize()
        return df
    

    def rmcats(self):
        df = self._df.copy()
        for c in df.select_dtypes("category"):
            df[c] = df[c].cat.remove_unused_categories()
        return df


def profile(df):
    profile_dict = {}
    
    for col in df.columns:
        series = df[col]
        total = len(series)
        dtype = str(series.dtype)

        # --- Core stats ---
        value_count_ = series.count()
        value_count_percent = round(value_count_ / total * 100, 2) if total > 0 else 0.0
        distinct_count = series.nunique(dropna=True)
        distinct_percent = round(distinct_count / value_count_ * 100, 2) if value_count_ > 0 else 0.0
        missing_count = series.isna().sum()
        missing_percent = round(missing_count / total * 100, 2) if total > 0 else 0.0
        is_unique_ = series.is_unique
        
        

        # --- Type detection ---
        numeric = pd.api.types.is_numeric_dtype(series)
        is_datetime = pd.api.types.is_datetime64_any_dtype(series)
        is_cat_dtype = isinstance(series.dtype, pd.CategoricalDtype)
        #catlike = is_cat_dtype or pd.api.types.is_object_dtype(series)

        # --- Min / Max / Mean / Sum ---
        if numeric:
            min_val = series.min()
            max_val = series.max()
            mean_val = round(series.mean(), 3) if total - missing_count > 0 else "---"
            sum_val = series.sum()
            empty_string = "---"
            zero_count = (series == 0).sum()
            negative_count = (series < 0).sum()
            positive_count = (series > 0).sum()
        elif is_datetime:
            non_na = series.dropna()
            min_val = non_na.min().date() if not non_na.empty else "---"
            max_val = non_na.max().date() if not non_na.empty else "---"
            mean_val = "---"
            sum_val = "---"
            empty_string = "---"
            zero_count = "---"
            negative_count = "---"
            positive_count = "---"
        else:
            min_val = "---"
            max_val = "---"
            mean_val = "---"
            sum_val = "---"
            empty_string = (series.isin([''])).sum()
            zero_count = "---"
            negative_count = "---"
            positive_count = "---"

        # ---------------------------
        # Prepare a frequency map aligned to display for datetimes
        # ---------------------------
        if is_datetime:
            # convert to date-only series for frequency calculations
            series_for_freq = series.dt.date
        else:
            series_for_freq = series

        # ----------------------------------------
        # Top 10 by Count — Value - count (percent%)
        # (use series_for_freq so datetimes become dates here too)
        # ----------------------------------------
        top10_counts = series_for_freq.value_counts(dropna=True).head(10)
        top10_count_lines = []
        for value, count in top10_counts.items():
            # value is already date-only for datetimes
            percent = round((count / total) * 100, 2) if total > 0 else 0.0
            top10_count_lines.append(f"{value} - {count} ({percent}%)")
        top10_by_count = "\n".join(top10_count_lines)

        

        # ----------------------------------------
        # Assemble profile
        # ----------------------------------------
        profile_dict[col] = {
            "Type": dtype,
            "Uniqueness": is_unique_,
            "Total": f"{value_count_} ({value_count_percent}%)",
            "Missing": f"{missing_count} ({missing_percent}%)",
            "Unique": f"{distinct_count} ({distinct_percent}%)",
            "Empty string": empty_string,
            "Neg | Zero | Pos": f"{negative_count} | {zero_count} | {positive_count}",
            "Min": min_val,
            "Max": max_val,
            "Mean": mean_val,
            "Sum": sum_val,
            "Top 10 Count": top10_by_count,
         }

    # --- Transpose for readability ---
    profile_df = pd.DataFrame(profile_dict)
    profile_df.index.name = "Rows: " + str(total)
    profile_df.columns.name = str(int(df.memory_usage(deep=True).sum()/1000)) + " KB"

    return profile_df

def clean(df_):
    df = df_.copy()
    df.columns = df.columns.map(str)
    
    obj_cols = df.select_dtypes(include=["object", "string"]).columns
    df[obj_cols] = df[obj_cols].replace(["na", "n/a", "none", "missing", ""], np.nan)
    
    df.dropna(axis = 0,how="all",inplace = True)
    df.drop_duplicates(inplace = True)
    df.columns = df.columns.str.strip().str.lower().str.replace(r"\W+","_",regex=True).str.replace(r"_+","_",regex=True).str.strip("_")

    if df.columns.duplicated().any():
        new_cols = []
        counts = {}
        for col in df.columns:
            counts[col] = counts.get(col, 0) + 1
            new_name = f"{col}_{counts[col]}" if counts[col] > 1 else col
            new_cols.append(new_name)
        df.columns = new_cols

    for col in df.select_dtypes(include=['datetime64[ns]']).columns:
        df[col] = df[col].dt.normalize()

    return df

def rmcats(df):
    for c in df.select_dtypes("category"):
        df[c] = df[c].cat.remove_unused_categories()
    return
