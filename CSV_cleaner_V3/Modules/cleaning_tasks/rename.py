import streamlit as st

def dedupe_columns(cols):
    # This helper function ensures all column names are unique.
    # If a name appears more than once, we append _1, _2, etc.
    seen = {}
    new_cols = []

    for col in cols:
        if col not in seen:
            # First time we've seen this name
            seen[col] = 0
            new_cols.append(col)
        else:
            # We've seen this name before → create a unique version
            seen[col] += 1
            new_cols.append(f"{col}_{seen[col]}")

    return new_cols

def rename_cols(df, standardized_names):
    """
    Rename the columns of a DataFrame in a safe and predictable way.

    This function:
        • works on a copy of the DataFrame (the original is never changed)
        • checks that the number of new names matches the number of existing columns
        • trims whitespace and converts all new names to strings
        • automatically fixes duplicate names by appending _1, _2, etc.
        • applies the new names to the DataFrame
        • returns a summary describing what changed

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame whose columns you want to rename.

    standardized_names : list[str]
        A list of new column names, in the same order as the existing columns.
        The list must have the same length as df.columns.
        Duplicate names are allowed — they will be made unique automatically.

        Example:
            ["site", "date", "date", "value"]
            becomes:
            ["site", "date", "date_1", "value"]

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A copy of the original DataFrame with updated column names.

    summary : dict
        Information about the renaming process.
        Structure:
            {
                "renamed": True/False,
                "old_names": [...],
                "new_names": [...],
                "changed_count": number of columns whose names actually changed
            }

    Notes
    -----
    • If the number of new names does not match the number of columns,
      the function does not rename anything and returns a warning.
    • The helper function `dedupe_columns()` ensures all new names are unique.

    Example
    -------
    >>> df.columns
    ["A", "B", "C"]

    >>> rename_cols(df, ["site", "date", "date"])
    new names → ["site", "date", "date_1"]

    >>> summary["changed_count"]
    3
    """


    # Work on a copy so the original DataFrame is never modified.
    cleaned_df = df.copy()

    # Safety check:
    # The number of new names must match the number of existing columns.
    # If not, renaming would misalign the data.
    if len(cleaned_df.columns) != len(standardized_names):
        st.warning(
            "Column count mismatch — this file was not renamed. "
            "Ensure all uploaded files have the same structure.",
            icon="⚠️"
        )
        return cleaned_df, {"renamed": False}

    # Clean the new names:
    #   • convert everything to strings
    #   • strip whitespace
    safe_names = dedupe_columns([str(n).strip() for n in standardized_names])

    # Store the old names for the summary.
    old_names = list(cleaned_df.columns)

    # Apply the new names.
    cleaned_df.columns = safe_names

    # Build a summary describing what changed.
    summary = {
        "renamed": True,
        "old_names": old_names,
        "new_names": safe_names,
        "changed_count": sum(o != n for o, n in zip(old_names, safe_names))
    }

    return cleaned_df, summary