import pandas as pd

def add_row(df, row_values=None, as_header=False, auto_headers=False):
    """
    Insert a new row into a DataFrame or generate alphabetical headers.

    This function supports:
      1. Adding a user‑entered row (either as data row or as a new header)
      2. Automatically generating alphabetical headers (A, B, C, …)
         for files that were uploaded without a proper header row.

    Parameters
    ----------
    df : pandas.DataFrame
        The input table.

    row_values : list of str or None
        The values for the new row. Only used when auto_headers=False.
        ***Must have the same number of elements as the number of columns.

    as_header : bool, optional
        If True, the new row is promoted to become the header.
        The row is inserted at the top, then removed from the data
        after becoming the new column names.

    auto_headers : bool, optional
        If True, the function ignores row_values and instead generates
        alphabetical headers (A, B, C, …). This is useful when the
        uploaded file did not contain a real header row and pandas
        incorrectly treated the first data row as the header.

        In this mode:
            - The original first row (stored in df.columns) is restored
              into the data.
            - Alphabetical headers replace the column names.

    Returns
    -------
    df : pandas.DataFrame
        The updated DataFrame.

    summary : dict
        A dictionary describing what was done. Keys include:
            - "operation": name of the task
            - "as_header": whether a row was promoted to header
            - "auto_headers": whether alphabetical headers were used
            - "new_header": the new column names
            - "inserted_row": the row added as data (if applicable)
            - "recovered_first_row": the restored row from df.columns
              when auto_headers=True

    --------------------------------------------------------------------
    Pure Python Usage (no Streamlit)
    --------------------------------------------------------------------
    >>> import pandas as pd
    >>> from add_row import add_row

    # Example DataFrame
    >>> df = pd.DataFrame({
    ...     "A": [1, 2],
    ...     "B": [3, 4]
    ... })

    # Add a normal data row
    >>> new_df, summary = add_row(df, row_values=["x", "y"], as_header=False)

    # Promote a row to header
    >>> new_df, summary = add_row(df, row_values=["Col1", "Col2"], as_header=True)

    # Generate alphabetical headers (A, B, C, ...)
    >>> new_df, summary = add_row(df, auto_headers=True)
    """

    # ---------------------------------------------------------
    # AUTO-GENERATE ALPHABETICAL HEADERS (A, B, C, ...)
    # ---------------------------------------------------------
    if auto_headers:
        # Recover the original first row (pandas used it as header)
        recovered_first_row = list(df.columns)

        # Insert the recovered row back into the data as row 0
        df = pd.concat(
            [pd.DataFrame([recovered_first_row], columns=df.columns), df],
            ignore_index=True
        )

        # Create alphabetical headers: A, B, C, ...
        new_header = [chr(65 + i) for i in range(len(df.columns))]

        # Replace the column names with the alphabetical headers
        df.columns = new_header

        summary = {
            "operation": "add_row",
            "as_header": True,
            "auto_headers": True,
            "new_header": new_header,
            "recovered_first_row": recovered_first_row
        }
        return df, summary

    # ---------------------------------------------------------
    # NORMAL ADD ROW BEHAVIOR
    # ---------------------------------------------------------
    # Make sure the user-provided row has the correct number of values
    if len(row_values) != len(df.columns):
        raise ValueError(
            f"Row has {len(row_values)} values but DataFrame has {len(df.columns)} columns."
        )

    # Convert the list of values into a one-row DataFrame
    new_row_df = pd.DataFrame([row_values], columns=df.columns)

    # ---------------------------------------------------------
    # PROMOTE ROW TO HEADER
    # ---------------------------------------------------------
    if as_header:
        # Insert the new row at the top of the table
        df = pd.concat([new_row_df, df], ignore_index=True)

        # Convert the row values into the new column names
        new_header = [str(v) if pd.notna(v) else "" for v in row_values]
        df.columns = new_header

        # Remove the promoted row from the data
        df = df.iloc[1:].reset_index(drop=True)

        summary = {
            "operation": "add_row",
            "as_header": True,
            "auto_headers": False,
            "new_header": new_header
        }
        return df, summary

    # ---------------------------------------------------------
    # INSERT ROW AS NORMAL DATA
    # ---------------------------------------------------------
    # Add the new row at the top of the table
    df = pd.concat([new_row_df, df], ignore_index=True)

    summary = {
        "operation": "add_row",
        "as_header": False,
        "auto_headers": False,
        "inserted_row": row_values
    }
    return df, summary
