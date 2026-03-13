import streamlit as st
import pandas as pd

def render_merge_header_rows_summary(summary, filename=None):
    """
    Summary renderer for the merge_header_rows task.
    """

    st.success("Header Row Merge Completed")

    st.write("### Rows Merged")

    row1 = summary.get("first_merged_row")
    row2 = summary.get("second_merged_row")

    st.write(f"- **First merged row:** {row1 if row1 is not None else 'None'}")
    st.write(f"- **Second merged row:** {row2 if row2 is not None else 'None'}")

    warnings = summary.get("warnings", [])
    if warnings:
        st.write("### Warnings")
        for msg in warnings:
            st.warning(msg)
