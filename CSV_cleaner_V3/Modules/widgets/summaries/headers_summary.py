import streamlit as st
import pandas as pd

def render_clean_headers_summary(summary, filename=None):
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
        st.write("##### Updated Column Names")
        for old, new in summary["changed"].items():
            st.write(f"- **{old}** → {new}")
    else:
        st.write("No column names were changed.")

    # Unchanged headers
    if summary.get("unchanged"):
        st.write("##### Unchanged Columns")
        st.write(", ".join(summary["unchanged"]))

    # Errors
    if summary.get("errors"):
        st.write("##### Issues Encountered")
        for err in summary["errors"]:
            st.error(err)

    # Metadata table (optional but helpful)
    if summary.get("header_metadata"):
        st.write("##### Variable Transformation Table")

        # Convert to DataFrame
        meta_df = pd.DataFrame(summary["header_metadata"])

        # Transpose for readability
        meta_df = meta_df.transpose()

        # Optional: reset index so the row labels become a column
        meta_df = meta_df.reset_index().rename(columns={"index": "field"})

        st.dataframe(meta_df, use_container_width=True)

