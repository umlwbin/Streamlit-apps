import streamlit as st
import pandas as pd
import os
import sys
from io import StringIO

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

        # Clear previous data
        st.session_state.original_data = {}
        st.session_state.current_data = {}
        st.session_state.task_history = {}
        st.session_state.history_stack = {}
        st.session_state.redo_stack = {}
        st.session_state.non_rectangular_files = set()

    uploaded_files = st.file_uploader(
        "Choose CSV file(s)",
        accept_multiple_files=True,
        type="csv",
        on_change=newUpload,
        key="new_upload"
    )

    if uploaded_files and not st.session_state.files_processed:

        non_rectangular_detected = []

        for file in uploaded_files:
            filename = file.name
            raw_bytes = file.read().decode("utf-8", errors="replace")

            # Split into rows and columns
            rows = raw_bytes.splitlines()
            split_rows = [r.split(",") for r in rows]

            # Check for a rectangular table (consistent columns)
            lengths = {len(r) for r in split_rows}
            is_rectangular = len(lengths) == 1

            if not is_rectangular:
                # Track this file but do not warn yet
                st.session_state.non_rectangular_files.add(filename)
                non_rectangular_detected.append(filename)

                # Load something usable so the metadata-removal task can operate
                try:
                    df = pd.read_csv(StringIO(raw_bytes), header=None)
                except Exception:
                    df = pd.DataFrame(split_rows)

                st.session_state.original_data[filename] = df.copy()
                st.session_state.current_data[filename] = df.copy()
                st.session_state.task_history[filename] = []
                st.session_state.history_stack[filename] = []
                st.session_state.redo_stack[filename] = []
                continue

            # Normal rectangular file
            try:
                df = pd.read_csv(StringIO(raw_bytes))
                st.session_state.original_data[filename] = df.copy()
                st.session_state.current_data[filename] = df.copy()
                st.session_state.task_history[filename] = []
                st.session_state.history_stack[filename] = []
                st.session_state.redo_stack[filename] = []
            except Exception as e:
                st.error(f"Failed to read `{filename}`: {str(e)}")

        # After processing all files, show a single warning if needed
        # if non_rectangular_detected:
        #     st.warning(
        #         "One or more uploaded files have inconsistent row lengths. "
        #         "Only the Remove metadata rows task is available until the tables are cleaned."
        #     )

        if st.session_state.original_data:
            st.session_state.files_processed = True
            st.success("Files uploaded and initialized.")


    return uploaded_files or []
