import streamlit as st

def init_session_state():
    default_values = {
        # File data
        "original_data": {},      # filename → original df
        "current_data": {},       # filename → cleaned df
        "row_map": {},            # filename → row_map list

        # Undo/redo
        "history_stack": {},      # filename → list of snapshots
        "redo_stack": {},         # filename → list of snapshots
        "task_history": {},       # filename → list of task names

        # Upload state
        "uploader_key": 0,
        "uploaded_files": [],
        "files_processed": False,
        "non_rectangular_files": set(),

        # Summaries
        "all_summaries": {},
        "supplementary_outputs": {},

        # Task flags
        "task_applied": False,
        "merge_header_rows_submitted": False,

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
