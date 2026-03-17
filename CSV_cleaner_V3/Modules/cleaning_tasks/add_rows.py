import pandas as pd

def add_row(
    df: pd.DataFrame,
    *,
    filename=None,
    row_values=None,
    as_header=False,
    auto_headers=False
):
    """
    Add a new row to the DataFrame or generate alphabetical headers.

    Parameters
    ----------
    df : pd.DataFrame
        The input dataframe.
    row_values : list[Any] or None
        Values for the new row (ignored if auto_headers=True).
    as_header : bool
        If True, the new row becomes the header row.
    auto_headers : bool
        If True, generate alphabetical headers (A, B, C, ...).

    Returns
    -------
    cleaned_df : pd.DataFrame
        The updated dataframe.
    summary : dict
        A dictionary describing what was added or changed.
    summary_df : None
        No supplementary dataframe for this task.
    """

    # -----------------------------------------------------
    # 1. VALIDATION (raise errors)
    # -----------------------------------------------------
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    if auto_headers and (row_values is not None or as_header):
        raise ValueError("Auto generated headers cannot be combined with adding row values or as_header=True.")

    if not auto_headers:
        if row_values is None:
            raise ValueError("row values must be provided unless auto_headers=True.")

        if len(row_values) != len(df.columns):
            raise ValueError(
                f"Row has {len(row_values)} values but DataFrame has "
                f"{len(df.columns)} columns."
            )

    # -----------------------------------------------------
    # 2. CORE PROCESSING LOGIC
    # -----------------------------------------------------
    cleaned_df = df.copy()

    # -----------------------------------------------------
    # CASE 1: AUTO-GENERATE ALPHABETICAL HEADERS
    # -----------------------------------------------------
    if auto_headers:
        # Recover the original first row (pandas used it as header)
        recovered_first_row = list(cleaned_df.columns)

        # Insert the recovered row back into the data
        cleaned_df = pd.concat(
            [pd.DataFrame([recovered_first_row], columns=cleaned_df.columns),
             cleaned_df],
            ignore_index=True
        )

        # Create alphabetical headers: A, B, C, ...
        new_header = [chr(65 + i) for i in range(len(cleaned_df.columns))]
        cleaned_df.columns = new_header

        summary = {
            "auto_headers": True,
            "new_headers": new_header,
            "row_added": None,
        }

        return cleaned_df, summary, None

    # -----------------------------------------------------
    # CASE 2: NORMAL ADD ROW BEHAVIOR
    # -----------------------------------------------------
    new_row_df = pd.DataFrame([row_values], columns=cleaned_df.columns)

    # -----------------------------------------------------
    # CASE 2A: PROMOTE ROW TO HEADER
    # -----------------------------------------------------
    if as_header:
        # Insert the new row at the top
        cleaned_df = pd.concat([new_row_df, cleaned_df], ignore_index=True)

        # Convert row values into new column names
        new_header = [str(v) if pd.notna(v) else "" for v in row_values]
        cleaned_df.columns = new_header

        # Remove the promoted row from the data
        cleaned_df = cleaned_df.iloc[1:].reset_index(drop=True)

        summary = {
            "as_header": True,
            "new_headers": new_header,
            "row_added": None,
        }

        return cleaned_df, summary, None

    # -----------------------------------------------------
    # CASE 2B: INSERT ROW AS NORMAL DATA
    # -----------------------------------------------------
    cleaned_df = pd.concat([new_row_df, cleaned_df], ignore_index=True)

    summary = {
        "as_header": False,
        "row_added": row_values,
        "row_index": 0,
    }

    # -----------------------------------------------------
    # 4. SUMMARY DATAFRAME (optional)
    # -----------------------------------------------------
    summary_df = None

    # -----------------------------------------------------
    # 5. RETURN STANDARDIZED OUTPUT
    # -----------------------------------------------------
    return cleaned_df, summary, summary_df
