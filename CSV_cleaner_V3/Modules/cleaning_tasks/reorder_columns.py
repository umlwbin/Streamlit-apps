import streamlit as st
import pandas as pd

def reorder(df, reordered_variables):
    """
    Reorder the columns of a DataFrame in a safe and predictable way.

    This function:
        • works on a copy of the DataFrame (the original is never changed)
        • checks which requested columns actually exist
        • warns the user about any missing columns
        • reorders the DataFrame using only the valid column names
        • appends any leftover columns at the end to avoid data loss
        • returns a summary describing the final order

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame whose columns you want to reorder.

    reordered_variables : list[str]
        A list of column names in the order the user wants.
        Columns that do not exist in the DataFrame are ignored safely.
        Any columns not listed here will be added to the end automatically.

        Example:
            If df has columns ["A", "B", "C", "D"] and the user provides:
                ["C", "A"]
            the final order becomes:
                ["C", "A", "B", "D"]

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A copy of the original DataFrame with columns in the new order.

    summary : dict
        Information about the reordering process.
        Structure:
            {
                "requested_order": [...],   # what the user asked for
                "final_order": [...],       # the actual order applied
                "missing_columns": [...],   # columns that were requested but not found
                "changed": True/False       # whether the order changed at all
            }

    Example
    -------
    >>> df.columns
    ["A", "B", "C"]

    >>> cleaned_df, summary = reorder(df, ["C", "A"])

    >>> cleaned_df.columns
    ["C", "A", "B"]

    >>> summary["missing_columns"]
    []
    """

    # Work on a copy so the original DataFrame stays unchanged.
    cleaned_df = df.copy()

    # Convert all column names to strings.
    # This avoids issues where a column might be named 1 instead of "1".
    cleaned_df.columns = cleaned_df.columns.astype(str)

    # Identify which requested columns do NOT exist in the DataFrame.
    # This helps us warn the user instead of silently ignoring mistakes.
    missing = [c for c in reordered_variables if c not in cleaned_df.columns]

    if missing:
        st.warning(
            f"Some columns were not found and could not be reordered: {missing}",
            icon="⚠️"
        )

    # Keep only the requested columns that actually exist.
    # This prevents errors if the user includes invalid names.
    valid_order = [c for c in reordered_variables if c in cleaned_df.columns]

    # Identify any columns that were NOT included in the user's list.
    # These will be added at the end to avoid losing data.
    leftovers = [c for c in cleaned_df.columns if c not in valid_order]

    # The final order is:
    #   1. all valid requested columns (in the order the user gave)
    #   2. all leftover columns (in their original order)
    final_order = valid_order + leftovers

    # Reorder the DataFrame using the final order.
    cleaned_df = cleaned_df[final_order] # the same syntax used for selecting/subsetting columns also controls their order!

    # Build a summary describing what happened.
    summary = {
        "requested_order": reordered_variables,     # what the user asked for
        "final_order": final_order,                 # what was actually applied
        "missing_columns": missing,                 # which requested columns didn't exist
        "changed": reordered_variables != list(df.columns)  # did anything change?
    }

    return cleaned_df, summary
