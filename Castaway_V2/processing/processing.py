import pandas as pd

# Import name cleaning + normalization helpers
from processing.normalizing_headers import clean_metadata_name, normalize_column_name

# Import general utilities
from processing.helpers import safe_insert_column, drop_columns


def apply_standard_names(name):
    n = name.lower()

    if "cruise" in n:
        return "Cruise"
    if "station" in n:
        return "Station"
    if "type" in n:
        return "Type"
    if "date" in n:
        return "yyyy-mm-ddThh:mm:ss.sss"
    if "longitude" in n:
        return "Longitude [degrees_east]"
    if "latitude" in n:
        return "Latitude [degrees_north]"
    if "depth" in n:
        return "Bot. Depth [m]"

    return clean_metadata_name(name)


# ------------------------------------------------------------
# FINAL DATAFRAME BUILDER
# ------------------------------------------------------------
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
    - The extracted data tables
    - Selected metadata variables
    - Required ODV variables (Cruise, Station, Type)
    - Auto-extracted Bot. Depth [m]
    - User-added variables
    - Columns the user wants to omit
    - User renaming (no additional normalization)
    """

    final_frames = []

    for df, meta in zip(data_list, metadata_list):

        df = df.copy()

        # --------------------------------------------------------
        # 1. Insert selected metadata variables
        # --------------------------------------------------------
        meta = meta.dropna(axis=1, how="all")

        for var in selected_vars:
            var_clean = clean_metadata_name(var)
            row = meta[meta["Variable"].astype(str).str.contains(var, regex=False)]
            if not row.empty:
                value = row["Value"].iloc[0]
                safe_insert_column(df, var_clean, value)

        # --------------------------------------------------------
        # 2. Insert required ODV variables (Cruise, Station, Type)
        # --------------------------------------------------------
        required = {"Cruise": "", "Station": "", "Type": ""}
        for k, v in required.items():
            safe_insert_column(df, k, v)

        # --------------------------------------------------------
        # 3. Insert user-defined variables
        # --------------------------------------------------------
        if new_vars:
            for name, value in new_vars.items():
                safe_insert_column(df, name, value)

        # --------------------------------------------------------
        # 4. Auto-extract Bot. Depth [m] from last Depth value
        # --------------------------------------------------------
        if "Depth" in df.columns:
            bottom_depth = df["Depth"].dropna().iloc[-1]
            df["Bot. Depth [m]"] = bottom_depth

        # --------------------------------------------------------
        # 5. Remove unwanted columns
        # --------------------------------------------------------
        if omit_list:
            df = df.drop(columns=omit_list, errors="ignore")

        # --------------------------------------------------------
        # 6. Apply renaming rules
        # --------------------------------------------------------
        new_cols = []
        for col in df.columns:

            col_stripped = col.strip()
            lowered = col_stripped.lower()

            # ODV auto-standardization
            if "cruise" in lowered:
                new_cols.append("Cruise")
                continue
            if "station" in lowered:
                new_cols.append("Station")
                continue
            if "type" in lowered:
                new_cols.append("Type")
                continue
            if "date" in lowered:
                new_cols.append("yyyy-mm-ddThh:mm:ss.sss")
                continue
            if "longitude" in lowered:
                new_cols.append("Longitude [degrees_east]")
                continue
            if "latitude" in lowered:
                new_cols.append("Latitude [degrees_north]")
                continue
            if lowered == "bot. depth [m]" or "bot" in lowered:
                new_cols.append("Bot. Depth [m]")
                continue

            # User overrides
            if custom_names and col in custom_names:
                new_cols.append(custom_names[col])
                continue

            # Default: keep as-is (only trim whitespace)
            new_cols.append(col_stripped)

        df.columns = new_cols

        final_frames.append(df)

    # --------------------------------------------------------
    # 7. Combine all cleaned files
    # --------------------------------------------------------
    final_df = pd.concat(final_frames, ignore_index=True)

    # --------------------------------------------------------
    # 8. Enforce ODV column order
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # 9. Move "File name" to the end if present
    # --------------------------------------------------------
    if "File name" in final_df.columns:
        cols = [c for c in final_df.columns if c != "File name"]
        cols.append("File name")
        final_df = final_df[cols]

    return final_df
