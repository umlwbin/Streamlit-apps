import pandas as pd

def convert_to_iso(df, date_time_col, ambiguous_mode="Flag ambiguous rows only"):
    """
    Convert a date or datetime column into ISO 8601 format
    (YYYY-MM-DDTHH:MM:SS) with built-in safety checks.

    This function:
        • parses each value in the column safely
        • detects ambiguous dates (e.g., 03/04/2024 could be March 4 or April 3)
        • optionally resolves ambiguity using a user-selected rule
        • detects values that cannot be parsed at all
        • inserts a new ISO-formatted column beside the original
        • removes the original column after conversion

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the date or datetime column you want to convert.

    date_time_col : str
        The name of the column to convert.
        This column should contain date strings, datetime strings,
        or mixed formats (e.g., "2024-01-01", "01/02/24 14:30", "3/4/2024").

    ambiguous_mode : str, optional
        Controls how ambiguous dates are handled.
        Options:
            • "Flag ambiguous rows only" (default)
                - ambiguous values are NOT converted
                - they are recorded in the summary
                - the output contains NaT for those rows

            • "Assume month-first (MM/DD/YYYY)"
                - ambiguous values are interpreted as month-first

            • "Assume day-first (DD/MM/YYYY)"
                - ambiguous values are interpreted as day-first

        Examples:
            "03/04/2024"
                - could be March 4 (MM/DD)
                - or April 3 (DD/MM)

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A copy of the original DataFrame with:
            • a new ISO-formatted column inserted
            • the original date column removed

    summary : dict
        Information about what happened during conversion.
        Structure:
            {
                "converted_rows": number of successfully parsed rows,
                "ambiguous_rows": [(row_index, original_value), ...],
                "unparsed_rows":  [(row_index, original_value), ...],
                "new_column": name of the ISO column created,
                "ambiguous_mode": the mode used for ambiguity handling
            }

    Notes
    -----
    • ISO 8601 format looks like: "2024-01-15T14:30:00"
    • Rows that cannot be parsed become NaT (Not a Time)
    • Ambiguous rows are either flagged or resolved depending on the mode

    Example
    -------
    >>> df["date"]
    ["03/04/2024", "2024-01-01", "13/01/2024"]

    >>> cleaned_df, summary = convert_to_iso(df, "date")

    >>> cleaned_df.columns
    ["date_ISO"]

    >>> cleaned_df["date_ISO"]
    ["NaT", "2024-01-01T00:00:00", "2024-01-13T00:00:00"]
    """

    cleaned_df = df.copy()

    # Before parsing anything, convert the entire column to strings.
    # Real-world CSVs often mix types (ints, floats, datetimes, None).
    # Converting to string ensures every value is treated consistently.
    series = cleaned_df[date_time_col].astype(str)

    # This dictionary keeps track of what happened during conversion.
    summary = {
        "converted_rows": 0,       # how many rows were successfully parsed
        "ambiguous_rows": [],      # rows where the date could mean two different things
        "unparsed_rows": [],       # rows that could not be interpreted as dates at all
        "new_column": None,        # the name of the ISO column we will create
        "ambiguous_mode": ambiguous_mode
    }

    # We will store parsed datetime objects (or NaT) here.
    iso_values = []

    # Decide how to handle ambiguous dates based on the user's choice.
    # resolve_dayfirst:
    #   True  → interpret ambiguous dates as DD/MM/YYYY
    #   False → interpret ambiguous dates as MM/DD/YYYY
    #   None  → do NOT resolve ambiguity; just flag ambiguous rows
    if ambiguous_mode == "Assume month-first (MM/DD/YYYY)":
        resolve_dayfirst = False
    elif ambiguous_mode == "Assume day-first (DD/MM/YYYY)":
        resolve_dayfirst = True
    else:
        resolve_dayfirst = None   # "Flag ambiguous rows only"

    # Loop through each row in the column.
    # .items() gives us (index, value) pairs.
    for idx, value in series.items():

        # Try parsing the value in BOTH ways:
        #   d1 = day-first interpretation
        #   d2 = month-first interpretation
        #
        # errors="coerce" means:
        #   - If parsing fails, pandas returns NaT instead of raising an error.
        try:
            d1 = pd.to_datetime(value, errors="coerce", dayfirst=True)
            d2 = pd.to_datetime(value, errors="coerce", dayfirst=False)
        except Exception:
            # This block only runs for truly unexpected failures
            # (e.g., bizarre objects that can't even be coerced).
            summary["unparsed_rows"].append((idx, value))
            iso_values.append(pd.NaT)
            continue

        # If BOTH interpretations failed (both are NaT),
        # then the value is simply not a valid date.
        if pd.isna(d1) and pd.isna(d2):
            summary["unparsed_rows"].append((idx, value))
            iso_values.append(pd.NaT)
            continue

        # If BOTH interpretations succeed but produce DIFFERENT dates,
        # then the value is ambiguous (e.g., "03/04/2024").
        if not pd.isna(d1) and not pd.isna(d2) and d1 != d2:

            # If the user chose "flag only", we do NOT convert it.
            if resolve_dayfirst is None:
                summary["ambiguous_rows"].append((idx, value))
                iso_values.append(pd.NaT)
                continue

            # Otherwise, resolve ambiguity using the user's rule.
            parsed = pd.to_datetime(value, errors="coerce", dayfirst=resolve_dayfirst)
            iso_values.append(parsed)
            summary["converted_rows"] += 1
            continue

        # If we reach this point, only ONE interpretation succeeded.
        # That means the date is safe and unambiguous.
        parsed = d1 if not pd.isna(d1) else d2
        iso_values.append(parsed)
        summary["converted_rows"] += 1

    # Must Convert the list of parsed datetime objects into a pandas Series; only Series objects support .dt.strftime().
    # To get a column of ISO strings → you MUST use `.dt.strftime()`
    # Single value → pd.to_datetime(value); Whole column/list → convert to Series → use .dt
    iso_series = pd.Series(pd.to_datetime(iso_values)).dt.strftime("%Y-%m-%dT%H:%M:%S")

    # Decide on the new column name. If the original column was already called "date_time" or "datetime",
    # use a cleaner replacement. Otherwise, append "_ISO".
    if date_time_col.lower() in ["date_time", "datetime"]:
        new_col = "DateTime_ISO"
    else:
        new_col = f"{date_time_col}_ISO"

    summary["new_column"] = new_col

    # Insert the new ISO column right beside the original column.
    orig_index = cleaned_df.columns.get_loc(date_time_col)
    cleaned_df.insert(orig_index, new_col, iso_series)

    # Remove the original messy column.
    cleaned_df.drop(columns=[date_time_col], inplace=True)

    return cleaned_df, summary
        