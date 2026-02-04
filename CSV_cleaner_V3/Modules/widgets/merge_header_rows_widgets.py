import streamlit as st

def merge_header_rows_widget(df):
    """
    Widget for merging Units and VMV code rows into the header row.
    """
    st.markdown("""
    Some provincial chemistry files include extra rows containing:
    - Units (e.g., mg/L, µS/cm)
    - VMV codes (e.g., 864, 3533)

    This tool merges those rows into the header names so the file has a single clean header row.
    """)

    # Remove unnamed columns (common in CSV exports)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed", case=False)]

    # Show first few rows so user can identify header rows
    st.markdown("#### Preview of the first few rows")
    st.dataframe(df.head(5), use_container_width=True)

    row_options = [str(i) for i in range(min(5, len(df)))]

    st.markdown("#### Select rows containing metadata")
    c1, c2 = st.columns(2)

    vmv_row = c1.selectbox(
        "Row containing VMV codes",
        ["None"] + row_options,
        index=0
    )

    unit_row = c2.selectbox(
        "Row containing Units",
        ["None"] + row_options,
        index=0
    )

    # Convert to integers or None
    vmv_row = int(vmv_row) if vmv_row != "None" else None
    unit_row = int(unit_row) if unit_row != "None" else None

    st.markdown("---")
    apply_now = st.button("Merge Header Rows", type="primary")

    if apply_now:
        return {
            "vmv_row": vmv_row,
            "unit_row": unit_row
        }