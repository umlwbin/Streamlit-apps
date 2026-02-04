import pandas as pd
import streamlit as st

def merge(df, date_column, time_column):
    """
    Merge a separate date column and time column into a single ISO 8601
    datetime column (YYYY-MM-DDTHH:MM:SS). Designed for messy real-world
    data where dates and times may be incomplete, inconsistent, or unparsed.

    This function:
        • safely parses the date column
        • safely parses the time column
        • records any rows that cannot be parsed
        • fills missing times with midnight (00:00:00)
        • combines the parsed date + time into a single datetime
        • formats the result as an ISO 8601 string
        • inserts the new column beside the original date column
        • removes the original date, time, and temporary helper columns

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the date and time columns you want to merge.

    date_column : str
        The name of the column containing date values.
        This column may contain:
            - strings (e.g., "2024-01-15", "01/15/24")
            - mixed formats
            - missing values
            - values that fail to parse

    time_column : str
        The name of the column containing time values.
        This column may contain:
            - strings (e.g., "14:30", "2:30 PM")
            - empty strings
            - missing values
            - values that fail to parse

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A copy of the original DataFrame with:
            • a new ISO datetime column named "Date_Time"
            • the original date and time columns removed
            • all temporary parsing columns removed

    summary : dict
        Information about what happened during merging.
        Structure:
            {
                "merged_rows": number of successfully merged rows,
                "unparsed_dates": [(row_index, original_value), ...],
                "unparsed_times": [(row_index, original_value), ...],
                "new_column": "Date_Time"
            }

    Notes
    -----
    • Missing or unparsed times are replaced with midnight (00:00:00)
    • Unparsed dates or times result in NaT in the final merged column
    • ISO 8601 format looks like: "2024-01-15T14:30:00"

    Example
    -------
    >>> df[["date", "time"]]
         date        time
    0   2024-01-01   14:30
    1   01/02/24     09:00
    2   2024/03/05   ""

    >>> cleaned_df, summary = merge(df, "date", "time")

    >>> cleaned_df["Date_Time"]
    0   2024-01-01T14:30:00
    1   2024-01-02T09:00:00
    2   2024-03-05T00:00:00
    """


    cleaned_df = df.copy()

    # This summary dictionary keeps track of everything that happens during merging.
    summary = {
        "merged_rows": 0,          # how many rows successfully produced a combined datetime
        "unparsed_dates": [],      # rows where the date could not be parsed
        "unparsed_times": [],      # rows where the time could not be parsed
        "new_column": "Date_Time"  # the name of the final ISO column
    }

    # --- Parse DATE column ---
    # We try to parse the date column using pandas' flexible parser.
    # format="mixed" allows pandas to handle multiple date formats in the same column.
    # errors="coerce" means: if parsing fails, return NaT instead of raising an error.
    try:
        parsed_dates = pd.to_datetime(cleaned_df[date_column], format="mixed", errors="coerce")
    except Exception:
        # This only triggers for catastrophic failures (e.g., column full of objects).
        st.error("Error parsing the date column. Please check your data.", icon="🚨")
        return df, summary

    # Track which date values failed to parse.
    # parsed_dates[idx] will be NaT for unparsed values.
    for idx, val in cleaned_df[date_column].items():
        if pd.isna(parsed_dates[idx]):
            summary["unparsed_dates"].append((idx, val))

    # Convert parsed dates into pure date objects (YYYY-MM-DD without time).
    cleaned_df["_temp_date"] = parsed_dates.dt.date


    # --- Parse TIME column ---
    # Replace empty strings with pandas' missing-value marker so they can be detected.
    cleaned_df["_temp_time_raw"] = cleaned_df[time_column].replace("", pd.NA)

    # Parse the time column. Again, errors="coerce" turns failures into NaT.
    parsed_times = pd.to_datetime(cleaned_df["_temp_time_raw"], errors="coerce")

    # Track unparsed times.
    for idx, val in cleaned_df["_temp_time_raw"].items():
        if pd.isna(parsed_times[idx]):
            summary["unparsed_times"].append((idx, val))

    # Convert parsed times into pure time objects (HH:MM:SS).
    cleaned_df["_temp_time"] = parsed_times.dt.time

    # Any missing or unparsed time becomes midnight (00:00:00). This ensures the merge always has a valid time component.
    cleaned_df["_temp_time"] = cleaned_df["_temp_time"].fillna(
        pd.to_datetime("00:00:00").time() # Here you need one specific time value (midnight), not a Series, so you use the Python .time() version.
    )


    # --- Combine date + time ---
    # We combine the date and time columns by converting both to strings and joining them with a space, e.g. "2024-01-15 14:30:00".
    # Then we parse the combined string into a full datetime.
    combined = pd.to_datetime(
        cleaned_df["_temp_date"].astype(str) + " " + cleaned_df["_temp_time"].astype(str),
        errors="coerce"
    )

    # Count how many rows successfully produced a valid datetime.
    summary["merged_rows"] = combined.notna().sum()

    # Convert the merged datetime values into ISO 8601 strings.
    # We convert to a Series so we can use .dt.strftime().
    iso_series = pd.Series(combined).dt.strftime("%Y-%m-%dT%H:%M:%S")

    # Insert the new ISO column right beside the original date column.
    orig_index = cleaned_df.columns.get_loc(date_column)
    cleaned_df.insert(orig_index, "Date_Time", iso_series)

    # Remove all temporary helper columns.
    cleaned_df.drop(
        columns=["_temp_date", "_temp_time_raw", "_temp_time"],
        inplace=True
    )

    return cleaned_df, summary
