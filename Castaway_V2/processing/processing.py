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
    normalization_mode="Keep cleaned names"
):

    final_frames = []

    for df, meta in zip(data_list, metadata_list):

        meta = meta.dropna(axis=1, how="all")

        # 1. Insert selected metadata variables
        for var in selected_vars:
            var_clean = clean_metadata_name(var)
            row = meta[meta["Variable"].astype(str).str.contains(var, regex=False)]
            if not row.empty:
                value = row["Value"].iloc[0]
                safe_insert_column(df, var_clean, value)

        # 2. Insert new user-defined variables
        for name, value in new_vars.items():
            safe_insert_column(df, name, value)

        # 3. Remove unwanted columns
        df = drop_columns(df, omit_list)


        # 4. Normalize column names
        new_cols = []
        for col in df.columns:

            # Trim whitespace only
            col_stripped = col.strip()

            lowered = col_stripped.lower()

            # Step 1: automatic ODV standardization (only these 7)
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
            if "depth" in lowered:
                new_cols.append("Bot. Depth [m]")
                continue

            # Step 2: user overrides (from Step 4)
            if col in custom_names:
                new_cols.append(custom_names[col])
                continue

            # Step 3: no additional cleaning — keep exactly as provided
            new_cols.append(col_stripped)

        df.columns = new_cols


        final_frames.append(df)

    # --------------------------------------------------------
    # 5. Combine all cleaned files
    # --------------------------------------------------------
    final_df = pd.concat(final_frames, ignore_index=True)

    # --------------------------------------------------------
    # 6. Enforce ODV column order (AFTER concatenation)
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

    # 7. Move "File name" to the end if present
    if "File name" in final_df.columns:
        cols = [c for c in final_df.columns if c != "File name"]
        cols.append("File name")
        final_df = final_df[cols]


    return final_df
