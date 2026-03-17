import streamlit as st

def merge_header_rows_widget():
    """
    Widget for selecting a single metadata row to merge into the header.

    Notes
    -----
    - The preview uses *0-based* row numbers for simplicity.
    - The task function expects *1-based* original row numbers (to match row_map).
    - We convert 0-based → 1-based before returning.
    - Only the first file is previewed, but the selected row will be applied
      to *all* files when the task runner loops over them.

    Offline / non-Streamlit usage
    ------------------------------
    If running this task outside Streamlit, simply pass:

        {"row": <1-based row number>}

    directly to the task function.
    """

    # ---------------------------------------------------------
    # 1. Select the first file for preview only
    # ---------------------------------------------------------
    filenames = list(st.session_state.current_data.keys())
    if not filenames:
        st.warning("No files loaded.")
        return None

    preview_filename = filenames[0]
    df = st.session_state.current_data[preview_filename]

    # ---------------------------------------------------------
    # 2. Build a simple 0-based preview
    # ---------------------------------------------------------
    preview = df.copy()
    preview.insert(0, "row_index", range(len(df)))

    st.markdown("#### Table Preview")
    st.dataframe(preview.head(5), use_container_width=True)

    # ---------------------------------------------------------
    # 3. Row selection (0-based)
    # ---------------------------------------------------------
    st.markdown("#### Select the row to merge into the header")

    row_options = list(range(len(df)))  # 0-based
    selected_row_0_based = st.selectbox(
        "Row to merge (0-based index)",
        ["None"] + row_options
    )

    # Convert to int or None
    if selected_row_0_based == "None":
        selected_row_0_based = None

    # ---------------------------------------------------------
    # 4. Convert 0-based → 1-based for the task
    # ---------------------------------------------------------
    if selected_row_0_based is not None:
        selected_row_1_based = selected_row_0_based + 1
    else:
        selected_row_1_based = None

    # ---------------------------------------------------------
    # 5. Trigger
    # ---------------------------------------------------------
    if st.button("Merge Header Row", type="primary"):
        return {
            "row": selected_row_1_based
        }

    return None
