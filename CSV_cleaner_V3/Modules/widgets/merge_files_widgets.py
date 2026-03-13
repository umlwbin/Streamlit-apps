import streamlit as st

def merge_widgets(df):
    """
    Widget for merging multiple uploaded files into one.

    Ensures:
        - at least two files exist
        - all files have matching column names
        - clear feedback for mismatches
        - one-shot trigger behavior

    Returns
    -------
    dict or None
        {
            "add_source": bool
        }
        or None if the user has not completed the widget.
    """

    st.markdown("#### You have multiple files, let's merge them!")

    # ---------------------------------------------------------
    # Retrieve uploaded files from session state
    # ---------------------------------------------------------
    files = st.session_state.current_data

    # Ignore previously merged files (they contain a 'source_file' column)
    files = {
        name: df
        for name, df in files.items()
        if "source_file" not in df.columns
    }

    # ---------------------------------------------------------
    # If only one file, nothing to merge
    # ---------------------------------------------------------
    if len(files) == 1:
        left, right = st.columns([0.8, 0.2])
        left.info("There is only one file uploaded, so no work for us 😌", icon="ℹ️")
        return None

    # ---------------------------------------------------------
    # Check column consistency across files
    # ---------------------------------------------------------
    all_columns = {name: list(df.columns) for name, df in files.items()}
    unique_column_sets = {tuple(cols) for cols in all_columns.values()}

    if len(unique_column_sets) > 1:
        st.error("⚠️ Column mismatch detected across files. They must have identical columns to merge.")

        with st.expander("View column differences", expanded=False):
            file_names = list(all_columns.keys())
            base_name = file_names[0]
            base_cols = set(all_columns[base_name])

            for name in file_names[1:]:
                cols = set(all_columns[name])

                missing_in_this = base_cols - cols
                extra_in_this = cols - base_cols

                st.markdown(f"###### Comparing **{name}** to **{base_name}**")

                if missing_in_this:
                    st.error(f"Columns missing in **{name}**:")
                    st.code(sorted(missing_in_this))

                if extra_in_this:
                    st.warning(f"Extra columns in **{name}**:")
                    st.code(sorted(extra_in_this))

                if not missing_in_this and not extra_in_this:
                    st.success(f"No differences found between {name} and {base_name}.")

        # Do not stop the app - just return None
        return None

    # ---------------------------------------------------------
    # Options
    # ---------------------------------------------------------
    add_source = st.checkbox("Add source filename column", value=True)

    # ---------------------------------------------------------
    # Trigger
    # ---------------------------------------------------------
    clicked = st.button("Merge Files", type="primary", key="merge_files_button")

    if clicked:
        return {"add_source": add_source}

    return None
