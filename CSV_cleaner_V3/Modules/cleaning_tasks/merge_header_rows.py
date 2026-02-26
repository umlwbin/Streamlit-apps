import pandas as pd
import re

def merge_header_rows(df, row1=None, row2=None):
    """
    Merge VMV and/or Units rows into the header row.
    """

    # Normalize column names to strings
    df.columns = df.columns.map(str)

    # Extract original headers
    headers = list(df.columns)

    # Prepare working header list
    merged_headers = headers.copy()

    # ---------------------------------------------------------
    # Merge VMV codes
    # ---------------------------------------------------------
    if row1 is not None:
        vmv_values = list(df.iloc[row1])
        merged_headers = [
            f"{h}_{v}" if pd.notna(v) else h
            for h, v in zip(merged_headers, vmv_values)
        ]
        df = df.drop(index=row1)

    # ---------------------------------------------------------
    # Merge Units
    # ---------------------------------------------------------
    if row2 is not None:
        unit_values = list(df.iloc[row2])
        merged_headers = [
            f"{h}_{u}" if pd.notna(u) else h
            for h, u in zip(merged_headers, unit_values)
        ]
        df = df.drop(index=row2)

    df.columns = merged_headers

    # Reset index after dropping rows
    df = df.reset_index(drop=True)

    # Summary
    summary = {
        "vmv_row_used": row1,
        "unit_row_used": row2,
    }

    return df, summary