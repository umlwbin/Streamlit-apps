import pandas as pd
import re

def merge_header_rows(df, vmv_row=None, unit_row=None):
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
    if vmv_row is not None:
        vmv_values = list(df.iloc[vmv_row])
        merged_headers = [
            f"{h}_{v}" if pd.notna(v) else h
            for h, v in zip(merged_headers, vmv_values)
        ]
        df = df.drop(index=vmv_row)

    # ---------------------------------------------------------
    # Merge Units
    # ---------------------------------------------------------
    if unit_row is not None:
        unit_values = list(df.iloc[unit_row])
        merged_headers = [
            f"{h}_{u}" if pd.notna(u) else h
            for h, u in zip(merged_headers, unit_values)
        ]
        df = df.drop(index=unit_row)

    # ---------------------------------------------------------
    # Clean headers
    # ---------------------------------------------------------
    cleaned_headers = []
    keep_chars = "µ"
    pattern = rf"[^A-Za-z0-9\s{re.escape(keep_chars)}]"

    for h in merged_headers:
        h = h.strip()
        h = re.sub(pattern, "_", h)
        h = re.sub(r"_+", "_", h)
        if h.endswith("_"):
            h = h[:-1]
        cleaned_headers.append(h)

    df.columns = cleaned_headers

    # Reset index after dropping rows
    df = df.reset_index(drop=True)

    # Summary
    summary = {
        "vmv_row_used": vmv_row,
        "unit_row_used": unit_row,
        "new_headers": cleaned_headers
    }

    return df, summary