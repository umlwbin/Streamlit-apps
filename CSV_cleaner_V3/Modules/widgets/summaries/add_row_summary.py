import streamlit as st

def render_add_row_summary(summary, filename=None):
    """
    Summary renderer for the 'Add row' task.
    Expected summary keys:
        - auto_headers: bool (optional)
        - as_header: bool (optional)
        - new_headers: list[str] (optional)
        - row_added: list[Any] or None
        - row_index: int (optional)
    """

    st.success("Add Row Completed")

    # -----------------------------------------------------
    # CASE 1 - Auto-generate alphabetical headers
    # -----------------------------------------------------
    if summary.get("auto_headers"):
        st.write("Alphabetical headers were generated:")
        st.write(", ".join(summary.get("new_headers", [])))
        return

    # -----------------------------------------------------
    # CASE 2 - Row promoted to header
    # -----------------------------------------------------
    if summary.get("as_header"):
        st.write("A new header row was created:")
        st.write(", ".join(summary.get("new_headers", [])))
        return

    # -----------------------------------------------------
    # CASE 3 - Normal row insertion
    # -----------------------------------------------------
    row = summary.get("row_added")
    if row is not None:
        st.write("New row added at the top of the table:")
        st.write(row)
    else:
        st.write("A new row was added.")
