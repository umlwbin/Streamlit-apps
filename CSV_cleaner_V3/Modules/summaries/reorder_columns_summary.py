import streamlit as st
import pandas as pd

def render_reorder_columns_summary(summary, filename=None):
    """
    Summary renderer for the reorder_columns task.
    """

    st.success("Reordered Columns")

    warnings = summary.get("warnings", [])
    if warnings:
        st.write("### Warnings")
        for msg in warnings:
            st.warning(msg)

    requested = summary.get("requested_order", [])
    st.write("**Requested order:** " + (", ".join(requested) if requested else "None"))

    final_order = summary.get("final_order", [])
    if final_order:
        st.write("### Final Column Order")
        st.dataframe(pd.DataFrame({"Column Order": final_order}), use_container_width=True)

    missing = summary.get("missing_columns", [])
    if missing:
        st.warning("Some requested columns were not found: " + ", ".join(missing))

    changed = summary.get("changed", False)
    st.write(f"**Order changed:** {'Yes' if changed else 'No'}")
