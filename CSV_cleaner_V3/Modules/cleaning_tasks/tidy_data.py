import numpy as np
import pandas as pd
import re
from Modules.cleaning_tasks.headers import clean_headers as advanced_clean_headers

# =========================================================
# TIDY DATA CLEANING PIPELINE
# ---------------------------------------------------------
# This module performs a sequence of lightweight, safe,
# automatic cleaning steps that prepare a dataset for
# downstream processing. Each step returns:
#     (cleaned_df, summary_dict)
#
# The final `basic_cleaning()` function chains all steps
# together and merges their summaries.
# =========================================================


# ---------------------------------------------------------
# 1. Remove columns that contain ONLY missing values
# ---------------------------------------------------------
def remove_empty_columns(df):
    # Identify columns where *every* value is missing.
    empty_cols = [col for col in df.columns if df[col].isnull().all()]

    # Drop them only if any exist; otherwise return a safe copy.
    cleaned_df = df.drop(columns=empty_cols) if empty_cols else df.copy()

    summary = {"empty_columns_removed": empty_cols}
    return cleaned_df, summary



# ---------------------------------------------------------
# 2. Remove rows that contain ONLY missing values
# ---------------------------------------------------------
def remove_empty_rows(df):
    # A row is "empty" if all its values are NaN.
    empty_rows_mask = df.isna().all(axis=1)
    empty_rows_count = empty_rows_mask.sum() 

    # Keep only the non-empty rows.
    #Columns are removed by name, so we use drop(columns=...).Rows are removed by condition, so we filter with a boolean mask.
    cleaned_df = df[~empty_rows_mask].copy()

    summary = {"empty_rows_removed": empty_rows_count}
    return cleaned_df, summary



# ---------------------------------------------------------
# 3. Standardize NaN-like values into a single representation
# ---------------------------------------------------------
def standardize_nans(df, nans=None):
    # Default tokens commonly used to represent missing values.
    na_values = ['NA', '?', 'N/A', '', np.nan, None, 'Nan', 'NaN']

    # Add user-provided tokens from the UI.
    # Note: --append adds the whole object, such as a list as a single item ; --extend adds each element of the object individually.
    if nans:
        na_values.extend(nans)

    # Count how many cells match any NaN-like token.
    nan_mask = df.isin(na_values) # performs a cell‑by‑cell lookup; does this cell’s value equal to any element in na_values?
    nan_count = nan_mask.sum().sum() # First sum sums across columns, second sum takes a sum of that series, giving the total nans in the df

    # Replace all NaN-like tokens with a single representation: empty string.
    cleaned_df = df.replace(na_values, '')

    summary = {"nans_replaced": nan_count}
    return cleaned_df, summary



# ---------------------------------------------------------
# 4. Fix duplicate column names by appending suffixes
# ---------------------------------------------------------
def dedupe_columns(cols):
    seen = {}
    new_cols = []
    for col in cols:
        if col not in seen:
            seen[col] = 0
            new_cols.append(col)
        else:
            seen[col] += 1
            new_cols.append(f"{col}_{seen[col]}")
    return new_cols


def fix_duplicate_columns(df):
    original_cols = list(df.columns)

    # Find columns that appear more than once.
    duplicates = [col for col in original_cols if original_cols.count(col) > 1]

    if duplicates:
        cleaned_df = df.copy()

        # Use helper to append _1, _2, etc. to duplicates.
        cleaned_df.columns = dedupe_columns(original_cols)

        summary = {
            "duplicate_columns_found": duplicates,
            "duplicate_columns_fixed": True,
            "new_column_names": list(cleaned_df.columns)
        }
        return cleaned_df, summary

    # No duplicates → nothing to fix.
    return df.copy(), {
        "duplicate_columns_found": [],
        "duplicate_columns_fixed": False
    }



# ---------------------------------------------------------
# 5. Trim whitespace from column names and string cells
# ---------------------------------------------------------
def trim_whitespace(df):
    cleaned_df = df.copy()

    # Trim whitespace from column names.
    cleaned_df.columns = [str(c).strip() for c in cleaned_df.columns]

    # Trim whitespace inside every string cell.
    cleaned_df = cleaned_df.applymap(
        lambda x: x.strip() if isinstance(x, str) else x # applymap() applies the lambda to every single cell in the DataFrame, one by one.
    )

    summary = {"whitespace_trimmed": True}
    return cleaned_df, summary


# ---------------------------------------------------------
# 7. Detect columns that contain mixed data types
# ---------------------------------------------------------
def detect_mixed_types(df):
    mixed = {}

    for col in df.columns:
        # Collect the Python types present in the column.
        types = set(type(v) for v in df[col].dropna()) # A set keeps only unique items.

        # If more than one type appears, the column is "mixed".
        if len(types) > 1:
            mixed[col] = list(types)

    summary = {
        "mixed_type_columns": mixed,
        "mixed_type_count": len(mixed)
    }

    return df.copy(), summary



