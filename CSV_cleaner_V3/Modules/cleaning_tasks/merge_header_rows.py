import pandas as pd
import streamlit as st


def merge_header_rows(
    df: pd.DataFrame,
    *,
    row=None,
    filename=None,
    **kwargs
):
    """
    Merge a selected metadata row (based on ORIGINAL row numbers)
    into the existing header row.

    Parameters
    ----------
    df : pd.DataFrame
        The input dataframe.
    row : int or None
        The ORIGINAL row number (1-based) to merge into the header.
        This is supplied by the widget layer.
    filename : str or None
        The name of the file being processed. Required in Streamlit mode
        to retrieve the authoritative row_map from session_state.

    Returns
    -------
    cleaned_df : pd.DataFrame
        The transformed dataframe with the selected row merged into the header.
    summary : dict
        A dictionary describing the changes made by the task, including
        the updated row_map.
    summary_df : None
        This task does not produce a supplementary table.

    ----------------------------------------------------------------------
    OFFLINE / NON‑STREAMLIT USAGE
    ----------------------------------------------------------------------
    If running this task outside Streamlit (e.g., in a notebook), you can
    manually construct a row_map like this:

        row_map = list(range(1, len(df) + 1))

    And replace the session_state lookup:

        # Instead of:
        row_map = st.session_state.row_map[filename]

        # Use:
        row_map = list(range(1, len(df) + 1))

    IMPORTANT:
        - This will renumber rows after each merge.
        - Undo/redo and provenance will NOT be preserved.
        - This is only recommended for simple, one‑off usage.
    ----------------------------------------------------------------------
    """

    # -----------------------------------------------------
    # 1. HARD VALIDATION (raise errors)
    # -----------------------------------------------------
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    if row is None:
        raise ValueError("A row number must be provided for merging.")

    if filename is None:
        raise ValueError("filename must be provided to retrieve row_map.")

    if filename not in st.session_state.row_map:
        raise ValueError(f"No row_map found for file '{filename}'.")

    # -----------------------------------------------------
    # 2. SOFT VALIDATION
    # -----------------------------------------------------
    warnings = []

    # Retrieve authoritative row_map - FOR STREAMLIT USE
    row_map = st.session_state.row_map[filename]

    #********** If running without streamlit, use:
    # row_map = list(range(1, len(df) + 1)) 

    if len(row_map) != len(df):
        raise ValueError(
            "row_map length does not match DataFrame length. "
            "This indicates an internal workflow error."
        )

    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------
    cleaned_df = df.copy()

    # Map ORIGINAL row number → current index
    try:
        idx = row_map.index(row)
    except ValueError:
        warnings.append(f"Row {row} not found in this file. It was skipped.")
        return cleaned_df, {"warnings": warnings, "row_map": row_map}, None

    # Merge selected row into header
    header = list(cleaned_df.columns.astype(str))
    vals = list(cleaned_df.iloc[idx])

    header = [
        f"{h}_{v}" if pd.notna(v) and str(v).strip() != "" else h
        for h, v in zip(header, vals)
    ]

    # Drop merged row + update row_map
    cleaned_df = cleaned_df.drop(index=[idx]).reset_index(drop=True)

    new_row_map = [
        row_map[i] for i in range(len(row_map)) if i != idx
    ]

    cleaned_df.columns = header

    # -----------------------------------------------------
    # 4. SUMMARY DICTIONARY
    # -----------------------------------------------------
    summary = {
        "merged_row": row,
        "row_map": new_row_map,
    }

    if warnings:
        summary["warnings"] = warnings

    # -----------------------------------------------------
    # 5. OPTIONAL SUMMARY DATAFRAME
    # -----------------------------------------------------
    summary_df = None

    # -----------------------------------------------------
    # 6. RETURN STANDARDIZED OUTPUT
    # -----------------------------------------------------
    return cleaned_df, summary, summary_df
