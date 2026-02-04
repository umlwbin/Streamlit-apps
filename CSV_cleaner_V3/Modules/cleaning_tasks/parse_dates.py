import pandas as pd
import numpy as np
import streamlit as st

def parse_func(df, date_time_col, extract_time=True):
    """
    Parse a datetime column into separate Year, Month, Day, and optionally Time
    columns. Designed for messy real‑world data where datetime values may be
    inconsistent, partially missing, or unparsed.

    This function:
        • safely converts the column into datetime objects
        • records any rows that fail to parse
        • extracts Year, Month, Day as nullable integers (Int64)
        • optionally extracts the Time component
        • inserts the new columns directly beside the original column
        • leaves the original datetime column untouched

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the datetime column you want to parse.

    date_time_col : str
        The name of the column containing datetime values.
        This column may include:
            - ISO strings (e.g., "2024-01-15T14:30:00")
            - date-only strings (e.g., "2024-01-15")
            - mixed formats (e.g., "01/15/24 2:30 PM")
            - missing values
            - values that fail to parse

    extract_time : bool, optional
        Whether to extract the time component.
        If True (default):
            A "Time" column is created using the time portion of the parsed datetime.
            Midnight-only times (00:00:00) are treated as missing (NaN) to avoid
            implying a real time when none was provided.
        If False:
            Only Year, Month, and Day are extracted.

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A copy of the original DataFrame with new columns inserted:
            • Year
            • Month
            • Day
            • Time (optional)
        The original datetime column remains unchanged.

    summary : dict
        Information about the parsing process.
        Structure:
            {
                "parsed_rows": number of successfully parsed rows,
                "unparsed_rows": [(row_index, original_value), ...],
                "new_columns": ["Year", "Month", "Day"] + (["Time"] if extract_time else [])
            }

    Notes
    -----
    • Unparsed values become NaT in the temporary parsed column.
    • Year, Month, and Day use pandas' nullable integer type ("Int64") so missing
      values remain as <NA> instead of becoming floats.
    • The Time column contains Python datetime.time objects or NaN.

    Example
    -------
    >>> df["timestamp"]
    ["2024-01-01 14:30", "2024/02/05", "not a date"]

    >>> cleaned_df, summary = parse_func(df, "timestamp")

    >>> cleaned_df[["timestamp", "Year", "Month", "Day", "Time"]]
         timestamp              Year  Month  Day        Time
    0    2024-01-01 14:30       2024     1    1   14:30:00
    1    2024/02/05             2024     2    5        NaN
    2    not a date             <NA>   <NA>  <NA>       NaN
    """

    cleaned_df = df.copy()

    # This summary dictionary keeps track of everything that happens during parsing.
    summary = {
        "parsed_rows": 0,                 # how many rows successfully parsed as datetimes
        "unparsed_rows": [],              # rows that could not be interpreted as dates
        "new_columns": ["Year", "Month", "Day"] + (["Time"] if extract_time else [])
    }

    # --- Parse datetime column ---
    # Convert the column into datetime objects.
    # errors="coerce" means: if parsing fails, pandas returns NaT instead of raising an error.
    parsed = pd.to_datetime(cleaned_df[date_time_col], errors="coerce")

    # Track which rows failed to parse.
    # parsed[idx] will be NaT for unparsed values.
    for idx, val in cleaned_df[date_time_col].items():
        if pd.isna(parsed[idx]):
            summary["unparsed_rows"].append((idx, val))

    # Store the parsed datetime values in a temporary column.
    cleaned_df["_parsed_dt"] = parsed

    # Count how many rows successfully parsed.
    summary["parsed_rows"] = parsed.notna().sum()

    # --- Extract components ---
    # Extract Year, Month, Day from the parsed datetime column.
    # .dt.year / .dt.month / .dt.day give integer values.
    # We convert them to pandas' nullable integer type ("Int64") so missing values stay as <NA>.
    cleaned_df["Year"] = cleaned_df["_parsed_dt"].dt.year.astype("Int64")
    cleaned_df["Month"] = cleaned_df["_parsed_dt"].dt.month.astype("Int64")
    cleaned_df["Day"] = cleaned_df["_parsed_dt"].dt.day.astype("Int64")

    if extract_time:
        # Extract the time component (HH:MM:SS) from each datetime.
        cleaned_df["Time"] = cleaned_df["_parsed_dt"].dt.time

        # Optional cleanup:
        # If the time is exactly midnight (00:00:00) AND the original value had no time,
        # treat it as missing. This avoids misleading "midnight" values.
        cleaned_df["Time"] = cleaned_df["Time"].apply(
            lambda t: t if t is not None and t != pd.Timestamp.min.time() else np.nan
        )

    # --- Insert new columns next to original ---
    # Find where the original datetime column is located.
    orig_index = cleaned_df.columns.get_loc(date_time_col)

    # Remove extracted columns temporarily so we can reinsert them in the correct order.
    year_col = cleaned_df.pop("Year")
    month_col = cleaned_df.pop("Month")
    day_col = cleaned_df.pop("Day")
    time_col = cleaned_df.pop("Time") if extract_time else None

    # Insert the new columns immediately after the original datetime column.
    cleaned_df.insert(orig_index + 1, "Year", year_col)
    cleaned_df.insert(orig_index + 2, "Month", month_col)
    cleaned_df.insert(orig_index + 3, "Day", day_col)

    if extract_time:
        cleaned_df.insert(orig_index + 4, "Time", time_col)

    # Remove the temporary parsed datetime column.
    cleaned_df.drop(columns=["_parsed_dt"], inplace=True)

    return cleaned_df, summary
