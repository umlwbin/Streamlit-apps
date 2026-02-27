import pandas as pd
import re

def split_numeric_columns(df, columns, new_col_suffixes=("A", "B")):
    """
    Split columns that contain two numeric values separated by whitespace
    (spaces or tabs). E.g.
        "15.2     14.3"
        "9.4   9.6"

    The function detects these patterns, extracts the two numbers, creates
    two new columns (e.g., "K_A" and "K_B"), and removes the original
    column once the split is successful.

    Parameters
    ----------
    df : pandas.DataFrame
        The input table.

    columns : list of str
        Column names to check and split. Only columns that actually match
        the numeric‑pair pattern will be split.

    new_col_suffixes : tuple of str, optional
        Suffixes to append to the new columns created from each split.
        Default is ("A", "B"), producing columns like "K_A" and "K_B".

    Returns
    -------
    df : pandas.DataFrame
        The updated DataFrame with new split columns added and the
        original columns removed (only if a split occurred).

    summary : dict
        A dictionary describing what was split. Keys include:
            - "operation": name of the task
            - "columns_processed": list of columns that were split
            - "columns_split": mapping of original → new columns
            - "rows_split": number of rows successfully split per column

    --------------------------------------------------------------------
    Pure Python Usage (no Streamlit)
    --------------------------------------------------------------------
    >>> import pandas as pd
    >>> from split_numeric_cols import split_numeric_columns

    # Example DataFrame
    >>> df = pd.DataFrame({
    ...     "K": ["15.2 14.3", "9.4 9.6", "not a pair"],
    ...     "Other": [1, 2, 3]
    ... })

    # Call the function directly
    >>> new_df, summary = split_numeric_columns(df, columns=["K"])

    # Inspect results
    >>> print(new_df)
       K_A   K_B  Other
    0 15.2  14.3      1
    1  9.4   9.6      2
    2 None  None      3

    >>> print(summary)
    {
        'operation': 'split_numeric_columns',
        'columns_processed': ['K'],
        'columns_split': {'K': ['K_A', 'K_B']},
        'rows_split': {'K': 2}
    }

    This allows students to test the function in a normal Python script
    or Jupyter notebook without needing Streamlit.
    """

    summary = {
        "operation": "split_numeric_columns",
        "columns_processed": [],
        "columns_split": {},
        "rows_split": {},
    }

    pattern = re.compile(
        r"^\s*([+-]?\d*\.?\d+)\s+([+-]?\d*\.?\d+)\s*$"
    )

    for col in columns:
        # Skip this column name if it doesn't exist in the DataFrame
        if col not in df.columns:
            continue

        # Create names for the two new columns that will hold the split values
        new_col1 = f"{col}_{new_col_suffixes[0]}"
        new_col2 = f"{col}_{new_col_suffixes[1]}"

        # These lists will store the split values for each row
        split_col1 = []
        split_col2 = []

        # Count how many rows were successfully split
        rows_split_count = 0

        # Loop through every value in the column (convert to string just in case)
        for val in df[col].astype(str):

            # Remove extra spaces/tabs and collapse them into a single space
            cleaned = re.sub(r"\s+", " ", val.strip())

            # Remove any weird trailing artifacts like "14.6.1" → "14.6"(foudn this in PDF extractions)
            artifact_match = re.match(r"^([+-]?\d*\.?\d+)\.\d$", cleaned)
            if artifact_match:
                cleaned = artifact_match.group(1)

            # Try to match the "number number" pattern using the regex
            match = pattern.match(cleaned)

            if match:
                # If the pattern matches, extract the two numbers
                v1, v2 = match.groups()

                # Store them in the new column lists
                split_col1.append(v1)
                split_col2.append(v2)

                # Keep track of how many rows were split
                rows_split_count += 1
            else:
                # If the pattern does NOT match, store None for both new columns
                split_col1.append(None)
                split_col2.append(None)

        # Only create new columns if at least one row matched the pattern
        if rows_split_count > 0:

            # Add the new columns to the DataFrame
            df[new_col1] = split_col1
            df[new_col2] = split_col2

            # Remove the original column now that it has been split
            df = df.drop(columns=[col])

            # Update the summary information for reporting back to user
            summary["columns_processed"].append(col)
            summary["columns_split"][col] = [new_col1, new_col2]
            summary["rows_split"][col] = rows_split_count


    return df, summary
