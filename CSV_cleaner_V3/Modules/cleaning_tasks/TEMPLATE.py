import pandas as pd

def my_task(df: pd.DataFrame, *, param1=None, param2=None):
    """
    Short, plain-language description of what this task does.

    Parameters
    ----------
    df : pd.DataFrame
        The input dataframe.
    param1, param2 : any
        Task-specific parameters supplied by the widget layer.

    Returns
    -------
    cleaned_df : pd.DataFrame
        The transformed dataframe.
    summary : dict
        A dictionary describing the changes made by the task.
    summary_df : pd.DataFrame or None
        Optional supplementary table for display.
    """

    # -----------------------------------------------------
    # 1. HARD VALIDATION (raise errors)
    # -----------------------------------------------------
    # These checks stop execution immediately if the task
    # cannot run safely or meaningfully.
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    # Example:
    # if "col_x" not in df.columns:
    #     raise ValueError("Column 'col_x' is required for this task.")

    # -----------------------------------------------------
    # 2. SOFT VALIDATION
    # -----------------------------------------------------
    # These checks do not stop execution. They adjust behavior
    # or record warnings in the summary.
    warnings = []

    # Example:
    # if df["col_x"].isna().any():
    #     warnings.append("Column 'col_x' contains missing values.")

    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------
    cleaned_df = df.copy()

    # Example:
    # cleaned_df["new_col"] = cleaned_df["col_x"] * 2

    # -----------------------------------------------------
    # 4. SUMMARY DICTIONARY
    # -----------------------------------------------------
    summary = {
        # "columns_added": ["new_col"],
        # "rows_modified": len(cleaned_df),
    }

    if warnings:
        summary["warnings"] = warnings

    # -----------------------------------------------------
    # 5. OPTIONAL SUMMARY DATAFRAME
    # -----------------------------------------------------
    summary_df = None
    # Example:
    # summary_df = pd.DataFrame({
    #     "column": ["new_col"],
    #     "description": ["Created by task"]
    # })

    # -----------------------------------------------------
    # 6. RETURN STANDARDIZED OUTPUT
    # -----------------------------------------------------
    return cleaned_df, summary, summary_df
