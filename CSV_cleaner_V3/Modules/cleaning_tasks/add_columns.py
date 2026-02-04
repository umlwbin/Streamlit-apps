def add_cols(df, variable_names, values, columns):
    """
    Add new columns to a DataFrame.

    Parameters:
        df (DataFrame):
            The data you want to modify.

        variable_names (list of str):
            The names of the new columns.
            Example: ["site_id", "qc_flag"]

        values (list):
            The values for each new column.
            Each item can be a single value or a list of values.
            Example: ["LWB001", "OK"]

        columns (list of int):
            The positions where each new column should be inserted.
            Positions start at 1.
            Example: [1, 3]

    Returns:
        cleaned_df (DataFrame):
            The DataFrame with the new columns added.

        summary (dict):
            Information about what was added or skipped.
    """


    cleaned_df = df.copy()
    summary = {
        "columns_added": [],
        "errors": []
    }

    # Basic validation
    if not (len(variable_names) == len(values) == len(columns)):
        summary["errors"].append("Input lists must have the same length.")
        return cleaned_df, summary

    # Insert columns one by one
    for name, value, pos in zip(variable_names, values, columns):

        # Skip empty names; A name could be " " or a /n or /t etc, so the length check doesn't catch it
        if not name or name.strip() == "":
            summary["errors"].append("A column with an empty name was skipped.")
            continue

        # Prevent duplicate names
        if name in cleaned_df.columns:
            summary["errors"].append(f"Column '{name}' already exists and was skipped.")
            continue

        # Validate position
        if pos < 1 or pos > len(cleaned_df.columns) + 1:
            summary["errors"].append(
                f"Invalid position {pos} for column '{name}'. Skipped."
            )
            continue

        # Insert the column
        cleaned_df.insert(pos - 1, name, value)
        summary["columns_added"].append(name)

    return cleaned_df, summary