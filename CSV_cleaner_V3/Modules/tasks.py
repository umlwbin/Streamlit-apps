import streamlit as st

# Import all processing functions
from Modules.cleaning_tasks import (
    add_columns,
    remove_columns,
    reorder_columns,
    merge_files,
    headers,
    rename,
    parse_dates,
    tidy_data,
    reshape,
    assign_datatype,
    iso,
    merge_date_time,
    provincial_pivot,
    merge_header_rows,
    add_rvqs
)
import importlib
importlib.reload(headers)

# Import all widget functions
from Modules.widgets import (
    add_columns_widgets,
    remove_columns_widgets,
    reorder_columns_widgets,
    merge_files_widgets,
    headers_widgets,
    rename_widgets,
    parse_dates_widgets,
    tidy_data_widgets,
    reshape_widgets,
    assign_datatype_widgets,
    iso_widgets,
    merge_date_time_widgets,
    provincial_pivot_widgets,
    merge_header_rows_widgets,
    add_rvqs_widgets
)


# =========================================================
# TASK DEFINITIONS
# =========================================================
def define_task_functions():
    """
    Return a dictionary describing all available cleaning tasks.

    Each task entry includes:
        - type: "single" or "multi"
        - func: the processing function
        - widget: the UI widget for collecting inputs
        - description: a short explanation shown in the UI
    """

    return {
        "Tidy Data Checker": {
            "type": "single",
            "func": tidy_data.basic_cleaning,
            "widget": tidy_data_widgets.tidy_data_widgets,
            "description": "Run a general cleaning pass: remove empty rows/columns, standardize NaNs, trim whitespace, fix duplicates, detect mixed types, and clean headers."
        },

        "Add columns": {
            "type": "single",
            "func": add_columns.add_cols,
            "widget": add_columns_widgets.how_many_vars_widget,
            "description": "Add one or more new columns with user‑defined values."
        },

        "Reorder columns": {
            "type": "single",
            "func": reorder_columns.reorder,
            "widget": reorder_columns_widgets.redorder_widget,
            "description": "Drag and drop columns into a new order."
        },

        "Remove columns": {
            "type": "single",
            "func": remove_columns.remove_cols,
            "widget": remove_columns_widgets.which_cols_widgets,
            "description": "Remove one or more columns from the dataset."
        },

        "Merge multiple files": {
            "type": "multi",
            "func": merge_files.merge,
            "widget": merge_files_widgets.merge_widgets,
            "description": "Combine multiple uploaded files into a single dataset."
        },

        "Clean column headers": {
            "type": "single",
            "func": headers.clean_headers,
            "widget": headers_widgets.headers_widgets,
            "description": "Clean messy headers: normalize characters, enforce naming style, and ensure uniqueness."
        },

        "Rename columns": {
            "type": "single",
            "func": rename.rename_cols,
            "widget": rename_widgets.rename_widgets,
            "description": "Rename one or more columns."
        },

        "Merge date and time columns": {
            "type": "single",
            "func": merge_date_time.merge,
            "widget": merge_date_time_widgets.merge_date_time_widgets,
            "description": "Combine separate date and time columns into a single timestamp."
        },

        "Convert DateTime column to ISO format": {
            "type": "single",
            "func": iso.convert_to_iso,
            "widget": iso_widgets.iso_widgets,
            "description": "Convert a timestamp column into ISO‑8601 format."
        },

        "Parse Date": {
            "type": "single",
            "func": parse_dates.parse_func,
            "widget": parse_dates_widgets.parse_dates_widgets,
            "description": "Parse a date column using a specified format."
        },

        "Reshape Data - Transpose or Pivot": {
            "type": "single",
            "func": reshape.reshape,
            "widget": reshape_widgets.reshape_widgets,
            "description": "Transpose the table or reshape between wide and long formats."
        },

        "Assign & Standardize Data Types": {
            "type": "single",
            "func": assign_datatype.assign,
            "widget": assign_datatype_widgets.assign_datatype_widgets,
            "description": "Assign or standardize data types for selected columns, including automatic cleanup of messy date and time formats."
        },

        "🧪 Provincial Chemistry Pivot": {
            "type": "single",
            "func": provincial_pivot.provincial_pivot,
            "widget": provincial_pivot_widgets.provincial_pivot_widget,
            "description": (
                "Restructure provincial chemistry files where variables/parameters "
                "are stored in a column and values in another. Each variable becomes "
                "its own column, and optional metadata (Units, VMV codes, Variable "
                "codes) can be merged into the header names."
            )
        },

        "🧪 Merge Header Rows (Units + VMV)": {
            "type": "single",
            "func": merge_header_rows.merge_header_rows,
            "widget": merge_header_rows_widgets.merge_header_rows_widget,
            "description": "Merge Units and VMV code rows into the header row."
        },

        "Add Result Value Qualifiers (RVQs)":{
            "type": "single",
            "func": add_rvqs.apply_rvq_rules,
            "widget": add_rvqs_widgets.render,
            "description": "Detect numeric variables and add Result Value Qualifiers based on user-defined codes."

        }



    }


# =========================================================
# WIDGET ROUTING
# =========================================================
def get_task_inputs(task_name):
    """
    Retrieve widget inputs for the selected task.
    Widgets are defined directly in the task dictionary.
    """

    tasks = define_task_functions()
    task_info = tasks.get(task_name)

    if not task_info:
        st.error("Task not found.")
        return None

    widget = task_info.get("widget")
    if not widget:
        return {}

    # ---------------------------------------------------------
    # Get the most current file and dataframe
    # ---------------------------------------------------------
    filenames = list(st.session_state.current_data.keys())
    if not filenames:
        st.error("No files loaded.")
        return None

    # The first file is the active file for single-file tasks
    filename = filenames[0]
    df = st.session_state.current_data[filename]

    # ---------------------------------------------------------
    # Special case: Tidy Data does not receive anything
    # ---------------------------------------------------------
    if task_name == "Tidy Data Checker":
        return widget()

    # ---------------------------------------------------------
    # All other widgets receive only the dataframe
    # ---------------------------------------------------------
    return widget(df)