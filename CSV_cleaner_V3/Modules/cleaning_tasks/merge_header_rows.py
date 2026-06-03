import pandas as pd
import streamlit as st


def merge_header_rows(
    df: pd.DataFrame,
    *,
    row: int,
    filename: str,
    **kwargs
):
    """
    This task:
        - Uses row_map to translate ORIGINAL row → current index
        - Merges values from that row into the header
        - Drops the merged row
        - Updates row_map accordingly
        - Returns only cleaned_df

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
    # 1. VALIDATION – Hard Errors
    # -----------------------------------------------------

    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    if row is None:
        raise ValueError("A row number must be provided for merging.")

    if not filename:
        raise ValueError("filename must be provided to retrieve row_map.")

    if "row_map" not in st.session_state:
        raise ValueError("row_map not found in session_state.")

    if filename not in st.session_state.row_map:
        raise ValueError(f"No row_map found for file '{filename}'.")

    row_map = st.session_state.row_map[filename]

    if len(row_map) != len(df):
        raise ValueError(
            "row_map length does not match DataFrame length. "
            "This indicates an internal workflow error."
        )

    cleaned_df = df.copy()

    # -----------------------------------------------------
    # 2. CORE PROCESSING
    # -----------------------------------------------------

    # Convert ORIGINAL row number → current index
    try:
        idx = row_map.index(row)
    except ValueError:
        # Row not found → nothing to merge
        return cleaned_df

    # Merge selected row into header
    header = list(cleaned_df.columns.astype(str))
    vals = list(cleaned_df.iloc[idx])

    merged_header = [
        f"{h}_{v}" if pd.notna(v) and str(v).strip() != "" else h
        for h, v in zip(header, vals)
    ]

    # Drop the merged row
    cleaned_df = cleaned_df.drop(index=[idx]).reset_index(drop=True)

    # -----------------------------------------------------
    # 3. UPDATE ROW MAP (Streamlit mode)
    # -----------------------------------------------------
    new_row_map = [row_map[i] for i in range(len(row_map)) if i != idx]
    st.session_state.row_map[filename] = new_row_map

    # -----------------------------------------------------
    # 4. PURE PYTHON MODE (no Streamlit)
    # -----------------------------------------------------
    # If using this function outside Streamlit, you must maintain your own row_map.
    #
    # Example:
    #     # ORIGINAL row_map before merging
    #     row_map = list(range(1, len(df) + 1))
    #
    #     # Remove the merged row (idx is the CURRENT index)
    #     new_row_map = [row_map[i] for i in range(len(row_map)) if i != idx]
    #
    # The task itself does NOT depend on Streamlit; only the row_map update does.

    # Apply new header
    cleaned_df.columns = merged_header

    # -----------------------------------------------------
    # 5. RETURN
    # -----------------------------------------------------
    return cleaned_df
