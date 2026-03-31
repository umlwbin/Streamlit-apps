import streamlit as st
import pandas as pd
import os
import sys
from io import StringIO

"""
File Upload and Initialization Module
====================================

This module handles all logic for safely loading user‑uploaded CSV/TXT files.
This module does **not** perform any cleaning or transformation. It only
prepares files so that the task widgets and processing functions can operate
safely and consistently.

---------------------------------------------------------------------------
Core Responsibilities
---------------------------------------------------------------------------

1. Reset Session State on New Upload
   ---------------------------------
   When the user uploads new files, all workflow‑related session state is
   cleared and reinitialized. This ensures that:
       • previous task history does not leak into new uploads
       • undo/redo stacks start clean
       • row maps and metadata flags are rebuilt from scratch

2. Detect Metadata BEFORE Parsing
   -------------------------------
   Many scientific CSVs contain metadata rows above the true header. To avoid
   misinterpreting metadata as data, the module:
       • scans raw text line‑by‑line
       • identifies the first “wide enough” row (likely header)
       • flags files where metadata is present
       • avoids header promotion for non‑rectangular files

3. Load Files Safely
   ------------------
   Files are loaded using a forgiving parsing strategy:
       • Python engine for maximum flexibility
       • dtype=str to preserve all values exactly as written
       • fallback to manual splitting if parsing fails

   This ensures that even messy or irregular CSVs load without crashing.

4. Initialize Row Maps
   --------------------
   Every file receives a `row_map` that records the original row numbers from
   the uploaded file. This map is preserved across all transformations and is
   essential for:
       • metadata extraction
       • header merging
       • provenance tracking
       • reversible operations

5. Normalize Empty Columns
   ------------------------
   Completely empty columns (common in CSV exports) are filled with empty
   strings to avoid:
       • dtype inconsistencies
       • PyArrow failures
       • accidental column drops

6. Promote Header Row (Rectangular Files Only)
   -------------------------------------------
   If no metadata is detected:
       • the first row becomes the header
       • empty header cells are replaced with `unnamed_i`
       • duplicate names are made unique
       • the row map is updated accordingly

   If metadata *is* detected:
       • generic column names (`col_0`, `col_1`, …) are assigned
       • header promotion is deferred to a dedicated widget

7. Store Files in Session State
   -----------------------------
   For each file, the module initializes:
       • original_data      (immutable reference)
       • current_data       (mutable working copy)
       • task_history       (per‑file task log)
       • history_stack      (undo)
       • redo_stack         (redo)
       • non_rectangular_files
       • row_map

   These structures are used by all downstream widgets and tasks.

"""


# Output Path
path = os.path.abspath(os.curdir)

# Add Modules
sys.path.append(f"{path}/Modules")
import state.session_initializer as session_initializer
from Modules.upload.metadata_detection import detect_metadata_rows


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

        st.session_state.original_data = {}
        st.session_state.current_data = {}
        st.session_state.task_history = {}
        st.session_state.history_stack = {}
        st.session_state.redo_stack = {}
        st.session_state.non_rectangular_files = set()
        st.session_state.row_map = {}

    uploaded_files = st.file_uploader(
        "Choose CSV file(s)",
        accept_multiple_files=True,
        type="csv",
        on_change=newUpload,
        key=f"uploader_{st.session_state.uploader_key}"
    )

    if uploaded_files and not st.session_state.files_processed:

        for file in uploaded_files:
            filename = file.name
            raw_bytes = file.read().decode("utf-8", errors="replace")

            # -------------------------------------------------
            # STEP 1: Metadata detection (delegated)
            # -------------------------------------------------
            has_metadata, header_index = detect_metadata_rows(raw_bytes, sep=",")

            if has_metadata:
                st.session_state.non_rectangular_files.add(filename)

            # -------------------------------------------------
            # STEP 2: Load file safely
            # -------------------------------------------------
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

            # -------------------------------------------------
            # STEP 3: Initialize row_map BEFORE modifications
            # -------------------------------------------------
            st.session_state.row_map[filename] = list(range(1, len(df) + 1))

            # -------------------------------------------------
            # STEP 4: Fix empty columns
            # -------------------------------------------------
            empty_cols = df.columns[
                df.isna().all() |
                (df.apply(lambda col: col.astype(str).str.strip() == "").all())
            ]
            for idx in empty_cols:
                df[idx] = df[idx].fillna("")

            # -------------------------------------------------
            # STEP 5: Promote header for rectangular files only
            # -------------------------------------------------
            if not has_metadata:
                header = df.iloc[0].astype(str).tolist()
                header = [h if str(h).strip() != "" else f"unnamed_{i}" for i, h in enumerate(header)]
                header = make_unique_columns(header)

                df.columns = header
                df = df[1:].reset_index(drop=True)

                st.session_state.row_map[filename] = st.session_state.row_map[filename][1:]

            else:
                df.columns = [f"col_{i}" for i in range(df.shape[1])]

            # -------------------------------------------------
            # STEP 6: Store file
            # -------------------------------------------------
            st.session_state.original_data[filename] = df.copy()
            st.session_state.current_data[filename] = df.copy()
            st.session_state.task_history[filename] = []
            st.session_state.history_stack[filename] = []
            st.session_state.redo_stack[filename] = []

        st.session_state.files_processed = True
        st.success("Files uploaded and initialized.")

    return uploaded_files or []
