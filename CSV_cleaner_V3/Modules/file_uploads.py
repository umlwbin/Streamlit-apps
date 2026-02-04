import streamlit as st
import pandas as pd
import os
import sys

#Output Path
path = os.path.abspath(os.curdir)

#Add Modules
sys.path.append(f'{path}/Modules')
import session_initializer

def fileuploadfunc():
    st.markdown("#### Upload a CSV/TXT File to begin")

    def newUpload():
        session_initializer.reset_widget_flags()
        st.session_state.files_processed = False
        st.session_state.task_applied = False

        # Clear any previous data
        st.session_state.original_data = {}
        st.session_state.current_data = {}
        st.session_state.task_history = {}
        st.session_state.history_stack = {}
        st.session_state.redo_stack = {}

    uploaded_files = st.file_uploader(
        "Choose CSV file(s)",
        accept_multiple_files=True,
        type="csv",
        on_change=newUpload,
        key="new_upload"
    )

    if uploaded_files and not st.session_state.files_processed:
        for file in uploaded_files:
            filename = file.name
            try:
                df = pd.read_csv(file)
                # ✅ Populate session state immediately
                st.session_state.original_data[filename] = df.copy()
                st.session_state.current_data[filename] = df.copy()
                st.session_state.task_history[filename] = []
                st.session_state.history_stack[filename] = []
                st.session_state.redo_stack[filename] = []
            except Exception as e:
                st.error(f"❌ Failed to read `{filename}`: {str(e)}")

        if st.session_state.original_data:
            st.session_state.files_processed = True
            st.success("Files uploaded and initialized.")

    return uploaded_files or []