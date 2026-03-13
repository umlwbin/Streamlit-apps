import streamlit as st
import pandas as pd

def render_parse_dates_summary(summary, filename=None):
    """
    Summary renderer for the parse_dates task.
    """

    st.success("Parsed Datetime Column")

    st.write(f"**Successfully parsed rows:** {summary.get('parsed_rows', 0)}")

    new_cols = summary.get("new_columns", [])
    if new_cols:
        st.write("**New columns created:** " + ", ".join(new_cols))

    warnings = summary.get("warnings", [])
    if warnings:
        st.write("### Warnings")
        for msg in warnings:
            st.warning(msg)

    unparsed = summary.get("unparsed_rows", [])
    if unparsed:
        st.error(f"Unparsed rows: {len(unparsed)}")
        df_unparsed = pd.DataFrame(unparsed, columns=["Row", "Value"])
        st.dataframe(df_unparsed, use_container_width=True)
