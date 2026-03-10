import streamlit as st

def merge_header_rows_widget(df):
    """
    Widget for selecting one or two metadata rows (e.g., units, VMV codes)
    to merge into the header row. This helps clean files where important
    descriptors are stored above the actual header.
    """

    st.markdown("""
        This tool merges up to two rows into the header row.  
        Use it when units, codes, or other descriptors appear above the actual column names.
    """)

    # ---------------------------------------------------------
    # Clean up the DataFrame for preview
    # ---------------------------------------------------------
    df = df.copy()

    # Convert all column names to strings (prevents errors with numeric headers)
    df.columns = df.columns.map(str)

    # Remove "Unnamed" columns (common in messy CSV exports)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed", case=False)]

    # ---------------------------------------------------------
    # Show a preview so the user can identify which rows to merge
    # ---------------------------------------------------------
    st.markdown("#### Preview of the first few rows")
    st.dataframe(df.head(5), use_container_width=True)

    # Build a list of row indices as strings for the dropdowns
    row_options = [str(i) for i in range(len(df))]

    st.markdown("#### Select metadata rows to merge (row numbers refer to the preview above)")
    c1, c2 = st.columns(2)

    # First metadata row (required or optional)
    row1 = c1.selectbox(
        "First row to merge into header",
        ["None"] + row_options,
        index=0
    )

    # Second metadata row (optional)
    row2 = c2.selectbox(
        "Second row to merge into header (optional)",
        ["None"] + row_options,
        index=0
    )

    # Convert dropdown values to integers or None
    row1 = int(row1) if row1 != "None" else None
    row2 = int(row2) if row2 != "None" else None

    st.markdown("---")

    # ---------------------------------------------------------
    # One-shot trigger: only run once when the user clicks the button
    # ---------------------------------------------------------
    apply_now = st.button("Merge Header Rows", type="primary")

    if apply_now:
        # Return the selected rows to the task runner
        return {
            "row1": row1,
            "row2": row2
        }

    # If the button wasn't pressed, do nothing yet
    return None
