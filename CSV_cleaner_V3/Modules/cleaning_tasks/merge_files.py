import pandas as pd

def merge(dfs_dict, add_source=False):
    """
    Merge multiple DataFrames vertically (row‑wise) into a single DataFrame.
    Designed for workflows where a user uploads several files that all share
    the same structure (same columns) and wants them combined into one dataset.

    This function:
        • copies each DataFrame to avoid modifying the originals
        • optionally adds a 'source_file' column so the user can trace where
          each row came from
        • concatenates all DataFrames into one continuous table
        • resets the index so the final DataFrame is clean and predictable

    Parameters
    ----------
    dfs_dict : dict[str, pandas.DataFrame]
        A dictionary where:
            - the keys are filenames (strings)
            - the values are DataFrames loaded from those files
        Example:
            {
                "file1.csv": df1,
                "file2.csv": df2,
                "file3.csv": df3
            }

    add_source : bool, optional
        If True:
            A new column named 'source_file' is added to each DataFrame before merging.
            This column contains the filename for each row.
        If False (default):
            No source column is added.

    Returns
    -------
    merged_df : pandas.DataFrame
        A single DataFrame containing all rows from all input DataFrames,
        stacked vertically.

    summary : dict
        Information about the merge operation.
        Structure:
            {
                "merged_files": [list of filenames merged],
                "added_source_column": True/False
            }

    Example
    -------
    >>> dfs = {
            "jan.csv": df_jan,
            "feb.csv": df_feb
        }

    >>> merged, summary = merge(dfs, add_source=True)

    >>> merged.columns
    [..., "source_file"]

    >>> summary
    {
        "merged_files": ["jan.csv", "feb.csv"],
        "added_source_column": True
    }
    """


    # We will collect cleaned copies of each DataFrame here.
    # Using copies ensures we never modify the original user data.
    frames = []

    # Loop through each file and its DataFrame.
    # dfs_dict looks like: {"file1.csv": df1, "file2.csv": df2, ...}
    for filename, df in dfs_dict.items():
        temp = df.copy()   # work on a safe copy

        # If the user wants to keep track of where each row came from,
        # add a new column containing the filename.
        if add_source:
            temp["source_file"] = filename

        # Add the prepared DataFrame to our list.
        frames.append(temp)

    # Concatenate all DataFrames vertically.
    # ignore_index=True resets the index so the final table is clean and continuous.
    merged_df = pd.concat(frames, ignore_index=True)

    # Build a simple summary describing what happened.
    summary = {
        "merged_files": list(dfs_dict.keys()),   # which files were merged
        "added_source_column": add_source        # whether we added the source column
    }

    return merged_df, summary