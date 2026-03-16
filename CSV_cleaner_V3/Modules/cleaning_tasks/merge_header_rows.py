import pandas as pd


def merge_header_rows(
    df: pd.DataFrame,
    *,
    row_map,
    row1=None,
    row2=None,
    filename=None   # <-- harmless and ignored. The UI aneeds it, not task
):
    """
    Merge one or two user-selected rows (based on ORIGINAL row numbers)
    into the existing header row.

    This task is used when a dataset contains metadata rows above the true
    header row (e.g., variable names in one row and units in another). The
    function maps original row numbers to the current DataFrame index using
    a provided row_map, merges the selected rows into the header, drops the
    merged rows, and updates the row_map accordingly.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset whose header will be modified.

    row_map : list[int]
        A list mapping *current* DataFrame row indices to *original* row numbers.
        Example: row_map[5] = 12 means current row 5 came from original row 12.

    row1 : int or None, optional
        Original row number to merge into the header.

    row2 : int or None, optional
        Second original row number to merge into the header.

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A copy of the input DataFrame with an updated header and merged rows removed.

    summary : dict
        {
            "first_merged_row": int or None,
            "second_merged_row": int or None,
            "warnings": [list of soft validation messages]
        }

    summary_df : None
        Always None for this task (included for template consistency).

    Notes
    -----
    - Hard validation errors (e.g., invalid row_map) raise exceptions.
    - Soft validation issues (e.g., row not found) appear in summary["warnings"]
      but do not stop execution.
    """

    _ = filename # just stating this is intentionally unused. 

    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors (A, B, C…)
    # -----------------------------------------------------

    # A. df must be a DataFrame
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    # B. row_map must be a list of integers
    if not isinstance(row_map, list) or not all(isinstance(x, int) for x in row_map):
        raise ValueError("row_map must be a list of integers.")

    # C. row_map length must match df length
    if len(row_map) != len(df):
        raise ValueError(
            "row_map length does not match DataFrame length. "
            "This indicates an internal workflow error."
        )

    cleaned_df = df.copy()

    # -----------------------------------------------------
    # 2. VALIDATION - Soft Checks (A, B, C…)
    # -----------------------------------------------------
    warnings = []

    # Helper: map original row number → current index
    def map_original_to_current(original_idx):
        try:
            return row_map.index(original_idx)
        except ValueError:
            return None

    # A. Map row1
    mapped1 = None
    if row1 is not None:
        mapped1 = map_original_to_current(row1)
        if mapped1 is None:
            warnings.append(f"Row {row1} not found in the dataset. It was skipped.")
        row1 = mapped1

    # B. Map row2
    mapped2 = None
    if row2 is not None:
        mapped2 = map_original_to_current(row2)
        if mapped2 is None:
            warnings.append(f"Row {row2} not found in the dataset. It was skipped.")
        row2 = mapped2

    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------

    # Start with existing header
    header = list(cleaned_df.columns.astype(str))

    # Merge row1
    if row1 is not None:
        vals = list(cleaned_df.iloc[row1])
        header = [
            f"{h}_{v}" if pd.notna(v) and str(v).strip() != "" else h
            for h, v in zip(header, vals)
        ]

    # Merge row2
    if row2 is not None:
        vals = list(cleaned_df.iloc[row2])
        header = [
            f"{h}_{v}" if pd.notna(v) and str(v).strip() != "" else h
            for h, v in zip(header, vals)
        ]

    # Drop merged rows
    rows_to_drop = [r for r in [row1, row2] if r is not None]
    cleaned_df = cleaned_df.drop(index=rows_to_drop).reset_index(drop=True)

    # Update row_map
    new_row_map = [
        row_map[i] for i in range(len(row_map)) if i not in rows_to_drop
    ]

    # Soft warning if mismatch occurs (should not happen)
    if len(new_row_map) != len(cleaned_df):
        warnings.append(
            "Internal warning: row_map and DataFrame length mismatch after merge."
        )

    # Apply merged header
    cleaned_df.columns = header

    # -----------------------------------------------------
    # 4. SUMMARY
    # -----------------------------------------------------
    summary = {
        "first_merged_row": row1,
        "second_merged_row": row2,
        "warnings": warnings,
        "row_map": new_row_map
    }


    # -----------------------------------------------------
    # 5. SUMMARY DATAFRAME
    # -----------------------------------------------------
    summary_df = None

    # -----------------------------------------------------
    # 6. RETURN
    # -----------------------------------------------------
    return cleaned_df, summary, summary_df
