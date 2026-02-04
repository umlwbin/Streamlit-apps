import numpy as np
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
# 6. Normalize column name case (lower, upper, title)
# ---------------------------------------------------------
def normalize_case(df, mode="none"):
    cleaned_df = df.copy()

    # Apply the selected casing mode.
    if mode == "lower":
        cleaned_df.columns = [str(c).lower() for c in cleaned_df.columns]
    elif mode == "upper":
        cleaned_df.columns = [str(c).upper() for c in cleaned_df.columns]
    elif mode == "title":
        cleaned_df.columns = [str(c).title() for c in cleaned_df.columns]

    summary = {"case_normalization": mode}
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
def basic_cleaning(df, nans=None, case_mode="none"):
    """
    Run a lightweight, safe, automatic cleaning pipeline that prepares a dataset
    for downstream processing. This pipeline focuses on structural issues that
    commonly appear in real-world CSV files: empty rows, placeholder NaNs,
    duplicate column names, inconsistent casing, and header-like rows inside
    the data.

    The pipeline performs the following steps in order:
        1. Remove columns that contain only missing values.
        2. Remove rows that contain only missing values.
        3. Standardize NaN-like tokens (e.g., "NA", "?", "", "N/A") into a single representation.
        4. Trim whitespace from column names and string cells.
        5. Fix duplicate column names by appending suffixes (_1, _2, ...).
        6. Normalize column name casing (lower, upper, title, or none).
        7. Detect columns that contain mixed data types.
        8. Detect header-like rows inside the data.
        9. Clean column headers using the advanced scientific header cleaner.

    Parameters
    ----------
    df : pandas.DataFrame
        The input dataset to clean.

    nans : list[str], optional
        Additional tokens that should be treated as missing values.
        These are added to the default list of NaN-like strings.

    case_mode : {"none", "lower", "upper", "title"}, optional
        How to normalize column name casing.
        "none" leaves casing unchanged.

    Returns
    -------
    cleaned_df : pandas.DataFrame
        The cleaned dataset after all steps have been applied.

    summary : dict
        A combined dictionary containing the summaries from all steps.
        Each key corresponds to a cleaning step and records what was changed,
        detected, or standardized.

    Example
    -------
    from tidy_data import basic_cleaning
    cleaned, summary = basic_cleaning(raw, nans=["?"], case_mode="lower")

    """


    summary = {}

    # Step 1 — Remove empty columns
    df, s1 = remove_empty_columns(df)
    summary.update(s1)

    # Step 2 — Remove empty rows
    df, s2 = remove_empty_rows(df)
    summary.update(s2)

    # Step 3 — Standardize NaN-like values
    df, s3 = standardize_nans(df, nans)
    summary.update(s3)

    # Step 4 — Trim whitespace
    df, s4 = trim_whitespace(df)
    summary.update(s4)

    # Step 5 — Fix duplicate column names
    df, s5 = fix_duplicate_columns(df)
    summary.update(s5)

    # Step 6 — Normalize case
    df, s6 = normalize_case(df, mode=case_mode)
    summary.update(s6)

    # Step 7 — Detect mixed data types
    df, s7 = detect_mixed_types(df)
    summary.update(s7)

    # Step 8 — Detect header-like rows
    df, s8 = detect_header_rows(df)
    summary.update(s8)

    # Step 9 — Clean column headers using advanced scientific cleaner (external module)
    df, s9 = advanced_clean_headers(
        df,
        naming_style="none",
        preserve_units=True
    )
    summary.update({"header_cleaning": s9})

    return df, summary