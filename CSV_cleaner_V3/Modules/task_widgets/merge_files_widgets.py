import streamlit as st

def merge_widgets(df):
    """
    Widget for merging multiple uploaded files into one.

    Supports:
        - ensuring at least two files exist
        - detecting column mismatches
        - showing detailed differences
        - optional source-file tracking
        - execute-once trigger pattern

    Returns
    -------
    dict or None
        {
            "add_source": bool
        }
        or None until user confirms.
    """

    st.write("#### Merge Multiple Files")
    st.caption("Combine all uploaded files into a single dataset.")

    # ---------------------------------------------------------
    # Retrieve uploaded files from session state
    # ---------------------------------------------------------
    files = st.session_state.current_data

    # Ignore previously merged files (they contain a 'source_file' column)
    # This prevents accidental re-merging of already merged output.
    files = {
        name: df
        for name, df in files.items()
        if "source_file" not in df.columns
    }

    # ---------------------------------------------------------
    # If only one file, nothing to merge
    # ---------------------------------------------------------
    if len(files) <= 1:
        st.info("Only one file is available - nothing to merge.", icon="ℹ️")
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

                st.markdown(f"##### Comparing **{name}** to **{base_name}**")

                if missing_in_this:
                    st.error("Missing columns:")
                    st.code(sorted(missing_in_this))

                if extra_in_this:
                    st.warning("Extra columns:")
                    st.code(sorted(extra_in_this))

                if not missing_in_this and not extra_in_this:
                    st.success(f"No differences found between {name} and {base_name}.")

        # Do not proceed - user must fix mismatches first
        return None

    # ---------------------------------------------------------
    # Options
    # ---------------------------------------------------------
    st.write("#### Options")

    add_source = st.checkbox( "Add a 'source_file' column to track where each row came from",value=True )

    # ---------------------------------------------------------
    # Execute-once trigger button
    # ---------------------------------------------------------
    if st.button("Merge Files", type="primary"):
        st.session_state.merge_trigger = True

    triggered = st.session_state.get("merge_trigger", False)
    st.session_state.merge_trigger = False

    if not triggered:
        return None

    # ---------------------------------------------------------
    # SUCCESS ---> Return kwargs for merge_files task
    # ---------------------------------------------------------
    return {"add_source": add_source}
