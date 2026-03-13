import pandas as pd
import re


def split_column(
    df: pd.DataFrame,
    *,
    column,
    delimiters
):
    """
    Split a single column into multiple new columns using one or more delimiters.

    This task:
    - normalizes whitespace (including NBSP from PDF exports)
    - collapses repeated whitespace
    - splits the column using literal or regex delimiters
    - inserts new columns next to the original
    - removes the original column only if multiple new columns were created
    - returns a summary describing the split operation

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset.

    column : str
        Name of the column to split.

    delimiters : list[str]
        List of delimiters to split on. Each may be:
        - a literal character (",", "|", "/", etc.)
        - a regex pattern (e.g., "\\s+")

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A copy of the input DataFrame with new split columns added.

    summary : dict
        {
            "column": str,
            "delimiters": list[str],
            "new_columns": list[str],
            "rows_split": int,
            "warnings": list[str]
        }

    summary_df : None
        Always None for this task.

    Notes
    -----
    - Hard validation errors (e.g., missing column) raise exceptions.
    - Soft validation issues (e.g., no splits detected) appear in
      summary["warnings"] but do not stop execution.
    """

    # -----------------------------------------------------
    # 1. VALIDATION — Hard Errors
    # -----------------------------------------------------

    # A. df must be a DataFrame
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    # B. column must be a string
    if not isinstance(column, str):
        raise ValueError("column must be a string.")

    # C. delimiters must be a list of strings
    if not isinstance(delimiters, list) or not all(isinstance(d, str) for d in delimiters):
        raise ValueError("delimiters must be a list of strings.")

    cleaned_df = df.copy()

    # -----------------------------------------------------
    # 2. VALIDATION — Soft Checks
    # -----------------------------------------------------
    warnings = []

    # A. Column must exist
    if column not in cleaned_df.columns:
        warnings.append(f"Column '{column}' not found. No split performed.")
        summary = {
            "column": column,
            "delimiters": delimiters,
            "new_columns": [],
            "rows_split": 0,
            "warnings": warnings,
        }
        return cleaned_df, summary, None

    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------

    # Normalize whitespace
    cleaned_series = (
        cleaned_df[column]
        .astype(str)
        .str.replace("\u00A0", " ", regex=False)   # NBSP → space
        .str.replace(r"\s+", " ", regex=True)      # collapse whitespace
        .str.strip()
    )

    # Build regex pattern
    escaped = [
        d if d.startswith("\\") else re.escape(d)
        for d in delimiters
    ]
    pattern = "|".join(escaped)

    # Perform split
    split_df = cleaned_series.str.split(pattern, expand=True)

    # If no split occurred
    if split_df.shape[1] <= 1:
        warnings.append("No splits detected using the provided delimiter(s).")
        summary = {
            "column": column,
            "delimiters": delimiters,
            "new_columns": [],
            "rows_split": 0,
            "warnings": warnings,
        }
        return cleaned_df, summary, None

    # Insert new columns
    original_idx = cleaned_df.columns.get_loc(column)
    cleaned_df = cleaned_df.drop(columns=[column])

    new_cols = []
    for i in range(split_df.shape[1]):
        new_col = f"{column}_{i+1}"
        cleaned_df.insert(original_idx + i, new_col, split_df[i])
        new_cols.append(new_col)

    rows_split = (split_df.notna().sum(axis=1) > 1).sum()

    # -----------------------------------------------------
    # 4. SUMMARY
    # -----------------------------------------------------
    summary = {
        "column": column,
        "delimiters": delimiters,
        "new_columns": new_cols,
        "rows_split": rows_split,
        "warnings": warnings,
    }

    # -----------------------------------------------------
    # 5. SUMMARY DATAFRAME
    # -----------------------------------------------------
    summary_df = None

    # -----------------------------------------------------
    # 6. RETURN
    # -----------------------------------------------------
    return cleaned_df, summary, summary_df
