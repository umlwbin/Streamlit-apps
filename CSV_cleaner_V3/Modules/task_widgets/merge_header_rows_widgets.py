import streamlit as st
from Modules.utils.ui_utils import big_caption

def merge_header_rows_widget(df):
    """
    Widget for selecting a single metadata row to merge into the header.
    """

    big_caption("Merge a row into the current header row")

    # ---------------------------------------------------------
    # 1. Select the first file for preview only
    # ---------------------------------------------------------
    filenames = list(st.session_state.current_data.keys())
    if not filenames:
        st.warning("No files loaded.")
        return None

    preview_filename = filenames[0]
    preview_df = st.session_state.current_data[preview_filename]

    # ---------------------------------------------------------
    # 2. Build a simple 0-based preview
    # ---------------------------------------------------------
    preview = preview_df.copy()
    preview.insert(0, "row_index", range(len(preview_df)))

    st.markdown("#### Table Preview")
    st.dataframe(preview.head(5), use_container_width=True)

    if st.button("Reload Preview"):
        st.rerun()

    st.info("ℹ️ If you plan to merge another row, click **Reload Preview** first to update the table.")

    # ---------------------------------------------------------
    # 3. Row selection (0-based)
    # ---------------------------------------------------------
    st.markdown('')
    st.markdown("#### Select the row to merge into the header")

    row_options = list(range(len(preview_df)))  # 0-based
    selected_row_0_based = st.selectbox(
        "Row to merge (use 0-based index as shown in preview table)",
        ["None"] + row_options
    )

    if selected_row_0_based == "None":
        selected_row_0_based = None

    # Convert preview index ---> original row number using row_map
    if selected_row_0_based is not None:
        selected_row_1_based = st.session_state.row_map[preview_filename][selected_row_0_based]
    else:
        selected_row_1_based = None

    # ---------------------------------------------------------
    # 4. Trigger button!
    # ---------------------------------------------------------
    if st.button("Merge Header Row", type="primary"):
        st.session_state._merge_trigger = True
        return {"row": selected_row_1_based }

    return None
