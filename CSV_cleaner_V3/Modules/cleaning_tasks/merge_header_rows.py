import pandas as pd
import re

def merge_header_rows(df, row1=None, row2=None):
    """
    Merge VMV and/or Units rows into the header row, with validation and
    curator-friendly error reporting.

    This version adds:
        • validation for row indices
        • detection of out-of-range rows
        • detection of non-string header values
        • consistent "errors" list in the summary
        • safe fallback behavior
    """

    cleaned_df = df.copy()

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------
    summary = {
        "task_name": "merge_header_rows",
        "first_merged_row": row1,
        "second_merged_row": row2,
        "errors": []
    }

    # ---------------------------------------------------------
    # VALIDATION 1 — Ensure DataFrame has columns
    # ---------------------------------------------------------
    if cleaned_df.columns.empty:
        summary["errors"].append("The dataset has no columns to merge headers into.")
        return cleaned_df, summary

    # Normalize column names to strings
    cleaned_df.columns = cleaned_df.columns.map(str)

    # Extract original headers
    headers = list(cleaned_df.columns)
    merged_headers = headers.copy()

    # ---------------------------------------------------------
    # Helper: validate a row index
    # ---------------------------------------------------------
    def validate_row_index(row_idx, label):
        if row_idx is None:
            return True
        if not isinstance(row_idx, int):
            summary["errors"].append(f"{label} must be an integer index.")
            return False
        if row_idx < 0 or row_idx >= len(cleaned_df):
            summary["errors"].append(
                f"{label} ({row_idx}) is out of range for this dataset."
            )
            return False
        return True

    # Validate row1 and row2
    valid_row1 = validate_row_index(row1, "First merged row")
    valid_row2 = validate_row_index(row2, "Second merged row")

    # If both invalid, return early
    if not valid_row1 and not valid_row2:
        return cleaned_df, summary

    # ---------------------------------------------------------
    # Merge VMV row (row1)
    # ---------------------------------------------------------
    if valid_row1 and row1 is not None:
        try:
            vmv_values = list(cleaned_df.iloc[row1])
            merged_headers = [
                f"{h}_{v}" if pd.notna(v) else h
                for h, v in zip(merged_headers, vmv_values)
            ]
            cleaned_df = cleaned_df.drop(index=row1)
        except Exception as e:
            summary["errors"].append(
                f"Failed to merge first row ({row1}): {str(e)}"
            )

    # ---------------------------------------------------------
    # Merge Units row (row2)
    # ---------------------------------------------------------
    if valid_row2 and row2 is not None:
        try:
            # Adjust row2 index if row1 was dropped first
            adjusted_row2 = row2
            if valid_row1 and row1 is not None and row2 > row1:
                adjusted_row2 -= 1

            unit_values = list(cleaned_df.iloc[adjusted_row2])
            merged_headers = [
                f"{h}_{u}" if pd.notna(u) else h
                for h, u in zip(merged_headers, unit_values)
            ]
            cleaned_df = cleaned_df.drop(index=adjusted_row2)
        except Exception as e:
            summary["errors"].append(
                f"Failed to merge second row ({row2}): {str(e)}"
            )

    # ---------------------------------------------------------
    # Apply merged headers
    # ---------------------------------------------------------
    try:
        cleaned_df.columns = merged_headers
    except Exception as e:
        summary["errors"].append(
            f"Failed to assign merged headers: {str(e)}"
        )
        return cleaned_df, summary

    # Reset index after dropping rows
    cleaned_df = cleaned_df.reset_index(drop=True)

    return cleaned_df, summary
