import pandas as pd


def merge_files(
    dfs_dict: dict,
    *,
    add_source=False
):
    """
    Merge multiple DataFrames vertically (row‑wise) into a single DataFrame.

    This task is designed for workflows where a user uploads several files
    that share the same structure (same columns) and wants them combined into
    one dataset. The function performs safe copying, optional source tracking,
    and concatenation with index reset.

    Parameters
    ----------
    dfs_dict : dict[str, pandas.DataFrame]
        A dictionary mapping filenames to DataFrames.
        Example:
            {
                "file1.csv": df1,
                "file2.csv": df2
            }

    add_source : bool, optional
        If True, a new column named 'source_file' is added to each DataFrame
        before merging, containing the filename for each row.

    Returns
    -------
    merged_df : pandas.DataFrame
        The vertically concatenated DataFrame containing all rows from all
        input DataFrames.

    summary : dict
        {
            "merged_files": list of filenames merged,
            "added_source_column": bool,
            "warnings": list of soft validation messages
        }

    summary_df : pandas.DataFrame or None
        Always None for this task (included for template consistency).

    Notes
    -----
    - Hard validation errors (e.g., non‑DataFrame inputs) raise exceptions.
    - Soft validation issues (e.g., mismatched columns) are recorded in
      summary["warnings"] but do not stop execution.
    """

    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors (A, B, C…)
    # -----------------------------------------------------

    # A. dfs_dict must be a dictionary
    if not isinstance(dfs_dict, dict):
        raise ValueError("dfs_dict must be a dictionary of {filename: DataFrame}.")

    # B. Dictionary cannot be empty
    if len(dfs_dict) == 0:
        raise ValueError("dfs_dict is empty - no files to merge.")

    # C. All values must be DataFrames
    for key, val in dfs_dict.items():
        if not isinstance(val, pd.DataFrame):
            raise ValueError(f"Value for '{key}' is not a pandas DataFrame.")

    # -----------------------------------------------------
    # 2. VALIDATION - Soft Checks (A, B, C…)
    # -----------------------------------------------------
    warnings = []

    # A. Warn if DataFrames have different columns
    all_columns = [tuple(df.columns) for df in dfs_dict.values()]
    if len(set(all_columns)) > 1:
        warnings.append(
            "Input files do not share identical columns. "
            "Missing columns will be filled with NaN during merge."
        )

    # B. Warn if any DataFrame is empty
    for filename, df in dfs_dict.items():
        if df.empty:
            warnings.append(f"File '{filename}' is empty.")

    # C. Warn if add_source=True but 'source_file' already exists
    if add_source:
        for filename, df in dfs_dict.items():
            if "source_file" in df.columns:
                warnings.append(
                    f"File '{filename}' already contains a 'source_file' column. "
                    "Existing values will be overwritten."
                )

    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------
    frames = []

    for filename, df in dfs_dict.items():
        temp = df.copy()

        if add_source:
            temp["source_file"] = filename

        frames.append(temp)

    merged_df = pd.concat(frames, ignore_index=True)

    # -----------------------------------------------------
    # 4. SUMMARY
    # -----------------------------------------------------
    summary = {
        "merged_files": list(dfs_dict.keys()),
        "added_source_column": add_source,
        "warnings": warnings,
    }

    # -----------------------------------------------------
    # 5. SUMMARY DATAFRAME
    # -----------------------------------------------------
    summary_df = None

    # -----------------------------------------------------
    # 6. RETURN
    # -----------------------------------------------------
    return merged_df, summary, summary_df
