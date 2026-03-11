import streamlit as st
import pandas as pd
import os
import sys
from io import StringIO

# Output Path
path = os.path.abspath(os.curdir)

# Add Modules
sys.path.append(f'{path}/Modules')
import session_initializer


# ---------------------------------------------------------
# Helper: Make column names unique (safe for PyArrow)
# ---------------------------------------------------------
def make_unique_columns(cols):
    seen = {}
    new_cols = []
    for col in cols:
        if col not in seen:
            seen[col] = 0
            new_cols.append(col)
        else:
            seen[col] += 1
            new_cols.append(f"{col}_{seen[col]}")
    return new_cols


# ---------------------------------------------------------
# Main upload function
# ---------------------------------------------------------
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

        for file in uploaded_files:
            filename = file.name
            raw_bytes = file.read().decode("utf-8", errors="replace")

            # ---------------------------------------------------------
            # Load file safely using Python engine
            # ---------------------------------------------------------
            try:
                df = pd.read_csv(
                    StringIO(raw_bytes),
                    header=None,
                    sep=",",
                    engine="python",
                    dtype=str
                )
            except Exception:
                rows = raw_bytes.splitlines()
                split_rows = [r.split(",") for r in rows]
                df = pd.DataFrame(split_rows)

            # ---------------------------------------------------------
            # Detect metadata above header
            # ---------------------------------------------------------
            header_len = df.shape[1]
            first_row_len = df.iloc[0].count()

            file_has_metadata = first_row_len < header_len

            if file_has_metadata:
                st.session_state.non_rectangular_files.add(filename)

            # ---------------------------------------------------------
            # Promote header ONLY for rectangular files
            # ---------------------------------------------------------
            if not file_has_metadata:

                # Extract header row
                header = df.iloc[0].astype(str).tolist()

                # Deduplicate header names
                header = make_unique_columns(header)

                # Drop header row
                df = df.iloc[1:].reset_index(drop=True)

                # Assign deduped header
                df.columns = header

            else:
                # Metadata-heavy files keep placeholder column names
                df.columns = [f"col_{i}" for i in range(df.shape[1])]

            # ---------------------------------------------------------
            # Add original row numbers AFTER header promotion
            # ---------------------------------------------------------
            df["_original_row"] = range(len(df))

            # ---------------------------------------------------------
            # Store file in session state
            # ---------------------------------------------------------
            st.session_state.original_data[filename] = df.copy()
            st.session_state.current_data[filename] = df.copy()
            st.session_state.task_history[filename] = []
            st.session_state.history_stack[filename] = []
            st.session_state.redo_stack[filename] = []

        # ---------------------------------------------------------
        # Mark upload complete
        # ---------------------------------------------------------
        if st.session_state.original_data:
            st.session_state.files_processed = True
            st.success("Files uploaded and initialized.")

    return uploaded_files or []
