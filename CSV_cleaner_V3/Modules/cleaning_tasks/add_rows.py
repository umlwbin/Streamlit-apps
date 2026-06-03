import pandas as pd

def add_row(
    df: pd.DataFrame,
    *,
    row_values=None,
    as_header=False,
    auto_headers=False,
    position=0,
    **kwargs
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

    position: numeric
        position of row

    Returns
    -------
    cleaned_df : pd.DataFrame
        The updated dataframe.
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
    # CASE 1: AUTO-GENERATE HEADERS
    # -----------------------------------------------------
    if auto_headers:
        recovered_first_row = list(cleaned_df.columns)

        cleaned_df = pd.concat(
            [pd.DataFrame([recovered_first_row], columns=cleaned_df.columns),
             cleaned_df],
            ignore_index=True
        )

        new_header = [chr(65 + i) for i in range(len(cleaned_df.columns))]
        cleaned_df.columns = new_header

        return cleaned_df

    # -----------------------------------------------------
    # CASE 2: NORMAL ADD ROW BEHAVIOR
    # -----------------------------------------------------
    new_row_df = pd.DataFrame([row_values], columns=cleaned_df.columns)

    # -----------------------------------------------------
    # CASE 2A: PROMOTE ROW TO HEADER
    # -----------------------------------------------------
    if as_header:
        cleaned_df = pd.concat([new_row_df, cleaned_df], ignore_index=True)
        new_header = [str(v) if pd.notna(v) else "" for v in row_values]
        cleaned_df.columns = new_header
        cleaned_df = cleaned_df.iloc[1:].reset_index(drop=True)
        return cleaned_df

    # -----------------------------------------------------
    # CASE 2B: INSERT ROW AT SPECIFIC POSITION
    # -----------------------------------------------------
    top = cleaned_df.iloc[:position]
    bottom = cleaned_df.iloc[position:]

    cleaned_df = pd.concat([top, new_row_df, bottom], ignore_index=True)

    return cleaned_df