import streamlit as st
import pandas as pd

def render_rename_summary(summary, filename=None):
    """
    Summary renderer for the rename_columns task.
    """

    if not summary.get("renamed", False):
        st.error("Columns were not renamed due to a column count mismatch.")
        warnings = summary.get("warnings", [])
        for msg in warnings:
            st.warning(msg)
        return

    st.success("Renamed Columns")

    warnings = summary.get("warnings", [])
    if warnings:
        st.write("### Warnings")
        for msg in warnings:
            st.warning(msg)

    old_names = summary.get("old_names", [])
    new_names = summary.get("new_names", [])
    changed = summary.get("changed_count", 0)

    if old_names and new_names:
        st.write("### Updated Column Names")
        df = pd.DataFrame({"Old Name": old_names, "New Name": new_names})
        st.dataframe(df, use_container_width=True)

    st.write(f"**Number of columns renamed:** {changed}")
