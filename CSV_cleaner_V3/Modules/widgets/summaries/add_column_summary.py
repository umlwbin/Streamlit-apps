import streamlit as st

def render_add_column_summary(summary):
    """
    Summary renderer for the 'add_columns' task.
    Expected summary keys:
        - task_name: "add_columns"
        - columns_added: list of new column names
    """

    st.success("Columns Added")
    # Added columns
    added = summary.get("columns_added", [])
    if added:
        st.write("**New columns created:** " + ", ".join(added))
    else:
        st.info("No new columns were added.")
