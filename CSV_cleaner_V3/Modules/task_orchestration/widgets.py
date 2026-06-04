# Modules/task_orchestration/widgets.py
from Modules.task_widgets.add_columns_widgets import how_many_vars_widget
from Modules.task_widgets.add_rows_widgets import add_row_widget
from Modules.task_widgets.assign_datatype_widgets import assign_datatype_widgets
from Modules.task_widgets.iso_widgets import iso_widgets
from Modules.task_widgets.merge_date_time_widgets import merge_date_time_widgets
from Modules.task_widgets.add_rvqs_widgets import add_rvqs_widget
from Modules.task_widgets.merge_files_widgets import merge_widgets
from Modules.task_widgets.headers_widgets import headers_widgets
from Modules.task_widgets.merge_header_rows_widgets import merge_header_rows_widget
from Modules.task_widgets.parse_dates_widgets import parse_dates_widgets
from Modules.task_widgets.provincial_pivot_widgets import provincial_pivot_widget
from Modules.task_widgets.remove_columns_widgets import remove_columns_widgets
from Modules.task_widgets.remove_metadata_rows_widgets import remove_metadata_rows_widget
from Modules.task_widgets.rename_widgets import rename_widgets
from Modules.task_widgets.reorder_columns_widgets import reorder_columns_widget
from Modules.task_widgets.reshape_widgets import reshape_widgets
from Modules.task_widgets.split_cols_widgets import split_column_widget
from Modules.task_widgets.tidy_data_widgets import tidy_data_widgets
from Modules.task_widgets.merge_ymd_widgets import merge_ymd_widgets
from Modules.task_widgets.remove_rows_widgets import remove_rows_widgets


# ---------------------------------------------------------
# WIDGET REGISTRY
# ---------------------------------------------------------
# Each widget returns a dict of kwargs for the task.
# ---------------------------------------------------------
WIDGETS = {
    "Tidy Data Checker":tidy_data_widgets,
    "Add columns" : how_many_vars_widget,
    "Add rows":add_row_widget,
    "Add Result Value Qualifiers (RVQs)":add_rvqs_widget,
    "Assign and Standardize Data Types": assign_datatype_widgets,
    "Clean column headers":headers_widgets,
    "Convert DateTime column to ISO format":iso_widgets,
    "Merge multiple files":merge_widgets,
    "Merge year, month, day columns":merge_ymd_widgets,
    "Merge date and time columns":merge_date_time_widgets,
    "Parse Date":parse_dates_widgets,
    "Reorder columns":reorder_columns_widget,
    "Remove columns":remove_columns_widgets,
    "Remove rows":remove_rows_widgets,
    "Remove Metadata Rows":remove_metadata_rows_widget,
    "Rename columns":rename_widgets,
    "Reshape Data - Transpose or Pivot":reshape_widgets,
    "Split columns":split_column_widget,
    "🧪 Provincial Chemistry Pivot":provincial_pivot_widget,
    "🧪 Merge Header Rows":merge_header_rows_widget
}
