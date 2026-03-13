import streamlit as st

def render_assign_datatype_summary(summary, filename=None):
    st.success("Assign Data Types Completed")

    converted = summary.get("converted", [])
    if converted:
        st.write("### Converted Columns")
        for col, dtype in converted:
            st.write(f"- **{col}** → {dtype}")
    else:
        st.info("No columns were successfully converted.")

    warnings = summary.get("warnings", [])
    if warnings:
        st.write("### Warnings")
        for msg in warnings:
            st.warning(msg)
