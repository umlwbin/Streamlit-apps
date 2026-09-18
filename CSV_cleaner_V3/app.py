'''
I like to call app.py the Orchestartor; it pulls everything togetehr so the different components run smoothly.
It does not make any changes to the data itself, it simply orchestrates the workflow. 
To understand its layout better, please see docs/orchestrator and docs/architecture_overview.
To understand the different session state varibales used see docs/state_bundles.md.

'''

import streamlit as st
import pandas as pd

from Modules.state import session_initializer
from Modules.state.undo_redo import restart_app
from Modules.state.undo_redo import commit_new_action

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
st.set_page_config(page_title="CSV Curation Studio", page_icon="🔖", layout="wide")

# ---------------------------------------------------------
# INITIALIZE SESSION
# ---------------------------------------------------------
session_initializer.init_session_state()


# ---------------------------------------------------------
# Increase the size of widget labels
# ---------------------------------------------------------
st.html("""
<style>
    div[data-testid="stTextInput"] label p,
    div[data-testid="stSelectbox"] label p,
    div[data-testid="stRadio"] [data-testid="stWidgetLabel"] p,
    div[data-testid="stMarkdownContainer"] p,
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
# FRAGMENT TO ISOLATE DOWNLOADS SO STREAMLIT DOESNT RE-RUN THE WHOLE APP
# ---------------------------------------------------------
@st.fragment
def download_fragment():
    download.download_output()
    #download.excel_download()


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

        # 1. Always render the uploader widget so it stays visible on screen
        uploaded_files = file_uploads.fileuploadfunc()

        # 2. Handle metadata resets ONLY if the user actually changed the uploaded files
        if not st.session_state.get("history_step_active", False):  # Only run this block if we are NOT currently performing undo or redo. When undo/redo is happening, do not treat anything as a new upload.
            if uploaded_files != st.session_state.get("last_uploaded_files"): # Did the user actually upload new files? If they differ, then it was a real uplaod event and we can reset
                st.session_state.metadata_outputs = {}
                st.session_state.supplementary_outputs = {}
                session_initializer.reset_widget_flags()
                st.session_state.last_uploaded_files = uploaded_files

        # --- Dropdown Task Selection Widget Creation [see docs/dropdown_selection.md] ---
        # Always show dropdown when files are loaded in memory
        if st.session_state.current_data:
            st.markdown("#### 🎯 Which task would you like to run?")
            allowed_tasks = get_allowed_tasks()
            
            # Establish a baseline selector index tracker if it doesn't exist
            if "selector_index_counter" not in st.session_state:
                st.session_state.selector_index_counter = 0

            # If a reset flag is caught, increment the counter to force-reset the widget
            if st.session_state.get("clear_selector_flag", False):
                st.session_state.selector_index_counter += 1
                st.session_state.clear_selector_flag = False  # Set it back to False immediately so it doesn’t fire again on the next rerun

            # Determine allowed tasks (handles non-rectangular mode)
            allowed_tasks = get_allowed_tasks()
            
            # Create a dynamic widget key format using the index counter
            current_widget_key = f"task_selector_run_{st.session_state.selector_index_counter}"
            # -------------------------------------------


            # Task selection widget
            selected_task = st.selectbox("Select", ["Choose an option"] + allowed_tasks,  key=current_widget_key, index=0)

            if selected_task != "Choose an option":
                st.markdown("")
                with st.container(border=True):
                    st.markdown(f"### {selected_task}")

                    widget_func = WIDGETS[selected_task]
                    task_func = TASKS[selected_task]
                    df_for_widget = next(iter(st.session_state.current_data.values())) 


                    # ---------------------------------------------------------
                    # WIDGETS
                    # ---------------------------------------------------------
                    # 3. 🎯 Collect task inputs directly from the WIDGET
                    task_inputs = widget_func(df_for_widget)

                    if task_inputs is not None:
                        st.session_state.setdefault("metadata_outputs", {})


                        # CHECK THE SHIELD: If we just clicked Undo/Redo, drop the shield and skip execution
                        if st.session_state.get("history_step_active", False):
                            st.session_state.history_step_active = False # Consume immediately
                        
                        else:
                            # Running tasks is safe now!! 🎉
                            commit_new_action() # Saves the current state as a checkpoint before running a new task, so undo can return to this point

                            # ---------------------------------------------------------
                            # 🏃🏻‍♀️ RUN TASKS
                            # ---------------------------------------------------------

                            # --- CASE A: MERGE MULTIPLE FILES ---
                            if selected_task == "Merge multiple files":

                                # Run task!
                                task_func = TASKS[selected_task]
                                result = task_func(st.session_state.current_data, filename=None, **task_inputs)

                                # Normalize return signatures safely
                                if isinstance(result, tuple) and len(result) >= 2:
                                    merged_df = result[0]
                                    metadata_df = result[1] if isinstance(result[1], pd.DataFrame) else None
                                else:
                                    merged_df = result[0] if isinstance(result, tuple) else result
                                    metadata_df = None

                                # Overwrite data structures cleanly into the single merged file
                                st.session_state.current_data = {"merged.csv": merged_df}
                                st.session_state.row_map = {"merged.csv": list(range(1, len(merged_df) + 1))}

                                if metadata_df is not None:
                                    st.session_state.metadata_outputs = {"merged.csv": {"Merge multiple files": metadata_df}}

                                st.session_state.task_applied = True
                                st.session_state.preview_cache = {}
                                                            
                                # Store success markers and clear out rset selector
                                st.session_state.merge_success_msg = "Files merged successfully! See the **Live Data Preview** tab."
                                st.session_state.clear_selector_flag = True 
                                st.rerun() 

                            # --- CASE B: NORMAL PER-FILE TASKS ---
                            else:
                                new_data = {}
                                task_func = TASKS[selected_task]

                                for fname, df in st.session_state.current_data.items():

                                    # Run task!
                                    result = task_func(df, filename=fname, **task_inputs)

                                    # Normalize return signatures safely
                                    if isinstance(result, tuple) and len(result) >= 2:
                                        cleaned_df = result[0]
                                        metadata_df = result[1] if isinstance(result[1], pd.DataFrame) else None
                                    else:
                                        cleaned_df = result[0] if isinstance(result, tuple) else result
                                        metadata_df = None

                                    new_data[fname] = cleaned_df

                                    if metadata_df is not None:
                                        st.session_state.metadata_outputs.setdefault(fname, {})
                                        st.session_state.metadata_outputs[fname][selected_task] = metadata_df

                                st.session_state.current_data = new_data
                                st.session_state.preview_cache = {}  
                                st.session_state.task_applied = True 

                                # Store success markers and clear out rset selector
                                st.session_state.normal_success_msg = "Task completed! Check the **Live Data Preview** tab."
                                st.session_state.clear_selector_flag = True 
                                st.rerun() 

                    
            # Notifications render directly outside since we are using st.rerun() after tasks
            merge_message_slot = st.empty()
            
            if "merge_success_msg" in st.session_state and st.session_state.merge_success_msg:
                merge_message_slot.success(st.session_state.merge_success_msg)
                st.session_state.merge_success_msg = None  

            if "normal_success_msg" in st.session_state and st.session_state.normal_success_msg:
                merge_message_slot.success(st.session_state.normal_success_msg)
                st.session_state.normal_success_msg = None  

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
        if (st.session_state.original_data and st.session_state.current_data and st.session_state.task_applied):
            st.markdown("####")
            with st.container(border=True):
                st.markdown("#### Download Your Cleaned Data")
                big_caption("These files update automatically after each task.")

                show_downloads = st.toggle("Show Download Options")

                if show_downloads:
                    download_fragment()


        # ---------------------------------------------------------
        # RESTART BUTTON
        # ---------------------------------------------------------
        st.markdown("---")
        if st.button("🔄 Restart Application", type="secondary", key="restart_app_btn"):
            restart_app()  # Purges all state keys and increments the file uploader key
            st.rerun()     # Forces a clean slate execution pass


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
