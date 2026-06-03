import pandas as pd

def merge_files(
    dfs_dict: dict,
    *,
    add_source=False,
    filename=None,
    **kwargs
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
    """

    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors
    # -----------------------------------------------------

    if not isinstance(dfs_dict, dict):
        raise ValueError("dfs_dict must be a dictionary of {filename: DataFrame}.")

    if len(dfs_dict) == 0:
        raise ValueError("dfs_dict is empty - no files to merge.")

    for key, val in dfs_dict.items():
        if not isinstance(val, pd.DataFrame):
            raise ValueError(f"Value for '{key}' is not a pandas DataFrame.")

    # -----------------------------------------------------
    # 2. CORE PROCESSING
    # -----------------------------------------------------

    frames = []

    for filename, df in dfs_dict.items():
        temp = df.copy()

        # Optional provenance tracking
        if add_source:
            temp["source_file"] = filename

        frames.append(temp)

    merged_df = pd.concat(frames, ignore_index=True)

    # -----------------------------------------------------
    # 3. RETURN
    # -----------------------------------------------------
    return merged_df
