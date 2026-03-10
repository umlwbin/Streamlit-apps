def add_cols(df, variable_names, values, columns):
    """
    Add new columns to a DataFrame.

    This function inserts one or more new columns at user-selected positions.
    Each new column can contain a single repeated value or a full list of values.

    Returns:
        cleaned_df: the updated DataFrame
        summary: a dictionary describing what was added or skipped

    Example with pure python:
    # Sample dataframe
    df = pd.DataFrame({
        "A": [10, 20, 30],
        "B": [40, 50, 60]
    })

    # Define new columns to add
    variable_names = ["site_id", "qc_flag"]
    values = ["LWB001", "OK"]          # single values will broadcast to all rows
    positions = [1, 3]                 # insert at column 1 and column 3 (1-based)

    # Run the task
    cleaned_df, summary = add_cols(df, variable_names, values, positions)

    print(cleaned_df)
    print(summary)

    """

    cleaned_df = df.copy()

    # Summary shown to the user
    summary = {
        "task_name": "add_columns",
        "columns_added": [],
        "errors": []
    }

    # ---------------------------------------------------------
    # Basic validation: all lists must be the same length
    # ---------------------------------------------------------
    if not (len(variable_names) == len(values) == len(columns)):
        summary["errors"].append(
            "The number of names, values, and positions must match."
        )
        return cleaned_df, summary

    # ---------------------------------------------------------
    # Insert columns one by one
    # ---------------------------------------------------------
    for name, value, pos in zip(variable_names, values, columns):

        # Skip empty or whitespace-only names
        if not name or name.strip() == "":
            summary["errors"].append("A column with an empty name was skipped.")
            continue

        # Prevent duplicate names
        if name in cleaned_df.columns:
            summary["errors"].append(
                f"Column '{name}' already exists and was skipped."
            )
            continue

        # Validate insert position (1-based index)
        if pos < 1 or pos > len(cleaned_df.columns) + 1:
            summary["errors"].append(
                f"Invalid position {pos} for column '{name}'. Skipped."
            )
            continue

        # ---------------------------------------------------------
        # Validate value length
        # If the user provides a list, it must match the number of rows. ** Not supported right now, but feel free to add later! :)
        # If the user provides a single value, pandas will broadcast it.
        # ---------------------------------------------------------
        if isinstance(value, list) and len(value) != len(cleaned_df):
            summary["errors"].append(
                f"Column '{name}' was skipped because its value list "
                f"has {len(value)} items but the table has {len(cleaned_df)} rows."
            )
            continue

        # Insert the column (pos is 1-based, insert expects 0-based)
        cleaned_df.insert(pos - 1, name, value)
        summary["columns_added"].append(name)

    return cleaned_df, summary
