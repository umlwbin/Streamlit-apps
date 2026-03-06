import streamlit as st

def render_merge_files_summary(summary):
    """
    Summary renderer for the 'merge_files' task.

    Expected summary keys:
        - task_name: "merge_files"
        - merged_files: list of filenames
        - added_source_column: bool
    """

    st.success("Merged Files")

    # List of merged files
    merged = summary.get("merged_files", [])
    if merged:
        st.write("**Files merged:**")
        for f in merged:
            st.write(f"• {f}")
    else:
        st.info("No files were merged.")

    # Whether a source column was added
    if summary.get("added_source_column"):
        st.write("**Source column added:** `source_file`")
    else:
        st.write("**Source column added:** No")
