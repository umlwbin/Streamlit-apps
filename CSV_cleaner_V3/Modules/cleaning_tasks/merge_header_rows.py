import pandas as pd
import re
def merge_header_rows(df, row1=None, row2=None):
    """
    Merge two user-selected rows (based on ORIGINAL row numbers)
    into the existing header row.

    Works for:
        • rectangular files (header already promoted)
        • metadata-cleaned files
    """

    cleaned_df = df.copy()

    summary = {
        "task_name": "merge_header_rows",
        "first_merged_row": row1,
        "second_merged_row": row2,
        "errors": []
    }

    # ---------------------------------------------------------
    # Validate that _original_row exists
    # ---------------------------------------------------------
    if "_original_row" not in cleaned_df.columns:
        summary["errors"].append(
            "Internal error: _original_row column missing. Cannot map row numbers."
        )
        return cleaned_df, summary

    # ---------------------------------------------------------
    # Helper: map original row number → current DataFrame index
    # ---------------------------------------------------------
    def map_original_to_current(original_idx):
        matches = cleaned_df.index[cleaned_df["_original_row"] == original_idx]
        if len(matches) == 1:
            return matches[0]
        return None

    # Map row1
    if row1 is not None:
        mapped1 = map_original_to_current(row1)
        if mapped1 is None:
            summary["errors"].append(f"Row {row1} not found in the dataset.")
            return cleaned_df, summary
        row1 = mapped1

    # Map row2
    if row2 is not None:
        mapped2 = map_original_to_current(row2)
        if mapped2 is None:
            summary["errors"].append(f"Row {row2} not found in the dataset.")
            return cleaned_df, summary
        row2 = mapped2

    # ---------------------------------------------------------
    # Start with the existing header (already promoted)
    # ---------------------------------------------------------
    header = list(cleaned_df.columns.astype(str))
    header.remove("_original_row")  # do not merge into this column

    # ---------------------------------------------------------
    # Merge row1
    # ---------------------------------------------------------
    if row1 is not None:
        vals = list(cleaned_df.drop(columns=["_original_row"]).iloc[row1])
        header = [
            f"{h}_{v}" if pd.notna(v) and str(v).strip() != "" else h
            for h, v in zip(header, vals)
        ]

    # ---------------------------------------------------------
    # Merge row2
    # ---------------------------------------------------------
    if row2 is not None:
        vals = list(cleaned_df.drop(columns=["_original_row"]).iloc[row2])
        header = [
            f"{h}_{v}" if pd.notna(v) and str(v).strip() != "" else h
            for h, v in zip(header, vals)
        ]

    # ---------------------------------------------------------
    # Drop the merged rows
    # ---------------------------------------------------------
    rows_to_drop = []
    if row1 is not None:
        rows_to_drop.append(row1)
    if row2 is not None:
        rows_to_drop.append(row2)

    cleaned_df = cleaned_df.drop(index=rows_to_drop)
    cleaned_df = cleaned_df.reset_index(drop=True)

    # ---------------------------------------------------------
    # Apply merged header
    # ---------------------------------------------------------
    cleaned_df.columns = header + ["_original_row"]

    # ---------------------------------------------------------
    # Update _original_row after dropping rows
    # ---------------------------------------------------------
    cleaned_df["_original_row"] = range(len(cleaned_df))

    return cleaned_df, summary
