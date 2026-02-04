import streamlit as st

def init_session_state():
    default_values = {
        # Data storage
        "original_data": {},      # filename → original df
        "current_data": {},       # filename → cleaned df
        "task_history": {},       # filename → list of past tasks
        "history_stack": {},      # filename → undo stack
        "redo_stack": {},         # filename → redo stack

        # File upload state
        "uploaded_files": [],
        "files_processed": False,

        # Type selection (used in Assign Data Type)
        "selected_types": {},

        #when a task is applied
        "task_applied": False,

        # Widget flags (only keep the ones actually used)
        "cleanupContinue": False,

        # Summaries
        "all_summaries": {},
    }

    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_widget_flags():
    """
    Reset all widget flags that follow the 'Next' pattern.
    This keeps widgets predictable when new files are uploaded.
    """
    for key in list(st.session_state.keys()):
        if "Next" in key and "WidgetKey" not in key:
            st.session_state[key] = False