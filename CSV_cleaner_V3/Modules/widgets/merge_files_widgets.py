import streamlit as st

def merge_widgets(df):
    """
    Widget for merging multiple uploaded files into one.
    Ensures:
      • at least two files exist
      • all files have matching column names
      • one‑shot trigger behavior
      • clear feedback for mismatches
    """

    st.markdown("#### You have multiple files — let's merge them!")

    files = st.session_state.current_data

    # If only one file, nothing to merge
    if len(files) == 1:
        left, right = st.columns([0.8, 0.2])
        left.info("There is only one file uploaded, so no work for us 😌", icon="ℹ️")
        return None

    # --- Check column consistency across files ---
    all_columns = {name: list(df.columns) for name, df in files.items()}
    unique_column_sets = {tuple(cols) for cols in all_columns.values()}

    if len(unique_column_sets) > 1:
        st.error("⚠️ Column mismatch detected across files. They must have identical columns to merge.")
        
        # Show mismatches in an expander
        with st.expander("View column differences", expanded=False):
            for name, cols in all_columns.items():
                st.write(f"**{name}**")
                st.code(cols)

        st.stop()

    add_source = st.checkbox("Add source filename column", value=True)
    clicked = st.button("Merge Files", type="primary", key="merge_files_button")
    if clicked:
        return {"add_source": add_source}

    return None
