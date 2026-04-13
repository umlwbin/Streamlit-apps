import streamlit as st
import pandas as pd
from Modules.task_orchestration import tasks
from Modules.summaries.summary_display import show_summary


# ---------------------------------------------------------
# Run a task function safely so the app never crashes
# ---------------------------------------------------------
def _safe_execute(task_func, df, **kwargs):
    try:
        cleaned_df, summary, summary_df = task_func(df, **kwargs)
        return (cleaned_df, summary, summary_df), None

    except Exception as e:
        # Convert exception into a summary-like structure
        error_summary = {
            "errors": [
                {
                    "error_type": type(e).__name__,
                    "message": str(e),
                }
            ]
        }
        return None, error_summary


# ---------------------------------------------------------
# Remove empty or irrelevant fields from summaries
# ---------------------------------------------------------
def _clean_summary(summary):
    if not summary:
        return {}

    cleaned = {}
    for k, v in summary.items():

        # Ensure row_map is not removed
        if k == "row_map":
            cleaned[k] = v
            continue

        # Skip None or empty strings
        if v is None or v == "":
            continue

        # Skip empty lists or dicts
        if isinstance(v, (list, dict)) and len(v) == 0:
            continue

        # Skip empty DataFrames or Series
        if hasattr(v, "empty") and v.empty:
            continue

        cleaned[k] = v

    return cleaned


# ---------------------------------------------------------
# Handle RVQ tasks (these return a third DataFrame)
# ---------------------------------------------------------
def _handle_rvq_output(filename, summary_df):
    if (
        summary_df is not None
        and isinstance(summary_df, pd.DataFrame)
        and "Detection Limit" in summary_df.columns
    ):
        if "supplementary_outputs" not in st.session_state:
            st.session_state.supplementary_outputs = {}

        st.session_state.supplementary_outputs[f"{filename}_RVQ_summary.csv"] = summary_df


# ---------------------------------------------------------
# Apply a task to a single file
# ---------------------------------------------------------
def _run_single_file(task_func, renderer, filename, df, kwargs):

    # Save undo history
    st.session_state.history_stack[filename].append({
        "df": st.session_state.current_data[filename].copy(),
        "row_map": st.session_state.row_map[filename].copy()
    })
    st.session_state.redo_stack[filename] = []

    # Always use the authoritative DataFrame
    current_df = st.session_state.current_data[filename].copy()
    
    # Run the task safely
    # ************************
    result, error_summary = _safe_execute(task_func, current_df, filename=filename, **kwargs)
    # ************************

    if error_summary:
        show_summary(error_summary, renderer=renderer, title="Error", filename=filename)
        st.session_state.task_applied = False
        return

    cleaned_df, summary, summary_df = result

    # Update stored data
    st.session_state.current_data[filename] = cleaned_df
    st.session_state.task_history[filename].append(task_func.__name__)

    # Update row_map if provided
    if "row_map" in summary:
        st.session_state.row_map[filename] = summary["row_map"]


    # Handle RVQ tasks
    _handle_rvq_output(filename, summary_df)

    # Clean summary
    summary = _clean_summary(summary)

    # Store & show summary
    if summary:
        st.session_state.all_summaries[filename] = summary
        st.info("Expand for summary")
        show_summary(summary, renderer=renderer, title="**Task Summary**", filename=filename)
    else:
        st.success(f"Task applied successfully to {filename}")

    st.session_state.task_applied = True
    st.session_state.merge_header_rows_submitted = False



# ---------------------------------------------------------
# Apply a multi-file task
# ---------------------------------------------------------
def _run_multi_file(task_func, renderer, kwargs):

    result, error_summary = _safe_execute(task_func, st.session_state.current_data, **kwargs)

    if error_summary:
        show_summary(error_summary, renderer=renderer, title="Error", filename="merged_output.csv")
        st.session_state.task_applied = False
        return

    merged_df, summary, summary_df = result
    merged_filename = "merged_output.csv"

    # Store merged output
    st.session_state.original_data[merged_filename] = merged_df.copy()
    st.session_state.current_data[merged_filename] = merged_df.copy()

    # Store summary
    summary = _clean_summary(summary)
    if summary:
        st.session_state.all_summaries[merged_filename] = summary
        show_summary(summary, renderer=renderer, title="Task Summary", filename=merged_filename)
    else:
        st.success("Task applied successfully.")

    # Initialize history
    st.session_state.task_history[merged_filename] = [task_func.__name__]
    st.session_state.history_stack[merged_filename] = []
    st.session_state.redo_stack[merged_filename] = []

    st.session_state.task_applied = True


# ---------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------
def run_task(task_name, **kwargs):
    """
    Main entry point for running any task.

    This function:
        1. Looks up the task
        2. Runs it safely
        3. Updates session state
        4. Displays summaries
    """

    if not st.session_state.current_data:
        st.warning("No data available to run tasks on.")
        return

    # -----------------------------------------
    # Lookup using TASK_DICT (Task objects)
    # -----------------------------------------
    task = tasks.TASK_DICT.get(task_name)
    if not task:
        st.error(f"Task '{task_name}' not found.")
        return

    task_type = task.type
    task_func = task.func
    renderer = task.summary_renderer

    # -----------------------------------------
    # Loop through ALL the files and run task depending on type 
    # -----------------------------------------
    if task_type == "single":
        for filename, df in st.session_state.current_data.items():
            _run_single_file(task_func, renderer, filename, df, kwargs)

    elif task_type == "multi":
        _run_multi_file(task_func, renderer, kwargs)
