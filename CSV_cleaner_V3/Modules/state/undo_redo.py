import streamlit as st
import pandas as pd

# =========================================================
# FAST + SAFE DATAFRAME COPY (used for Undo/Redo snapshots)
# =========================================================
# Why this exists:
#   Pandas' normal df.copy() performs a *full deep copy* of every
#   internal data block. This is very slow on large CSV files and undo/redo require taking snapshots often.
#
# What this function does:
#   1. Makes a *shallow* copy of the DataFrame wrapper; This is instant (no data duplicated yet)
#   2. Deep-copies ONLY the underlying BlockManager
#      - This duplicates the actual column data safely
#      - But avoids Pandas' expensive full-copy overhead

# =========================================================
def _fast_deepcopy_df(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy(deep=False)              # cheap wrapper copy
    df_copy._mgr = df._mgr.copy(deep=True)    # deep copy underlying blocks
    return df_copy


# =========================================================
# Helper: Build a complete file-state snapshot
# =========================================================
def _get_state(filename):
    """Return a full snapshot of the file state (df + row_map)."""
    return {
        "df": _fast_deepcopy_df(st.session_state.current_data[filename]),
        "row_map": st.session_state.row_map[filename].copy(),
    }


# =========================================================
# Helper: Restore a file-state snapshot
# =========================================================
def _restore_state(filename, state):
    """Restore df + row_map from a saved snapshot."""
    st.session_state.current_data[filename] = state["df"]
    st.session_state.row_map[filename] = state["row_map"]


# =========================================================
# Reset all files to their original state
# =========================================================
def reset_all_files():
    for filename in st.session_state.original_data:

        # Restore original DataFrame (fast deep copy)
        st.session_state.current_data[filename] = _fast_deepcopy_df(
            st.session_state.original_data[filename]
        )

        # Reset row_map to 1-based index
        n = len(st.session_state.original_data[filename])
        st.session_state.row_map[filename] = list(range(1, n + 1))

        # Reset history
        st.session_state.task_history[filename] = []
        st.session_state.history_stack[filename] = []
        st.session_state.redo_stack[filename] = []

    # Reset flags + metadata
    st.session_state.task_applied = False
    st.session_state.metadata_outputs = {}
    st.session_state.supplementary_outputs = {}

    # Clear caches
    st.session_state.preview_cache = {}


# =========================================================
# Undo last task
# =========================================================
def undo_last_task():
    for filename in st.session_state.current_data:

        if st.session_state.history_stack[filename]:

            # Save current state to redo stack
            st.session_state.redo_stack[filename].append(_get_state(filename))

            # Restore previous state
            prev_state = st.session_state.history_stack[filename].pop()
            _restore_state(filename, prev_state)

            # Update task history
            if st.session_state.task_history[filename]:
                st.session_state.task_history[filename].pop()


# =========================================================
# Redo last undone task
# =========================================================
def redo_last_task():
    for filename in st.session_state.current_data:

        if st.session_state.redo_stack[filename]:

            # Save current state to undo stack
            st.session_state.history_stack[filename].append(_get_state(filename))

            # Restore redo state
            next_state = st.session_state.redo_stack[filename].pop()
            _restore_state(filename, next_state)


# =========================================================
# Restart app
# =========================================================
def restart_app():
    """
    Completely reset the application state:
    - Remove all loaded files
    - Clear all DataFrames and row_maps
    - Clear all history stacks and summaries
    - Reset task flags
    - Remove all widget states so UI fully resets
    """

    # File-related states
    st.session_state.original_data = {}
    st.session_state.current_data = {}
    st.session_state.row_map = {}

    # History
    st.session_state.history_stack = {}
    st.session_state.redo_stack = {}
    st.session_state.task_history = {}

    # Metadata
    st.session_state.all_summaries = {}
    st.session_state.supplementary_outputs = {}
    st.session_state.metadata_outputs = {}

    # Flags
    st.session_state.task_applied = False
    st.session_state.merge_header_rows_submitted = False

    # UI selections
    st.session_state.selected_task = None
    st.session_state.selected_file = None

    # Reset file upload widget
    st.session_state.uploader_key += 1

    # Clear caches
    st.session_state.preview_cache = {}

    # -----------------------------------------------------
    # Remove all widget keys so UI fully resets
    # -----------------------------------------------------
    keys_to_clear = [
        k for k in st.session_state.keys()
        if k not in ["uploader_key"]  # keep uploader_key
    ]

    for k in keys_to_clear:
        st.session_state.pop(k, None)
