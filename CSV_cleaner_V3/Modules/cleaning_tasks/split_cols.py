import pandas as pd
import re

def split_column(df, column, delimiters):
    """
    Split one column of a table into several new columns.

    This function looks at a single column in a pandas DataFrame and breaks
    each cell into multiple parts using a chosen delimiter (for example a
    space, tab, comma, or slash). It then creates new columns for each part.

    How it works:
    - The function first cleans the text by converting unusual whitespace
      (including non‑breaking spaces from PDF exports) into normal spaces.
    - It then collapses all repeated whitespace into a single space.
    - It splits the cleaned text using the delimiter(s) you provide.
    - It inserts the new columns next to the original column.
    - It removes the original column only if the split produced more than
      one new column.

    Parameters
    ----------
    df : pandas.DataFrame
        The input table.

    column : str
        The name of the column you want to split.

    delimiters : list of str
        A list of delimiters to split on. Each delimiter can be a literal
        character (",", "|", "/", etc.) or a regular expression such as
        "\\s+" for "one or more whitespace characters".

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A new DataFrame with the split columns added.

    summary : dict
        A small dictionary describing what happened.

    Example (pure Python)
    ---------------------
    >>> import pandas as pd
    >>> from split_cols import split_column

    >>> df = pd.DataFrame({
    ...     "J": ["15.2 14.3", "9.4 9.6", "94 94"]
    ... })

    # Split on one or more spaces
    >>> cleaned, summary = split_column(df, "J", ["\\s+"])

    >>> print(cleaned)
         J_1   J_2
    0   15.2  14.3
    1    9.4   9.6
    2     94    94

    >>> print(summary)
    {
        "task_name": "split_column",
        "operation": "split_column",
        "column": "J",
        "delimiters": ["\\s+"],
        "new_columns": ["J_1", "J_2"],
        "rows_split": 3
    }
    """


    cleaned_df = df.copy()

    summary = {
        "task_name": "split_column",
        "operation": "split_column",
        "column": column,
        "delimiters": delimiters,
        "new_columns": [],
        "rows_split": 0
    }

    if column not in cleaned_df.columns:
        summary["warning"] = f"Column '{column}' not found."
        return cleaned_df, summary

    # Normalize whitespace BEFORE splitting
    cleaned_series = (
        df[column]
        .astype(str)
        .str.replace("\u00A0", " ", regex=False)   # convert NBSP → space
        .str.replace(r"\s+", " ", regex=True)      # collapse all whitespace
        .str.strip()                               # remove leading/trailing
    )


    # Build regex pattern (regex delimiters are NOT escaped)
    escaped = [
        d if d.startswith("\\") else re.escape(d)
        for d in delimiters
    ]
    pattern = "|".join(escaped)

    # Perform the split
    split_df = cleaned_series.str.split(pattern, expand=True)

    if split_df.shape[1] <= 1:
        summary["warning"] = "No splits detected using the provided delimiter(s)."
        return cleaned_df, summary

    # Insert new columns in place of the original
    original_idx = cleaned_df.columns.get_loc(column)
    cleaned_df = cleaned_df.drop(columns=[column])

    new_cols = []
    for i in range(split_df.shape[1]):
        new_col = f"{column}_{i+1}"
        cleaned_df.insert(original_idx + i, new_col, split_df[i])
        new_cols.append(new_col)

    summary["new_columns"] = new_cols
    summary["rows_split"] = (split_df.notna().sum(axis=1) > 1).sum()

    return cleaned_df, summary
