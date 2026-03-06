import streamlit as st
import pandas as pd

def render_assign_datatype_summary(summary):
    """
    Summary renderer for the 'assign_datatype' task.

    Expected summary keys:
        - task_name: "assign_datatype"
        - converted: list of (column, dtype)
        - failed: dict of {column: error_message}
        - skipped: list of columns not found
    """

    st.success("Data Type Assignment")

    # Successful conversions
    converted = summary.get("converted", [])
    if converted:
        st.write("**Converted columns:**")
        df = pd.DataFrame(converted, columns=["Column", "Assigned Type"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No columns were successfully converted.")

    # Failed conversions
    failed = summary.get("failed", {})
    if failed:
        st.error("Failed conversions:")
        fail_df = pd.DataFrame(
            [(col, msg) for col, msg in failed.items()],
            columns=["Column", "Error"]
        )
        st.dataframe(fail_df, use_container_width=True)

    # Skipped columns
    skipped = summary.get("skipped", [])
    if skipped:
        st.warning("Skipped columns (not found in the dataset):")
        st.write(", ".join(skipped))
