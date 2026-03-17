import streamlit as st

def render_merge_header_rows_summary(summary, filename=None):
    st.markdown("##### Merge Header Rows - Summary")

    merged_row = summary.get("merged_row")
    preview_index = summary.get("preview_index")

    if merged_row is not None:
        if preview_index is not None:
            st.write(f"**Preview row index:** {preview_index}")
        else:
            st.write("**Preview row index:** Not available")
    else:
        st.write("**Merged original row:** None")

    warnings = summary.get("warnings", [])
    if warnings:
        st.warning("Warnings were generated during this task:")
        for w in warnings:
            st.write(f"- {w}")
    else:
        st.success("No warnings.")

