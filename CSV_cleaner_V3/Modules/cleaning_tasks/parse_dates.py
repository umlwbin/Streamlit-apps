import pandas as pd
import numpy as np


def parse_dates(
    df: pd.DataFrame,
    *,
    date_time_col,
    extract_time=True
):
    """
    Parse a datetime column into separate Year, Month, Day, and optionally Time columns.

    This task safely converts a datetime-like column into pandas datetime objects,
    records unparsed rows, extracts date components as nullable integers, optionally
    extracts the time component, and inserts the new columns beside the original
    column without modifying the original values.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset containing the datetime column.

    date_time_col : str
        Name of the column containing datetime-like values. May include:
        - ISO strings
        - date-only strings
        - mixed formats
        - missing values
        - unparseable values

    extract_time : bool, optional
        If True (default), extract the time component into a new "Time" column.
        Midnight-only times (00:00:00) are treated as missing (NaN).

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A copy of the input DataFrame with new columns inserted:
        - Year (Int64)
        - Month (Int64)
        - Day (Int64)
        - Time (optional)

    summary : dict
        {
            "parsed_rows": int,
            "unparsed_rows": [(row_index, original_value)],
            "new_columns": [...],
            "warnings": [list of soft validation messages]
        }

    summary_df : pandas.DataFrame or None
        A table of unparsed rows, or None if none exist.

    Notes
    -----
    - Hard validation errors (e.g., missing column) raise exceptions.
    - Soft validation issues (e.g., empty column) appear in summary["warnings"]
      but do not stop execution.
    - Year/Month/Day use pandas' nullable integer type ("Int64").
    """

    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors (A, B, C…)
    # -----------------------------------------------------

    # A. df must be a DataFrame
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    # B. Column must exist
    if date_time_col not in df.columns:
        raise ValueError(f"Column '{date_time_col}' does not exist in the dataset.")

    # C. extract_time must be boolean
    if not isinstance(extract_time, bool):
        raise ValueError("extract_time must be a boolean value.")

    cleaned_df = df.copy()

    # -----------------------------------------------------
    # 2. VALIDATION - Soft Checks (A, B, C…)
    # -----------------------------------------------------
    warnings = []

    # A. Column is empty or blank
    col_series = cleaned_df[date_time_col]
    if col_series.isna().all() or col_series.astype(str).str.strip().eq("").all():
        warnings.append(f"Column '{date_time_col}' is empty or blank.")

        # Create empty columns
        cleaned_df["Year"] = pd.Series([pd.NA] * len(cleaned_df), dtype="Int64")
        cleaned_df["Month"] = pd.Series([pd.NA] * len(cleaned_df), dtype="Int64")
        cleaned_df["Day"] = pd.Series([pd.NA] * len(cleaned_df), dtype="Int64")
        if extract_time:
            cleaned_df["Time"] = np.nan

        summary = {
            "parsed_rows": 0,
            "unparsed_rows": [(i, v) for i, v in col_series.items()],
            "new_columns": ["Year", "Month", "Day"] + (["Time"] if extract_time else []),
            "warnings": warnings,
        }
        return cleaned_df, summary, None

    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------

    # Parse datetime column
    parsed = pd.to_datetime(cleaned_df[date_time_col], errors="coerce")

    # Track unparsed rows
    unparsed_rows = []
    for idx, val in cleaned_df[date_time_col].items():
        if pd.isna(parsed[idx]):
            unparsed_rows.append((idx, val))

    # Temporary parsed column
    cleaned_df["_parsed_dt"] = parsed

    # Extract components
    cleaned_df["Year"] = cleaned_df["_parsed_dt"].dt.year.astype("Int64")
    cleaned_df["Month"] = cleaned_df["_parsed_dt"].dt.month.astype("Int64")
    cleaned_df["Day"] = cleaned_df["_parsed_dt"].dt.day.astype("Int64")

    if extract_time:
        cleaned_df["Time"] = cleaned_df["_parsed_dt"].dt.time
        cleaned_df["Time"] = cleaned_df["Time"].apply(
            lambda t: t if t is not None and t != pd.Timestamp.min.time() else np.nan
        )

    # Insert new columns beside original
    orig_index = cleaned_df.columns.get_loc(date_time_col)

    year_col = cleaned_df.pop("Year")
    month_col = cleaned_df.pop("Month")
    day_col = cleaned_df.pop("Day")
    time_col = cleaned_df.pop("Time") if extract_time else None

    cleaned_df.insert(orig_index + 1, "Year", year_col)
    cleaned_df.insert(orig_index + 2, "Month", month_col)
    cleaned_df.insert(orig_index + 3, "Day", day_col)

    if extract_time:
        cleaned_df.insert(orig_index + 4, "Time", time_col)

    # Remove temp column
    cleaned_df.drop(columns=["_parsed_dt"], inplace=True)

    # -----------------------------------------------------
    # 4. SUMMARY
    # -----------------------------------------------------
    summary = {
        "parsed_rows": parsed.notna().sum(),
        "unparsed_rows": unparsed_rows,
        "new_columns": ["Year", "Month", "Day"] + (["Time"] if extract_time else []),
        "warnings": warnings,
    }

    # -----------------------------------------------------
    # 5. SUMMARY DATAFRAME
    # -----------------------------------------------------
    summary_df = None
    if unparsed_rows:
        summary_df = pd.DataFrame(unparsed_rows, columns=["row", "value"])

    # -----------------------------------------------------
    # 6. RETURN
    # -----------------------------------------------------
    return cleaned_df, summary, summary_df
