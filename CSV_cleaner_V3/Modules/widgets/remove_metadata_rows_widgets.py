import streamlit as st

def remove_metadata_rows_widget(df):
    """
    Widget for collecting user input for the remove_metadata_rows task.

    The user provides three identifiers that must appear in the true header row.
    These identifiers are used to detect where the real table begins.
    """

    st.write("Enter three column names that appear in the true header row.")
    st.write("These will be used to locate the first real row of the table.")

    col1, col2, col3 = st.columns(3)

    with col1:
        id1 = st.text_input("Header name 1", "")
    with col2:
        id2 = st.text_input("Header name 2", "")
    with col3:
        id3 = st.text_input("Header name 3", "")

    identifiers = [id1.strip(), id2.strip(), id3.strip()]

    # Basic validation: ensure all three identifiers are provided
    if any(x == "" for x in identifiers):
        st.info("Enter all three header names to enable this task.")
        return None

    return {
        "identifiers": identifiers
    }
