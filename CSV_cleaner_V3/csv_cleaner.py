import streamlit as st
import pandas as pd
import os
import sys

#Set page config
st.set_page_config(page_title=None, page_icon="📖", layout="wide", initial_sidebar_state="expanded", menu_items=None)

#Output Path
path=os.path.abspath(os.curdir)

#Add Modules
sys.path.append(f'{path}/Modules') #adding the Modules directory to Python's search path at runtime.

#Module Imports for the different sections
import  session_initializer, sidebar_intro, tasks, view_undo_redo, file_uploads, add_columns,reorder_variables,remove_columns, merge_files, headers, rename,merge_date_time, iso, parse_dates, tidy_data, pivot_data, assign_dataType, download 

# Initialize Session States
session_initializer.init_session_state()

#Set Up the Sidebar with intro
with st.sidebar:
    sidebar_intro.sidebar()

#Create reset, undo and redo buttons
view_undo_redo.reset_undo_redo_buttons()
tab_list=["🧰 Main App", "  ", "👀 Live Data Preview"]
tab1, Extraspace, tab2 = st.tabs(tab_list)
 
# Define the Tasks and the functions that will be run to perform the task processing
TASKS=tasks.define_task_functions()

# -------------------------------
# 🎯 RUN TASK FUNCTION
# -------------------------------   
all_summaries = {} # Basic Cleaning Summary Dictionary
def run_task(task_name, **kwargs):
    task_info = TASKS[task_name]
    task_type = task_info["type"]
    task_func = task_info["func"]

    if task_type == "single":
        for filename, df in st.session_state.current_data.items():
            cleaned_df=pd.DataFrame()

            # ↩️ Update Undo and Redo stacks -------
            st.session_state.history_stack[filename].append(df.copy())
            st.session_state.redo_stack[filename] = []

            # ⏩️ Processing Function----------------
            result = task_func(df.copy(), **kwargs)

            # Handle summary if returned
            if isinstance(result, tuple):
                cleaned_df, summary = result
            else:
                cleaned_df = result
                summary = {}
            
            # 💽 Store Current Data and Update Task History------
            if not cleaned_df.empty:
                st.session_state.current_data[filename] = cleaned_df
                st.session_state.task_history[filename].append(task_name)

                all_summaries[filename] = summary # Update Summary if any

    # Merging Files Task
    elif task_type == "multi":
        # ⏩️ Processing Function----------------
        merged_df = task_func(st.session_state.current_data, **kwargs)
        merged_filename = "merged_output.csv"

        # 🔼 Update Session states----------------
        st.session_state.original_data[merged_filename] = merged_df.copy()
        st.session_state.current_data[merged_filename] = merged_df.copy()
        st.session_state.task_history[merged_filename] = [task]
        st.session_state.history_stack[merged_filename] = []
        st.session_state.redo_stack[merged_filename] = []

    # All Done Msg
    view_undo_redo.show_snapshot()



