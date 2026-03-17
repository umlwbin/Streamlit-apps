import pandas as pd


def dedupe_columns(cols):
    """
    Ensure column names are unique by appending suffixes (_1, _2, ...).
    """
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


def rename_columns(
    df: pd.DataFrame,
    *,
    filename=None,
    standardized_names
):
    """
    Rename the columns of a DataFrame in a safe and predictable way.

    This task:
    - works on a copy of the DataFrame
    - validates that the number of new names matches the number of existing columns
    - trims whitespace and converts new names to strings
    - ensures uniqueness by appending suffixes (_1, _2, ...)
    - returns a summary describing what changed

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset whose columns will be renamed.

    standardized_names : list[str]
        New column names, in the same order as df.columns.
        Duplicate names are allowed; they will be made unique automatically.

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A copy of the input DataFrame with updated column names.

    summary : dict
        {
            "renamed": bool,
            "old_names": list[str],
            "new_names": list[str],
            "changed_count": int,
            "warnings": list[str]
        }

    summary_df : None
        Always None for this task (included for template consistency).

    Notes
    -----
    - Hard validation errors (e.g., wrong input types) raise exceptions.
    - Soft validation issues (e.g., column count mismatch) appear in
      summary["warnings"] and renaming is skipped.
    """

    # -----------------------------------------------------
    # 1. VALIDATION — Hard Errors (A, B, C…)
    # -----------------------------------------------------

    # A. df must be a DataFrame
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    # B. standardized_names must be a list
    if not isinstance(standardized_names, list):
        raise ValueError("standardized_names must be a list of column names.")

    # C. All names must be convertible to strings
    try:
        standardized_names = [str(n).strip() for n in standardized_names]
    except Exception:
        raise ValueError("All standardized_names must be convertible to strings.")

    cleaned_df = df.copy()

    # -----------------------------------------------------
    # 2. VALIDATION — Soft Checks (A, B, C…)
    # -----------------------------------------------------
    warnings = []

    # A. Column count mismatch → skip renaming
    if len(cleaned_df.columns) != len(standardized_names):
        warnings.append(
            "Column count mismatch — renaming skipped. "
            "Ensure all uploaded files have the same structure."
        )

        summary = {
            "renamed": False,
            "warnings": warnings,
        }
        return cleaned_df, summary, None

    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------

    # Ensure uniqueness
    safe_names = dedupe_columns(standardized_names)

    old_names = list(cleaned_df.columns)
    cleaned_df.columns = safe_names

    # -----------------------------------------------------
    # 4. SUMMARY
    # -----------------------------------------------------
    summary = {
        "renamed": True,
        "old_names": old_names,
        "new_names": safe_names,
        "changed_count": sum(o != n for o, n in zip(old_names, safe_names)),
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
