import streamlit as st
import pandas as pd

def render_merge_header_rows_summary(summary, filename=None):
    """
    Summary renderer for the 'merge_header_rows' task.

    Expected summary keys:
        - task_name: "merge_header_rows"
        - first_merged_row: int or None
        - second_merged_row: int or None
        - errors: list of error messages
    """

    st.success("Header Row Merge Completed")

    # Rows merged
    vmv = summary.get("first_merged_row")
    units = summary.get("second_merged_row")

    st.write("### Rows Merged")

    if vmv is not None:
        st.write(f"- **First merged row:** {vmv}")
    else:
        st.write("- **First merged row:** None")

    if units is not None:
        st.write(f"- **Second merged row:** {units}")
    else:
        st.write("- **Second merged row:** None")

    # Errors
    errors = summary.get("errors", [])
    if errors:
        st.write("### Issues Encountered")
        for err in errors:
            st.error(err)
