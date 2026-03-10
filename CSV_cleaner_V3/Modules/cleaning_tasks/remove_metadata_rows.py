import pandas as pd

def remove_metadata_rows(df, identifiers, filename=None, metadata_extract=None):
    """
    Remove metadata rows that appear above the true header row.

    This version is written for clarity and transparency. It:
        • detects the header row using user‑provided identifiers
        • removes all rows above the header (metadata rows)
        • promotes the detected header row to column names
        • returns a preview of the metadata rows (first 10)
        • includes the filename so the UI can combine metadata later

    Parameters
    ----------
    df : pandas.DataFrame
        The uploaded dataset. May contain metadata rows above the header.

    identifiers : list[str]
        A list of strings that must appear in the true header row.
        Matching is case‑insensitive and whitespace‑trimmed.

    filename : str, optional
        The name of the file being processed. Used for provenance.

    Returns
    -------
    cleaned_df : pandas.DataFrame
        The dataset with metadata rows removed and a clean header applied.

    summary : dict
        A summary containing:
            - task name
            - metadata preview (first 10 rows)
            - filename (for combining metadata across files)
    """

    # ---------------------------------------------------------
    # Helper: ensure column names are unique
    # ---------------------------------------------------------
    def make_unique(names):
        """
        If a header row contains duplicate names, add suffixes (_1, _2, ...).
        """
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

    # ---------------------------------------------------------
    # Normalize identifiers for matching
    # ---------------------------------------------------------
    identifiers = [str(x).strip().lower() for x in identifiers]

    # Convert all cells to lowercase strings for safe comparison
    df_str = df.astype(str).applymap(lambda x: x.strip().lower())

    header_index = None

    # ---------------------------------------------------------
    # Detect the header row
    # ---------------------------------------------------------
    for idx, row in df_str.iterrows():
        row_values = set(row.tolist())

        # Check if all identifiers appear in this row
        if all(identifier in row_values for identifier in identifiers):
            header_index = idx
            break

    # ---------------------------------------------------------
    # If no header row is found, return the dataset unchanged
    # ---------------------------------------------------------
    if header_index is None:
        summary = {
            "task_name": "remove_metadata_rows",
            "metadata_preview": [],
            "filename": filename
        }
        return df.copy(), summary

    # ---------------------------------------------------------
    # Extract metadata rows (everything above the header)
    # ---------------------------------------------------------
    metadata_df = df.iloc[:header_index].copy()

    # ---------------------------------------------------------
    # Promote the detected header row to column names
    # ---------------------------------------------------------
    new_header = df.iloc[header_index].astype(str).tolist()
    new_header = make_unique(new_header)

    cleaned_df = df.iloc[header_index + 1:].copy()
    cleaned_df.columns = new_header
    cleaned_df = cleaned_df.reset_index(drop=True)

    # ---------------------------------------------------------
    # Build metadata preview (first 10 rows)
    # ---------------------------------------------------------
    preview = metadata_df.head(10).to_dict(orient="records")


    # ---------------------------------------------------------
    # Add extracted metadata as new columns
    # ---------------------------------------------------------
    if metadata_extract:
        for new_col, info in metadata_extract.items():
            row_idx = info["row"]
            col_index = info["col_index"]

            # Extract raw value from THIS file’s metadata
            row = metadata_df.iloc[row_idx]
            non_empty = [cell for cell in row.tolist() if str(cell).strip() != ""]
            raw_value = non_empty[col_index]

            # Apply user edit if provided
            final_value = info["edit"] if info.get("edit") else raw_value

            # Add the value to every row in the cleaned dataset
            cleaned_df[new_col] = final_value

            

    # ---------------------------------------------------------
    # Build summary for the UI
    # ---------------------------------------------------------
    summary = {
        "task_name": "remove_metadata_rows",
        "metadata_preview": preview,
        "filename": filename
    }

    return cleaned_df, summary
