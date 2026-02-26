import streamlit as st

def merge_header_rows_widget(df):
    """
    Merge one or two metadata rows into the header row. 
    This is useful for files where units, codes, or other descriptors are stored in separate rows above the actual header.    
    """

    st.markdown("""
        Some files include one or more metadata rows between the header and the actual data.
        These rows may contain units, codes, instrument identifiers, or other descriptors.

        This tool merges up to two such rows into the header so the file ends up with a single,
        clean header row.
        """)

    # Remove unnamed columns (common in CSV exports)
    df = df.copy()
    df.columns = df.columns.map(str)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed", case=False)]

    # Show first few rows so user can identify header rows
    st.markdown("#### Preview of the first few rows")
    st.dataframe(df.head(5), use_container_width=True)

    row_options = [str(i) for i in range(len(df))]

    st.markdown("#### Select metadata rows to merge (row numbers refer to the preview above)")
    c1, c2 = st.columns(2)

    row1 = c1.selectbox("First row to merge into header", ["None"] + row_options, index=0)
    row2 = c2.selectbox("Second row to merge into header (optional)", ["None"] + row_options, index=0)

    # Convert to integers or None
    row1 = int(row1) if row1 != "None" else None
    row2 = int(row2) if row2 != "None" else None

    st.markdown("---")
    apply_now = st.button("Merge Header Rows", type="primary")

    if apply_now:
        return {
            "row1": row1,
            "row2": row2
        }