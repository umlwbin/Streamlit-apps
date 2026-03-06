import streamlit as st
import pandas as pd

def render_reshape_summary(summary):
    """
    Summary renderer for the 'reshape' task.

    Expected summary keys vary by operation:

    For transpose:
        - operation: "transpose"
        - rows_before, cols_before
        - rows_after, cols_after

    For wide_to_long:
        - operation: "wide_to_long"
        - id_cols
        - value_cols
        - rows_before
        - rows_after

    For long_to_wide:
        - operation: "long_to_wide"
        - variable_col
        - value_col
        - id_cols
        - rows_before
        - rows_after
    """

    op = summary.get("operation")

    st.success(f"Reshape Operation: {op}")

    # ---------------------------------------------------------
    # TRANSPOSE
    # ---------------------------------------------------------
    if op == "transpose":
        st.write("**Rows before:**", summary.get("rows_before"))
        st.write("**Columns before:**", summary.get("cols_before"))
        st.write("**Rows after:**", summary.get("rows_after"))
        st.write("**Columns after:**", summary.get("cols_after"))
        return

    # ---------------------------------------------------------
    # WIDE → LONG
    # ---------------------------------------------------------
    if op == "wide_to_long":
        id_cols = summary.get("id_cols", [])
        value_cols = summary.get("value_cols", [])

        st.write("**Identifier columns:** " + ", ".join(id_cols))
        st.write("**Value columns unpivoted:** " + ", ".join(value_cols))
        st.write("**Rows before:**", summary.get("rows_before"))
        st.write("**Rows after:**", summary.get("rows_after"))
        return

    # ---------------------------------------------------------
    # LONG → WIDE
    # ---------------------------------------------------------
    if op == "long_to_wide":
        st.write("**Variable column:**", summary.get("variable_col"))
        st.write("**Value column:**", summary.get("value_col"))

        id_cols = summary.get("id_cols", [])
        st.write("**Identifier columns:** " + ", ".join(id_cols))

        st.write("**Rows before:**", summary.get("rows_before"))
        st.write("**Rows after:**", summary.get("rows_after"))
        return

    # ---------------------------------------------------------
    # Unknown operation (should not happen)
    # ---------------------------------------------------------
    st.error("Unknown reshape operation.")
