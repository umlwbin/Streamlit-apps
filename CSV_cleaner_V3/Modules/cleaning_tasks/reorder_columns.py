import pandas as pd

def reorder_columns(
    df: pd.DataFrame,
    *,
    filename=None,
    reordered_variables,
    **kwargs
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
    """
    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors
    # -----------------------------------------------------

    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    if not isinstance(reordered_variables, list):
        raise ValueError("reordered_variables must be a list of column names.")

    try:
        reordered_variables = [str(v) for v in reordered_variables]
    except Exception:
        raise ValueError("All values in reordered_variables must be convertible to strings.")

    cleaned_df = df.copy()

    # Ensure all column names are strings
    cleaned_df.columns = cleaned_df.columns.astype(str)

    # -----------------------------------------------------
    # 2. CORE PROCESSING
    # -----------------------------------------------------

    # Keep only valid requested columns
    valid_order = [c for c in reordered_variables if c in cleaned_df.columns]

    # Append leftover columns
    leftovers = [c for c in cleaned_df.columns if c not in valid_order]

    final_order = valid_order + leftovers

    cleaned_df = cleaned_df[final_order]

    # -----------------------------------------------------
    # 3. RETURN
    # -----------------------------------------------------
    return cleaned_df
