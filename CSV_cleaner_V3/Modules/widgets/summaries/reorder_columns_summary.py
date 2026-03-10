import streamlit as st
import pandas as pd

def render_reorder_columns_summary(summary, filename=None):
    """
    Summary renderer for the 'reorder_columns' task.

    Expected summary keys:
        - task_name: "reorder_columns"
        - requested_order: list of column names the user asked for
        - final_order: list of column names actually applied
        - missing_columns: list of requested columns not found
        - changed: bool indicating whether the order changed
    """

    st.success("Reordered Columns")

    # Requested order
    requested = summary.get("requested_order", [])
    if requested:
        st.write("**Requested order:** " + ", ".join(requested))
    else:
        st.write("**Requested order:** None")

    # Final applied order
    final_order = summary.get("final_order", [])
    if final_order:
        st.write("**Final column order:**")
        st.dataframe(pd.DataFrame({"Column Order": final_order}), use_container_width=True)

    # Missing columns
    missing = summary.get("missing_columns", [])
    if missing:
        st.warning("Some requested columns were not found: " + ", ".join(missing))

    # Whether anything changed
    changed = summary.get("changed", False)
    st.write(f"**Order changed:** {'Yes' if changed else 'No'}")
