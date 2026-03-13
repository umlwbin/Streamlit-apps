import streamlit as st
import pandas as pd

def render_split_column_summary(summary, filename=None):
    """
    Summary renderer for the split_column task.
    """

    st.success("Split Column")

    warnings = summary.get("warnings", [])
    if warnings:
        st.write("### Warnings")
        for msg in warnings:
            st.warning(msg)

    col = summary.get("column")
    new_cols = summary.get("new_columns", [])
    delims = summary.get("delimiters", [])
    rows = summary.get("rows_split", 0)

    st.write(f"**Column:** {col}")
    st.write(f"**Delimiters:** {', '.join(delims)}")
    st.write(f"**Rows split:** {rows}")

    if new_cols:
        st.write("**New columns created:** " + ", ".join(new_cols))
    else:
        st.info("No new columns were created.")
