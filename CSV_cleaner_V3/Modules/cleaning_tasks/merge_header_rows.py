import pandas as pd
import streamlit as st

def merge_header_rows(df, filename, row1=None, row2=None):
    """
    Merge two user-selected rows (based on ORIGINAL row numbers)
    into the existing header row.
    """

    cleaned_df = df.copy()

    summary = {
        "task_name": "merge_header_rows",
        "first_merged_row": row1,
        "second_merged_row": row2,
        "errors": []
    }

    # ---------------------------------------------------------
    # Validate row_map exists
    # ---------------------------------------------------------
    if "row_map" not in st.session_state or filename not in st.session_state.row_map:
        summary["errors"].append(
            "Internal error: row_map missing. Cannot map row numbers."
        )
        return cleaned_df, summary

    row_map = st.session_state.row_map[filename]

    # ---------------------------------------------------------
    # Helper: map original row number → current DataFrame index
    # ---------------------------------------------------------
    def map_original_to_current(original_idx):
        if original_idx in row_map:
            return row_map.index(original_idx)
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

    # ---------------------------------------------------------
    # Merge row1
    # ---------------------------------------------------------
    if row1 is not None:
        vals = list(cleaned_df.iloc[row1])
        header = [
            f"{h}_{v}" if pd.notna(v) and str(v).strip() != "" else h
            for h, v in zip(header, vals)
        ]

    # ---------------------------------------------------------
    # Merge row2
    # ---------------------------------------------------------
    if row2 is not None:
        vals = list(cleaned_df.iloc[row2])
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

    cleaned_df = cleaned_df.drop(index=rows_to_drop).reset_index(drop=True)

    # ---------------------------------------------------------
    # Update row_map to match the new DataFrame
    # ---------------------------------------------------------
    new_row_map = [
        row_map[i] for i in range(len(row_map)) if i not in rows_to_drop
    ]

    # Safety: ensure row_map length matches df length
    if len(new_row_map) != len(cleaned_df):
        summary["errors"].append(
            "Internal error: row_map and DataFrame length mismatch."
        )
        return cleaned_df, summary

    st.session_state.row_map[filename] = new_row_map

    # ---------------------------------------------------------
    # Apply merged header
    # ---------------------------------------------------------
    cleaned_df.columns = header

    return cleaned_df, summary
