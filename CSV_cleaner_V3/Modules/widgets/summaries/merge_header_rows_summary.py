import streamlit as st

def render_merge_header_rows_summary(summary):
    """
    Summary renderer for the 'merge_header_rows' task.

    Expected summary keys:
        - task_name: "merge_header_rows"
        - first_merged_row: int or None
        - second_merged_row: int or None
    """

    st.success("Merged Header Rows")

    vmv = summary.get("first_merged_row")
    units = summary.get("second_merged_row")

    # VMV row
    if vmv is not None:
        st.write(f"**First row merged:** Row {vmv}")
    else:
        st.write("**First row not merged**")

    # Units row
    if units is not None:
        st.write(f"**Second row merged:** Row {units}")
    else:
        st.write("**Second row not merged**")

