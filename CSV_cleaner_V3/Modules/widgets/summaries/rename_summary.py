import streamlit as st
import pandas as pd

def render_rename_summary(summary, filename=None):
    """
    Summary renderer for the 'rename' task.

    Expected summary keys:
        - task_name: "rename"
        - renamed: bool
        - old_names: list of original column names
        - new_names: list of new column names
        - changed_count: int
    """

    # If renaming failed (column count mismatch), the task returns {"renamed": False}
    if not summary.get("renamed", False):
        st.error("Columns were not renamed due to a column count mismatch.")
        return

    st.success("Renamed Columns")

    old_names = summary.get("old_names", [])
    new_names = summary.get("new_names", [])
    changed = summary.get("changed_count", 0)

    # Show old vs new names in a table
    if old_names and new_names:
        st.write("**Updated column names:**")
        df = pd.DataFrame({
            "Old Name": old_names,
            "New Name": new_names
        })
        st.dataframe(df, use_container_width=True)

    # Count of changed names
    st.write(f"**Number of columns renamed:** {changed}")
