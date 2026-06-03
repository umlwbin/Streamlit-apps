import pandas as pd

def merge_ymd(
    df: pd.DataFrame,
    *,
    year_column: str,
    month_column: str,
    day_column: str,
    **kwargs
):
    """
    Merge year, month, and day columns into a single ISO date column.
    """

    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors
    # -----------------------------------------------------

    # A. df must be a DataFrame
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    # B. Required columns must exist
    missing = [c for c in [year_column, month_column, day_column] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")

    cleaned_df = df.copy()

    # -----------------------------------------------------
    # 2. CORE PROCESSING
    # -----------------------------------------------------

    # --- Parse YEAR column ---
    y = pd.to_numeric(cleaned_df[year_column], errors="coerce")

    # --- Parse MONTH column (missing ---> 1) ---
    m = pd.to_numeric(cleaned_df[month_column], errors="coerce").fillna(1)

    # --- Parse DAY column (missing ---> 1) ---
    d = pd.to_numeric(cleaned_df[day_column], errors="coerce").fillna(1)

    # --- Combine into a datetime ---
    combined = pd.to_datetime(
        dict(year=y, month=m, day=d),
        errors="coerce"
    )

    # --- Format as ISO date ---
    iso_series = combined.dt.strftime("%Y-%m-%d")

    # Insert new column beside the original year column
    orig_index = cleaned_df.columns.get_loc(year_column)

    if "Date" not in cleaned_df.columns:
        cleaned_df.insert(orig_index, "Date", iso_series)
    else:
        cleaned_df.insert(orig_index, "Merged_Date", iso_series)

    # Drop original columns
    #cleaned_df.drop(columns=[year_column, month_column, day_column], inplace=True)

    # -----------------------------------------------------
    # 3. RETURN
    # -----------------------------------------------------
    return cleaned_df
