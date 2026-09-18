import streamlit as st
import pandas as pd

from Modules.state import session_initializer
from Modules.state.undo_redo import restart_app
from Modules.state.undo_redo import push_to_undo_stack

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
st.set_page_config( page_title="CSV Curation Studio", page_icon="🔖", layout="wide")

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
        if st.session_state.current_data:
            st.markdown(" ")
            st.markdown("#### 🎯 Which task would you like to run?")



            # 🌟 STEP 1: Establish a baseline selector index tracker if it doesn't exist
            if "selector_index_counter" not in st.session_state:
                st.session_state.selector_index_counter = 0

            # If the flag is caught, increment the counter to force-reset the position index
            if st.session_state.get("clear_selector_flag", False):
                st.session_state.selector_index_counter += 1
                st.session_state.clear_selector_flag = False  # Consume flag immediately

            # Determine allowed tasks (handles non-rectangular mode)
            allowed_tasks = get_allowed_tasks()

            # 🌟 STEP 2: Use the counter inside a dynamic widget key format.
            # This completely bypasses the instantiation error by letting the 
            # widget clear its own memory state naturally!
            current_widget_key = f"task_selector_run_{st.session_state.selector_index_counter}"

            # Task selection widget
            selected_task = st.selectbox(
                "Select", 
                ["Choose an option"] + allowed_tasks,
                key=current_widget_key,
                index=0
            )


            

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

                        # 2. Representative DataFrame for widgets (first uploaded file)
                        df_for_widget = next(iter(st.session_state.current_data.values())) #next(inter()) quickly points to and grabs the first in the dict, less space used

                        # ---------------------------------------------------------
                        # WIDGETS
                        # ---------------------------------------------------------
                        # 3. 🎯 Collect task inputs from the WIDGET
                        task_inputs = widget_func(df_for_widget)

                        if task_inputs is not None:
                            st.session_state.setdefault("metadata_outputs", {})

                            # Safeguard history stacks against duplicate modifications
                            # We stringify the inputs to create a distinct state verification hash key
                            current_inputs_hash = str(task_inputs) + selected_task
                            
                            if st.session_state.get("last_executed_inputs_hash") != current_inputs_hash:
                                
                                # Only log a history step if a user actually executed a new action choice
                                push_to_undo_stack()
                                st.session_state.last_executed_inputs_hash = current_inputs_hash


                                # ---------------------------------------------------------
                                # SPECIAL CASE: MERGE MULTIPLE FILES
                                # ---------------------------------------------------------
                                if selected_task == "Merge multiple files":

                                    # 🏃🏻‍♀️🏃🏻‍♀️ Run merge ONCE with all files
                                    task_func = TASKS[selected_task]
                                    result = task_func(st.session_state.current_data, filename=None, **task_inputs)

                                    # Normalize return signature
                                    if isinstance(result, tuple) and len(result) >= 2:
                                        merged_df = result[0]
                                        metadata_df = result[1] if isinstance(result[1], pd.DataFrame) else None
                                    else:
                                        # Handle single DataFrames or single-element tuples cleanly
                                        merged_df = result[0] if isinstance(result, tuple) else result
                                        metadata_df = None


                                    # Transform current data environment into the merged file 
                                    st.session_state.current_data = {"merged.csv": merged_df}
                                    st.session_state.row_map = {"merged.csv": list(range(1, len(merged_df) + 1))}

                                    if metadata_df is not None:
                                        st.session_state.metadata_outputs = {"merged.csv": {"Merge multiple files": metadata_df}}

                                    st.session_state.task_applied = True
                                    st.session_state.preview_cache = {}
                                                                
                                    # Store the success message in session state BEFORE rerunning
                                    st.session_state.merge_success_msg = "Files merged successfully! See the **Live Data Preview** tab."

                                    st.session_state.clear_selector_flag = True #sets it back to "Choose an option"
                                    st.rerun() # Refresh smoothly to let preview panels sync cleanly

                                # ---------------------------------------------------------
                                # NORMAL CASE: PER-FILE TASKS
                                # ---------------------------------------------------------
                                else:
                                    new_data = {}

                                    #Get task
                                    task_func = TASKS[selected_task]

                                    for fname, df in st.session_state.current_data.items():

                                        # 🏃🏻‍♀️🏃🏻‍♀️ RUN THE TASK
                                        result = task_func(df, filename=fname, **task_inputs)

                                        #Normalize return
                                        if isinstance(result, tuple) and len(result) >= 2:
                                            cleaned_df = result[0]
                                            metadata_df = result[1] if isinstance(result[1], pd.DataFrame) else None
                                        else:
                                            # Handle single DataFrames or single-element tuples cleanly
                                            cleaned_df = result[0] if isinstance(result, tuple) else result
                                            metadata_df = None


                                        # Clean data & metadata
                                        new_data[fname] = cleaned_df

                                        if metadata_df is not None:
                                            st.session_state.metadata_outputs.setdefault(fname, {})
                                            st.session_state.metadata_outputs[fname][selected_task] = metadata_df

                                    #Replace all data with cleaned versions
                                    st.session_state.current_data = new_data
                                    st.session_state.preview_cache = {}  # Clear preview cache because data changed
                                    st.session_state.task_applied = True # Mark that a task was applied

                                    # Save normal success msg to a session state flag
                                    st.session_state.normal_success_msg = "Task completed! Check the **Live Data Preview** tab."
                                    
                                    st.session_state.clear_selector_flag = True # sets it back to "Choose an option"
                                    st.rerun() 

                    
                    # Success message for merge renders here after everything inside the container has rendered
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
        if st.button("🔄 Restart Application", type="secondary", key="restart_app_btn"):
            from Modules.state.undo_redo import restart_app
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
