import streamlit as st

def render_merge_header_rows_summary(summary, filename=None):
    st.markdown("##### Merge Header Rows - Summary")

    merged_row = summary.get("merged_row")

    if merged_row is not None:
        st.write(f"**Merged original row:** {merged_row}")

        # Preview index = original row - 1
        preview_index = merged_row - 1
        st.write(f"**Preview row index:** {preview_index}")

    else:
        st.write("**Merged original row:** None")

    warnings = summary.get("warnings", [])
    if warnings:
        st.warning("Warnings were generated during this task:")
        for w in warnings:
            st.write(f"- {w}")
    else:
        st.success("No warnings.")
