import streamlit as st
import pandas as pd

def render_merge_date_time_summary(summary, filename=None):
    """
    Summary renderer for the 'merge_date_time' task.

    Expected summary keys:
        - task_name: "merge_date_time"
        - unparsed_dates: list of (row_index, original_value)
        - unparsed_times: list of (row_index, original_value)
        - errors: list of error messages
        - new_column: str
    """

    st.success("Date + Time Merge Completed")

    # New column created
    new_col = summary.get("new_column")
    if new_col:
        st.write(f"**New merged column:** `{new_col}`")

    # Structural or parsing errors
    errors = summary.get("errors", [])
    if errors:
        st.write("### Issues Encountered")
        for err in errors:
            st.error(err)

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
