import streamlit as st

def remove_cols(df, variables_to_remove):
    """
    Remove one or more columns from a DataFrame in a safe, predictable way.

    This function:
        • works on a copy of the DataFrame (the original is never modified)
        • checks whether each requested column actually exists
        • warns the user about any missing columns
        • removes only the columns that are present
        • returns a summary describing what was removed and what remains

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame from which columns should be removed.

    variables_to_remove : list[str]
        A list of column names the user wants to remove.
        Column names are treated as strings, so values like 1 or 2 will be
        converted to "1" or "2" if needed.

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A copy of the original DataFrame with the selected columns removed.

    summary : dict
        Information about the removal process.
        Structure:
            {
                "removed_columns": [...],     # the columns the user asked to remove
                "remaining_columns": [...],   # the columns still in the DataFrame
                "removed_count": int,         # how many columns were removed
                "remaining_count": int        # how many columns remain
            }

    Example
    -------
    >>> df.columns
    ["A", "B", "C", "D"]

    >>> cleaned_df, summary = remove_cols(df, ["B", "D"])

    >>> cleaned_df.columns
    ["A", "C"]

    >>> summary
    {
        "removed_columns": ["B", "D"],
        "remaining_columns": ["A", "C"],
        "removed_count": 2,
        "remaining_count": 2
    }
    """

    # Work on a copy so the original DataFrame is never changed.
    cleaned_df = df.copy()

    # Safety step:
    # Ensure all column names are strings.
    # This avoids issues where a column might be named 1 or 2 instead of "1" or "2".
    cleaned_df.columns = cleaned_df.columns.astype(str)

    # Identify which requested columns do NOT exist in the DataFrame.
    # This helps us warn the user instead of failing silently.
    missing = [c for c in variables_to_remove if c not in cleaned_df.columns]
    if missing:
        st.warning(f"Some selected columns were not found: {missing}")

    # Drop only the columns that actually exist.
    # This prevents errors if the user selected a column that isn't present.
    cleaned_df = cleaned_df.drop(
        columns=[c for c in variables_to_remove if c in cleaned_df.columns]
    )

    # Build a summary describing what happened.
    summary = {
        "removed_columns": variables_to_remove,      # what the user asked to remove
        "remaining_columns": list(cleaned_df.columns),  # what is left
        "removed_count": len(variables_to_remove),   # how many were requested
        "remaining_count": cleaned_df.shape[1],      # how many columns remain
    }

    return cleaned_df, summary
