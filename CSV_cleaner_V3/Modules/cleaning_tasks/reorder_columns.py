import pandas as pd


def reorder_columns(
    df: pd.DataFrame,
    *,
    filename=None,
    reordered_variables
):
    """
    Reorder the columns of a DataFrame in a safe and predictable way.

    This task:
    - works on a copy of the DataFrame
    - validates that reordered_variables is a list
    - warns about requested columns that do not exist
    - reorders using only valid column names
    - appends leftover columns at the end to avoid data loss
    - returns a summary describing the final order

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset whose columns will be reordered.

    reordered_variables : list[str]
        Desired column order. Columns not present in the DataFrame are ignored.
        Columns not listed here are appended at the end.

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A copy of the input DataFrame with columns in the new order.

    summary : dict
        {
            "requested_order": list[str],
            "final_order": list[str],
            "missing_columns": list[str],
            "changed": bool,
            "warnings": list[str]
        }

    summary_df : None
        Always None for this task (included for template consistency).

    Notes
    -----
    - Hard validation errors (e.g., wrong input types) raise exceptions.
    - Soft validation issues (e.g., missing columns) appear in summary["warnings"]
      but do not stop execution.
    """

    # -----------------------------------------------------
    # 1. VALIDATION — Hard Errors (A, B, C…)
    # -----------------------------------------------------

    # A. df must be a DataFrame
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    # B. reordered_variables must be a list
    if not isinstance(reordered_variables, list):
        raise ValueError("reordered_variables must be a list of column names.")

    # C. All entries must be convertible to strings
    try:
        reordered_variables = [str(v) for v in reordered_variables]
    except Exception:
        raise ValueError("All values in reordered_variables must be convertible to strings.")

    cleaned_df = df.copy()

    # -----------------------------------------------------
    # 2. VALIDATION — Soft Checks (A, B, C…)
    # -----------------------------------------------------
    warnings = []

    # Ensure all column names are strings
    cleaned_df.columns = cleaned_df.columns.astype(str)

    # A. Identify missing columns
    missing = [c for c in reordered_variables if c not in cleaned_df.columns]
    if missing:
        warnings.append(f"Some requested columns were not found: {missing}")

    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------

    # Keep only valid requested columns
    valid_order = [c for c in reordered_variables if c in cleaned_df.columns]

    # Append leftover columns
    leftovers = [c for c in cleaned_df.columns if c not in valid_order]

    final_order = valid_order + leftovers

    cleaned_df = cleaned_df[final_order]

    # -----------------------------------------------------
    # 4. SUMMARY
    # -----------------------------------------------------
    summary = {
        "requested_order": reordered_variables,
        "final_order": final_order,
        "missing_columns": missing,
        "changed": final_order != list(df.columns),
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
