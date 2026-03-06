import streamlit as st
import pandas as pd

def render_merge_date_time_summary(summary):
    """
    Summary renderer for the 'merge_date_time' task.

    Expected summary keys:
        - task_name: "merge_date_time"
        - merged_rows: int
        - unparsed_dates: list of (row_index, original_value)
        - unparsed_times: list of (row_index, original_value)
        - new_column: str
    """

    st.success("Date + Time Merge")

    # New column created
    new_col = summary.get("new_column")
    if new_col:
        st.write(f"**New merged column:** `{new_col}`")

    # Successfully merged rows
    merged = summary.get("merged_rows", 0)
    st.write(f"**Successfully merged rows:** {merged}")

    # Unparsed dates
    unparsed_dates = summary.get("unparsed_dates", [])
    if unparsed_dates:
        st.error(f"Unparsed dates: {len(unparsed_dates)}")
        df_dates = pd.DataFrame(unparsed_dates, columns=["Row", "Value"])
        st.dataframe(df_dates, use_container_width=True)

    # Unparsed times
    unparsed_times = summary.get("unparsed_times", [])
    if unparsed_times:
        st.warning(f"Unparsed times: {len(unparsed_times)}")
        df_times = pd.DataFrame(unparsed_times, columns=["Row", "Value"])
        st.dataframe(df_times, use_container_width=True)
