import pandas as pd

def merge(df, date_column, time_column):
    """
    Merge a separate date column and time column into a single ISO 8601
    datetime column (YYYY-MM-DDTHH:MM:SS), with strong validation and
    curator-friendly error reporting.

    This version adds:
        • column existence checks
        • empty-column detection
        • safer parsing for date and time
        • consistent "errors" list in the summary
        • predictable fallback behavior
    """

    cleaned_df = df.copy()

    # ---------------------------------------------------------
    # Summary structure
    # ---------------------------------------------------------
    summary = {
        "task_name": "merge_date_time",
        "unparsed_dates": [],
        "unparsed_times": [],
        "errors": [],
        "new_column": "Date_Time"
    }

    # ---------------------------------------------------------
    # VALIDATION 1 — Both columns must exist
    # ---------------------------------------------------------
    missing_cols = [col for col in [date_column, time_column] if col not in df.columns]
    if missing_cols:
        summary["errors"].append(
            f"Missing required column(s): {', '.join(missing_cols)}"
        )
        return cleaned_df, summary

    # ---------------------------------------------------------
    # VALIDATION 2 — Detect empty or all-blank columns
    # ---------------------------------------------------------
    if cleaned_df[date_column].isna().all() or cleaned_df[date_column].astype(str).str.strip().eq("").all():
        summary["errors"].append(f"Date column '{date_column}' is empty or blank.")
        cleaned_df["Date_Time"] = pd.NaT
        cleaned_df.drop(columns=[date_column, time_column], inplace=True)
        return cleaned_df, summary

    if cleaned_df[time_column].isna().all() or cleaned_df[time_column].astype(str).str.strip().eq("").all():
        summary["errors"].append(
            f"Time column '{time_column}' is empty or blank. Missing times will be replaced with midnight."
        )

    # ---------------------------------------------------------
    # STEP 1 — Parse DATE column safely
    # ---------------------------------------------------------
    try:
        # format="mixed" allows multiple date formats in the same column
        parsed_dates = pd.to_datetime(cleaned_df[date_column], format="mixed", errors="coerce")
    except Exception as e:
        summary["errors"].append(f"Unexpected error parsing date column: {str(e)}")
        cleaned_df["Date_Time"] = pd.NaT
        return cleaned_df, summary

    # Track unparsed dates
    for idx, val in cleaned_df[date_column].items():
        if pd.isna(parsed_dates[idx]):
            summary["unparsed_dates"].append((idx, val))

    # Convert parsed dates to pure date objects
    cleaned_df["_temp_date"] = parsed_dates.dt.date

    # ---------------------------------------------------------
    # STEP 2 — Parse TIME column safely
    # ---------------------------------------------------------
    cleaned_df["_temp_time_raw"] = cleaned_df[time_column].replace("", pd.NA)

    try:
        parsed_times = pd.to_datetime(cleaned_df["_temp_time_raw"], errors="coerce")
    except Exception as e:
        summary["errors"].append(f"Unexpected error parsing time column: {str(e)}")
        cleaned_df["Date_Time"] = pd.NaT
        return cleaned_df, summary

    # Track unparsed times
    for idx, val in cleaned_df["_temp_time_raw"].items():
        if pd.isna(parsed_times[idx]):
            summary["unparsed_times"].append((idx, val))

    # Convert parsed times to pure time objects
    cleaned_df["_temp_time"] = parsed_times.dt.time

    # Replace missing/unparsed times with midnight
    cleaned_df["_temp_time"] = cleaned_df["_temp_time"].fillna(
        pd.to_datetime("00:00:00").time()
    )

    # ---------------------------------------------------------
    # STEP 3 — Combine date + time into full datetime
    # ---------------------------------------------------------
    combined = pd.to_datetime(
        cleaned_df["_temp_date"].astype(str) + " " + cleaned_df["_temp_time"].astype(str),
        errors="coerce"
    )

    # Convert to ISO 8601 strings
    iso_series = pd.Series(combined).dt.strftime("%Y-%m-%dT%H:%M:%S")

    # ---------------------------------------------------------
    # STEP 4 — Insert new ISO column beside original date column
    # ---------------------------------------------------------
    orig_index = cleaned_df.columns.get_loc(date_column)
    cleaned_df.insert(orig_index, "Date_Time", iso_series)

    # ---------------------------------------------------------
    # STEP 5 — Remove original + temporary columns
    # ---------------------------------------------------------
    cleaned_df.drop(
        columns=[date_column, time_column, "_temp_date", "_temp_time_raw", "_temp_time"],
        inplace=True
    )

    return cleaned_df, summary
