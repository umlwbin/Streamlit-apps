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
        st.session_state.row_map = {}   # NEW: row map lives here

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
            # STEP 1: Detect metadata BEFORE loading into DataFrame
            # ---------------------------------------------------------
            raw_lines = raw_bytes.splitlines()
            split_lines = [line.split(",") for line in raw_lines]

            row_widths = [len(r) for r in split_lines]
            max_width = max(row_widths)

            HEADER_THRESHOLD = 0.9  # 90% of max width
            candidate_header_index = None

            for i, w in enumerate(row_widths):
                # A header row must be "wide enough"
                if w >= HEADER_THRESHOLD * max_width:
                    candidate_header_index = i
                    break

            # If the first wide-enough row is NOT row 0 → metadata exists
            file_has_metadata = candidate_header_index not in (0, None)

            if file_has_metadata:
                st.session_state.non_rectangular_files.add(filename)

            # ---------------------------------------------------------
            # STEP 2: Load file safely using Python engine
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
                df = pd.DataFrame([r.split(",") for r in rows])

            # ---------------------------------------------------------
            # STEP 3: Initialize row_map BEFORE any modifications
            # ---------------------------------------------------------
            st.session_state.row_map[filename] = list(range(len(df)))

            # ---------------------------------------------------------
            # STEP 4: Fix completely empty columns (after detection)
            # ---------------------------------------------------------
            empty_cols = df.columns[
                df.isna().all() |
                (df.apply(lambda col: col.astype(str).str.strip() == "").all())
            ]

            for idx in empty_cols:
                df[idx] = df[idx].fillna("")

            # ---------------------------------------------------------
            # STEP 5: Promote header ONLY for rectangular files
            # ---------------------------------------------------------
            if not file_has_metadata:

                header = df.iloc[0].astype(str).tolist()

                header = [
                    h if str(h).strip() != "" else f"unnamed_{i}"
                    for i, h in enumerate(header)
                ]

                header = make_unique_columns(header)

                # Drop header row
                df = df.iloc[1:].reset_index(drop=True)

                # Update row_map to match
                st.session_state.row_map[filename] = st.session_state.row_map[filename][1:]

                df.columns = header

            else:
                # Metadata-heavy file → assign generic column names
                df.columns = [f"col_{i}" for i in range(df.shape[1])]

            # ---------------------------------------------------------
            # STEP 6: Store file in session state
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
