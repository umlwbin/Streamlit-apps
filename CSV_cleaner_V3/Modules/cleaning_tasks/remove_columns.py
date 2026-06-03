import pandas as pd


def remove_columns(
    df: pd.DataFrame,
    *,
    variables_to_remove,
    **kwargs
):
    """
    Remove one or more columns from a DataFrame in a safe, predictable way.

    This task:
    - works on a copy of the DataFrame
    - ensures column names are treated as strings
    - removes only columns that exist

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
    """


    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors
    # -----------------------------------------------------

    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    if not isinstance(variables_to_remove, list):
        raise ValueError("variables_to_remove must be a list of column names.")

    # Convert all to strings
    try:
        variables_to_remove = [str(v) for v in variables_to_remove]
    except Exception:
        raise ValueError("All values in variables_to_remove must be convertible to strings.")

    cleaned_df = df.copy()

    # Ensure all column names are strings
    cleaned_df.columns = cleaned_df.columns.astype(str)

    # -----------------------------------------------------
    # 2. CORE PROCESSING
    # -----------------------------------------------------

    # Drop only columns that exist
    to_drop = [c for c in variables_to_remove if c in cleaned_df.columns]
    cleaned_df = cleaned_df.drop(columns=to_drop)

    # -----------------------------------------------------
    # 3. RETURN
    # -----------------------------------------------------
    return cleaned_df
