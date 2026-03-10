import streamlit as st

def render_add_row_summary(summary):
    """
    Summary renderer for the 'add_row' task.

    Expected summary keys:
        - task_name: "add_row"
        - row_added: list or None
        - as_header: bool
    """

    st.success("Add Row Completed")

    # If the row became the header
    if summary.get("as_header"):
        st.write("A new header row was created.")
        return

    # Otherwise, a normal row was added
    row = summary.get("row_added")
    if row is not None:
        st.write("New row added:")
        st.write(row)
    else:
        st.write("A new row was added.")
