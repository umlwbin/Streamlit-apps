"""
Unified Datagarrison processing engine.

This file is the source procesing file for:
- Streamlit workflow
- Pure Python workflow

All cleaning logic lives here.
Only the file-reading entry point differs.
"""

from pathlib import Path
import pandas as pd
from io import BytesIO

from .column_map import COLUMN_MAP
from .qualifier_columns import QUALIFIER_COLUMNS
from .units_map import UNITS_MAP

# =====================================================================
# Helper: Logging messages
# =====================================================================

def _log(message: str):
    """
    Prints helpful messages only when VERBOSE = True in config.py.
    """
    if globals().get("VERBOSE", False):
        print(message)



# =====================================================================
# 1. READ RAW FILE (Pure Python Workflow: uses Path)
# =====================================================================

def read_datagarrison_path(path: Path, remove_metadata=True):
    """
    Read a Datagarrison file from disk.
    Used by the pure‑Python workflow.
    """
    file_bytes = path.read_bytes() # read the whole file into memeory as a bytes object
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

    text = file_bytes.decode("utf-8", errors="replace") # convert to a python string
    lines = text.splitlines() #get all the lines

    delim = "\t" 

    if not remove_metadata:
        return pd.read_csv(BytesIO(file_bytes), sep=delim, engine="python")

    # Searches the first 20 lines and returns the index of first line that has "temperature" or None
    header_row = next(
        (i for i, line in enumerate(lines[:20]) if "temperature" in line.lower()),
        None
    )

    # If we didnt find temp, than read the entire file
    if header_row is None:
        return pd.read_csv(BytesIO(file_bytes), sep=delim, engine="python")

    # if there is a header row, return the dataframe with the header_row index 
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
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")] # Keep only those columns that DO NOT have "Unanamed"
    df = df.dropna(axis=1, how="all") # Drop all empty columns
    return df



# =====================================================================
# 3. STANDARDIZE COLUMN NAMES
# =====================================================================

def standardize_columns(df):
    """
    Renames raw Datagarrison columns to standardized names using COLUMN_MAP.

    COLUMN_MAP is a dictionary like:
        {"RawName": "standard_name"}
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
    """
    for col, qcol in QUALIFIER_COLUMNS.items():
        if col in df.columns:
            idx = df.columns.get_loc(col)
            df.insert(idx + 1, qcol, pd.NA)
            df[qcol] = df[qcol].astype("string")

    return df


# =====================================================================
# 5. WIND UNIT CONVERSION
# =====================================================================

def convert_wind_units(df, raw_units, convert_choice):
    """
    Convert wind units based on raw units and user output choice.

    Rules:
    - If user wants to KEEP raw units → do nothing.
    - If raw is km/h and user wants m/s → convert km/h → m/s.
    - If raw is m/s and user wants km/h → convert m/s → km/h.
    """

    # ---------------------------------------------------------------
    # 0. If user wants to keep raw units, do NOTHING
    # ---------------------------------------------------------------
    if convert_choice == "Keep raw units":
        return df

    # ---------------------------------------------------------------
    # 1. RAW km/h → user wants m/s
    # ---------------------------------------------------------------
    if raw_units == "km/h" and convert_choice == "Convert to m/s":
        if "wind_speed" in df.columns:
            df["wind_speed"] = df["wind_speed"] / 3.6
        if "wind_speed_of_gust" in df.columns:
            df["wind_speed_of_gust"] = df["wind_speed_of_gust"] / 3.6
        return df

    # ---------------------------------------------------------------
    # 2. RAW m/s → user wants km/h
    # ---------------------------------------------------------------
    if raw_units == "m/s" and convert_choice == "Convert to km/h":
        if "wind_speed" in df.columns:
            df["wind_speed"] = df["wind_speed"] * 3.6
        if "wind_speed_of_gust" in df.columns:
            df["wind_speed_of_gust"] = df["wind_speed_of_gust"] * 3.6
        return df

    # ---------------------------------------------------------------
    # 3. RAW m/s → user wants m/s (no change)
    # ---------------------------------------------------------------
    # RAW km/h → user wants km/h (no change)
    # Already covered by "Keep raw units", but safe to return
    return df



# =====================================================================
# 6. APPLY QC RULES
# =====================================================================

