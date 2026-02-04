import streamlit as st

from Modules import session_initializer, file_uploads, download, tasks, task_runner
from Modules.widgets import task_selector, preview, sidebar_intro
from Modules.widgets.toolbar import toolbar


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="CSV Curation Studio",
    page_icon="📖",
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
# MAIN CSV CURATION WORKFLOW
# ---------------------------------------------------------
def run_csv_curation_studio():

    st.markdown("## 🛠️ CSV Curation Studio")
    toolbar()

    tab1, tab2 = st.tabs(["🧰 Main App", "👀 Live Data Preview"])

    # -----------------------------
    # TAB 1 — MAIN APP
    # -----------------------------
    with tab1:
        uploaded_files = file_uploads.fileuploadfunc()

        if uploaded_files and st.session_state.current_data:
            st.markdown(" ")
            st.markdown("#### What would you like to do? 🤔")

            task = task_selector.what_to_do_widgets()

            if task and task != "Choose an option":
                st.markdown("")
                st.markdown("")

                with st.container(border=True):
                    st.markdown(f"#### {task}")
                    task_inputs = tasks.get_task_inputs(task)

                    if task_inputs:
                        task_runner.run_task(task, **task_inputs)

        # Download section
        if (
            uploaded_files
            and st.session_state.current_data
            and st.session_state.task_applied
        ):
            st.markdown("####")
            with st.container(border=True):
                st.markdown("#### 📦 Download Your Cleaned Data")
                st.caption("These files update automatically after each task.")
                download.download_output()
                download.excel_download()

    # -----------------------------
    # TAB 2 — LIVE PREVIEW
    # -----------------------------
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
