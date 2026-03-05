import streamlit as st
import pandas as pd
from Modules import tasks
from Modules.widgets.summary_display import show_summary


# ---------------------------------------------------------
# SAFE EXECUTION WRAPPER
# ---------------------------------------------------------
def _safe_execute(task_func, df, **kwargs):
    """
    Execute a task function safely.

    Returns:
        (result, error_summary)
        - result: whatever the task function returns, or None on error
        - error_summary: dict with structured error info, or None
    """
    try:
        result = task_func(df, **kwargs)
        return result, None

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
# MAIN TASK RUNNER
# ---------------------------------------------------------
def run_task(task_name, **kwargs):
    if not st.session_state.current_data:
        st.warning("No data available to run tasks on.")
        return

    task_info = tasks.define_task_functions()[task_name]
    task_type = task_info["type"]
    task_func = task_info["func"]

    # ---------------------------------------------------------
    # Helper: Deep-clean summary dict
    # ---------------------------------------------------------
    def _clean_summary(summary):
        if not summary:
            return {}

        cleaned = {}
        for k, v in summary.items():

            # Remove None, False, empty string
            if v in (None, False, ""):
                continue

            # Remove empty list or empty dict
            if isinstance(v, (list, dict)) and len(v) == 0:
                continue

            # Remove empty DataFrame or empty Series
            if hasattr(v, "empty") and v.empty:
                continue

            cleaned[k] = v

        return cleaned

    # ---------------------------------------------------------
    # SINGLE-FILE TASKS
    # ---------------------------------------------------------
    if task_type == "single":

        for filename in list(st.session_state.current_data.keys()):
            df = st.session_state.current_data[filename]

            # Save state for undo
            st.session_state.history_stack[filename].append(df.copy())
            st.session_state.redo_stack[filename] = []

            # ---------------------------------------------------------
            # SAFE EXECUTION
            # ---------------------------------------------------------
            result, error_summary = _safe_execute(task_func, df.copy(), **kwargs)

            # If the task crashed, show error and DO NOT update df
            if error_summary:
                show_summary(error_summary, title="Error", filename=filename)
                st.session_state.task_applied = False
                continue

            # ---------------------------------------------------------
            # NORMAL RESULT HANDLING
            # ---------------------------------------------------------
            cleaned_df, summary, summary_df = None, {}, None

            if isinstance(result, tuple):
                if len(result) == 3:
                    cleaned_df, summary, summary_df = result
                elif len(result) == 2:
                    cleaned_df, summary = result
                else:
                    cleaned_df = result[0]
            else:
                cleaned_df = result

            # Update dataset
            st.session_state.current_data[filename] = cleaned_df
            st.session_state.task_history[filename].append(task_name)

            # ---------------------------------------------------------
            # Detect RVQ task automatically
            # ---------------------------------------------------------
            is_rvq_task = (
                summary_df is not None
                and isinstance(summary_df, pd.DataFrame)
                and "Detection Limit" in summary_df.columns
            )

            if is_rvq_task:
                summary["_rvq_task"] = True
                summary["detection_limits"] = {}

                for _, row in summary_df.iterrows():
                    var = row["Variable"]
                    rvq = row["RVQ Code"]
                    limit = row["Detection Limit"]
                    count = row["Count"]

                    summary["detection_limits"].setdefault(var, {})
                    summary["detection_limits"][var].setdefault(rvq, {})
                    summary["detection_limits"][var][rvq][limit] = count

                if "supplementary_outputs" not in st.session_state:
                    st.session_state.supplementary_outputs = {}
                st.session_state.supplementary_outputs[
                    f"{filename}_RVQ_summary.csv"
                ] = summary_df

            # ---------------------------------------------------------
            # Clean summary deeply
            # ---------------------------------------------------------
            summary = _clean_summary(summary)

            # ---------------------------------------------------------
            # Store summary only if non-empty
            # ---------------------------------------------------------
            if summary:
                st.session_state.all_summaries[filename] = summary
            else:
                st.session_state.all_summaries.pop(filename, None)

            # ---------------------------------------------------------
            # Display summary or success message
            # ---------------------------------------------------------
            if summary:
                show_summary(summary, title="Task Summary", filename=filename)
            else:
                st.success(f"Task '{task_name}' applied successfully.")

            st.session_state.task_applied = True

    # ---------------------------------------------------------
    # MULTI-FILE TASKS
    # ---------------------------------------------------------
    elif task_type == "multi":

        result, error_summary = _safe_execute(
            task_func, st.session_state.current_data, **kwargs
        )

        if error_summary:
            show_summary(error_summary, title="Error", filename="merged_output.csv")
            st.session_state.task_applied = False
            return

        if isinstance(result, tuple):
            merged_df, summary = result
        else:
            merged_df = result
            summary = {}

        merged_filename = "merged_output.csv"

        st.session_state.original_data[merged_filename] = merged_df.copy()
        st.session_state.current_data[merged_filename] = merged_df.copy()

        if summary:
            st.session_state.all_summaries[merged_filename] = summary

        if summary:
            show_summary(summary, title="Task Summary", filename=merged_filename)
        else:
            st.success(f"Task '{task_name}' applied successfully.")

        st.session_state.task_history[merged_filename] = [task_name]
        st.session_state.history_stack[merged_filename] = []
        st.session_state.redo_stack[merged_filename] = []

        st.session_state.task_applied = True
