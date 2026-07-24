import streamlit as st
import pandas as pd

from Modules.state import session_initializer
from Modules.state.undo_redo import restart_app
from Modules.upload import file_uploads
from ui_components import download, sidebar_intro, preview
from ui_components.toolbar import toolbar
from Modules.utils.ui_utils import big_caption

from Modules.task_orchestration.tasks import TASKS
from Modules.task_orchestration.widgets import WIDGETS
from Modules.task_orchestration.allowed_tasks import get_allowed_tasks


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="CSV Curation Studio",
    page_icon="🔖",
    layout="wide"
)

# ---------------------------------------------------------
# INITIALIZE SESSION
# ---------------------------------------------------------
session_initializer.init_session_state()


# ---------------------------------------------------------
# Increase the size of widget labels
# ---------------------------------------------------------
st.html("""
<style>
    /* 1. Standard inputs and selectbox labels */
    div[data-testid="stTextInput"] label p,
    div[data-testid="stSelectbox"] label p,

    /* 2. Radio group header labels */
    div[data-testid="stRadio"] [data-testid="stWidgetLabel"] p,

    /* 3. Markdown text */
    div[data-testid="stMarkdownContainer"] p,

    /* 4. Caption text */
    div[data-testid="stCaptionContainer"] p {
        font-size: 18px !important;
    }
</style>
""")