with tab1:
    # -------------------------------
    # 🎯 Step 1: Task Selection
    # -------------------------------
    task=tasks.what_to_do_widgets()or None

    if task:
        # -------------------------------
        #  📤 Step 2: File Upload
        # ------------------------------- 
        uploaded_files=file_uploads.fileuploadfunc()

        if st.session_state.get("new_upload") and not st.session_state.files_processed: #If new files have been uplaoded        
            # Clear previous data
            st.session_state.original_data = {}
            st.session_state.current_data = {}

            for file in uploaded_files:
                filename = file.name

                try:
                    df = pd.read_csv(file)

                    # If successful, store the DataFrame
                    # Save original only once
                    if filename not in st.session_state.original_data:
                        st.session_state.original_data[filename] = df.copy()
                        st.session_state.current_data[filename] = df.copy() # Add a copy to current_data
                        st.session_state.task_history[filename] = []
                        st.session_state.history_stack[filename] = []
                        st.session_state.redo_stack[filename] = []
                except Exception as e:
                    st.error(f"❌ Failed to read `{filename}`: {str(e)}")

            if st.session_state.original_data:
                st.session_state.files_processed = True
                st.success("Files uploaded and initialized.")

        # -------------------------------
        # 🔁 Step 3: Apply Task to Current Data - See Run Task Function above
        # ------------------------------- 
        if uploaded_files and task and st.session_state.original_data: # At least one GOOD file was read into a DataFrame
        
            if task is not None:
                st.markdown('-------------')
                st.markdown(f'### {task}')
                st.markdown(' ')
                cols=list(list(st.session_state.current_data.values())[0].columns)

            if task=='Add columns':                                   
                task_inputs=add_columns.how_many_vars_widget(cols) or {} # Create Widgets and get user inputs
                if st.session_state.get("addColsNext2_WidgetKey"):       # Last Next Button Clicked
                    run_task(task, **task_inputs)                        # Run Processing Function and Update Undo, Redo, Current states.

            if task=='Reorder columns':                                   
                task_inputs=reorder_variables.redorder_widget(cols) or {} 
                if st.session_state.get("reorderNext_WidgetKey"):       
                    run_task(task, **task_inputs)                                 

            if task=='Remove columns':                                   
                task_inputs=remove_columns.which_cols_widgets(cols) or {} 
                if st.session_state.get("removeColsNext_WidgetKey"):       
                    run_task(task, **task_inputs)                       

            if task=='Clean column headers':                                   
                task_inputs={}              
                run_task(task, **task_inputs)  

            if task=='Rename columns':                                   
                task_inputs=rename.rename_cols_widgets(cols) or {} 
                if st.session_state.get("renameNext_WidgetKey"):       
                    run_task(task, **task_inputs)                        

            if task=='Merge date and time columns':                                                
                task_inputs=merge_date_time.merge_dt_widgets(cols) or {}
                if st.session_state.get("mergeDateNext_WidgetKey"):      
                    run_task(task, **task_inputs)                       

            if task=='Convert DateTime column to ISO format':                                                
                task_inputs=iso.convert_dateTime_widgets(cols) or {}
                if st.session_state.get("convertISONext1_WidgetKey"):      
                    run_task(task, **task_inputs)

            if task=='Parse Date':                                                
                task_inputs=parse_dates.parse_dateTime_widgets(cols) or {}
                if st.session_state.get("ParseNext_WidgetKey"):      
                    run_task(task, **task_inputs)

            if task=='Transpose Data': 
                task_inputs={}              
                run_task(task, **task_inputs)  

            if task=='Assign Data Type': 
                first_df=list(st.session_state.current_data.values())[0]                                 
                task_inputs=assign_dataType.assign_widgets(first_df, cols) or {}
                if st.session_state.get("assignNext_WidgetKey"):          
                    run_task(task, **task_inputs)

            if task=='Tidy Data Checker':
                task_inputs=tidy_data.file_cleanup_widgets(cols) or {}
                if st.session_state.get("cleanupContinue"):      
                    run_task(task, **task_inputs)

                    # Display Summary of cleaning
                    st.markdown(" ")
                    st.markdown("#### 🧼 Cleaning Summary Dashboard")
                    for filename, summary in all_summaries.items():
                        with st.expander(f"📄 {filename}", expanded=False):
                            st.write(f"**Empty Columns Removed:** {len(summary.get('empty_columns_removed', []))}")
                            st.write(f"**Empty Rows Removed:** {summary.get('empty_rows_removed', 0)}")
                            st.write(f"**NaNs Replaced:** {summary.get('nans_replaced', 0)}")
                            if summary.get("columns_cleaned"):
                                st.success("✅ Column headers cleaned")


        if uploaded_files and not st.session_state.original_data:
            st.warning("⚠️ All uploaded files failed to load. Please check the format and try again.")


# -------------------------------
# 👀 Step 4: Live Preview
# ------------------------------- 
with tab2:
    st.markdown("#### 🔎 Live Preview of Processed Files")
    st.markdown("")

    if st.session_state.current_data:
        filenames = list(st.session_state.current_data.keys())
        selected_file = st.selectbox("📂 Choose a file to preview", filenames, key="preview_file") #Drowpdownbox to select file

        current_df = st.session_state.current_data[selected_file]
        original_df = st.session_state.original_data[selected_file]
        history = st.session_state.task_history.get(selected_file, [])

        st.markdown("")
        st.markdown(f" 📑 **File:** `{selected_file}`")
        st.markdown(f" ✅ **Tasks Applied:** {', '.join(history) if history else 'None'}")
        st.markdown("")
        compare = st.checkbox("Compare with Original", key="sidebar_compare")

        if compare:
            st.markdown("**Original (Top 5 rows):**")
            st.dataframe(original_df.head(5), use_container_width=True)

            st.markdown("**Processed (Top 5 rows):**")
            st.dataframe(current_df.head(5), use_container_width=True)
        else:
            st.markdown("**Processed Data (Top 5 rows):**")
            st.dataframe(current_df.head(5), use_container_width=True)
    else:
        st.info("Upload files to see a live preview.")



# -------------------------------
# ⬇️ Download
# ------------------------------- 
with st.sidebar:
    download.download_output()
    download.excel_download()