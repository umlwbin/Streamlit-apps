import streamlit as st

# ---------------------------------------------------------
# Import processing functions
# Each module contains the actual data‑cleaning logic.
# ---------------------------------------------------------
from Modules.cleaning_tasks import (
    add_columns,
    add_rows,
    remove_columns,
    reorder_columns,
    split_cols,
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
    add_rvqs,
    remove_metadata_rows,
)

# ---------------------------------------------------------
# Import widget functions
# Each widget collects user input for its corresponding task.
# ---------------------------------------------------------
from Modules.widgets import (
    add_columns_widgets,
    add_rows_widgets,
    remove_columns_widgets,
    reorder_columns_widgets,
    split_cols_widgets,
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
    add_rvqs_widgets,
    remove_metadata_rows_widgets,
)

# =========================================================
# TASK REGISTRY
# Each entry describes one cleaning task.
# =========================================================

TASKS = [
    {
        "name": "Tidy Data Checker",
        "type": "single",
        "func": tidy_data.basic_cleaning,
        "widget": tidy_data_widgets.tidy_data_widgets,
        "description": "Run a general cleaning pass: remove empty rows and columns, standardize NaNs, trim whitespace, fix duplicates, detect mixed types, and clean headers.",
    },
    {
        "name": "Add columns",
        "type": "single",
        "func": add_columns.add_cols,
        "widget": add_columns_widgets.how_many_vars_widget,
        "description": "Add one or more new columns with user defined values.",
    },
    {
        "name": "Add rows",
        "type": "single",
        "func": add_rows.add_row,
        "widget": add_rows_widgets.add_row_widget,
        "description": "Add a new row at the top of the table.",
    },
    {
        "name": "Reorder columns",
        "type": "single",
        "func": reorder_columns.reorder,
        "widget": reorder_columns_widgets.redorder_widget,
        "description": "Drag and drop columns into a new order.",
    },
    {
        "name": "Remove columns",
        "type": "single",
        "func": remove_columns.remove_cols,
        "widget": remove_columns_widgets.which_cols_widgets,
        "description": "Remove one or more columns from the dataset.",
    },
    {
        "name": "Split columns",
        "type": "single",
        "func": split_cols.split_column,
        "widget": split_cols_widgets.split_column_widget,
        "description": "Split cells containing multiple values using user selected delimiters.",
    },
    {
        "name": "Merge multiple files",
        "type": "multi",
        "func": merge_files.merge,
        "widget": merge_files_widgets.merge_widgets,
        "description": "Combine multiple uploaded files into a single dataset.",
    },
    {
        "name": "Clean column headers",
        "type": "single",
        "func": headers.clean_headers,
        "widget": headers_widgets.headers_widgets,
        "description": "Clean messy headers and ensure uniqueness.",
    },
    {
        "name": "Rename columns",
        "type": "single",
        "func": rename.rename_cols,
        "widget": rename_widgets.rename_widgets,
        "description": "Rename one or more columns.",
    },
    {
        "name": "Merge date and time columns",
        "type": "single",
        "func": merge_date_time.merge,
        "widget": merge_date_time_widgets.merge_date_time_widgets,
        "description": "Combine separate date and time columns into a single timestamp.",
    },
    {
        "name": "Convert DateTime column to ISO format",
        "type": "single",
        "func": iso.convert_to_iso,
        "widget": iso_widgets.iso_widgets,
        "description": "Convert a timestamp column into ISO 8601 format.",
    },
    {
        "name": "Parse Date",
        "type": "single",
        "func": parse_dates.parse_func,
        "widget": parse_dates_widgets.parse_dates_widgets,
        "description": "Parse a date column using a specified format.",
    },
    {
        "name": "Reshape Data - Transpose or Pivot",
        "type": "single",
        "func": reshape.reshape,
        "widget": reshape_widgets.reshape_widgets,
        "description": "Transpose the table or reshape between wide and long formats.",
    },
    {
        "name": "Assign and Standardize Data Types",
        "type": "single",
        "func": assign_datatype.assign,
        "widget": assign_datatype_widgets.assign_datatype_widgets,
        "description": "Assign or standardize data types for selected columns.",
    },
    {
        "name": "🧪 Provincial Chemistry Pivot",
        "type": "single",
        "func": provincial_pivot.provincial_pivot,
        "widget": provincial_pivot_widgets.provincial_pivot_widget,
        "description": "Restructure provincial chemistry files by pivoting variables into columns.",
    },
    {
        "name": "🧪 Merge Header Rows",
        "type": "single",
        "func": merge_header_rows.merge_header_rows,
        "widget": merge_header_rows_widgets.merge_header_rows_widget,
        "description": "Merge one or two metadata rows into the header row.",
    },
    {
        "name": "Add Result Value Qualifiers (RVQs)",
        "type": "single",
        "func": add_rvqs.apply_rvq_rules,
        "widget": add_rvqs_widgets.render,
        "description": "Detect numeric variables and add Result Value Qualifiers.",
    },
    {
        "name": "Remove Metadata Rows",
        "type": "single",
        "func": remove_metadata_rows.remove_metadata_rows,
        "widget": remove_metadata_rows_widgets.remove_metadata_rows_widget,
        "description": "Remove unwanted metadata rows above the data table.",
    },
]

# =========================================================
# Build the task dictionary
# =========================================================
def define_task_functions():
    """
    Convert the TASKS list into a dictionary keyed by task name.
    This makes lookup fast and keeps the registry easy to maintain.
    """
    return {task["name"]: task for task in TASKS}


# =========================================================
# WIDGET ROUTING
# =========================================================
def get_task_inputs(task_name):
    """
    Retrieve widget inputs for the selected task.
    Widgets collect user parameters before running the task.
    """

    task_dict = define_task_functions()
    task_info = task_dict.get(task_name)

    if not task_info:
        st.error("Task not found.")
        return None

    widget = task_info.get("widget")
    if not widget:
        return {}

    # Get the active file
    filenames = list(st.session_state.current_data.keys())
    if not filenames:
        st.error("No files loaded.")
        return None

    df = st.session_state.current_data[filenames[0]]

    # Tidy Data Checker does not need the dataframe
    if task_name == "Tidy Data Checker":
        return widget()

    return widget(df)


def get_all_task_names():
    """
    Return a list of all task names.
    """
    return list(define_task_functions().keys())
