import pandas as pd

def assign(df, type_mapping):
    """
    Convert selected columns to user‑assigned data types in a safe,
    predictable way.

    This function lets the user specify the desired data type for each
    column. It applies the conversion, records which conversions succeeded,
    which failed, and which columns were skipped because they were not found.

    Supported data types
    --------------------
    "date"        → full datetime (YYYY‑MM‑DD HH:MM:SS)
    "date_only"   → Python date objects (YYYY‑MM‑DD)
    "time_only"   → Python time objects (HH:MM:SS)
    "integer"     → nullable integer type (Int64)
    "float"       → floating‑point numbers
    "string"      → pandas string dtype

    Conversion rules
    ----------------
    • All conversions use `errors='coerce'`, meaning invalid values become NaN.
    • Columns that do not exist are skipped.
    • Unknown dtype names are recorded as failures.
    • Each conversion is wrapped in a try/except block so one failure does not
      stop the entire process.

    Parameters
    ----------
    df : pandas.DataFrame
        The input dataset.

    type_mapping : dict
        A dictionary mapping column names to desired data types.
        Example:
            {
                "date_col": "date_only",
                "time_col": "time_only",
                "value": "float"
            }

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A copy of the DataFrame with conversions applied.

    summary : dict
        A dictionary describing what happened:
            {
                "converted": [(col, dtype), ...],
                "failed": {col: error_message, ...},
                "skipped": [col, ...]
            }
    
    Example
    -----
    from assign_datatype import assign

    cleaned, summary = assign(df, {
        "date_col": "date_only",
        "time_col": "time_only",
        "value": "float",
        "count": "integer",
        "label": "string"
    })

    Notes
    -----
    • This function does not infer types; it only applies what the user requests.
    """

    # Work on a copy so the original DataFrame is never modified.
    cleaned_df = df.copy()

    # Prepare a summary structure to record what happened.
    summary = {
        "converted": [],   # list of (column, dtype) pairs that succeeded
        "failed": {},      # columns that failed with error messages
        "skipped": []      # columns not found in the DataFrame
    }

    # ---------------------------------------------------------
    # Converters for each supported dtype
    # ---------------------------------------------------------
    # Each converter is a function that takes a Series and returns a converted Series.
    converters = {
        # Convert to full datetime; invalid values become NaT.
        "date": lambda s: pd.to_datetime(s, errors="coerce"),

        # Convert to datetime, then extract only the date part.
        "date_only": lambda s: pd.to_datetime(s, errors="coerce").dt.date,

        # Convert to datetime, then extract only the time part.
        "time_only": lambda s: pd.to_datetime(s, errors="coerce").dt.time,

        # Convert to integer using pandas' nullable Int64 dtype.
        "integer": lambda s: pd.to_numeric(s, errors="coerce").astype("Int64"),

        # Convert to float; invalid values become NaN.
        "float": lambda s: pd.to_numeric(s, errors="coerce").astype(float),

        # Convert to pandas' string dtype.
        "string": lambda s: s.astype("string")
    }

    # ---------------------------------------------------------
    # Apply conversions column by column
    # ---------------------------------------------------------
    for col, dtype in type_mapping.items():

        # Skip columns that do not exist in the DataFrame.
        if col not in cleaned_df.columns:
            summary["skipped"].append(col)
            continue

        # Skip unknown dtype names.
        if dtype not in converters:
            summary["failed"][col] = f"Unknown dtype '{dtype}'"
            continue

        try:
            # Apply the converter function to the column.
            cleaned_df[col] = converters[dtype](cleaned_df[col]) # Calls the lambda function and passes the column e.g., pd.to_numeric(cleaned_df[col], errors="coerce").astype(float)

            # Record success.
            summary["converted"].append((col, dtype))

        except Exception as e:
            # Record the error message if conversion fails.
            summary["failed"][col] = str(e)

    return cleaned_df, summary
