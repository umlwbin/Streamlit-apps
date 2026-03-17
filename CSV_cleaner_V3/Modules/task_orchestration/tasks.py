import streamlit as st

# Import task class
from Modules.task_orchestration.task_class import Task

# ---------------------------------------------------------
# Import processing functions
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
# Import widgets
# ---------------------------------------------------------
from Modules.task_widgets import (
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

# ---------------------------------------------------------
# Import summary renderers
# ---------------------------------------------------------
from Modules.summaries.split_column_summary import render_split_column_summary
from Modules.summaries.add_column_summary import render_add_column_summary
from Modules.summaries.add_row_summary import render_add_row_summary
from Modules.summaries.assign_datatype_summary import render_assign_datatype_summary
from Modules.summaries.headers_summary import render_clean_headers_summary
from Modules.summaries.add_rvqs_summary import render_add_rvqs_summary
from Modules.summaries.iso_summary import render_iso_summary
from Modules.summaries.merge_date_time_summary import render_merge_date_time_summary
from Modules.summaries.merge_files_summary import render_merge_files_summary
from Modules.summaries.merge_header_rows_summary import render_merge_header_rows_summary
from Modules.summaries.parse_dates_summary import render_parse_dates_summary
from Modules.summaries.provincial_pivot_summary import render_provincial_pivot_summary
from Modules.summaries.remove_columns_summary import render_remove_columns_summary
from Modules.summaries.rename_summary import render_rename_summary
from Modules.summaries.reorder_columns_summary import render_reorder_columns_summary
from Modules.summaries.reshape_summary import render_reshape_summary
from Modules.summaries.tidy_data_summary import render_tidy_data_summary
from Modules.summaries.remove_metadata_rows_summary import render_remove_metadata_rows_summary


# ---------------------------------------------------------
# TASK REGISTRY (single source of truth)
# ---------------------------------------------------------
TASKS = [

    Task(
        "Tidy Data Checker",
        tidy_data.basic_cleaning,
        tidy_data_widgets.tidy_data_widgets,
        "Run a general cleaning pass: remove empty rows and columns, standardize NaNs, "
        "trim whitespace, fix duplicates, detect mixed types, and clean headers.",
        type="single",
        summary_renderer=render_tidy_data_summary,
    ),

    Task(
        "Add columns",
        add_columns.add_cols,
        add_columns_widgets.how_many_vars_widget,
        "Add one or more new columns with user defined values.",
        type="single",
        summary_renderer=render_add_column_summary,
    ),

    Task(
        "Add rows",
        add_rows.add_row,
        add_rows_widgets.add_row_widget,
        "Add a new row at the top of the table.",
        type="single",
        summary_renderer=render_add_row_summary,
    ),

    Task(
        "Add Result Value Qualifiers (RVQs)",
        add_rvqs.apply_rvq_rules,
        add_rvqs_widgets.add_rvqs_widget,
        "Detect numeric variables and add Result Value Qualifiers.",
        type="single",
        summary_renderer=render_add_rvqs_summary,
    ),

    Task(
        "Assign and Standardize Data Types",
        assign_datatype.assign_datatype,
        assign_datatype_widgets.assign_datatype_widgets,
        "Assign or standardize data types for selected columns.",
        type="single",
        summary_renderer=render_assign_datatype_summary,
    ),

    Task(
        "Clean column headers",
        headers.clean_headers,
        headers_widgets.headers_widgets,
        "Clean messy headers and ensure uniqueness.",
        type="single",
        summary_renderer=render_clean_headers_summary,
    ),

    Task(
        "Convert DateTime column to ISO format",
        iso.convert_to_iso,
        iso_widgets.iso_widgets,
        "Convert a timestamp column into ISO 8601 format.",
        type="single",
        summary_renderer=render_iso_summary,
    ),

    Task(
        "Merge multiple files",
        merge_files.merge_files,
        merge_files_widgets.merge_widgets,
        "Combine multiple uploaded files into a single dataset.",
        type="multi",
        summary_renderer=render_merge_files_summary,
    ),

    Task(
        "Merge date and time columns",
        merge_date_time.merge_date_time,
        merge_date_time_widgets.merge_date_time_widgets,
        "Combine separate date and time columns into a single timestamp.",
        type="single",
        summary_renderer=render_merge_date_time_summary,
    ),

    Task(
        "Parse Date",
        parse_dates.parse_dates,
        parse_dates_widgets.parse_dates_widgets,
        "Parse a date column using a specified format.",
        type="single",
        summary_renderer=render_parse_dates_summary,
    ),

    Task(
        "Reorder columns",
        reorder_columns.reorder_columns,
        reorder_columns_widgets.reorder_columns_widget,
        "Drag and drop columns into a new order.",
        type="single",
        summary_renderer=render_reorder_columns_summary,
    ),

    Task(
        "Remove columns",
        remove_columns.remove_columns,
        remove_columns_widgets.remove_columns_widgets,
        "Remove one or more columns from the dataset.",
        type="single",
        summary_renderer=render_remove_columns_summary,
    ),

    Task(
        "Remove Metadata Rows",
        remove_metadata_rows.remove_metadata_rows,
        remove_metadata_rows_widgets.remove_metadata_rows_widget,
        "Remove unwanted metadata rows above the data table.",
        type="single",
        summary_renderer=render_remove_metadata_rows_summary,
    ), 

    Task(
        "Rename columns",
        rename.rename_columns,
        rename_widgets.rename_widgets,
        "Rename one or more columns.",
        type="single",
        summary_renderer=render_rename_summary,
    ),

    Task(
        "Reshape Data - Transpose or Pivot",
        reshape.reshape,
        reshape_widgets.reshape_widgets,
        "Transpose the table or reshape between wide and long formats.",
        type="single",
        summary_renderer=render_reshape_summary,
    ),

    Task(
        "Split columns",
        split_cols.split_column,
        split_cols_widgets.split_column_widget,
        "Split cells containing multiple values using user selected delimiters.",
        type="single",
        summary_renderer=render_split_column_summary,
    ),

    Task(
        "🧪 Provincial Chemistry Pivot",
        provincial_pivot.provincial_pivot,
        provincial_pivot_widgets.provincial_pivot_widget,
        "Restructure provincial chemistry files by pivoting variables into columns.",
        type="single",
        summary_renderer=render_provincial_pivot_summary,
    ),

    Task(
        "🧪 Merge Header Rows",
        merge_header_rows.merge_header_rows,
        merge_header_rows_widgets.merge_header_rows_widget,
        "Merge one or two metadata rows into the header row.",
        type="single",
        summary_renderer=render_merge_header_rows_summary,
    ),

]

# ---------------------------------------------------------
# Build lookup dictionary
# ---------------------------------------------------------
TASK_DICT = {task.name: task for task in TASKS}


# ---------------------------------------------------------
# WIDGET ROUTING
# ---------------------------------------------------------
def get_task_inputs(task_name):
    task = TASK_DICT.get(task_name)
    if not task:
        st.error("Task not found.")
        return None

    widget = task.widget
    if not widget:
        return {}

    filenames = list(st.session_state.current_data.keys())
    if not filenames:
        st.error("No files loaded.")
        return None

    # Tasks that should NOT receive df
    if task_name in ["Tidy Data Checker", "🧪 Merge Header Rows"]:
        return widget()

    # All other tasks receive df
    df = st.session_state.current_data[filenames[0]]
    return widget(df)


def get_all_task_names():
    return list(TASK_DICT.keys())
