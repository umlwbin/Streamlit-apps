import streamlit as st

'''
See docs/state_bundles.md to read more on the state architecture and flow. Very important for this section.
Contains descriptions of the session state varibales and how they are modified across the different modules. 
'''

# ---------------------------------------------------------
# FULL STATE SNAPSHOT
# ---------------------------------------------------------
def capture_snapshot() -> dict:
    """Capture a complete state bundle."""
    return {
        # --- Core file state ---
        "current_data": {fname: df.copy(deep=True) for fname, df in st.session_state.current_data.items()},  # [deep-copy] see docs/deep_copy.md
        "row_map": {fname: rm.copy() for fname, rm in st.session_state.row_map.items()},
        "metadata_outputs": {
            fname: {task: md.copy() for task, md in tasks.items()}
            for fname, tasks in st.session_state.get("metadata_outputs", {}).items()
        },

        # --- UI state that must be restored for redo to work ---
        "task_applied": st.session_state.get("task_applied", False),
        "selector_index_counter": st.session_state.get("selector_index_counter", 0),
        "clear_selector_flag": st.session_state.get("clear_selector_flag", False),
        "last_uploaded_files": st.session_state.get("last_uploaded_files", None),
        "files_processed": st.session_state.get("files_processed", False),


        # --- Preview + history flags ---
        "preview_cache": {},  # always reset on restore
        "history_step_active": False,  # always false when snapshotting
    }


# ---------------------------------------------------------
# RESTORE SNAPSHOT
# ---------------------------------------------------------
def restore_snapshot(snapshot: dict):
    """Restore the entire application state exactly as it was."""
    # --- Core file state ---
    st.session_state.current_data = {fname: df.copy(deep=True) for fname, df in snapshot["current_data"].items()}
    st.session_state.row_map = {fname: rm.copy() for fname, rm in snapshot["row_map"].items()}
    st.session_state.metadata_outputs = snapshot["metadata_outputs"]


    # --- UI state ---
    st.session_state.task_applied = snapshot["task_applied"]
    st.session_state.selector_index_counter = snapshot["selector_index_counter"]
    st.session_state.clear_selector_flag = snapshot["clear_selector_flag"]
    st.session_state.last_uploaded_files = snapshot["last_uploaded_files"]
    st.session_state.files_processed = snapshot["files_processed"]


    # --- Preview + history flags ---
    st.session_state.preview_cache = {}
    st.session_state.history_step_active = True  # tells app.py to skip task execution

    # CRITICAL: prevent file_uploads from re-processing and overwriting restored state. 
    st.session_state.files_processed = True



# ---------------------------------------------------------
# COMMIT NEW ACTION
# ---------------------------------------------------------
def commit_new_action():
    """
    This function saves the current state as a checkpoint before running a new task, so undo can return to this point.
    It’s basically the “save point” before the app changes anything.
    """
    st.session_state.history_stack.append(capture_snapshot())
    st.session_state.redo_stack = []


# ---------------------------------------------------------
# UNDO
# ---------------------------------------------------------
def undo_last_task():
    """Move one step backward in history."""
    if st.session_state.history_stack:  # Is there at least one snapshot to undo? (This is before the pop)
        previous_snapshot = st.session_state.history_stack.pop()

        # Save current state to redo stack
        st.session_state.redo_stack.append(capture_snapshot())

        # Restore previous state
        restore_snapshot(previous_snapshot)

        st.session_state.clear_selector_flag = True
        st.session_state.preview_cache = {}
        st.session_state.task_applied = len(st.session_state.history_stack) > 0  # Now that we popped a snapshot, does the restored state still contain tasks, or are we back to the beginning?

        st.rerun()


# ---------------------------------------------------------
# REDO
# ---------------------------------------------------------
def redo_last_task():
    """Move one step forward in history."""
    if st.session_state.redo_stack:
        next_snapshot = st.session_state.redo_stack.pop()

        # Save current state back to undo stack
        st.session_state.history_stack.append(capture_snapshot())

        # Restore forward state
        restore_snapshot(next_snapshot)

        st.session_state.clear_selector_flag = True
        st.session_state.preview_cache = {}
        st.session_state.task_applied = True

        st.rerun()


# ---------------------------------------------------------
# RESET TO ORIGINAL FILES
# ---------------------------------------------------------
def reset_all_files():
    """Reset everything back to the pristine raw files."""
    if st.session_state.original_data:
        commit_new_action()

        st.session_state.current_data = {fname: df.copy(deep=True) for fname, df in st.session_state.original_data.items()}
        st.session_state.row_map = {fname: list(range(1, len(df) + 1)) for fname, df in st.session_state.original_data.items()}
        st.session_state.metadata_outputs = {}
        st.session_state.task_applied = False

        st.rerun()


# ---------------------------------------------------------
# FULL APPLICATION RESTART
# ---------------------------------------------------------
def restart_app():
    """Completely purge the application context and reset uploader."""
    st.session_state.original_data = {}
    st.session_state.current_data = {}
    st.session_state.row_map = {}
    st.session_state.history_stack = []
    st.session_state.redo_stack = []
    st.session_state.metadata_outputs = {}
    st.session_state.task_applied = False
    st.session_state.preview_cache = {}

    # Force uploader widget to reset
    st.session_state.uploader_key = st.session_state.get("uploader_key", 0) + 1

    # Clear everything except uploader key
    keys_to_clear = [k for k in st.session_state.keys() if k != "uploader_key"]
    for k in keys_to_clear:
        st.session_state.pop(k, None)
