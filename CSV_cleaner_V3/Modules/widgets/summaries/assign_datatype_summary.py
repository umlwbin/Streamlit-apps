import streamlit as st

def render_assign_datatype_summary(summary):
    """
    Summary renderer for the 'assign_datatype' task.

    Expected summary keys:
        - task_name: "assign_datatype"
        - converted: list of (column, dtype)
        - errors: list of error messages
    """

    st.success("Assign Data Types Completed")

    # Show successful conversions
    converted = summary.get("converted", [])
    if converted:
        st.write("### Converted Columns")
        for col, dtype in converted:
            st.write(f"- **{col}** → {dtype}")
    else:
        st.write("No columns were converted.")

    # Show errors, if any
    errors = summary.get("errors", [])
    if errors:
        st.write("### Issues Encountered")
        for err in errors:
            st.error(err)
