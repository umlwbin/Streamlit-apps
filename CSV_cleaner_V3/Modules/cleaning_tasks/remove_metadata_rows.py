import pandas as pd


def remove_metadata_rows(
    df: pd.DataFrame,
    *,
    identifiers,
    filename=None,
    metadata_extract=None
):
    """
    Remove metadata rows that appear above the true header row.

    This task:
    - detects the header row using user-provided identifiers
    - removes all rows above the header (metadata rows)
    - promotes the detected header row to column names
    - ensures column names are unique
    - optionally extracts metadata values into new columns
    - returns a preview of the metadata rows for UI display

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset that may contain metadata rows above the header.

    identifiers : list[str]
        Strings that must appear in the true header row.
        Matching is case-insensitive and whitespace-trimmed.

    filename : str, optional
        Name of the file being processed (for provenance).

    metadata_extract : dict or None, optional
        Mapping of new column name → extraction instructions:
            {
                "new_col": {
                    "row": int,          # row index within metadata_df
                    "col_index": int,    # index of non-empty cell to extract
                    "edit": str or None  # optional user override
                }
            }

    Returns
    -------
    cleaned_df : pandas.DataFrame
        DataFrame with metadata rows removed and a clean header applied.

    summary : dict
        {
            "metadata_preview": list[dict],
            "filename": str or None,
            "warnings": list[str]
        }

    summary_df : None
        Always None for this task (included for template consistency).

    Notes
    -----
    - Hard validation errors (e.g., invalid identifiers) raise exceptions.
    - Soft validation issues (e.g., missing metadata rows) appear in
      summary["warnings"] but do not stop execution.
    """

    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors (A, B, C…)
    # -----------------------------------------------------

    # A. df must be a DataFrame
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    # B. identifiers must be a list of strings
    if not isinstance(identifiers, list) or not all(isinstance(x, str) for x in identifiers):
        raise ValueError("identifiers must be a list of strings.")

    # C. metadata_extract must be dict or None
    if metadata_extract is not None and not isinstance(metadata_extract, dict):
        raise ValueError("metadata_extract must be a dictionary or None.")

    cleaned_df = df.copy()

    # -----------------------------------------------------
    # 2. VALIDATION - Soft Checks (A, B, C…)
    # -----------------------------------------------------
    warnings = []

    # Normalize identifiers
    identifiers_norm = [x.strip().lower() for x in identifiers]

    # Convert all cells to lowercase strings for matching
    df_str = cleaned_df.astype(str).applymap(lambda x: x.strip().lower())

    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------

    # Helper: ensure unique column names
    def make_unique(names):
        seen = {}
        unique = []
        for name in names:
            if name not in seen:
                seen[name] = 0
                unique.append(name)
            else:
                seen[name] += 1
                unique.append(f"{name}_{seen[name]}")
        return unique

    # Detect header row
    header_index = None
    for idx, row in df_str.iterrows():
        row_values = set(row.tolist())
        if all(identifier in row_values for identifier in identifiers_norm):
            header_index = idx
            break

    # If no header row found → soft warning, return unchanged
    if header_index is None:
        warnings.append(
            "No header row matched the provided identifiers. Dataset returned unchanged."
        )
        summary = {
            "metadata_preview": [],
            "filename": filename,
            "warnings": warnings,
        }
        return cleaned_df.copy(), summary, None

    # Extract metadata rows
    metadata_df = cleaned_df.iloc[:header_index].copy()

    # Promote header row
    new_header = cleaned_df.iloc[header_index].astype(str).tolist()
    new_header = make_unique(new_header)

    cleaned_df = cleaned_df.iloc[header_index + 1:].copy()
    cleaned_df.columns = new_header
    cleaned_df = cleaned_df.reset_index(drop=True)

    # Build metadata preview
    preview = metadata_df.head(10).to_dict(orient="records")

    # Extract metadata into new columns
    if metadata_extract:
        for new_col, info in metadata_extract.items():

            # Validate extraction instructions
            if "row" not in info or "col_index" not in info:
                warnings.append(f"Metadata extraction for '{new_col}' is missing required keys.")
                continue

            row_idx = info["row"]
            col_index = info["col_index"]

            # Ensure row exists
            if row_idx >= len(metadata_df):
                warnings.append(
                    f"Metadata extraction row {row_idx} out of range for '{new_col}'."
                )
                continue

            row = metadata_df.iloc[row_idx]
            non_empty = [cell for cell in row.tolist() if str(cell).strip() != ""]

            # Ensure col_index exists
            if col_index >= len(non_empty):
                warnings.append(
                    f"Metadata extraction col_index {col_index} out of range for '{new_col}'."
                )
                continue

            raw_value = non_empty[col_index]
            final_value = info.get("edit") or raw_value

            cleaned_df[new_col] = final_value

    # -----------------------------------------------------
    # 4. SUMMARY
    # -----------------------------------------------------
    summary = {
        "metadata_preview": preview,
        "filename": filename,
        "warnings": warnings,
    }

    # -----------------------------------------------------
    # 5. SUMMARY DATAFRAME
    # -----------------------------------------------------
    summary_df = None

    # -----------------------------------------------------
    # 6. RETURN
    # -----------------------------------------------------
    return cleaned_df, summary, summary_df
