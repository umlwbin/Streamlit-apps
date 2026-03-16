import streamlit as st

def merge_header_rows_widget(df):
    """
    Widget for selecting metadata rows (from the original file) to merge into the header.

    Returns
    -------
    dict or None
        {
            "filename": str,
            "row_map": list[int],
            "row1": int or None,
            "row2": int or None
        }
        or None if the user has not completed the widget.
    """

    st.markdown("""
        This tool merges up to two rows into the header row.  
        Row numbers refer to the **original file**, not the preview index.
    """)

    # ---------------------------------------------------------
    # Retrieve filename + row_map
    # ---------------------------------------------------------
    filenames = list(st.session_state.current_data.keys())
    filename = filenames[0]  # Only one file active at a time
    row_map = st.session_state.row_map[filename]

    # ---------------------------------------------------------
    # Preview with ORIGINAL row numbers
    # ---------------------------------------------------------
    preview = df.copy()
    preview.insert(0, "original_row", row_map)

    st.markdown("##### Preview (showing original row numbers in the first column)")
    st.dataframe(preview.head(5), use_container_width=True)

    # ---------------------------------------------------------
    # Build dropdown options from ORIGINAL row numbers
    # ---------------------------------------------------------
    row_options = [str(orig) for orig in row_map]

    st.markdown("##### Select metadata rows to merge (use original row numbers)")
    c1, c2 = st.columns(2)

    row1 = c1.selectbox("First row to merge", ["None"] + row_options)
    row2 = c2.selectbox("Second row to merge (optional)", ["None"] + row_options)

    row1 = int(row1) if row1 != "None" else None
    row2 = int(row2) if row2 != "None" else None

    st.markdown("---")

    # ---------------------------------------------------------
    # Trigger
    # ---------------------------------------------------------
    if st.button("Merge Header Rows", type="primary"):
        return {
            "filename": filename,
            "row_map": row_map,   # <-- REQUIRED for the task
            "row1": row1,
            "row2": row2
        }

    return None
