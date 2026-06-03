import pandas as pd
import re


def split_column(
    df: pd.DataFrame,
    *,
    filename=None,
    column,
    delimiters,
    **kwargs
):
    """
    Split a single column into multiple new columns using one or more delimiters.

    This task:
    - normalizes whitespace (including NBSP from PDF exports)
    - collapses repeated whitespace
    - splits the column using literal or regex delimiters
    - inserts new columns next to the original
    - removes the original column only if multiple new columns were created

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset.

    column : str
        Name of the column to split.

    delimiters : list[str]
        List of delimiters to split on. Each may be:
        - a literal character (",", "|", "/", etc.)
        - a regex pattern (e.g., "\\s+")

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A copy of the input DataFrame with new split columns added.
    """

    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors
    # -----------------------------------------------------

    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    if not isinstance(column, str):
        raise ValueError("column must be a string.")

    if not isinstance(delimiters, list) or not all(isinstance(d, str) for d in delimiters):
        raise ValueError("delimiters must be a list of strings.")

    if column not in df.columns:
        # In the new architecture, soft validation belongs in the widget.
        # If the column doesn't exist --> return unchanged.
        return df.copy()

    cleaned_df = df.copy()

    # -----------------------------------------------------
    # 2. CORE PROCESSING
    # -----------------------------------------------------

    # Normalize whitespace
    cleaned_series = (
        cleaned_df[column]
        .astype(str)
        .str.replace("\u00A0", " ", regex=False)   # NBSP --> space
        .str.replace(r"\s+", " ", regex=True)      # collapse whitespace
        .str.strip()
    )

    # Build regex pattern
    escaped = [
        d if d.startswith("\\") else re.escape(d)
        for d in delimiters
    ]
    pattern = "|".join(escaped)

    # Perform split
    split_df = cleaned_series.str.split(pattern, expand=True)

    # If no split occurred --> return unchanged
    if split_df.shape[1] <= 1:
        return cleaned_df

    # Insert new columns
    original_idx = cleaned_df.columns.get_loc(column)
    cleaned_df = cleaned_df.drop(columns=[column])

    for i in range(split_df.shape[1]):
        new_col = f"{column}_{i+1}"
        cleaned_df.insert(original_idx + i, new_col, split_df[i])

    return cleaned_df
