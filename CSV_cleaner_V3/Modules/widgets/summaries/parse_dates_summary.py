import streamlit as st
import pandas as pd

def render_parse_dates_summary(summary):
    """
    Summary renderer for the 'parse_dates' task.

    Expected summary keys:
        - task_name: "parse_dates"
        - parsed_rows: int
        - unparsed_rows: list of (row_index, original_value)
        - new_columns: list of column names created
    """

    st.success("Parsed Datetime Column")

    # Successfully parsed rows
    parsed = summary.get("parsed_rows", 0)
    st.write(f"**Successfully parsed rows:** {parsed}")

    # New columns created
    new_cols = summary.get("new_columns", [])
    if new_cols:
        st.write("**New columns created:** " + ", ".join(new_cols))

    # Unparsed rows
    unparsed = summary.get("unparsed_rows", [])
    if unparsed:
        st.error(f"Unparsed rows: {len(unparsed)}")
        df_unparsed = pd.DataFrame(unparsed, columns=["Row", "Value"])
        st.dataframe(df_unparsed, use_container_width=True)
