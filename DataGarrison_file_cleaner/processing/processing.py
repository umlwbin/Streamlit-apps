"""
Unified Datagarrison processing engine.

This file is now the *single source of truth* for:
- Streamlit workflow (bytes-based)
- Pure Python workflow (path-based)

All cleaning logic lives here.
Only the file-reading entry point differs.
"""

from pathlib import Path
import pandas as pd
from io import BytesIO

from .column_map import COLUMN_MAP
from .qualifier_columns import QUALIFIER_COLUMNS


# =====================================================================
# Helper: Logging for beginners
# =====================================================================

def _log(message: str):
    """
    Prints helpful messages only when VERBOSE = True in config.py.
    """
    if globals().get("VERBOSE", False):
        print(message)



# =====================================================================
# 1. READ RAW FILE (Pure Python Workflow - uses Path)
# =====================================================================

def read_datagarrison_path(path: Path, remove_metadata=True):
    """
    Read a Datagarrison file from disk.
    Used by the pure‑Python workflow.
    """
    file_bytes = path.read_bytes()
    return read_datagarrison_bytes(file_bytes, remove_metadata=remove_metadata)



# =====================================================================
# 1. READ RAW FILE (Streamlit version: uses file_bytes)
# =====================================================================

def read_datagarrison_bytes(file_bytes, remove_metadata=True):
    """
    Convert raw file bytes into a pandas DataFrame.

    This function:
    1. Turns the bytes into text so we can inspect the first few lines.
    2. Detects the header row by looking for the word "temperature".
    3. Uses pandas to read the file into a DataFrame.
    4. Removes metadata rows if requested.
    """

    text = file_bytes.decode("utf-8", errors="replace")
    lines = text.splitlines()

    delim = "\t"

    if not remove_metadata:
        return pd.read_csv(BytesIO(file_bytes), sep=delim, engine="python")

    header_row = next(
        (i for i, line in enumerate(lines[:20]) if "temperature" in line.lower()),
        None
    )

    if header_row is None:
        return pd.read_csv(BytesIO(file_bytes), sep=delim, engine="python")

    return pd.read_csv(
        BytesIO(file_bytes),
        sep=delim,
        engine="python",
        header=header_row
    )



# =====================================================================
# 2. DROP UNNAMED COLUMNS
# =====================================================================

def drop_unnamed_columns(df):
    """
    Removes columns that pandas labels as 'Unnamed: ...'
    These usually appear when the raw file has extra delimiters.

    Also removes columns that are entirely empty.
    """
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df = df.dropna(axis=1, how="all")
    return df



# =====================================================================
# 3. STANDARDIZE COLUMN NAMES
# =====================================================================

def standardize_columns(df):
    """
    Renames raw Datagarrison columns to standardized names using COLUMN_MAP.

    COLUMN_MAP is a dictionary like:
        {"RawName": "standard_name"}

    This ensures that downstream steps always see consistent column names.
    """
    return df.rename(columns=COLUMN_MAP)



# =====================================================================
# 4. ADD QUALIFIER COLUMNS
# =====================================================================

def add_qualifier_columns(df):
    """
    Adds empty qualifier columns next to each measurement column.

    QUALIFIER_COLUMNS is a mapping like:
        {"temperature": "temperature_result_value_qualifier"}

    If the measurement column exists:
        Insert the qualifier column immediately after it.
    If not:
        Add the qualifier column at the end (filled with NaN).
    """
    for col, qcol in QUALIFIER_COLUMNS.items():
        if col in df.columns:
            idx = df.columns.get_loc(col)
            df.insert(idx + 1, qcol, pd.NA)
        else:
            df[qcol] = pd.NA

        df[qcol] = df[qcol].astype("string")

    return df



# =====================================================================
# 5. APPLY QC RULES
# =====================================================================

def apply_qc_rules(df, filename=None):
    """
    Applies Datagarrison-specific QC rules to the dataset.

    This includes:
    - Converting timestamps
    - Adding year/month/day columns
    - Applying upper/lower bounds for each variable
    - Special rules for winter precipitation
    - Special rules for wind speed and gusts
    """

    df["Date_and_time"] = pd.to_datetime(
        df["Date_and_time"],
        format="%m/%d/%y %H:%M:%S",
        errors="coerce"
    )

    df["year"] = df["Date_and_time"].dt.year
    df["month"] = df["Date_and_time"].dt.month
    df["day"] = df["Date_and_time"].dt.day

    # Air pressure
    q = QUALIFIER_COLUMNS["air_pressure"]
    df.loc[df["air_pressure"] > 1070, q] = "ADL"
    df.loc[df["air_pressure"] < 660, q] = "BDL"

    # PAR
    q = QUALIFIER_COLUMNS["Photosynthetically_Active_Radiation"]
    df.loc[df["Photosynthetically_Active_Radiation"] > 2500, q] = "ADL"
    df.loc[df["Photosynthetically_Active_Radiation"] < 0, q] = "BDL"

    # Temperature
    q = QUALIFIER_COLUMNS["air_temperature"]
    df.loc[df["air_temperature"] > 75, q] = "ADL"
    df.loc[df["air_temperature"] < -40, q] = "BDL"

    # Relative humidity
    q = QUALIFIER_COLUMNS["relative_humidity"]
    df.loc[df["relative_humidity"] > 100, q] = "ADL"
    df.loc[df["relative_humidity"] < 0, q] = "BDL"

    # Precip
    q = QUALIFIER_COLUMNS["Precip"]
    df.loc[df["Precip"] > 127, q] = "ADL"
    df.loc[df["Precip"] < 0, q] = "BDL"

    # Wind speed
    q = QUALIFIER_COLUMNS["wind_speed"]
    df.loc[df["wind_speed"] > 50, q] = "ADL"
    df.loc[df["wind_speed"] < 0, q] = "BDL"

    # Gust speed
    q = QUALIFIER_COLUMNS["wind_speed_of_gust"]
    df.loc[df["wind_speed_of_gust"] > 50, q] = "ADL"
    df.loc[df["wind_speed_of_gust"] < 0, q] = "BDL"

    # Wind speed == gust speed > 40
    q1 = QUALIFIER_COLUMNS["wind_speed"]
    q2 = QUALIFIER_COLUMNS["wind_speed_of_gust"]
    mask = (df["wind_speed"] == df["wind_speed_of_gust"]) & (df["wind_speed"] > 40)
    df.loc[mask, [q1, q2]] = "prob_bad"

    # Wind direction dead zone
    q = QUALIFIER_COLUMNS["wind_from_direction"]
    df.loc[(df["wind_from_direction"] > 355) & (df["wind_from_direction"] < 360), q] = "prob_bad"

    # Winter precip
    q = QUALIFIER_COLUMNS["Precip"]
    winter_mask = (df["month"] == 12) | (df["month"] < 3)
    df.loc[winter_mask, q] = "prob_bad"

    return df



