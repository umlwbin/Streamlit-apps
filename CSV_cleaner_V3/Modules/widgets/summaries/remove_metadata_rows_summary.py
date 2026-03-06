import streamlit as st
import pandas as pd

def render_remove_metadata_rows_summary(summary):
    """
    Summary renderer for the remove_metadata_rows task.

    Expected summary keys:
        - task_name: "remove_metadata_rows"
        - metadata_preview: list of dicts (up to 10 rows)
    """

    st.success("Metadata Rows Removed")

    preview = summary.get("metadata_preview", [])

    if preview:
        st.write("Preview of removed metadata rows:")
        st.dataframe(pd.DataFrame(preview), use_container_width=True)
    else:
        st.write("No metadata rows were removed or no preview available.")
