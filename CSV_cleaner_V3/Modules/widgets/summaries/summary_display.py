import streamlit as st
import pandas as pd

# Import all task-specific summary renderers
from .split_column_summary import render_split_column_summary
from .add_column_summary import render_add_column_summary
from .add_row_summary import render_add_row_summary
from .assign_datatype_summary import render_assign_datatype_summary
from .headers_summary import render_clean_headers_summary

from .iso_summary import render_iso_summary
from .merge_date_time_summary import render_merge_date_time_summary
from .merge_files_summary import render_merge_files_summary
from .merge_header_rows_summary import render_merge_header_rows_summary
from .parse_dates_summary import render_parse_dates_summary
from .provincial_pivot_summary import render_provincial_pivot_summary
from .remove_columns_summary import render_remove_columns_summary
from .rename_summary import render_rename_summary
from .reorder_columns_summary import render_reorder_columns_summary
from .reshape_summary import render_reshape_summary
from .tidy_data_summary import render_tidy_data_summary
from .remove_metadata_rows_summary import render_remove_metadata_rows_summary



# Registry mapping task_name → renderer function
TASK_SUMMARY_RENDERERS = {
    "split_column": render_split_column_summary,
    "add_column": render_add_column_summary,
    "add_row": render_add_row_summary,
    "assign_datatype": render_assign_datatype_summary,
    "clean_headers": render_clean_headers_summary,

    "iso": render_iso_summary,
    "merge_date_time": render_merge_date_time_summary,
    "merge_files": render_merge_files_summary,
    "merge_header_rows": render_merge_header_rows_summary,
    "parse_dates": render_parse_dates_summary,
    "provincial_pivot": render_provincial_pivot_summary,
    "remove_columns": render_remove_columns_summary,
    "rename": render_rename_summary,
    "reorder_columns": render_reorder_columns_summary,
    "reshape": render_reshape_summary,
    "tidy_data": render_tidy_data_summary,
    "remove_metadata_rows": render_remove_metadata_rows_summary,
}

def show_summary(summary, title="Task Summary", filename=None):
    """
    Robust summary renderer that safely handles:
    - dict-based errors
    - string-based errors
    - mixed formats
    - missing fields
    """

    if not summary:
        return

    label = f"{title}" if filename is None else f"{title} - {filename}"

    with st.expander(label, expanded=False):

        # ---------------------------------------------------------
        # ERROR HANDLING (always shown first)
        # ---------------------------------------------------------
        if "errors" in summary:
            st.markdown("##### ❌ Errors")

            for err in summary["errors"]:

                # Case 1: error is a dict
                if isinstance(err, dict):
                    etype = err.get("error_type", "Error")
                    msg = err.get("message", "")
                    details = err.get("details")

                # Case 2: error is a plain string
                else:
                    etype = "Error"
                    msg = str(err)
                    details = None

                # Display the error
                st.error(f"**{etype}**: {msg}")

                # Optional details block
                if details:
                    with st.expander("Details"):
                        st.write(details)

            return  # stop after showing errors

        # ---------------------------------------------------------
        # TASK-SPECIFIC SUMMARY RENDERING
        # ---------------------------------------------------------
        task_name = summary.get("task_name")

        if task_name in TASK_SUMMARY_RENDERERS:
            TASK_SUMMARY_RENDERERS[task_name](summary, filename)
            return

        # ---------------------------------------------------------
        # FALLBACK: raw summary
        # ---------------------------------------------------------
        st.warning("No summary renderer found for this task.")
        st.json(summary)
