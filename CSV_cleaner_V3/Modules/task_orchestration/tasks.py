# Modules/task_orchestration/tasks.py
from Modules.cleaning_tasks.add_columns import add_cols
from Modules.cleaning_tasks.add_rows import add_row
from Modules.cleaning_tasks.assign_datatype import assign_datatype
from Modules.cleaning_tasks.iso import convert_to_iso
from Modules.cleaning_tasks.merge_date_time import merge_date_time
from Modules.cleaning_tasks.add_rvqs import apply_rvq_rules
from Modules.cleaning_tasks.merge_files import merge_files
from Modules.cleaning_tasks.headers import clean_headers
from Modules.cleaning_tasks.merge_header_rows import merge_header_rows
from Modules.cleaning_tasks.parse_dates import parse_dates
from Modules.cleaning_tasks.provincial_pivot import provincial_pivot
from Modules.cleaning_tasks.remove_columns import remove_columns
from Modules.cleaning_tasks.remove_metadata_rows import remove_metadata_rows
from Modules.cleaning_tasks.rename import rename_columns
from Modules.cleaning_tasks.reorder_columns import reorder_columns
from Modules.cleaning_tasks.reshape import reshape
from Modules.cleaning_tasks.split_cols import split_column
from Modules.cleaning_tasks.tidy_data import basic_cleaning
from Modules.cleaning_tasks.merge_ymd import merge_ymd
from Modules.cleaning_tasks.remove_rows import remove_rows


# ---------------------------------------------------------
# WIDGET REGISTRY
# ---------------------------------------------------------
# Each widget returns a dict of kwargs for the task.
# ---------------------------------------------------------
TASKS = {
    "Tidy Data Checker":basic_cleaning,
    "Add columns" : add_cols,
    "Add rows":add_row,
    "Add Result Value Qualifiers (RVQs)":apply_rvq_rules,
    "Assign and Standardize Data Types": assign_datatype,
    "Clean column headers":clean_headers,
    "Convert DateTime column to ISO format":convert_to_iso,
    "Merge multiple files":merge_files,
    "Merge year, month, day columns":merge_ymd,
    "Merge date and time columns":merge_date_time,
    "Parse Date":parse_dates,
    "Reorder columns":reorder_columns,
    "Remove columns":remove_columns,
    "Remove rows":remove_rows,
    "Remove Metadata Rows":remove_metadata_rows,
    "Rename columns":rename_columns,
    "Reshape Data - Transpose or Pivot":reshape,
    "Split columns":split_column,
    "🧪 Provincial Chemistry Pivot":provincial_pivot,
    "🧪 Merge Header Rows":merge_header_rows
}
