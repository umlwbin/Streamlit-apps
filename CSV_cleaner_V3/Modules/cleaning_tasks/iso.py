import pandas as pd
import re


def convert_to_iso(
    df: pd.DataFrame,
    *,
    date_time_col: str,
    ambiguous_mode: str,
    **kwargs
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

    ambiguous_mode : {
                      "Assume month-first (MM/DD/YYYY)",
                      "Assume day-first (DD/MM/YYYY)",
                      "Assume year-first (YYYY-MM-DD)"}

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A copy of the input DataFrame with a new ISO-formatted column inserted
        beside the original. The original column is preserved.
    """

    # -----------------------------------------------------
    # 1. VALIDATION
    # -----------------------------------------------------
    if date_time_col not in df.columns:
        raise ValueError(f"Column '{date_time_col}' does not exist.")

    cleaned_df = df.copy()
    series = cleaned_df[date_time_col].astype(str)

    # -----------------------------------------------------
    # 2. Determine how to parse
    # -----------------------------------------------------
    if ambiguous_mode == "Assume month-first (MM/DD/YYYY)":
        dayfirst = False
        force_year_first = False

    elif ambiguous_mode == "Assume day-first (DD/MM/YYYY)":
        dayfirst = True
        force_year_first = False

    elif ambiguous_mode == "Assume year-first (YYYY-MM-DD)":
        dayfirst = None
        force_year_first = True

    else:
        dayfirst = None
        force_year_first = False

    iso_values = []

    # -----------------------------------------------------
    # 3. Parse each row
    # -----------------------------------------------------
    for value in series:

        # YEAR-FIRST strict branch
        if force_year_first and re.match(r"^\d{4}[\-/]", value.strip()):
            try:
                parsed = pd.to_datetime(value, errors="raise")
                iso_values.append(parsed)
                continue
            except Exception:
                pass  # fall through to flexible parsing

        # Flexible parsing
        try:
            d1 = pd.to_datetime(value, errors="coerce", dayfirst=True)
            d2 = pd.to_datetime(value, errors="coerce", dayfirst=False)
        except Exception:
            iso_values.append(pd.NaT)
            continue

        # Both failed
        if pd.isna(d1) and pd.isna(d2):
            iso_values.append(pd.NaT)
            continue

        # Ambiguous
        if not pd.isna(d1) and not pd.isna(d2) and d1 != d2:
            if dayfirst is None:
                iso_values.append(pd.NaT)
                continue
            parsed = pd.to_datetime(value, errors="coerce", dayfirst=dayfirst)
            iso_values.append(parsed)
            continue

        # Only one succeeded
        parsed = d1 if not pd.isna(d1) else d2
        iso_values.append(parsed)

    # -----------------------------------------------------
    # 4. Build ISO column
    # -----------------------------------------------------
    # Convert the parsed datetime values into a Series before formatting.
    # pd.to_datetime(iso_values) sometimes returns a DatetimeIndex (not a Series)and DatetimeIndex does NOT support the `.dt` accessor. 
    # Wrapping it in pd.Series(...) guarantees we always have a Series, so `.dt.strftime(...)` works reliably for all inputs.
    iso_series = pd.Series(pd.to_datetime(iso_values)).dt.strftime("%Y-%m-%dT%H:%M:%S")

    new_col = f"{date_time_col}_ISO"

    orig_index = cleaned_df.columns.get_loc(date_time_col)
    cleaned_df.insert(orig_index + 1, new_col, iso_series)

    return cleaned_df
