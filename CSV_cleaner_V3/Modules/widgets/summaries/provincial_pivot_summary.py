import streamlit as st
import pandas as pd

def render_provincial_pivot_summary(summary, filename=None):
    """
    Summary renderer for the provincial_pivot task.
    """

    st.success("Provincial Chemistry Pivot")

    st.write(f"**Variables processed:** {summary.get('variables_processed', 0)}")

    variables = summary.get("variable_names", [])
    if variables:
        st.write("**Variable names:** " + ", ".join(variables))

    metadata = summary.get("metadata_used", [])
    if metadata:
        st.write("**Metadata merged into headers:** " + ", ".join(metadata))
    else:
        st.write("**Metadata merged into headers:** None")

    warnings = summary.get("warnings", [])
    if warnings:
        st.write("### Warnings")
        for msg in warnings:
            st.warning(msg)

    details = summary.get("details", [])
    if details:
        st.write("### Column creation details")
        df_details = pd.DataFrame(details)
        st.dataframe(df_details, use_container_width=True)
