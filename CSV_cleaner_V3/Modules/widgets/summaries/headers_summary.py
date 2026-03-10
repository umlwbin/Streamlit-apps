import streamlit as st

def render_clean_headers_summary(summary):
    """
    Summary renderer for the 'clean_headers' task.

    Expected summary keys:
        - task_name: "clean_headers"
        - changed: dict of {old_name: new_name}
        - unchanged: list of column names
        - errors: list of error messages
        - header_metadata: dict of metadata per original header
    """

    st.success("Header Cleaning Completed")

    # Changed headers
    if summary.get("changed"):
        st.write("### Updated Column Names")
        for old, new in summary["changed"].items():
            st.write(f"- **{old}** → {new}")
    else:
        st.write("No column names were changed.")

    # Unchanged headers
    if summary.get("unchanged"):
        st.write("### Unchanged Columns")
        st.write(", ".join(summary["unchanged"]))

    # Errors
    if summary.get("errors"):
        st.write("### Issues Encountered")
        for err in summary["errors"]:
            st.error(err)

    # Metadata table (optional but helpful)
    if summary.get("header_metadata"):
        st.write("### Extracted Metadata")
        st.dataframe(summary["header_metadata"])