# ---------------------------------------------------------
# TAB STYLING
# ---------------------------------------------------------
def apply_tab_styling():
    st.markdown("""
    <style>
    .stTabs button p {
        font-size: 1.2rem !important;
        font-weight: 500 !important;
    }
    .stTabs button {
        margin-right: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

apply_tab_styling()

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

        # -------------------------------------------------
        # ⏫ Upload Files + Metadata detection
        # -------------------------------------------------
        uploaded_files = file_uploads.fileuploadfunc()

        # Detect an upload event (file list has changed)
        if uploaded_files != st.session_state.last_uploaded_files:
            # Reset all metadata + supplementary outputs
            st.session_state.metadata_outputs = {}
            st.session_state.supplementary_outputs = {}

            # Reset widget triggers
            session_initializer.reset_widget_flags()

            # Track the new file list
            st.session_state.last_uploaded_files = uploaded_files


        # Always show dropdown when files are uploaded
        if uploaded_files:
            st.markdown(" ")
            st.markdown("#### 🎯 Which task would you like to run?")

            # Determine allowed tasks (handles non-rectangular mode)
            allowed_tasks = get_allowed_tasks()

            # Task selection widget
            selected_task = st.selectbox("Select", ["Choose an option"] + allowed_tasks,key="task_selector")

            # Only run tasks if data exists
            if st.session_state.current_data:

                if selected_task != "Choose an option":

                    st.markdown("")
                    with st.container(border=True):
                        st.markdown(f"### {selected_task}")

                        # -----------------------------------------------------------------------------
                        # TASK EXECUTION BLOCK
                        # -----------------------------------------------------------------------------

                        # 1. Get the actual widget function for this task
                        widget_func = WIDGETS[selected_task]

                        # ---------------------------------------------------------
                        # Reset metadata when switching tasks
                        # ---------------------------------------------------------
                        current_task = selected_task

                        if st.session_state.get("selected_task") != current_task:
                            st.session_state.metadata_outputs = {}
                            st.session_state.selected_task = current_task

                        # 2. Representative DataFrame for widgets (first uploaded file)
                        df_for_widget = next(iter(st.session_state.current_data.values()))

                        # ---------------------------------------------------------
                        # WIDGETS
                        # ---------------------------------------------------------
                        # 3. 🎯 Collect task inputs from the WIDGET
                        task_inputs = widget_func(df_for_widget)

                        # Only proceed if widget returned something meaningful
                        if task_inputs is not None:

                            # Ensure metadata_outputs exists
                            st.session_state.setdefault("metadata_outputs", {})

                            # ---------------------------------------------------------
                            # SPECIAL CASE: MERGE MULTIPLE FILES
                            # ---------------------------------------------------------
                            # This is the ONLY task that operates on ALL files at once.
                            # It bypasses the per-file loop entirely.
                            # ---------------------------------------------------------
                            if selected_task == "merge_files":

                                # Save undo state BEFORE merging (all files)
                                st.session_state.history_stack["__merge__"] = [{
                                    "current_data": {
                                        fname: df.copy()
                                        for fname, df in st.session_state.current_data.items()
                                    },
                                    "row_map": {
                                        fname: rm.copy()
                                        for fname, rm in st.session_state.row_map.items()
                                    }
                                }]
                                st.session_state.redo_stack["__merge__"] = []

                                # 🏃🏻‍♀️🏃🏻‍♀️ Run merge ONCE with all files
                                task_func = TASKS[selected_task]
                                result = task_func(st.session_state.current_data, filename=None, **task_inputs)

                                # Normalize return signature
                                if isinstance(result, tuple):
                                    merged_df = result[0]
                                    metadata_df = (result[-1] if isinstance(result[-1], pd.DataFrame) else None )
                                else:
                                    merged_df = result
                                    metadata_df = None

                                # Replace all data with a single merged file
                                st.session_state.current_data = {"merged.csv": merged_df}
                                st.session_state.original_data = {"merged.csv": merged_df.copy()}

                                # Reset row_map
                                st.session_state.row_map = {"merged.csv": list(range(1, len(merged_df) + 1)) }

                                # Reset history structures
                                st.session_state.history_stack = {"merged.csv": []}
                                st.session_state.redo_stack = {"merged.csv": []}
                                st.session_state.task_history = {"merged.csv": []}

                                # Store metadata if present
                                if metadata_df is not None:
                                    st.session_state.metadata_outputs = { "merged.csv": {selected_task: metadata_df}}

                                st.session_state.task_applied = True
                                st.success("Files merged successfully! See the **Live Data Preview** tab.")
                                return  # IMPORTANT: Skip normal per-file loop


                            # ---------------------------------------------------------
                            # NORMAL CASE: PER-FILE TASKS
                            # ---------------------------------------------------------
                            new_data = {}

                            for fname, df in st.session_state.current_data.items():

                                # ---------------------------------------------------------
                                # Undo & Redo Stacks
                                # ---------------------------------------------------------
                                st.session_state.history_stack.setdefault(fname, [])
                                st.session_state.redo_stack.setdefault(fname, [])

                                # Save undo state BEFORE applying task
                                st.session_state.history_stack[fname].append({
                                    "df": st.session_state.current_data[fname].copy(),
                                    "row_map": st.session_state.row_map[fname].copy()
                                })

                                # Clear redo stack because a new action happened
                                st.session_state.redo_stack[fname] = []

                                # ---------------------------------------------------------
                                # 🏃🏻‍♀️🏃🏻‍♀️ RUN THE TASK
                                # ---------------------------------------------------------
                                task_func = TASKS[selected_task]

                                # Run the task directly on the DataFrame.
                                result = task_func(df, filename=fname, **task_inputs)

                                # ---------------------------------------------------------
                                # NORMALIZE RETURN
                                # ---------------------------------------------------------
                                if isinstance(result, tuple):
                                    cleaned_df = result[0]
                                    metadata_df = (result[-1] if isinstance(result[-1], pd.DataFrame) else None)
                                else:
                                    cleaned_df = result
                                    metadata_df = None


                                # ---------------------------------------------------------
                                # 🔖 CLEAN DATA + METADATA
                                # ---------------------------------------------------------
                                new_data[fname] = cleaned_df

                                if metadata_df is not None:
                                    st.session_state.metadata_outputs.setdefault(fname, {})
                                    st.session_state.metadata_outputs[fname][selected_task] = metadata_df

                            # ---------------------------------------------------------
                            # 5. Replace all data with cleaned versions
                            # ---------------------------------------------------------
                            st.session_state.current_data = new_data

                            # 🔄 Clear preview cache because data changed
                            st.session_state.preview_cache = {}


                            # 6. Mark that a task was applied
                            st.session_state.task_applied = True

                            # 7. Notify the user
                            st.success("Task completed! Check the **Live Data Preview** tab to see the updated data before downloading.", icon="✅")



            # -------------------------------------------------
            # SHOW METADATA (if any)
            # -------------------------------------------------
            if st.session_state.get("metadata_outputs"):
                st.markdown("")
                st.markdown("##### Metadata Output")

                # Tasks whose metadata table applies to all files
                global_metadata_tasks = ["Clean column headers", "Tidy Data Checker", "Rename columns"]

                # Track which global tasks we've already shown
                shown_global = set()

                for fname, task_dict in st.session_state.metadata_outputs.items():
                    st.markdown(f"**File**: {fname}")

                    for task_name, metadata_df in task_dict.items():

                        # -----------------------------------------
                        # 1. Global metadata (show once)
                        # -----------------------------------------
                        if task_name in global_metadata_tasks:
                            if task_name in shown_global:
                                continue

                            st.markdown(f"**{task_name}** (applies to all files)")
                            st.dataframe(metadata_df, use_container_width=True)
                            shown_global.add(task_name)
                            continue

                        # -----------------------------------------
                        # 2. All other tasks---> expander per file
                        # -----------------------------------------
                        with st.expander(f"{task_name} for {fname}", expanded=False):
                            st.dataframe(metadata_df, use_container_width=True)



        # -------------------------------------------------
        # DOWNLOAD SECTION
        # -------------------------------------------------
        if (uploaded_files and st.session_state.current_data and st.session_state.task_applied):
            st.markdown("####")
            with st.container(border=True):
                st.markdown("#### Download Your Cleaned Data")
                big_caption("These files update automatically after each task.")

                show_downloads = st.button("Show Download Options")

                if show_downloads:
                    download.download_output()
                    download.excel_download()





        # ---------------------------------------------------------
        # RESTART BUTTON
        # ---------------------------------------------------------
        st.markdown("---")
        if st.button("🔄 Restart Application", type="secondary"):
            st.session_state.preview_cache = {}   # clear preview cache
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