def apply_qc_rules(df, convert_choice, filename=None):
    """
    Applies Datagarrison-specific QC rules to the dataset.

    This includes:
    - Converting timestamps
    - Adding year/month/day columns
    - Applying upper/lower bounds for each variable
    - Special rules for winter precipitation
    - Special rules for wind speed and gusts
    """

    df["date_and_time"] = pd.to_datetime(
        df["date_and_time"],
        format="%m/%d/%y %H:%M:%S",
        errors="coerce"
    )

    df["year"] = df["date_and_time"].dt.year
    df["month"] = df["date_and_time"].dt.month
    df["day"] = df["date_and_time"].dt.day



    # ---------------------------------------------------------------
    # QC RULES (all columns checked safely)
    # ---------------------------------------------------------------

    # -------------------------
    # Air pressure
    # -------------------------
    if "air_pressure" in df.columns:
        q = QUALIFIER_COLUMNS["air_pressure"]
        df.loc[df["air_pressure"] > 1070, q] = "ADL"
        df.loc[df["air_pressure"] < 660, q] = "BDL"

    # -------------------------
    # PAR
    # -------------------------
    if "photosynthetically_active_radiation" in df.columns:
        q = QUALIFIER_COLUMNS["photosynthetically_active_radiation"]
        df.loc[df["photosynthetically_active_radiation"] > 2500, q] = "ADL"
        df.loc[df["photosynthetically_active_radiation"] < 0, q] = "BDL"

    # -------------------------
    # Temperature
    # -------------------------
    if "air_temperature" in df.columns:
        q = QUALIFIER_COLUMNS["air_temperature"]
        df.loc[df["air_temperature"] > 75, q] = "ADL"
        df.loc[df["air_temperature"] < -40, q] = "BDL"

    # -------------------------
    # Relative humidity
    # -------------------------
    if "relative_humidity" in df.columns:
        q = QUALIFIER_COLUMNS["relative_humidity"]
        df.loc[df["relative_humidity"] > 100, q] = "ADL"
        df.loc[df["relative_humidity"] < 0, q] = "BDL"

    # -------------------------
    # Precipitation
    # -------------------------
    if "precip" in df.columns:
        q = QUALIFIER_COLUMNS["precip"]
        df.loc[df["precip"] > 127, q] = "ADL"
        df.loc[df["precip"] < 0, q] = "BDL"

        # Winter precip rule
        winter_mask = (df["month"] == 12) | (df["month"] < 3)
        df.loc[winter_mask, q] = "prob_bad"


    # -------------------------
    # Wind direction
    # -------------------------
    if "wind_from_direction" in df.columns:
        q = QUALIFIER_COLUMNS["wind_from_direction"]
        df.loc[(df["wind_from_direction"] > 355) & (df["wind_from_direction"] < 360), q] = "prob_bad"


    # -------------------------
    # Precip
    # -------------------------
    if "precip" in df.columns:
        # Winter precip
        q = QUALIFIER_COLUMNS["precip"]
        winter_mask = (df["month"] == 12) | (df["month"] < 3)
        df.loc[winter_mask, q] = "prob_bad"



    # ---------------------------------------------------------------
    # Wind QC (based on final output units)
    # ---------------------------------------------------------------

    # Determine the units currently in the DataFrame
    # After convert_wind_units(), values are either km/h or m/s
    wind_in_ms = (convert_choice == "Convert to m/s")

    # Sensor detection limits always 0–100 m/s → convert to km/h if needed
    upper_sensor_limit = 100 if wind_in_ms else 360
    lower_sensor_limit = 0

    # Environmental thresholds - Inland Manitoba: ~25–30 m/s (90–108 km/h) are rare; are rare; https://www.weather.gov/media/epz/mesonet/CWOP-WMO8.pdf. chapter 5
    wind_prob_bad = 30 if wind_in_ms else 90  # sustained wind
    gust_prob_bad = 35 if wind_in_ms else 110 #gusts are slightly higher

    # -------------------------
    # Wind speed
    # -------------------------
    if "wind_speed" in df.columns:
        q = QUALIFIER_COLUMNS["wind_speed"]

        # Sensor limits
        df.loc[df["wind_speed"] < lower_sensor_limit, q] = "BDL"
        df.loc[df["wind_speed"] > upper_sensor_limit, q] = "ADL"

        # Environmental plausibility
        df.loc[df["wind_speed"] > wind_prob_bad, q] = "prob_bad"

    # -------------------------
    # Gust speed
    # -------------------------
    if "wind_speed_of_gust" in df.columns:
        q = QUALIFIER_COLUMNS["wind_speed_of_gust"]

        # Sensor limits
        df.loc[df["wind_speed_of_gust"] < lower_sensor_limit, q] = "BDL"
        df.loc[df["wind_speed_of_gust"] > upper_sensor_limit, q] = "ADL"

        # Environmental plausibility
        df.loc[df["wind_speed_of_gust"] > gust_prob_bad, q] = "prob_bad"

    # -------------------------
    # Gust should exceed sustained wind at higher speeds
    # -------------------------
    if "wind_speed" in df.columns and "wind_speed_of_gust" in df.columns:
        q1 = QUALIFIER_COLUMNS["wind_speed"]
        q2 = QUALIFIER_COLUMNS["wind_speed_of_gust"]

        # Once winds exceed roughly 40 km/h, gusts should almost always be higher than sustained wind
        equal_threshold = 11 if wind_in_ms else 40  # ~40 km/h ≈ 11 m/s

        mask = (df["wind_speed"] == df["wind_speed_of_gust"]) & (df["wind_speed"] > equal_threshold)
        df.loc[mask, [q1, q2]] = "prob_bad"

    return df


