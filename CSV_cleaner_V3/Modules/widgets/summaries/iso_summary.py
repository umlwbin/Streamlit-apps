import streamlit as st
import pandas as pd

def render_iso_summary(summary, filename=None):
    st.success("ISO 8601 Conversion Completed")

    new_col = summary.get("new_column")
    if new_col:
        st.write(f"**New ISO column:** `{new_col}`")

    mode = summary.get("ambiguous_mode")
    if mode:
        st.write(f"**Ambiguity handling:** {mode}")

    st.write(f"**Successfully converted rows:** {summary.get('converted_rows', 0)}")

    warnings = summary.get("warnings", [])
    if warnings:
        st.write("### Warnings")
        for msg in warnings:
            st.warning(msg)

    ambiguous = summary.get("ambiguous", [])
    if ambiguous:
        st.warning(f"Ambiguous rows: {len(ambiguous)}")
        amb_df = pd.DataFrame(ambiguous, columns=["Row", "Value"])
        st.dataframe(amb_df, use_container_width=True)

    unparsed = summary.get("unparsed", [])
    if unparsed:
        st.error(f"Unparsed rows: {len(unparsed)}")
        unp_df = pd.DataFrame(unparsed, columns=["Row", "Value"])
        st.dataframe(unp_df, use_container_width=True)
