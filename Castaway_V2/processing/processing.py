import pandas as pd
import re
import streamlit as st

# -------------------------------------------------------------------
# Helper functions used in this file:
#
# clean_metadata_name()  → from processing.normalizing_headers
#     - Removes punctuation, parentheses, symbols from metadata names
#     - Makes them safe to use as column names
#
# safe_insert_column()   → from processing.helpers
#     - Inserts a column only if it does not already exist
#     - Ensures consistent column order
# -------------------------------------------------------------------

from processing.normalizing_headers import clean_metadata_name
from processing.helpers import safe_insert_column


# ===================================================================
# FINAL DATAFRAME BUILDER
# ===================================================================
def build_final_dataframe(
    data_list,
    metadata_list,
    selected_vars,
    new_vars,
    omit_list,
    custom_names,
):
    """
    Build the final cleaned dataset by combining:
      • Extracted data tables
      • Selected metadata variables
      • Auto-standardized ODV variables (Cruise, Station, Type, Time, Lat, Lon)
      • Auto-extracted Bot. Depth [m]
      • User-added variables
      • Columns the user wants to omit
      • User renaming (no additional normalization)
    """

    final_frames = []

    # ===================================================================
    # PROCESS EACH FILE INDIVIDUALLY
    # ===================================================================
    for df, meta in zip(data_list, metadata_list):

        df = df.copy()

        # --------------------------------------------------------------
        # STEP 1 - Insert selected metadata variables
        # --------------------------------------------------------------
        # We normalize metadata names so that:
        #   "Cast time (UTC)"  → "cast time utc"
        #   "Cast time UTC"    → "cast time utc"
        # This ensures matching works even if punctuation differs.
        # --------------------------------------------------------------

        def normalize_meta_name(name):
            name = str(name)
            name = name.lstrip("%")          # remove leading %
            name = name.strip()
            name = re.sub(r"[^a-z0-9 ]", "", name.lower())
            return name

        # Pre-normalize metadata table
        meta["__norm__"] = meta["Variable"].astype(str).apply(normalize_meta_name)

        for var in selected_vars:
            var_clean = clean_metadata_name(var)   # cleaned column name
            var_norm = normalize_meta_name(var)    # normalized for matching

            row = meta[meta["__norm__"] == var_norm]

            if not row.empty:
                value = row["Value"].iloc[0]
                safe_insert_column(df, var_clean, value)

        # --------------------------------------------------------------
        # STEP 2 - Insert user-defined variables
        # --------------------------------------------------------------
        if new_vars:
            for name, value in new_vars.items():
                safe_insert_column(df, name, value)

        # --------------------------------------------------------------
        # STEP 3 - Auto-extract Bot. Depth [m] from last Depth value
        # --------------------------------------------------------------
        
        # Match any column containing the word "depth"
        depth_cols = [c for c in df.columns if "depth" in c.lower()]

        # Case 1 - No depth column at all
        if not depth_cols:
            # Create an empty Depth column
            df["Depth"] = None
            # Create an empty Bot. Depth column
            df["Bot. Depth [m]"] = None

        else:
            depth_col = depth_cols[0]
            depth_series = df[depth_col].dropna()

            # Case 2 - Depth column exists but has no valid values
            if len(depth_series) == 0:
                df["Bot. Depth [m]"] = None

            # Case 3 - Normal case
            else:
                bottom_depth = depth_series.iloc[-1]
                df["Bot. Depth [m]"] = bottom_depth



        # --------------------------------------------------------------
        # STEP 4 - Remove unwanted columns
        # --------------------------------------------------------------
        if omit_list:
            df = df.drop(columns=omit_list, errors="ignore")

        # --------------------------------------------------------------
        # STEP 5 - Apply renaming rules
        #
        # Order of precedence:
        #   1. Auto-standardize ODV-required variables
        #   2. Apply user overrides
        #   3. Keep cleaned names
        # --------------------------------------------------------------
        new_cols = []

        for col in df.columns:

            col_stripped = col.strip()
            lowered = col_stripped.lower()

            # ---- ODV auto-standardization ----
            if "cruise" in lowered:
                new_cols.append("Cruise"); continue

            if "station" in lowered:
                new_cols.append("Station"); continue

            if "cast time" in lowered:
                new_cols.append("yyyy-mm-ddThh:mm:ss.sss"); continue

            if "longitude" in lowered:
                new_cols.append("Longitude [degrees_east]"); continue

            if "latitude" in lowered:
                new_cols.append("Latitude [degrees_north]"); continue

            if lowered == "bot. depth [m]":
                new_cols.append("Bot. Depth [m]"); continue

            # ---- User overrides ----
            if custom_names and col in custom_names:
                new_cols.append(custom_names[col]); continue

            # ---- Default ----
            new_cols.append(col_stripped)

        df.columns = new_cols
        final_frames.append(df)

    # ===================================================================
    # STEP 6 - Combine all cleaned files
    # ===================================================================

    # --------------------------------------------------------
    # 6A. Collect all columns across all files - we need all files to have the same cols, in order to conactenate
    # --------------------------------------------------------
    all_columns = set()
    for frame in final_frames:
        all_columns.update(frame.columns)

    # --------------------------------------------------------
    # 6B. Ensure every file has every column
    # --------------------------------------------------------
    aligned_frames = []

    for frame in final_frames:
        missing = all_columns - set(frame.columns)
        for col in missing:
            frame[col] = None  # fill missing columns with None
        aligned_frames.append(frame[sorted(all_columns)])  # consistent order


    # --------------------------------------------------------
    # 6C. Combine all cleaned files
    # --------------------------------------------------------
    final_df = pd.concat(aligned_frames, ignore_index=True)


    # ===================================================================
    # STEP 7 - Enforce ODV column order
    # ===================================================================
    odv_order = [
        "Cruise",
        "Station",
        "Type",
        "yyyy-mm-ddThh:mm:ss.sss",
        "Longitude [degrees_east]",
        "Latitude [degrees_north]",
        "Bot. Depth [m]"
    ]

    present_odv_cols = [c for c in odv_order if c in final_df.columns]
    remaining_cols = [c for c in final_df.columns if c not in present_odv_cols]

    final_df = final_df[present_odv_cols + remaining_cols]

    # ===================================================================
    # STEP 8 - Move "File name" to the end (optional)
    # ===================================================================
    if "File name" in final_df.columns:
        cols = [c for c in final_df.columns if c != "File name"]
        cols.append("File name")
        final_df = final_df[cols]

    return final_df
