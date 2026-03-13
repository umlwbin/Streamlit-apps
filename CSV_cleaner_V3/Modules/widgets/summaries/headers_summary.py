import streamlit as st
import pandas as pd

def render_clean_headers_summary(summary, filename=None):
    st.success("Header Cleaning Completed")

    changed = summary.get("changed", {})
    if changed:
        st.write("##### Updated Column Names")
        for old, new in changed.items():
            st.write(f"- **{old}** → {new}")
    else:
        st.write("No column names were changed.")

    unchanged = summary.get("unchanged", [])
    if unchanged:
        st.write("##### Unchanged Columns")
        st.write(", ".join(unchanged))

    warnings = summary.get("warnings", [])
    if warnings:
        st.write("##### Warnings")
        for msg in warnings:
            st.warning(msg)

    metadata = summary.get("header_metadata")
    if metadata:
        st.write("##### Variable Transformation Table")
        meta_df = pd.DataFrame(metadata).transpose()
        meta_df = meta_df.reset_index().rename(columns={"index": "original_header"})
        st.dataframe(meta_df, use_container_width=True)
