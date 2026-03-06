import streamlit as st
import pandas as pd

def render_remove_columns_summary(summary):
    """
    Summary renderer for the 'remove_columns' task.

    Expected summary keys:
        - task_name: "remove_columns"
        - removed_columns: list of columns the user asked to remove
        - remaining_columns: list of columns still present
        - removed_count: int
        - remaining_count: int
    """

    st.success("Removed Columns")

    # Columns requested for removal
    removed = summary.get("removed_columns", [])
    if removed:
        st.write("**Columns requested for removal:** " + ", ".join(removed))
    else:
        st.write("**Columns requested for removal:** None")

    # Columns remaining
    remaining = summary.get("remaining_columns", [])
    if remaining:
        st.write("**Remaining columns:** " + ", ".join(remaining))

    # Counts
    st.write(f"**Number of columns removed:** {summary.get('removed_count', 0)}")
    st.write(f"**Number of columns remaining:** {summary.get('remaining_count', 0)}")
