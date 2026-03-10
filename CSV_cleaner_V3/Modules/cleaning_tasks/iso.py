import pandas as pd
import re

def convert_to_iso(df, date_time_col, ambiguous_mode="Flag ambiguous rows only"):
    """
    Convert a date or datetime column into ISO 8601 format (YYYY-MM-DDTHH:MM:SS)
    with strong validation, ambiguity handling, and curator-friendly error reporting.

    This version adds:
        • column existence checks
        • empty-column detection
        • detection of already-ISO formatted columns
        • timezone-awareness warnings
        • consistent "errors" list in the summary
        • safe fallbacks for unexpected parsing failures
    """

    # ---------------------------------------------------------
    # SUMMARY STRUCTURE
    # ---------------------------------------------------------
    summary = {
        "task_name": "iso",
        "converted_rows": 0,
        "ambiguous_rows": [],
        "unparsed_rows": [],
        "errors": [],
        "new_column": None,
        "ambiguous_mode": ambiguous_mode
    }

    # ---------------------------------------------------------
    # VALIDATION 1 — Column must exist
    # ---------------------------------------------------------
    if date_time_col not in df.columns:
        summary["errors"].append(
            f"Column '{date_time_col}' does not exist in the dataset."
        )
        return df.copy(), summary

    cleaned_df = df.copy()

    # ---------------------------------------------------------
    # VALIDATION 2 — Column must not be entirely empty
    # ---------------------------------------------------------
    col_series = cleaned_df[date_time_col]

    if col_series.isna().all() or col_series.astype(str).str.strip().eq("").all():
        summary["errors"].append(
            f"Column '{date_time_col}' is empty or contains only blank values."
        )
        # Replace with an empty ISO column
        new_col = f"{date_time_col}_ISO"
        cleaned_df[new_col] = pd.NaT
        cleaned_df.drop(columns=[date_time_col], inplace=True)
        summary["new_column"] = new_col
        return cleaned_df, summary

    # ---------------------------------------------------------
    # VALIDATION 3 — Detect if column is already ISO formatted
    # ---------------------------------------------------------
    iso_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")

    if col_series.astype(str).str.match(iso_pattern).all():
        # Column is already ISO → simply rename it
        new_col = f"{date_time_col}_ISO"
        cleaned_df[new_col] = col_series
        cleaned_df.drop(columns=[date_time_col], inplace=True)
        summary["new_column"] = new_col
        return cleaned_df, summary

    # ---------------------------------------------------------
    # Convert entire column to strings for consistent parsing
    # ---------------------------------------------------------
    series = col_series.astype(str)

    iso_values = []

    # ---------------------------------------------------------
    # Decide how to resolve ambiguous dates
    # ---------------------------------------------------------
    if ambiguous_mode == "Assume month-first (MM/DD/YYYY)":
        resolve_dayfirst = False
    elif ambiguous_mode == "Assume day-first (DD/MM/YYYY)":
        resolve_dayfirst = True
    else:
        resolve_dayfirst = None   # Flag ambiguous rows only

    # ---------------------------------------------------------
    # MAIN LOOP — Parse each row safely
    # ---------------------------------------------------------
    for idx, value in series.items():

        # Detect timezone-aware datetimes (e.g., "2024-01-01T12:00:00Z")
        if "Z" in value or "+" in value or "-" in value[10:]:
            summary["errors"].append(
                f"Row {idx}: timezone information detected and removed ('{value}')."
            )

        try:
            # Try parsing both interpretations
            d1 = pd.to_datetime(value, errors="coerce", dayfirst=True)
            d2 = pd.to_datetime(value, errors="coerce", dayfirst=False)
        except Exception as e:
            summary["unparsed_rows"].append((idx, value))
            iso_values.append(pd.NaT)
            continue

        # Case 1 — Both failed → not a valid date
        if pd.isna(d1) and pd.isna(d2):
            summary["unparsed_rows"].append((idx, value))
            iso_values.append(pd.NaT)
            continue

        # Case 2 — Both succeeded but differ → ambiguous
        if not pd.isna(d1) and not pd.isna(d2) and d1 != d2:

            if resolve_dayfirst is None:
                # User chose to flag ambiguous rows only
                summary["ambiguous_rows"].append((idx, value))
                iso_values.append(pd.NaT)
                continue

            # Resolve ambiguity using user rule
            parsed = pd.to_datetime(value, errors="coerce", dayfirst=resolve_dayfirst)
            iso_values.append(parsed)
            summary["converted_rows"] += 1
            continue

        # Case 3 — Only one interpretation succeeded → safe
        parsed = d1 if not pd.isna(d1) else d2
        iso_values.append(parsed)
        summary["converted_rows"] += 1

    # ---------------------------------------------------------
    # Convert parsed datetimes to ISO strings
    # ---------------------------------------------------------
    iso_series = pd.Series(pd.to_datetime(iso_values)).dt.strftime("%Y-%m-%dT%H:%M:%S")

    # ---------------------------------------------------------
    # Decide on new column name
    # ---------------------------------------------------------
    if date_time_col.lower() in ["date_time", "datetime"]:
        new_col = "DateTime_ISO"
    else:
        new_col = f"{date_time_col}_ISO"

    summary["new_column"] = new_col

    # Insert ISO column beside original
    orig_index = cleaned_df.columns.get_loc(date_time_col)
    cleaned_df.insert(orig_index, new_col, iso_series)

    # Remove original column
    cleaned_df.drop(columns=[date_time_col], inplace=True)

    return cleaned_df, summary
