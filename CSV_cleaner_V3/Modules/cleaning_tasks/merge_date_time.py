import pandas as pd


def merge_date_time(
    df: pd.DataFrame,
    *,
    date_column,
    time_column,
    **kwargs
):
    """
    Merge separate date and time columns into a single ISO 8601 datetime column.

    This task safely parses mixed-format date and time values, handles missing
    or unparseable entries, replaces missing times with midnight.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset containing the date and time columns.

    date_column : str
        Name of the column containing date values.

    time_column : str
        Name of the column containing time values.

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A copy of the input DataFrame with a new ISO datetime column inserted
        beside the original date column. Original date/time columns are removed.

    Notes
    -----
    - Hard validation errors (e.g., missing required columns) raise exceptions.
    """

    # -----------------------------------------------------
    # 1. VALIDATION
    # -----------------------------------------------------
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    missing = [c for c in [date_column, time_column] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")

    cleaned_df = df.copy()


    # -----------------------------------------------------
    # CORE PROCESSING
    #
    # 2. Parse DATE column
    # -----------------------------------------------------
    parsed_dates = pd.to_datetime(
        cleaned_df[date_column],
        format="mixed",
        errors="coerce"
    )

    cleaned_df["_temp_date"] = parsed_dates.dt.date

    # -----------------------------------------------------
    # 3. Parse TIME column
    # -----------------------------------------------------
    cleaned_df["_temp_time_raw"] = cleaned_df[time_column].replace("", pd.NA)

    parsed_times = pd.to_datetime(
        cleaned_df["_temp_time_raw"],
        errors="coerce"
    )

    cleaned_df["_temp_time"] = parsed_times.dt.time

    # Replace missing times with midnight
    cleaned_df["_temp_time"] = cleaned_df["_temp_time"].fillna(
        pd.to_datetime("00:00:00").time()
    )

    # -----------------------------------------------------
    # 4. Combine DATE + TIME
    # -----------------------------------------------------
    combined = pd.to_datetime(
        cleaned_df["_temp_date"].astype(str)
        + " "
        + cleaned_df["_temp_time"].astype(str),
        errors="coerce"
    )

    iso_series = pd.Series(combined).dt.strftime("%Y-%m-%dT%H:%M:%S")

    # Insert new column beside original date column
    orig_index = cleaned_df.columns.get_loc(date_column)

    if "Date_Time" not in cleaned_df.columns:
        cleaned_df.insert(orig_index, "Date_Time", iso_series)
    else:
        cleaned_df.insert(orig_index, "Merged_Date_Time", iso_series)

    # -----------------------------------------------------
    # 5. Cleanup
    # -----------------------------------------------------
    cleaned_df.drop(
        columns=["_temp_date", "_temp_time_raw", "_temp_time"],
        inplace=True
    )

    # -----------------------------------------------------
    # 6. Return
    # -----------------------------------------------------

    return cleaned_df
