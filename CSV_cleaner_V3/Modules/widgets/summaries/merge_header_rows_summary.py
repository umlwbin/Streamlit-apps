import streamlit as st

def render_merge_header_rows_summary(summary, filename=None):
    """
    Summary renderer for the merge_header_rows task.

    Displays:
        - The original row number that was merged (1-based)
        - Any warnings generated during the task

    Internal details such as row_map are intentionally not shown.
    """

    st.markdown("### Merge Header Rows — Summary")

    # 1. Merged row
    merged_row = summary.get("merged_row")
    if merged_row is not None:
        st.write(f"**Merged original row:** {merged_row}")
    else:
        st.write("**Merged original row:** None")

    # 2. Warnings
    warnings = summary.get("warnings", [])
    if warnings:
        st.warning("Warnings were generated during this task:")
        for w in warnings:
            st.write(f"- {w}")
    else:
        st.success("No warnings.")
