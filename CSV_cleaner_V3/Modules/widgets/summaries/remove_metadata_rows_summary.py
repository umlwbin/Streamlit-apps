import streamlit as st
import pandas as pd

def render_remove_metadata_rows_summary(summary, filename):
    """
    Summary renderer for the 'remove_metadata_rows' task.

    Behavior:
        • If multiple files exist, show ONE combined metadata table at the top
        • Then show the metadata preview for THIS file only
        • Avoid repeating the combined table for every file
    """

    # ---------------------------------------------------------
    # Metadata preview for file
    # ---------------------------------------------------------
    st.success("Metadata Rows Removed")
    st.write("##### File Processed")
    st.write(f"**{filename}**")

    preview = summary.get("metadata_preview", [])

    if preview:
        st.write("##### Metadata Preview (first 10 rows)")
        st.dataframe(pd.DataFrame(preview), use_container_width=True)
    else:
        st.write("No metadata rows detected above the header.")
