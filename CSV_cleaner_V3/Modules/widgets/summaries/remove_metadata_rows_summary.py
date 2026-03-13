import streamlit as st
import pandas as pd

def render_remove_metadata_rows_summary(summary, filename=None):
    """
    Summary renderer for the remove_metadata_rows task.
    """

    st.success("Metadata Rows Removed")

    st.write("##### File Processed")
    st.write(f"**{filename}**")

    warnings = summary.get("warnings", [])
    if warnings:
        st.write("### Warnings")
        for msg in warnings:
            st.warning(msg)

    preview = summary.get("metadata_preview", [])
    if preview:
        st.write("##### Metadata Preview (first 10 rows)")
        st.dataframe(pd.DataFrame(preview), use_container_width=True)
    else:
        st.write("No metadata rows detected above the header.")
