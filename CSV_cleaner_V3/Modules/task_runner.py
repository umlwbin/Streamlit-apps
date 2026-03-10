import streamlit as st
import pandas as pd
from Modules import tasks
from Modules.widgets.summaries.summary_display import show_summary


# ---------------------------------------------------------
# Run a task function safely so the app never crashes
# ---------------------------------------------------------
def _safe_execute(task_func, df, **kwargs):
    try:
        return task_func(df, **kwargs), None
    except Exception as e:
        return None, {
            "errors": [
                {
                    "error_type": type(e).__name__,
                    "message": str(e),
                }
            ]
        }


# ---------------------------------------------------------
# Normalize the return value from a task
# Ensures we always get: cleaned_df, summary, summary_df
# ---------------------------------------------------------
def _normalize_result(result):
    if not isinstance(result, tuple): #Is the result a tuple? If not treat the netire result as the cleaned df (no summary, no extra table)
        return result, {}, None

    if len(result) == 3:
        return result #This is in the case of RVQs if you go to wheere it is called you'll see --> cleaned_df, summary, summary_df = _normalize_result(result)
    if len(result) == 2:
        cleaned_df, summary = result
        return cleaned_df, summary, None

    return result[0], {}, None


# ---------------------------------------------------------
# Remove empty or irrelevant fields from summaries
# ---------------------------------------------------------
def _clean_summary(summary):
    if not summary:
        return {}

    cleaned = {}
    for k, v in summary.items():

        # Skip None or empty strings
        if v is None or v == "":
            continue

        # Skip empty lists or dicts
        if isinstance(v, (list, dict)) and len(v) == 0:
            continue

        # Skip empty DataFrames or Series
        if hasattr(v, "empty") and v.empty: # Does the object have an emoty attribute? then skip.
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

        st.session_state.supplementary_outputs[
            f"{filename}_RVQ_summary.csv"
        ] = summary_df


# ---------------------------------------------------------
# Apply a task to a single file
# ---------------------------------------------------------
def _run_single_file(task_func, filename, df, kwargs):
    # Save undo history
    st.session_state.history_stack[filename].append(df.copy())
    st.session_state.redo_stack[filename] = []

    # Run the task safely
    result, error_summary = _safe_execute(task_func, df.copy(), **kwargs)

    if error_summary:
        show_summary(error_summary, title="Error", filename=filename)
        st.session_state.task_applied = False
        return

    # Normalize the result
    cleaned_df, summary, summary_df = _normalize_result(result)

    # Update stored data
    st.session_state.current_data[filename] = cleaned_df
    st.session_state.task_history[filename].append(task_func.__name__)

    # Handle RVQ tasks
    _handle_rvq_output(filename, summary_df)

    # Clean summary
    summary = _clean_summary(summary)

    # Store summary
    if summary:
        st.session_state.all_summaries[filename] = summary
        show_summary(summary, title="Task Summary", filename=filename)
    else:
        st.success(f"Task applied successfully to {filename}")

    st.session_state.task_applied = True


# ---------------------------------------------------------
# Apply a multi-file task
# ---------------------------------------------------------
def _run_multi_file(task_func, kwargs):
    result, error_summary = _safe_execute(
        task_func, st.session_state.current_data, **kwargs
    )

    if error_summary:
        show_summary(error_summary, title="Error", filename="merged_output.csv")
        st.session_state.task_applied = False
        return

    merged_df, summary, _ = _normalize_result(result)
    merged_filename = "merged_output.csv"

    # Store merged output
    st.session_state.original_data[merged_filename] = merged_df.copy()
    st.session_state.current_data[merged_filename] = merged_df.copy()

    # Store summary
    if summary:
        st.session_state.all_summaries[merged_filename] = summary
        show_summary(summary, title="Task Summary", filename=merged_filename)
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

    task_info = tasks.define_task_functions()[task_name]
    task_type = task_info["type"]
    task_func = task_info["func"]

    if task_type == "single":
        for filename, df in st.session_state.current_data.items():
            _run_single_file(task_func, filename, df, kwargs)

    elif task_type == "multi":
        _run_multi_file(task_func, kwargs)
