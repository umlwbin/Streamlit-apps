import streamlit as st

def render_add_column_summary(summary, filename=None):
    """
    Summary renderer for the 'Add columns' task.
    Expected summary keys:
        - columns_added: list of new column names
        - insert_positions: list of 1-based insert positions
        - row_count: number of rows in the updated dataframe
    """

    st.success("Columns Added")

    added = summary.get("columns_added", [])
    positions = summary.get("insert_positions", [])
    row_count = summary.get("row_count")

    if added:
        st.write("**New columns created:** " + ", ".join(added))

        # Show positions if available
        if positions:
            pos_str = ", ".join(str(p) for p in positions)
            st.write(f"**Inserted at positions:** {pos_str}")

        if row_count is not None:
            st.write(f"**Rows in table:** {row_count}")

    else:
        st.info("No new columns were added.")
