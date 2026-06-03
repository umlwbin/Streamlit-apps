import pandas as pd
import numpy as np


def parse_dates(
    df: pd.DataFrame,
    *,
    date_time_col,
    extract_time=True,
    **kwargs
):
    """
    Parse a datetime column into separate Year, Month, Day, and optionally Time columns.

    This task safely converts a datetime-like column into pandas datetime objects, extracts date components, optionally
    extracts the time component, and inserts the new columns beside the original column without modifying the original values.

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
    """

    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors
    # -----------------------------------------------------

    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    if date_time_col not in df.columns:
        raise ValueError(f"Column '{date_time_col}' does not exist in the dataset.")

    if not isinstance(extract_time, bool):
        raise ValueError("extract_time must be a boolean value.")



    # -----------------------------------------------------
    # 2. CORE PROCESSING
    # -----------------------------------------------------
    cleaned_df = df.copy()

    # Parse datetime column (coerce errors → NaT)
    parsed = pd.to_datetime(cleaned_df[date_time_col], errors="coerce")

    # Temporary parsed column
    cleaned_df["_parsed_dt"] = parsed

    # Extract components
    cleaned_df["Year"] = cleaned_df["_parsed_dt"].dt.year.astype("Int64")
    cleaned_df["Month"] = cleaned_df["_parsed_dt"].dt.month.astype("Int64")
    cleaned_df["Day"] = cleaned_df["_parsed_dt"].dt.day.astype("Int64")

    if extract_time:
        cleaned_df["Time"] = cleaned_df["_parsed_dt"].dt.time
        cleaned_df["Time"] = cleaned_df["Time"].apply( lambda t: t if t not in (None, pd.Timestamp.min.time()) else np.nan)

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
    # 3. RETURN
    # -----------------------------------------------------
    return cleaned_df
