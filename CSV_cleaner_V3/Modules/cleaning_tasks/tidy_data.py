import numpy as np
import pandas as pd
import re
from Modules.cleaning_tasks.headers import clean_headers as advanced_clean_headers

# =========================================================
# TIDY DATA CLEANING PIPELINE
# ---------------------------------------------------------
# This module performs a sequence of lightweight, safe,
# automatic cleaning steps that prepare a dataset for
# downstream processing. 
# Each step returns:(cleaned_df)
#
# The final `basic_cleaning()` function chains all steps
# together and merges their summaries.
# =========================================================

# ---------------------------------------------------------
# 1. Remove columns that contain ONLY missing values
# ---------------------------------------------------------
def remove_empty_columns(df):
    empty_cols = [col for col in df.columns if df[col].isnull().all()]
    return df.drop(columns=empty_cols) if empty_cols else df.copy()


# ---------------------------------------------------------
# 2. Remove rows that contain ONLY missing values
# ---------------------------------------------------------
def remove_empty_rows(df):
    mask = ~df.isna().all(axis=1)
    return df[mask].copy()


# ---------------------------------------------------------
# 3. Standardize NaN-like values into a single representation
# ---------------------------------------------------------
def standardize_nans(df, nans=None):
    """
    Replace common NaN-like tokens with empty string.
    Widget handles soft validation.
    """
    na_values = ['NA', '?', 'N/A', '', np.nan, None, 'Nan', 'NaN','NAN', 'NA', 'Null']
    if nans:
        na_values.extend(nans)

    cleaned_df = df.replace(na_values, '')
    return cleaned_df


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
    if len(original_cols) != len(set(original_cols)):
        cleaned_df = df.copy()
        cleaned_df.columns = dedupe_columns(original_cols)
        return cleaned_df
    return df.copy()


# ---------------------------------------------------------
# 5. Trim whitespace from column names and string cells
# ---------------------------------------------------------
def trim_whitespace(df):
    cleaned_df = df.copy()
    cleaned_df.columns = [str(c).strip() for c in cleaned_df.columns]
    cleaned_df = cleaned_df.applymap(
        lambda x: x.strip() if isinstance(x, str) else x
    )
    return cleaned_df


# =========================================================
# 6. FULL CLEANING PIPELINE (ARCHITECTURE-ALIGNED)
# =========================================================
def basic_cleaning(
    df: pd.DataFrame,
    *,
    filename=None,
    nans=None,
    naming_style="snake_case",
    preserve_units=True,
    no_units_in_header=False,
    skip_headers=False,
    **kwargs
):
    """
    This pipeline prepares raw data for downstream processing by:
        • removing empty rows/columns
        • standardizing NaN-like tokens
        • trimming whitespace
        • fixing duplicate column names
        • cleaning headers (units + naming style)
    """

    # -----------------------------------------------------
    # 1. HARD VALIDATION ONLY
    # -----------------------------------------------------
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    if nans is not None and not isinstance(nans, list):
        raise ValueError("nans must be a list of strings or None.")

    valid_styles = {"snake_case", "camelCase", "Title Case"}
    if naming_style not in valid_styles:
        raise ValueError(f"Invalid naming_style '{naming_style}'.")

    for flag in [preserve_units, no_units_in_header]:
        if not isinstance(flag, bool):
            raise ValueError("preserve_units and no_units_in_header must be boolean.")

    cleaned_df = df.copy()

    # -----------------------------------------------------
    # 2. CORE PROCESSING (pure transformations)
    # -----------------------------------------------------

    metadata_df = None   # ensure this variable always exists

    # Step 1 - Remove empty columns
    cleaned_df = remove_empty_columns(cleaned_df)

    # Step 2 - Remove empty rows
    cleaned_df = remove_empty_rows(cleaned_df)

    # Step 3 - Standardize NaN-like tokens
    cleaned_df = standardize_nans(cleaned_df, nans)

    # Step 4 - Trim whitespace
    cleaned_df = trim_whitespace(cleaned_df)

    # Step 5 - Fix duplicate column names
    cleaned_df = fix_duplicate_columns(cleaned_df)


    # Step 6 - Clean headers (optional; returns metadata_df if used; called from the original clean headers function)
    if not skip_headers:
        cleaned_df, metadata_df = advanced_clean_headers(
            cleaned_df,
            naming_style=naming_style,
            preserve_units=preserve_units,
            no_units_in_header=no_units_in_header
        )
    else:
        metadata_df = pd.DataFrame({"info": ["Header cleaning skipped"]}) # if not used 

    # -----------------------------------------------------
    # 3. RETURN (cleaned_df, metadata_df)
    # -----------------------------------------------------
    return cleaned_df, metadata_df
