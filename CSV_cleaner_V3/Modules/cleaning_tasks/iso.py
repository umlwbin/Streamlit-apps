import pandas as pd
import re


def convert_to_iso(
    df: pd.DataFrame,
    *,
    date_time_col,
    ambiguous_mode="Flag ambiguous rows only"
):
    """
    Convert a date or datetime column into ISO 8601 format (YYYY-MM-DDTHH:MM:SS).

    This task performs robust parsing, ambiguity detection, timezone stripping,
    and curator-friendly reporting. Ambiguous or unparseable rows are preserved
    and reported without stopping execution.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset containing the date or datetime column.

    date_time_col : str
        Name of the column to convert.

    ambiguous_mode : {"Flag ambiguous rows only",
                      "Assume month-first (MM/DD/YYYY)",
                      "Assume day-first (DD/MM/YYYY)",
                      "Assume year-first (YYYY-MM-DD)"}, optional
        Strategy for resolving ambiguous dates.

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A copy of the input DataFrame with a new ISO-formatted column inserted
        beside the original. The original column is preserved.

    summary : dict
        {
            "new_column": str,
            "converted_rows": int,
            "ambiguous": [(row_index, value)],
            "unparsed": [(row_index, value)],
            "warnings": [list of soft validation messages],
            "ambiguous_mode": str
        }

    summary_df : pandas.DataFrame or None
        A table of ambiguous and unparsed rows, or None if none exist.

    Notes
    -----
    - Hard validation errors (e.g., missing column) raise exceptions.
    - Soft validation issues (e.g., timezone detected, empty column) appear in
      summary["warnings"] but do not stop execution.
    """


    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors
    # -----------------------------------------------------

    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    if date_time_col not in df.columns:
        raise ValueError(f"Column '{date_time_col}' does not exist in the dataset.")

    valid_modes = {
        "Flag ambiguous rows only",
        "Assume month-first (MM/DD/YYYY)",
        "Assume day-first (DD/MM/YYYY)",
        "Assume year-first (YYYY-MM-DD)",
    }
    if ambiguous_mode not in valid_modes:
        raise ValueError("Invalid ambiguous_mode value.")


    cleaned_df = df.copy()
    col_series = cleaned_df[date_time_col]


    # -----------------------------------------------------
    # 2. VALIDATION - Soft Checks
    # -----------------------------------------------------
    warnings = []

    if col_series.isna().all() or col_series.astype(str).str.strip().eq("").all():
        warnings.append(f"Column '{date_time_col}' is empty or blank.")
        new_col = f"{date_time_col}_ISO"
        cleaned_df[new_col] = pd.NaT

        summary = {
            "new_column": new_col,
            "converted_rows": 0,
            "ambiguous": [],
            "unparsed": [],
            "warnings": warnings,
            "ambiguous_mode": ambiguous_mode,
        }
        return cleaned_df, summary, None


    iso_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")
    if col_series.astype(str).str.match(iso_pattern).all():
        warnings.append(f"Column '{date_time_col}' is already ISO formatted.")
        new_col = f"{date_time_col}_ISO"
        cleaned_df[new_col] = col_series

        summary = {
            "new_column": new_col,
            "converted_rows": 0,
            "ambiguous": [],
            "unparsed": [],
            "warnings": warnings,
            "ambiguous_mode": ambiguous_mode,
        }
        return cleaned_df, summary, None


    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------
    series = col_series.astype(str)
    iso_values = []

    ambiguous = []
    unparsed = []
    converted_rows = 0


    # Determine ambiguity resolution
    if ambiguous_mode == "Assume month-first (MM/DD/YYYY)":
        resolve_dayfirst = False
        assume_year_first = False

    elif ambiguous_mode == "Assume day-first (DD/MM/YYYY)":
        resolve_dayfirst = True
        assume_year_first = False

    elif ambiguous_mode == "Assume year-first (YYYY-MM-DD)":
        resolve_dayfirst = None
        assume_year_first = True

    else:
        resolve_dayfirst = None
        assume_year_first = False


    for idx, value in series.items():

        # Soft warning: timezone detected
        if "Z" in value or "+" in value or "-" in value[10:]:
            warnings.append(
                f"Row {idx}: timezone information detected and removed ('{value}')."
            )

        # -----------------------------------------
        # YEAR-FIRST STRICT PARSING
        # -----------------------------------------
        if assume_year_first and re.match(r"^\d{4}[\-/]", value.strip()):
            strict_formats = [
                "%Y/%m/%d %H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y/%m/%d",
                "%Y-%m-%d",
            ]
            parsed = None
            for fmt in strict_formats:
                try:
                    parsed = pd.to_datetime(value, format=fmt)
                    break
                except Exception:
                    pass

            if parsed is not None:
                iso_values.append(parsed)
                converted_rows += 1
                continue
            # If strict year-first fails, fall through to flexible parsing


        # -----------------------------------------
        # FLEXIBLE PARSING (dayfirst=True and False)
        # -----------------------------------------
        try:
            d1 = pd.to_datetime(value, errors="coerce", dayfirst=True)
            d2 = pd.to_datetime(value, errors="coerce", dayfirst=False)
        except Exception:
            unparsed.append((idx, value))
            iso_values.append(pd.NaT)
            continue

        # Case 1 - both failed
        if pd.isna(d1) and pd.isna(d2):
            unparsed.append((idx, value))
            iso_values.append(pd.NaT)
            continue

        # Case 2 - ambiguous
        if not pd.isna(d1) and not pd.isna(d2) and d1 != d2:

            if resolve_dayfirst is None:
                ambiguous.append((idx, value))
                iso_values.append(pd.NaT)
                continue

            parsed = pd.to_datetime(value, errors="coerce", dayfirst=resolve_dayfirst)
            iso_values.append(parsed)
            converted_rows += 1
            continue

        # Case 3 - only one succeeded
        parsed = d1 if not pd.isna(d1) else d2
        iso_values.append(parsed)
        converted_rows += 1


    # Convert parsed datetimes to ISO strings
    iso_series = pd.Series(pd.to_datetime(iso_values)).dt.strftime("%Y-%m-%dT%H:%M:%S")

    # New column name
    new_col = f"{date_time_col}_ISO"

    # Insert ISO column beside original (do NOT remove original)
    orig_index = cleaned_df.columns.get_loc(date_time_col)
    cleaned_df.insert(orig_index + 1, new_col, iso_series)


    # -----------------------------------------------------
    # 4. SUMMARY
    # -----------------------------------------------------
    summary = {
        "new_column": new_col,
        "converted_rows": converted_rows,
        "ambiguous": ambiguous,
        "unparsed": unparsed,
        "warnings": warnings,
        "ambiguous_mode": ambiguous_mode,
    }


    # -----------------------------------------------------
    # 5. SUMMARY DATAFRAME
    # -----------------------------------------------------
    summary_df = None
    if ambiguous or unparsed:
        rows = []
        for idx, val in ambiguous:
            rows.append({"row": idx, "value": val, "type": "ambiguous"})
        for idx, val in unparsed:
            rows.append({"row": idx, "value": val, "type": "unparsed"})
        summary_df = pd.DataFrame(rows)


    # -----------------------------------------------------
    # 6. RETURN
    # -----------------------------------------------------
    return cleaned_df, summary, summary_df