# =====================================================================
# 7. COLUMN ORDERING
# =====================================================================

def order_columns(df):
    """
    Reorders columns into a predictable, curator‑friendly order.

    The order is:
    1. Timestamp columns (date_and_time, year, month, day)
    2. Standardized measurement columns (from COLUMN_MAP)
    3. Their qualifier columns (from QUALIFIER_COLUMNS)
    4. Any remaining columns
    """
    front = ["date_and_time", "year", "month", "day"]

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
    df = df.sort_values("date_and_time").drop_duplicates()
    df = order_columns(df)

    for col in ["year", "month", "day"]:
        if col in df.columns:
            df = df.drop(columns=[col])

    df["date_and_time"] = df["date_and_time"].dt.strftime("%Y-%m-%dT%H:%M:%S")
    return df



# =====================================================================
# 9. UNIFIED CLEANING PIPELINE
# =====================================================================

def clean_dataframe(df: pd.DataFrame, *, raw_units, convert_choice):
    """
    The unified cleaning pipeline. All workflows call this function.

    raw_units:       units in the RAW file ("km/h" or "m/s")
    convert_choice:  desired output units ("Keep raw units", "Convert to m/s", "Convert to km/h")
    """

    # 1. Remove unnamed/empty columns
    df = drop_unnamed_columns(df)

    # 2. Standardize column names
    df = standardize_columns(df)

    # 3. Add qualifier columns
    df = add_qualifier_columns(df)

    # 4. Convert wind units (raw → internal → output units)
    df = convert_wind_units(df, raw_units, convert_choice)

    # 5. Apply QC rules (based on FINAL units)
    df = apply_qc_rules(df, convert_choice)

    # 6. Final cleanup (sort, reorder, drop helper cols)
    df = finalize(df)

    return df



def clean_file_bytes(file_bytes: bytes, *, raw_units, convert_choice, remove_metadata=True):
    """
    Read raw bytes, parse into a DataFrame, and run the full cleaning pipeline. For streamlit reading.
    """
    df = read_datagarrison_bytes(file_bytes, remove_metadata=remove_metadata)
    return clean_dataframe(df, raw_units=raw_units, convert_choice=convert_choice)


def clean_file_path(path: Path, *, raw_units, convert_choice, remove_metadata=True):
    """
    Read a file from disk and run the full cleaning pipelin. For the pure python workflow.
    """
    df = read_datagarrison_path(path, remove_metadata=remove_metadata)
    return clean_dataframe(df, raw_units=raw_units, convert_choice=convert_choice)



# =====================================================================
# 10. COMPILE MULTIPLE FILES
# =====================================================================

def compile_files(list_of_dfs):
    """
    Combines multiple cleaned DataFrames into one.
    - Concatenates all DataFrames
    - Sorts by timestamp if available
    """
    if not list_of_dfs:
        return pd.DataFrame()

    df = pd.concat(list_of_dfs, ignore_index=True)

    if "date_and_time" in df.columns:
        df = df.sort_values("date_and_time")

    return df



# =====================================================================
# 11. DICTIONARY TABLE BUILDER
# =====================================================================

def build_dictionary_table(df, convert_choice):
    """
    Build a dictionary table in the exact order of the cleaned DataFrame columns.

    Columns:
        original_name
        cleaned_name
        units
    """

    reverse_map = {v: k for k, v in COLUMN_MAP.items()}
    rows = []

    for col in df.columns:
        original = reverse_map.get(col, "")
        units = UNITS_MAP.get(original, "")

        # Override wind units if conversion was applied
        if convert_choice == "Convert to m/s" and col in ["wind_speed", "wind_speed_of_gust"]:
            units = "m/s"

        rows.append({
            "original_name": original,
            "cleaned_name": col,
            "units": units
        })

    return pd.DataFrame(rows)

