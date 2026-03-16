import streamlit as st

# =========================================================
# Helper: Build a complete file-state snapshot
# =========================================================
def _get_state(filename):
    """Return a full snapshot of the file state (df + row_map)."""
    return {
        "df": st.session_state.current_data[filename].copy(),
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

        # Restore original DataFrame
        st.session_state.current_data[filename] = (
            st.session_state.original_data[filename].copy()
        )

        # Initialize row_map as 1-based index
        n = len(st.session_state.original_data[filename])
        st.session_state.row_map[filename] = list(range(1, n + 1))

        # Reset history
        st.session_state.task_history[filename] = []
        st.session_state.history_stack[filename] = []
        st.session_state.redo_stack[filename] = []

    st.session_state.task_applied = False


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
