import pandas as pd

# =========================================================
# Helper functions
# =========================================================

def dedupe_columns(cols):
    """
    Ensure column names are unique by appending suffixes (_1, _2, ...).
    """
    seen = {}
    new_cols = []
    for c in cols:
        if c not in seen:
            seen[c] = 0
            new_cols.append(c)
        else:
            seen[c] += 1
            new_cols.append(f"{c}_{seen[c]}")
    return new_cols


def transpose(df: pd.DataFrame):
    """
    Transpose a DataFrame and promote the first transposed row to the header.

    This task:
    - flips rows and columns
    - promotes the first transposed row to column names
    - ensures column names are unique
    - resets the index
    - returns a summary describing before/after dimensions

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset to transpose.

    Returns
    -------
    cleaned_df : pandas.DataFrame
        Transposed DataFrame with a clean header.

    summary : dict
        {
            "operation": "transpose",
            "rows_before": int,
            "cols_before": int,
            "rows_after": int,
            "cols_after": int,
            "warnings": list[str]
        }

    summary_df : None
        Always None for this task.
    """

    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors
    # -----------------------------------------------------
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    # -----------------------------------------------------
    # 2. VALIDATION - Soft Checks
    # -----------------------------------------------------
    warnings = []

    if df.empty:
        warnings.append("Input DataFrame is empty. Transpose will return an empty DataFrame.")

    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------
    t = df.transpose()

    if not t.empty:
        t.columns = t.iloc[0].astype(str)
        t = t.drop(t.index[0])
        t.columns = dedupe_columns(list(t.columns))

    t = t.reset_index(drop=True)

    # -----------------------------------------------------
    # 4. SUMMARY
    # -----------------------------------------------------
    summary = {
        "operation": "transpose",
        "rows_before": df.shape[0],
        "cols_before": df.shape[1],
        "rows_after": t.shape[0],
        "cols_after": t.shape[1],
        "warnings": warnings,
    }

    # -----------------------------------------------------
    # 5. SUMMARY DATAFRAME
    # -----------------------------------------------------
    summary_df = None

    # -----------------------------------------------------
    # 6. RETURN
    # -----------------------------------------------------
    return t, summary, summary_df



def wide_to_long(
    df: pd.DataFrame,
    *,
    id_cols,
    value_cols,
    var_name,
    value_name
):
    """
    Convert a wide-format table into long format using pandas.melt().

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset.

    id_cols : list[str]
        Columns that remain fixed (identifiers).

    value_cols : list[str]
        Columns to unpivot into long format.

    var_name : str
        Name of the new column that will store former column names.

    value_name : str
        Name of the new column that will store values.

    Returns
    -------
    cleaned_df : pandas.DataFrame
        Long-format DataFrame.

    summary : dict
        {
            "operation": "wide_to_long",
            "id_cols": list[str],
            "value_cols": list[str],
            "rows_before": int,
            "rows_after": int,
            "warnings": list[str]
        }

    summary_df : None
        Always None for this task.
    """

    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors
    # -----------------------------------------------------
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    for col in id_cols + value_cols:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' does not exist in the dataset.")

    # -----------------------------------------------------
    # 2. VALIDATION - Soft Checks
    # -----------------------------------------------------
    warnings = []

    if df.empty:
        warnings.append("Input DataFrame is empty. Output will also be empty.")

    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------
    long_df = df.melt(
        id_vars=id_cols,
        value_vars=value_cols,
        var_name=var_name,
        value_name=value_name
    )

    # -----------------------------------------------------
    # 4. SUMMARY
    # -----------------------------------------------------
    summary = {
        "operation": "wide_to_long",
        "id_cols": id_cols,
        "value_cols": value_cols,
        "rows_before": df.shape[0],
        "rows_after": long_df.shape[0],
        "warnings": warnings,
    }

    # -----------------------------------------------------
    # 5. SUMMARY DATAFRAME
    # -----------------------------------------------------
    summary_df = None

    # -----------------------------------------------------
    # 6. RETURN
    # -----------------------------------------------------
    return long_df, summary, summary_df




def long_to_wide(
    df: pd.DataFrame,
    *,
    variable_col,
    value_col,
    id_cols
):
    """
    Convert a long-format table into wide format using pivot_table().

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset.

    variable_col : str
        Column whose values become new column names.

    value_col : str
        Column whose values fill the new wide table.

    id_cols : list[str]
        Columns that uniquely identify each row.

    Returns
    -------
    cleaned_df : pandas.DataFrame
        Wide-format DataFrame.

    summary : dict
        {
            "operation": "long_to_wide",
            "variable_col": str,
            "value_col": str,
            "id_cols": list[str],
            "rows_before": int,
            "rows_after": int,
            "warnings": list[str]
        }

    summary_df : None
        Always None for this task.
    """

    # -----------------------------------------------------
    # 1. VALIDATION — Hard Errors
    # -----------------------------------------------------
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    for col in [variable_col, value_col] + id_cols:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' does not exist in the dataset.")

    # -----------------------------------------------------
    # 2. VALIDATION — Soft Checks
    # -----------------------------------------------------
    warnings = []

    if df.empty:
        warnings.append("Input DataFrame is empty. Output will also be empty.")

    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------
    wide_df = df.pivot_table(
        index=id_cols,
        columns=variable_col,
        values=value_col,
        aggfunc="first"
    ).reset_index()

    wide_df.columns = dedupe_columns(list(wide_df.columns))

    # -----------------------------------------------------
    # 4. SUMMARY
    # -----------------------------------------------------
    summary = {
        "operation": "long_to_wide",
        "variable_col": variable_col,
        "value_col": value_col,
        "id_cols": id_cols,
        "rows_before": df.shape[0],
        "rows_after": wide_df.shape[0],
        "warnings": warnings,
    }

    # -----------------------------------------------------
    # 5. SUMMARY DATAFRAME
    # -----------------------------------------------------
    summary_df = None

    # -----------------------------------------------------
    # 6. RETURN
    # -----------------------------------------------------
    return wide_df, summary, summary_df




# =========================================================
# Dispatcher
# =========================================================
DISPATCH = {
    "transpose": transpose,
    "wide_to_long": wide_to_long,
    "long_to_wide": long_to_wide,
}


def reshape(df: pd.DataFrame, *, filename=None, operation, **kwargs):
    """
    Dispatch reshape operations: transpose, wide_to_long, long_to_wide.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset.

    operation : str
        One of: "transpose", "wide_to_long", "long_to_wide".

    **kwargs :
        Additional arguments required by the selected operation.

    Returns
    -------
    cleaned_df : pandas.DataFrame
        Reshaped DataFrame.

    summary : dict
        Summary of the reshape operation.

    summary_df : pandas.DataFrame or None
        Optional summary table depending on the operation.
    """

    # -----------------------------------------------------
    # 1. VALIDATION — Hard Errors
    # -----------------------------------------------------
    if operation not in DISPATCH:
        raise ValueError(f"Unknown reshape operation: {operation}")

    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    # -----------------------------------------------------
    # 2. VALIDATION — Soft Checks
    # -----------------------------------------------------
    # (none needed here)

    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------
    func = DISPATCH[operation]
    return func(df, **kwargs)
