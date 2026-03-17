import streamlit as st

from Modules.state import session_initializer
from Modules.state.undo_redo import restart_app
from Modules.upload import file_uploads
from ui_components import download, sidebar_intro, preview
from Modules.task_orchestration import tasks, task_runner, task_selector
from ui_components.toolbar import toolbar



import pandas as pd

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="CSV Curation Studio",
    page_icon="🔖",
    layout="wide"
)

# ---------------------------------------------------------
# TAB STYLING (moved into a helper for clarity)
# ---------------------------------------------------------
def apply_tab_styling():
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

apply_tab_styling()


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

    for fname, summ in st.session_state.all_summaries.items():
        if "metadata_preview" in summ and summ["metadata_preview"]:
            for row in summ["metadata_preview"]:
                row_with_file = row.copy()
                row_with_file["filename"] = fname
                all_metadata.append(row_with_file)

    if not all_metadata:
        return

    st.markdown("##### Combined Metadata Previews (all files)")
    combined_df = pd.DataFrame(all_metadata)
    st.dataframe(combined_df, use_container_width=True)

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
    """
    Main entry point for the CSV Curation Studio UI.

    Responsibilities:
        • Handle file uploads
        • Determine allowed tasks based on file structure
        • Collect task inputs via widgets
        • Run tasks on all uploaded files
        • Display combined metadata previews
        • Provide download options
        • Show live preview in a separate tab

    This function orchestrates the entire workflow but delegates
    all logic to specialized modules (widgets, tasks, runner, etc.).
    """

    st.markdown("## CSV Curation Studio")
    toolbar()

    tab1, tab2 = st.tabs(["Main App", "Live Data Preview"])

    # -----------------------------------------------------
    # TAB 1: MAIN APP
    # -----------------------------------------------------
    with tab1:
        uploaded_files = file_uploads.fileuploadfunc()

        if uploaded_files and st.session_state.current_data:

            st.markdown(" ")
            st.markdown("#### What would you like to do")

            # Determine whether we are in metadata-only mode
            non_rectangular = bool(st.session_state.get("non_rectangular_files"))

            if non_rectangular:
                st.info(
                    "One or more uploaded files are not rectangular. "
                    "Only the **Remove Metadata Rows** task is available until the table is cleaned."
                )
                allowed_tasks = ["Remove Metadata Rows"]
            else:
                allowed_tasks = tasks.get_all_task_names()

            # Task selection
            selected_task = task_selector.what_to_do_widgets(allowed_tasks)

            if selected_task and selected_task != "Choose an option":
                st.markdown("")
                st.markdown("")

                with st.container(border=True):
                    st.markdown(f"### {selected_task}")

                    # Collect kwargs from the widget for this task
                    task_inputs = tasks.get_task_inputs(selected_task)

                    # Only run if widget returned something meaningful
                    if task_inputs is not None:
                        task_runner.run_task(selected_task, **task_inputs)

                # Show combined metadata after tasks run
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


        # ---------------------------------------------------------
        # RESTART BUTTON
        # ---------------------------------------------------------
        st.markdown("---")
        if st.button("🔄 Restart Application", type="secondary"):
            restart_app()
            st.rerun()



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