# ---------------------------------------------------------
# 8. Detect header-like rows inside the data
# ---------------------------------------------------------
def detect_header_rows(df):
    header_like_rows = []

    for idx, row in df.iterrows():
        # Convert row values and column names to comparable strings.
        values = row.astype(str).str.strip().tolist() # .str.strip() is specifically defined on a Series (which row is) so you can't just use .strip(), which is just the pandas string method
        cols = [str(c).strip() for c in df.columns]

        # Exact match: row matches column names.
        if values == cols:
            header_like_rows.append(idx)
        else:
            # Soft match: hecks whether every cell in the row looks like a word (letters only).
            if all(v.replace("_", "").isalpha() for v in values):
                header_like_rows.append(idx)

    summary = {
        "header_rows_detected": header_like_rows,
        "header_row_count": len(header_like_rows)
    }

    return df.copy(), summary



# =========================================================
# 9. FULL CLEANING PIPELINE
# ---------------------------------------------------------
# Runs all steps in a safe, predictable order.
# Returns:
#     cleaned_df, combined_summary
# =========================================================
def basic_cleaning(
    df: pd.DataFrame,
    *,
    filename=None,
    nans=None,
    naming_style="snake_case",
    preserve_units=True,
    extract_additional=True,
    no_units_in_header=False
):
    """
    Run a lightweight, safe, automatic cleaning pipeline that prepares a dataset
    for downstream processing.

    This pipeline performs the following steps in order:
        1. Remove empty columns.
        2. Remove empty rows.
        3. Standardize NaN-like tokens.
        4. Trim whitespace.
        5. Fix duplicate column names.
        6. Detect mixed data types.
        7. Detect header-like rows.
        8. Clean column headers using the unified scientific cleaner.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset to clean.

    nans : list[str] or None, optional
        Additional tokens to treat as missing values.

    naming_style : {"snake_case", "camelCase", "Title Case"}, optional
        Naming convention for cleaned headers.

    preserve_units : bool, optional
        Whether to include detected units in cleaned headers.

    extract_additional : bool, optional
        Whether to extract additional metadata from headers.

    no_units_in_header : bool, optional
        If True, bracket content is treated as descriptive text, not units.

    Returns
    -------
    cleaned_df : pandas.DataFrame
        The cleaned dataset after all steps.

    summary : dict
        Combined summary of all steps, including:
            - empty_columns_removed
            - empty_rows_removed
            - nans_replaced
            - whitespace_trimmed
            - duplicate_columns_found
            - mixed_type_columns
            - header_rows_detected
            - header_cleaning (from advanced cleaner)
            - warnings (soft validation issues)

    summary_df : None
        Always None for this pipeline.

    Notes
    -----
    - Hard validation errors (e.g., invalid naming_style) raise exceptions.
    - Soft validation issues (e.g., empty DataFrame) appear in summary["warnings"].
    """

    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors
    # -----------------------------------------------------

    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    if nans is not None and not isinstance(nans, list):
        raise ValueError("nans must be a list of strings or None.")

    valid_styles = {"snake_case", "camelCase", "Title Case"}
    if naming_style not in valid_styles:
        raise ValueError(f"Invalid naming_style '{naming_style}'.")

    for flag in [preserve_units, extract_additional, no_units_in_header]:
        if not isinstance(flag, bool):
            raise ValueError("preserve_units, extract_additional, and no_units_in_header must be boolean.")

    cleaned_df = df.copy()

    # -----------------------------------------------------
    # 2. VALIDATION - Soft Checks
    # -----------------------------------------------------
    warnings = []

    if cleaned_df.empty:
        warnings.append("Input DataFrame is empty. Cleaning steps will have no effect.")

    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------
    summary = {"task_name": "tidy_data", "warnings": warnings}

    # Step 1 - Remove empty columns
    cleaned_df, s1 = remove_empty_columns(cleaned_df)
    summary.update(s1)

    # Step 2 - Remove empty rows
    cleaned_df, s2 = remove_empty_rows(cleaned_df)
    summary.update(s2)

    # Step 3 - Standardize NaN-like values
    cleaned_df, s3 = standardize_nans(cleaned_df, nans)
    summary.update(s3)

    # Step 4 - Trim whitespace
    cleaned_df, s4 = trim_whitespace(cleaned_df)
    summary.update(s4)

    # Step 5 - Fix duplicate column names
    cleaned_df, s5 = fix_duplicate_columns(cleaned_df)
    summary.update(s5)

    # Step 6 - Detect mixed data types
    cleaned_df, s6 = detect_mixed_types(cleaned_df)
    summary.update(s6)

    # Step 7 - Detect header-like rows
    cleaned_df, s7 = detect_header_rows(cleaned_df)
    summary.update(s7)

    # Step 8 - Clean headers using advanced cleaner
    cleaned_df, s8 = advanced_clean_headers(
        cleaned_df,
        naming_style=naming_style,
        preserve_units=preserve_units,
        extract_additional=extract_additional,
        no_units_in_header=no_units_in_header
    )
    summary.update(s8)

    # -----------------------------------------------------
    # 4. SUMMARY
    # -----------------------------------------------------
    # (already built incrementally)

    # -----------------------------------------------------
    # 5. SUMMARY DATAFRAME
    # -----------------------------------------------------
    summary_df = None

    # -----------------------------------------------------
    # 6. RETURN
    # -----------------------------------------------------
    return cleaned_df, summary, summary_df