# =====================================================================
# 6. WIND UNIT CONVERSION
# =====================================================================

def convert_wind_units(df, raw_units, convert_choice):
    """
    Convert wind units only if explicitly requested.

    raw_units:
        "km/h (recommended)"
        "m/s"
        "I'm not sure"

    convert_choice:
        "No (keep original units)"
        "Convert to m/s"
    """
    if convert_choice == "No (keep original units)":
        return df

    if raw_units.startswith("km/h") and convert_choice == "Convert to m/s":
        for col in ["wind_speed", "wind_speed_of_gust"]:
            if col in df.columns:
                df[col] = df[col] / 3.6

    return df



# =====================================================================
# 7. COLUMN ORDERING
# =====================================================================

def order_columns(df):
    """
    Reorders columns into a predictable, curator‑friendly order.

    The order is:
    1. Timestamp columns (Date_and_time, year, month, day)
    2. Standardized measurement columns (from COLUMN_MAP)
    3. Their qualifier columns (from QUALIFIER_COLUMNS)
    4. Any remaining columns
    """
    front = ["Date_and_time", "year", "month", "day"]

    ordered_vars = []
    for raw, std in COLUMN_MAP.items():
        if std in df.columns:
            ordered_vars.append(std)
            qcol = QUALIFIER_COLUMNS.get(std)
            if qcol and qcol in df.columns:
                ordered_vars.append(qcol)

    ordered_vars = list(dict.fromkeys(ordered_vars))

    remaining = [c for c in df.columns if c not in front + ordered_vars]

    final_cols = list(dict.fromkeys(front + ordered_vars + remaining))

    return df[final_cols]



# =====================================================================
# 8. FINAL CLEANUP
# =====================================================================

def finalize(df):
    """
    Performs final cleanup steps:
    - Ensures timestamps are datetime
    - Sorts rows chronologically
    - Removes duplicate rows
    - Reorders columns
    - Removes helper columns (year, month, day)
    """
    df = df.sort_values("Date_and_time").drop_duplicates()
    df = order_columns(df)

    for col in ["year", "month", "day"]:
        if col in df.columns:
            df = df.drop(columns=[col])

    df["Date_and_time"] = df["Date_and_time"].dt.strftime("%Y-%m-%dT%H:%M:%S")
    return df



# =====================================================================
# 9. UNIFIED CLEANING PIPELINE
# =====================================================================

def clean_dataframe(df: pd.DataFrame, *, raw_units, convert_choice):
    """
    The unified cleaning pipeline.
    All workflows call this function.
    """
    df = drop_unnamed_columns(df)
    df = standardize_columns(df)
    df = add_qualifier_columns(df)
    df = convert_wind_units(df, raw_units, convert_choice)
    df = apply_qc_rules(df)
    df = finalize(df)
    return df



def clean_file_bytes(file_bytes: bytes, *, raw_units, convert_choice, remove_metadata=True):
    df = read_datagarrison_bytes(file_bytes, remove_metadata=remove_metadata)
    return clean_dataframe(df,
                           raw_units=raw_units,
                           convert_choice=convert_choice)



def clean_file_path(path: Path, *, raw_units, convert_choice, remove_metadata=True):
    df = read_datagarrison_path(path, remove_metadata=remove_metadata)
    return clean_dataframe(df,
                           raw_units=raw_units,
                           convert_choice=convert_choice)



# =====================================================================
# 10. COMPILE MULTIPLE FILES
# =====================================================================

def compile_files(list_of_dfs):
    """
    Combines multiple cleaned DataFrames into one.

    This is useful when:
    - Cleaning multiple raw files at once
    - Creating a single dataset for export

    The function:
    - Concatenates all DataFrames
    - Sorts by timestamp if available
    """
    if not list_of_dfs:
        return pd.DataFrame()

    df = pd.concat(list_of_dfs, ignore_index=True)

    if "Date_and_time" in df.columns:
        df = df.sort_values("Date_and_time")

    return df
