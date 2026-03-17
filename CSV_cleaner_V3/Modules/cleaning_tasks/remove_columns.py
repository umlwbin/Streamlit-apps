import pandas as pd


def remove_columns(
    df: pd.DataFrame,
    *,
    filename=None,
    variables_to_remove
):
    """
    Remove one or more columns from a DataFrame in a safe, predictable way.

    This task:
    - works on a copy of the DataFrame
    - ensures column names are treated as strings
    - removes only columns that exist
    - records missing columns as warnings
    - returns a summary describing what was removed and what remains

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset from which columns should be removed.

    variables_to_remove : list[str]
        List of column names to remove. Non-string values will be converted
        to strings for comparison.

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A copy of the input DataFrame with selected columns removed.

    summary : dict
        {
            "removed_columns": list[str],
            "remaining_columns": list[str],
            "removed_count": int,
            "remaining_count": int,
            "warnings": list[str]
        }

    summary_df : None
        Always None for this task (included for template consistency).

    Notes
    -----
    - Hard validation errors (e.g., invalid input types) raise exceptions.
    - Soft validation issues (e.g., missing columns) appear in summary["warnings"]
      but do not stop execution.
    """

    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors (A, B, C…)
    # -----------------------------------------------------

    # A. df must be a DataFrame
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    # B. variables_to_remove must be a list
    if not isinstance(variables_to_remove, list):
        raise ValueError("variables_to_remove must be a list of column names.")

    # C. All entries must be convertible to string
    try:
        variables_to_remove = [str(v) for v in variables_to_remove]
    except Exception:
        raise ValueError("All values in variables_to_remove must be convertible to strings.")

    cleaned_df = df.copy()

    # -----------------------------------------------------
    # 2. VALIDATION - Soft Checks (A, B, C…)
    # -----------------------------------------------------
    warnings = []

    # Ensure all column names are strings
    cleaned_df.columns = cleaned_df.columns.astype(str)

    # A. Identify missing columns
    missing = [c for c in variables_to_remove if c not in cleaned_df.columns]
    if missing:
        warnings.append(f"Some selected columns were not found: {missing}")

    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------

    # Remove only columns that exist
    to_drop = [c for c in variables_to_remove if c in cleaned_df.columns]
    cleaned_df = cleaned_df.drop(columns=to_drop)

    # -----------------------------------------------------
    # 4. SUMMARY
    # -----------------------------------------------------
    summary = {
        "removed_columns": variables_to_remove,
        "remaining_columns": list(cleaned_df.columns),
        "removed_count": len(to_drop),
        "remaining_count": cleaned_df.shape[1],
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
