import pandas as pd

def add_cols(df: pd.DataFrame, *, filename=None, variable_names, values, columns):

    """
    Add one or more new columns to a DataFrame at user-selected positions.

    Parameters
    ----------
    df : pd.DataFrame
        The input dataframe.
    variable_names : list[str]
        Names of the new columns to add.
    values : list[Any]
        Values for each new column. Single values will broadcast.
    columns : list[int]
        1-based positions where each new column should be inserted.

    Returns
    -------
    cleaned_df : pd.DataFrame
        The updated dataframe.
    summary : dict
        A dictionary describing what was added.
    summary_df : None
        No supplementary dataframe for this task.
    """

    # -----------------------------------------------------
    # 1. VALIDATION (raise errors)
    # -----------------------------------------------------
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    if not (len(variable_names) == len(values) == len(columns)):
        raise ValueError("The number of variable names, values, and positions must match.")

    # Validate each name
    for name in variable_names:
        if not name or name.strip() == "":
            raise ValueError("Column names cannot be empty.")

    # Validate positions
    for pos in columns:
        if pos < 1 or pos > len(df.columns) + 1:
            raise ValueError(
                f"Invalid insert position {pos}. "
                f"Valid range is 1 to {len(df.columns) + 1}."
            )

    # Validate list-valued inputs
    for name, value in zip(variable_names, values):
        if isinstance(value, list) and len(value) != len(df):
            raise ValueError(
                f"Column '{name}' has a list of {len(value)} values, "
                f"but the dataframe has {len(df)} rows."
            )

    # -----------------------------------------------------
    # 2. CORE PROCESSING LOGIC
    # -----------------------------------------------------
    cleaned_df = df.copy()

    for name, value, pos in zip(variable_names, values, columns):

        # Prevent duplicates
        if name in cleaned_df.columns:
            raise ValueError(
                f"Column '{name}' already exists. "
                "Column names must be unique."
            )

        # Insert the column (convert 1-based to 0-based)
        cleaned_df.insert(pos - 1, name, value)

    # -----------------------------------------------------
    # 3. SUMMARY DICT
    # -----------------------------------------------------
    summary = {
        "columns_added": variable_names,
        "insert_positions": columns,
        "row_count": len(cleaned_df),
    }

    # -----------------------------------------------------
    # 4. SUMMARY DATAFRAME (optional)
    # -----------------------------------------------------
    summary_df = None

    # -----------------------------------------------------
    # 5. RETURN STANDARDIZED OUTPUT
    # -----------------------------------------------------
    return cleaned_df, summary, summary_df
