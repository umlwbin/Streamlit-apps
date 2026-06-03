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


def transpose(df: pd.DataFrame, *, filename=None, **kwargs):
    """
    Safe transpose:
        - preserves original headers as a column
        - generates synthetic column names for transposed data
    """

    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    # Core transpose
    t = df.copy().T

    # Reset index so original headers become a column
    t = t.reset_index().rename(columns={"index": "Original Headers"})

    # Synthetic column names
    new_cols = ["Original Headers"] + [f"col_{i}" for i in range(t.shape[1] - 1)]
    t.columns = new_cols

    return t




def wide_to_long(
    df: pd.DataFrame,
    *,
    id_cols,
    value_cols,
    var_name,
    value_name,
    filename=None,
    **kwargs
):
    """
    Convert wide-format table to long format using melt().
    """

    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    for col in id_cols + value_cols:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' does not exist in the dataset.")

    long_df = df.melt(
        id_vars=id_cols,
        value_vars=value_cols,
        var_name=var_name,
        value_name=value_name
    )

    return long_df



def long_to_wide(
    df: pd.DataFrame,
    *,
    variable_col,
    value_col,
    id_cols,
    filename=None,
    **kwargs
):
    """
    Convert long-format table to wide format using pivot_table().
    """

    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    for col in [variable_col, value_col] + id_cols:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' does not exist in the dataset.")

    wide_df = df.pivot_table(
        index=id_cols,
        columns=variable_col,
        values=value_col,
        aggfunc="first"
    ).reset_index()

    wide_df.columns = dedupe_columns(list(wide_df.columns))

    return wide_df


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
    """


    if operation not in DISPATCH:
        raise ValueError(f"Unknown reshape operation: {operation}")

    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    func = DISPATCH[operation]
    return func(df, filename=filename, **kwargs)

