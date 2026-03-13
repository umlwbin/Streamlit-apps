import streamlit as st

def render_merge_files_summary(summary, filename=None):
    st.success("Merged Files")

    merged = summary.get("merged_files", [])
    if merged:
        st.write("**Files merged:**")
        for f in merged:
            st.write(f"• {f}")
    else:
        st.info("No files were merged.")

    if summary.get("added_source_column"):
        st.write("**Source column added:** `source_file`")
    else:
        st.write("**Source column added:** No")

    warnings = summary.get("warnings", [])
    if warnings:
        st.write("### Warnings")
        for msg in warnings:
            st.warning(msg)
