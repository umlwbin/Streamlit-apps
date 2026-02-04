import pandas as pd

# =========================================================
# Helper functions
# =========================================================

def transpose(df):
    """Transpose the dataframe."""
    
    # Transpose flips rows ↔ columns.
    # .transpose() returns a new DataFrame where:
    #   - original columns become rows
    #   - original rows become columns
    # .reset_index() turns the old row labels into a normal column.
    transposed = df.transpose().reset_index()

    summary = {
        "operation": "transpose",
        "rows_before": df.shape[0],
        "cols_before": df.shape[1],
        "rows_after": transposed.shape[0],
        "cols_after": transposed.shape[1],
    }

    return transposed, summary



def wide_to_long(df, id_cols, value_cols, var_name, value_name):
    """Convert wide format to long format."""
    
    # pd.melt() is the standard tool for converting wide → long.
    # id_vars: columns that stay the same (identifiers)
    # value_vars: columns that get unpivoted into rows
    # var_name: name of the new column that stores former column names
    # value_name: name of the new column that stores the values
    long_df = df.melt(
        id_vars=id_cols,
        value_vars=value_cols,
        var_name=var_name,
        value_name=value_name
    )

    summary = {
        "operation": "wide_to_long",
        "id_cols": id_cols,
        "value_cols": value_cols,
        "rows_before": df.shape[0],
        "rows_after": long_df.shape[0],
    }

    return long_df, summary



def long_to_wide(df, variable_col, value_col, id_cols):
    """Convert long format to wide format."""
    
    # pivot_table() is the standard tool for long → wide.
    # index: columns that uniquely identify each row
    # columns: values in this column become new column names
    # values: values that fill the new wide table
    # aggfunc="first": if duplicates exist, take the first value
    wide_df = df.pivot_table(
        index=id_cols,
        columns=variable_col,
        values=value_col,
        aggfunc="first"
    ).reset_index()

    summary = {
        "operation": "long_to_wide",
        "variable_col": variable_col,
        "value_col": value_col,
        "id_cols": id_cols,
        "rows_before": df.shape[0],
        "rows_after": wide_df.shape[0],
    }

    return wide_df, summary



# =========================================================
# Dispatcher
# =========================================================

DISPATCH = {
    "transpose": transpose,
    "wide_to_long": wide_to_long,
    "long_to_wide": long_to_wide,
}


# =========================================================
# Reshape Function
# =========================================================

def reshape(df, operation, **kwargs):
    """
    Reshape a DataFrame using one of three supported operations:
    transpose, wide→long, or long→wide.

    This function acts as a central dispatcher. It does not reshape the
    data itself — instead, it routes the request to the appropriate helper
    function based on the 'operation' argument.

    Supported operations
    --------------------
    "transpose"
        Flips rows and columns. Row labels become column labels and
        column labels become a new column.

    "wide_to_long"
        Converts a wide-format table (many columns of repeated structure)
        into a long-format table (one row per measurement).
        Requires:
            id_cols   – columns that identify each row (stay the same)
            value_cols – columns to unpivot into long format
            var_name   – name of the new column that will hold former column names
            value_name – name of the new column that will hold the values

    "long_to_wide"
        Converts a long-format table back into wide format.
        Requires:
            variable_col – column whose values become new column names
            value_col    – column whose values fill the new wide table
            id_cols      – columns that uniquely identify each row

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame to reshape.

    operation : str
        One of: "transpose", "wide_to_long", "long_to_wide".

    **kwargs :
        Additional arguments required by the selected operation.
        These are passed directly to the helper function.

    Returns
    -------
    cleaned_df : pandas.DataFrame
        The reshaped DataFrame.

    summary : dict
        A dictionary describing what operation was performed and
        key details such as row/column counts before and after.

    Raises
    ------
    ValueError
        If an unknown operation name is provided.

    Example
    -------
    >>> reshape(df, "wide_to_long",
                id_cols=["site"],
                value_cols=["jan", "feb", "mar"],
                var_name="month",
                value_name="value")
    """


    # Ensure the requested operation is supported.
    if operation not in DISPATCH:
        raise ValueError(f"Unknown reshape operation: {operation}")

    # Look up the correct helper function.
    func = DISPATCH[operation]

    # Call the helper with the DataFrame and any extra arguments.
    return func(df, **kwargs)
