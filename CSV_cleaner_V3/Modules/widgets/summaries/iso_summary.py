import streamlit as st
import pandas as pd

def render_iso_summary(summary):
    """
    Summary renderer for the 'iso' task.

    Expected summary keys:
        - task_name: "iso"
        - converted_rows: int
        - ambiguous_rows: list of (row_index, original_value)
        - unparsed_rows: list of (row_index, original_value)
        - new_column: str
        - ambiguous_mode: str
    """

    st.success("ISO 8601 Conversion")

    # New column created
    new_col = summary.get("new_column")
    if new_col:
        st.write(f"**New ISO column:** `{new_col}`")

    # Ambiguity handling mode
    mode = summary.get("ambiguous_mode")
    if mode:
        st.write(f"**Ambiguity handling:** {mode}")

    # Converted rows
    converted = summary.get("converted_rows", 0)
    st.write(f"**Successfully converted rows:** {converted}")

    # Ambiguous rows
    ambiguous = summary.get("ambiguous_rows", [])
    if ambiguous:
        st.warning(f"Ambiguous rows: {len(ambiguous)}")
        amb_df = pd.DataFrame(ambiguous, columns=["Row", "Value"])
        st.dataframe(amb_df, use_container_width=True)

    # Unparsed rows
    unparsed = summary.get("unparsed_rows", [])
    if unparsed:
        st.error(f"Unparsed rows: {len(unparsed)}")
        unp_df = pd.DataFrame(unparsed, columns=["Row", "Value"])
        st.dataframe(unp_df, use_container_width=True)
