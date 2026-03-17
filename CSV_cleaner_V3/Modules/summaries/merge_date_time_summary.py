import streamlit as st
import pandas as pd

def render_merge_date_time_summary(summary, filename=None):
    st.success("Date + Time Merge Completed")

    new_col = summary.get("new_column")
    if new_col:
        st.write(f"**New merged column:** `{new_col}`")

    warnings = summary.get("warnings", [])
    if warnings:
        st.write("### Warnings")
        for msg in warnings:
            st.warning(msg)

    unparsed_dates = summary.get("unparsed_dates", [])
    if unparsed_dates:
        st.error(f"Unparsed dates: {len(unparsed_dates)}")
        df_dates = pd.DataFrame(unparsed_dates, columns=["Row", "Value"])
        st.dataframe(df_dates, use_container_width=True)

    unparsed_times = summary.get("unparsed_times", [])
    if unparsed_times:
        st.warning(f"Unparsed times: {len(unparsed_times)}")
        df_times = pd.DataFrame(unparsed_times, columns=["Row", "Value"])
        st.dataframe(df_times, use_container_width=True)
