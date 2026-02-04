"""
processing.py — Core cleaning pipeline for Idronaut CTD files.

This module contains:
    • File reading and delimiter detection
    • Downcast subsetting
    • The main cleaning pipeline (clean_idronaut_file)

Helper modules:
    • date_parsing.py — date/time parsing utilities
    • header_validation.py — column validation logic
"""

import pandas as pd
import numpy as np

from processing.header_validation import validate_idronaut_headers
from processing.date_parsing import (
    parse_with_formats,
    IDRONAUT_DATE_FORMATS,
    IDRONAUT_TIME_FORMATS,
)
from processing.column_mapping import map_idronaut_column, rvq_name_for

# ============================================================
# 1. FILE READER (robust delimiter detection)
# ============================================================
def read_idronaut_file(uploaded_file):
    """
    Read an uploaded Idronaut file into a pandas DataFrame.

    Idronaut files come in two common formats:
      - TXT files with whitespace between columns
      - CSV files with commas or semicolons

    This function:
      1. Reads the file as text
      2. Tries whitespace-based parsing first (best for TXT files)
      3. Falls back to automatic delimiter detection (best for CSVs)
      4. Cleans column names
      5. Validates headers using the function above

    Returns:
      (df, None) if successful
      (None, "error message") if something goes wrong
    """

    uploaded_file.seek(0)
    content = uploaded_file.read().decode("utf-8", errors="replace")

    # First try whitespace-delimited parsing (common for Idronaut TXT)
    try:
        df = pd.read_csv(
            pd.io.common.StringIO(content),
            sep=r"\s+",
            engine="python"
        )
    except Exception:
        # Fallback: let pandas guess the delimiter
        df = pd.read_csv(
            pd.io.common.StringIO(content),
            sep=None,
            engine="python"
        )

    # Clean column names
    df.columns = [c.strip() for c in df.columns]

    # Validate headers
    df, error = validate_idronaut_headers(df)

    return df, error


# ============================================================
# 2. DOWNCAST SUBSETTING
# ============================================================
def subset_downcast(df, start, end):
    """
    Extract the rows corresponding to the downcast.

    The curator chooses start and end rows in the UI.
    This function:
      - Ensures the indices are within valid bounds
      - Returns an empty DataFrame if the range is invalid
      - Returns a copy of the selected rows otherwise

    Returns:
      A subset of the original DataFrame.
    """

    start = max(0, int(start))
    end = min(len(df) - 1, int(end))

    if start > end:
        return df.iloc[0:0].copy()  # empty df

    return df.iloc[start:end + 1].copy()


# ============================================================
# 3. CLEANING LOGIC
# ============================================================
def clean_idronaut_file(df, start, end, lat, lon, site):
    """
    Clean a single Idronaut file and prepare it for export.

    This is the full cleaning pipeline used by the workflow.
    It performs the following steps:

    1. Subset the downcast rows
    2. Combine Date + Time into a single Datetime column
    3. Insert metadata (Site ID, Latitude, Longitude)
    4. Rename columns to CanWIN standard names
    5. Add RVQ (Result Value Qualifier) columns for each variable

    Returns:
      A cleaned and standardized DataFrame.
    """

    # -----------------------------
    # 1. Subset downcast
    # -----------------------------
    down = subset_downcast(df, start, end)
    # -----------------------------
    # 2. Merge Date + Time into Datetime
    # -----------------------------
    # Clean up formatting (remove stray spaces)
    down["Date"] = down["Date"].astype(str).str.strip()
    down["Time"] = down["Time"].astype(str).str.strip()

    # Parse Date and Time separately using our helper
    parsed_date = parse_with_formats(down["Date"], IDRONAUT_DATE_FORMATS, "Date")
    parsed_time = parse_with_formats(down["Time"], IDRONAUT_TIME_FORMATS, "Time").dt.time

    # Combine into a single Datetime column
    down["Datetime"] = parsed_date.astype(str) + " " + parsed_time.astype(str)
    down["Datetime"] = pd.to_datetime(down["Datetime"], errors="coerce")

    # Drop original columns and move Datetime to the front
    down.drop(columns=["Date", "Time"], inplace=True)
    down.insert(0, "Datetime", down.pop("Datetime"))

    # -----------------------------
    # 3. Add metadata
    # -----------------------------
    down.insert(0, "Site ID", site)
    down.insert(2, "Latitude", lat)
    down.insert(3, "Longitude", lon)

    # -----------------------------
    # 4. Rename columns + add RVQ columns
    # -----------------------------
    curated_cols = []

    for col in list(down.columns):
        # Map the column to its standardized name
        new = map_idronaut_column(col)
        curated_cols.append(new)

        # Add an RVQ column (empty for now)
        rvq = rvq_name_for(new)
        if rvq not in down.columns:
            idx = down.columns.get_loc(col)
            down.insert(idx + 1, rvq, "")
        curated_cols.append(rvq)

    down.columns = curated_cols


    return down
