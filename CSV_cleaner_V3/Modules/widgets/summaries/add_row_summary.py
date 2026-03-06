import streamlit as st

def render_add_row_summary(summary):
    """
    Summary renderer for the 'add_row' task.

    Expected summary keys:
        - task_name: "add_row"
        - as_header: bool
        - auto_headers: bool
        - new_header: list or dict (the constructed header row)
        - recovered_first_row: list or dict (the original first row)
    """

    st.success("Row Added")

    # Was the row added as a header?
    if summary.get("as_header"):
        st.write("**A new header row was created and inserted at the top of the table.**")

        if summary.get("auto_headers"):
            st.write("Header values were generated automatically.")

        new_header = summary.get("new_header")
        if new_header is not None:
            st.write("**New header values:**")
            st.write(new_header)

        recovered = summary.get("recovered_first_row")
        if recovered is not None:
            st.write("**Original first row (now moved down):**")
            st.write(recovered)

    else:
        st.write("**A new data row was inserted at the top of the table.**")

        inserted = summary.get("new_header")
        if inserted is not None:
            st.write("**Inserted row values:**")
            st.write(inserted)
