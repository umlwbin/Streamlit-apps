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


# ---------------------------------------------------------
# STEP 0: Helper - Make column names unique (safe for PyArrow)
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
# STEP 1: Metadata Detection
# ---------------------------------------------------------
import csv
import re

def detect_metadata_rows(text, sep=","):
    """
    Detect whether metadata rows exist above the true header row.

    This version contains no helper functions - everything is written inline
    with clear comments so beginners can follow the logic.
    """

    # ------------------------------------------------------------
    # STEP 1 - Parse the CSV safely
    # ------------------------------------------------------------
    # Use csv.reader instead of split(',') so that quoted commas (e.g., "APHA, AWWA, WPCF") stay inside a single cell.
    # using split(','), those would incorrectly become 3 cells.
    raw_lines = text.splitlines()
    reader = csv.reader(raw_lines, delimiter=sep)
    split_lines = [row for row in reader]

    # If the file is empty, we cannot detect anything
    if not split_lines:
        return False, None

    # ------------------------------------------------------------
    # STEP 2 - Determine the maximum row width
    # ------------------------------------------------------------
    # The real header row is usually one of the widest rows in the file.
    row_widths = [len(r) for r in split_lines]
    max_width = max(row_widths)

    # ------------------------------------------------------------
    # STEP 3 - Define thresholds for deciding what looks like a header
    # ------------------------------------------------------------
    HEADER_THRESHOLD = 0.9        # Row must be almost full width
    NONEMPTY_THRESHOLD = 0.6      # Row must have many non-empty cells
    HEADER_TOKEN_THRESHOLD = 0.5  # At least half must look like header labels

    header_index = None

    # ------------------------------------------------------------
    # STEP 4 - Scan each row and evaluate whether it looks like a header
    # ------------------------------------------------------------
    for i, row in enumerate(split_lines):

        # -----------------------------
        # 4A - Check row width
        # -----------------------------
        # If the row is much narrower than the widest row,
        # it's probably metadata or junk.
        width = len(row)
        if width < HEADER_THRESHOLD * max_width:
            continue

        # -----------------------------
        # 4B - Check non-empty density
        # -----------------------------
        # Count how many cells are non-empty.
        nonempty_count = sum(1 for c in row if c.strip() != "")
        nonempty_fraction = nonempty_count / max_width

        if nonempty_fraction < NONEMPTY_THRESHOLD:
            continue

        # -----------------------------
        # 4C - Check how "header-like" the cells are
        # -----------------------------
        # A header cell usually:
        #   - is not empty
        #   - does not start with a number
        #   - is not a date
        #   - is not a sample number (SN...)
        header_like_count = 0

        for cell in row:
            cell_stripped = cell.strip()

            # Empty cells are not header-like
            if cell_stripped == "":
                continue

            # If it starts with a digit, it's probably data
            if re.match(r"^\d", cell_stripped):
                continue

            # If it looks like a date (YYYY-MM-DD), it's not a header
            if re.match(r"^\d{4}-\d{2}-\d{2}", cell_stripped):
                continue

            # If it contains "SN", it's likely a sample number
            if "SN" in cell_stripped.upper():
                continue

            # If none of the above disqualified it, count it as header-like
            header_like_count += 1

        header_token_fraction = header_like_count / max_width

        if header_token_fraction < HEADER_TOKEN_THRESHOLD:
            continue

        # If we reach this point, this row satisfies all header criteria
        header_index = i
        break

    # ------------------------------------------------------------
    # STEP 5 - Determine whether metadata exists above the header
    # ------------------------------------------------------------
    # If the header is not the first row (index 0), then metadata exists.
    has_metadata = header_index not in (0, None)

    return has_metadata, header_index
















# ---------------------------------------------------------
# Main upload function
# ---------------------------------------------------------
def fileuploadfunc():
    st.markdown("#### ⏫ Upload CSV or TXT File(s)")

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
        st.session_state.task_cache = {}


    uploaded_files = st.file_uploader(
        "Add files",
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
            # STEP 1: Metadata detection
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

        # -------------------------------------------------
        # Ensure undo/redo structures exist for all files
        # -------------------------------------------------
        for fname in st.session_state.current_data:
            st.session_state.row_map.setdefault(fname, [])
            st.session_state.history_stack.setdefault(fname, [])
            st.session_state.redo_stack.setdefault(fname, [])
            st.session_state.task_history.setdefault(fname, [])

        st.session_state.files_processed = True
        st.success("Files uploaded and initialized.")

    return uploaded_files or []
