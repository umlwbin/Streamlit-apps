import streamlit as st

from Modules import session_initializer, file_uploads, download, tasks, task_runner
from Modules.widgets import task_selector, preview, sidebar_intro
from Modules.widgets.toolbar import toolbar
import pandas as pd


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="CSV Curation Studio",
    page_icon="🔖",
    layout="wide"
)

# Tab styling
st.markdown("""
<style>
.stTabs button p {
    font-size: 1.0rem !important;
    font-weight: 500 !important;
}
.stTabs button {
    margin-right: 1rem !important;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# INITIALIZE SESSION
# ---------------------------------------------------------
session_initializer.init_session_state()


# ---------------------------------------------------------
# HELPER: Show combined metadata once after all files are processed
# ---------------------------------------------------------
def show_combined_metadata():
    """
    Build and display a single combined metadata table
    using metadata previews collected from all files.
    """

    all_metadata = []

    # Collect metadata from all summaries
    for fname, summ in st.session_state.all_summaries.items():
        if "metadata_preview" in summ and summ["metadata_preview"]:
            for row in summ["metadata_preview"]:
                row_with_file = row.copy()
                row_with_file["filename"] = fname
                all_metadata.append(row_with_file)

    # If no metadata exists, nothing to show
    if not all_metadata:
        return

    st.markdown("##### Combined Metadata Previews (all files)")
    combined_df = pd.DataFrame(all_metadata)
    st.dataframe(combined_df, use_container_width=True)

    # One download button for all metadata
    st.download_button(
        label="Download All Metadata Previews",
        data=combined_df.to_csv(index=False),
        file_name="all_metadata_previews.csv",
        mime="text/csv",
        key="download_all_metadata_once"
    )


# ---------------------------------------------------------
# MAIN CSV CURATION WORKFLOW
# ---------------------------------------------------------
def run_csv_curation_studio():

    st.markdown("## CSV Curation Studio")
    toolbar()

    tab1, tab2 = st.tabs(["Main App", "Live Data Preview"])

    # -----------------------------------------------------
    # TAB 1: MAIN APP
    # -----------------------------------------------------
    with tab1:
        uploaded_files = file_uploads.fileuploadfunc()

        # Only proceed if files are uploaded and stored
        if uploaded_files and st.session_state.current_data:

            st.markdown(" ")
            st.markdown("#### What would you like to do")

            # Determine whether we are in metadata-only mode
            non_rectangular = bool(st.session_state.get("non_rectangular_files"))

            if non_rectangular:
                st.info(
                    "One or more uploaded files are not rectangular. "
                    "Only the **Remove metadata rows** task is available until the table is cleaned."
                )
                allowed_tasks = ["Remove Metadata Rows"]
            else:
                allowed_tasks = tasks.get_all_task_names()

            # Task selection
            task = task_selector.what_to_do_widgets(allowed_tasks)

            if task and task != "Choose an option":
                st.markdown("")
                st.markdown("")

                with st.container(border=True):
                    st.markdown(f"### {task}")
                    task_inputs = tasks.get_task_inputs(task)

                    if task_inputs:
                        # Run the selected task on all files
                        task_runner.run_task(task, **task_inputs)

                # -------------------------------------------------
                # Show combined metadata once, after all summaries exist
                # -------------------------------------------------
                if st.session_state.task_applied:
                    show_combined_metadata()

        # -------------------------------------------------
        # DOWNLOAD SECTION
        # -------------------------------------------------
        if (
            uploaded_files
            and st.session_state.current_data
            and st.session_state.task_applied
        ):
            st.markdown("####")
            with st.container(border=True):
                st.markdown("#### Download Your Cleaned Data")
                st.caption("These files update automatically after each task.")
                download.download_output()
                download.excel_download()

    # -----------------------------------------------------
    # TAB 2: LIVE PREVIEW
    # -----------------------------------------------------
    with tab2:
        preview.show_live_preview()


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    sidebar_intro.sidebar()


# ---------------------------------------------------------
# RUN THE APP
# ---------------------------------------------------------
run_csv_curation_studio()
