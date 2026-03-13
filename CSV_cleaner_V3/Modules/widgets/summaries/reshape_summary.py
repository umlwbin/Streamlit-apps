import streamlit as st
import pandas as pd

def render_reshape_summary(summary, filename=None):
    """
    Summary renderer for the reshape task.
    """

    op = summary.get("operation")
    st.success(f"Reshape Operation: {op}")

    warnings = summary.get("warnings", [])
    if warnings:
        st.write("### Warnings")
        for msg in warnings:
            st.warning(msg)

    if op == "transpose":
        st.write("**Rows before:**", summary.get("rows_before"))
        st.write("**Columns before:**", summary.get("cols_before"))
        st.write("**Rows after:**", summary.get("rows_after"))
        st.write("**Columns after:**", summary.get("cols_after"))
        return

    if op == "wide_to_long":
        st.write("**Identifier columns:** " + ", ".join(summary.get("id_cols", [])))
        st.write("**Value columns unpivoted:** " + ", ".join(summary.get("value_cols", [])))
        st.write("**Rows before:**", summary.get("rows_before"))
        st.write("**Rows after:**", summary.get("rows_after"))
        return

    if op == "long_to_wide":
        st.write("**Variable column:**", summary.get("variable_col"))
        st.write("**Value column:**", summary.get("value_col"))
        st.write("**Identifier columns:** " + ", ".join(summary.get("id_cols", [])))
        st.write("**Rows before:**", summary.get("rows_before"))
        st.write("**Rows after:**", summary.get("rows_after"))
        return

    st.error("Unknown reshape operation.")
