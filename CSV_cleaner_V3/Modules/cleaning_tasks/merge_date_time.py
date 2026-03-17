import pandas as pd


def merge_date_time(
    df: pd.DataFrame,
    *,
    filename=None,
    date_column,
    time_column
):
    """
    Merge separate date and time columns into a single ISO 8601 datetime column.

    This task safely parses mixed-format date and time values, handles missing
    or unparseable entries, replaces missing times with midnight, and reports
    issues without stopping execution.

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

    summary : dict
        {
            "new_column": "Date_Time",
            "unparsed_dates": [(row_index, value)],
            "unparsed_times": [(row_index, value)],
            "warnings": [list of soft validation messages]
        }

    summary_df : pandas.DataFrame or None
        A table of unparsed date/time rows, or None if none exist.

    Notes
    -----
    - Hard validation errors (e.g., missing required columns) raise exceptions.
    - Soft validation issues (e.g., empty time column) appear in summary["warnings"]
      but do not stop execution.
    """


    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors (A, B, C…)
    # -----------------------------------------------------

    # A. df must be a DataFrame
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    # B. Required columns must exist
    missing = [c for c in [date_column, time_column] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")

    cleaned_df = df.copy()

    # -----------------------------------------------------
    # 2. VALIDATION - Soft Checks (A, B, C…)
    # -----------------------------------------------------
    warnings = []

    # A. Date column empty
    if cleaned_df[date_column].isna().all() or cleaned_df[date_column].astype(str).str.strip().eq("").all():
        warnings.append(f"Date column '{date_column}' is empty or blank.")
        cleaned_df["Date_Time"] = pd.NaT
        cleaned_df.drop(columns=[date_column, time_column], inplace=True)

        summary = {
            "new_column": "Date_Time",
            "unparsed_dates": [],
            "unparsed_times": [],
            "warnings": warnings,
        }
        return cleaned_df, summary, None

    # B. Time column empty
    if cleaned_df[time_column].isna().all() or cleaned_df[time_column].astype(str).str.strip().eq("").all():
        warnings.append(
            f"Time column '{time_column}' is empty or blank. Missing times replaced with midnight."
        )

    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------

    # --- Parse DATE column ---
    try:
        parsed_dates = pd.to_datetime(cleaned_df[date_column], format="mixed", errors="coerce")
    except Exception as e:
        warnings.append(f"Unexpected error parsing date column: {str(e)}")
        cleaned_df["Date_Time"] = pd.NaT
        summary = {
            "new_column": "Date_Time",
            "unparsed_dates": [],
            "unparsed_times": [],
            "warnings": warnings,
        }
        return cleaned_df, summary, None

    unparsed_dates = []
    for idx, val in cleaned_df[date_column].items():
        if pd.isna(parsed_dates[idx]):
            unparsed_dates.append((idx, val))

    cleaned_df["_temp_date"] = parsed_dates.dt.date

    # --- Parse TIME column ---
    cleaned_df["_temp_time_raw"] = cleaned_df[time_column].replace("", pd.NA)

    try:
        parsed_times = pd.to_datetime(cleaned_df["_temp_time_raw"], errors="coerce")
    except Exception as e:
        warnings.append(f"Unexpected error parsing time column: {str(e)}")
        cleaned_df["Date_Time"] = pd.NaT
        summary = {
            "new_column": "Date_Time",
            "unparsed_dates": unparsed_dates,
            "unparsed_times": [],
            "warnings": warnings,
        }
        return cleaned_df, summary, None

    unparsed_times = []
    for idx, val in cleaned_df["_temp_time_raw"].items():
        if pd.isna(parsed_times[idx]):
            unparsed_times.append((idx, val))

    cleaned_df["_temp_time"] = parsed_times.dt.time
    cleaned_df["_temp_time"] = cleaned_df["_temp_time"].fillna(
        pd.to_datetime("00:00:00").time()
    )

    # --- Combine DATE + TIME ---
    combined = pd.to_datetime(
        cleaned_df["_temp_date"].astype(str) + " " + cleaned_df["_temp_time"].astype(str),
        errors="coerce"
    )

    iso_series = pd.Series(combined).dt.strftime("%Y-%m-%dT%H:%M:%S")

    # Insert new column beside original date column
    orig_index = cleaned_df.columns.get_loc(date_column)
    cleaned_df.insert(orig_index, "Date_Time", iso_series)

    # Cleanup
    cleaned_df.drop(
        columns=[date_column, time_column, "_temp_date", "_temp_time_raw", "_temp_time"],
        inplace=True
    )

    # -----------------------------------------------------
    # 4. SUMMARY
    # -----------------------------------------------------
    summary = {
        "new_column": "Date_Time",
        "unparsed_dates": unparsed_dates,
        "unparsed_times": unparsed_times,
        "warnings": warnings,
    }

    # -----------------------------------------------------
    # 5. SUMMARY DATAFRAME
    # -----------------------------------------------------
    summary_df = None
    if unparsed_dates or unparsed_times:
        rows = []
        for idx, val in unparsed_dates:
            rows.append({"row": idx, "value": val, "type": "unparsed_date"})
        for idx, val in unparsed_times:
            rows.append({"row": idx, "value": val, "type": "unparsed_time"})
        summary_df = pd.DataFrame(rows)

    # -----------------------------------------------------
    # 6. RETURN
    # -----------------------------------------------------
    return cleaned_df, summary, summary_df
