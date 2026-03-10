import streamlit as st
import pandas as pd

def render_provincial_pivot_summary(summary, filename=None):
    """
    Summary renderer for the 'provincial_pivot' task.

    Expected summary keys:
        - task_name: "provincial_pivot"
        - variables_processed: int
        - variable_names: list of variable names
        - metadata_used: list of metadata column names merged into headers
        - details: list of dicts:
            {
                "variable": ...,
                "new_column_name": ...,
                "rows": ...
            }
    """

    st.success("Provincial Chemistry Pivot")

    # Number of variables processed
    count = summary.get("variables_processed", 0)
    st.write(f"**Variables processed:** {count}")

    # List of variable names
    variables = summary.get("variable_names", [])
    if variables:
        st.write("**Variable names:** " + ", ".join(variables))

    # Metadata columns used
    metadata = summary.get("metadata_used", [])
    if metadata:
        st.write("**Metadata merged into headers:** " + ", ".join(metadata))
    else:
        st.write("**Metadata merged into headers:** None")

    # Detailed breakdown
    details = summary.get("details", [])
    if details:
        st.write("**Column creation details:**")
        df_details = pd.DataFrame(details)
        st.dataframe(df_details, use_container_width=True)
