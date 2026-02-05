import pandas as pd


def merge_dataframes(stl_df, eccc_df):
    """
    Merge cleaned St. Laurent and ECCC weather station dataframes.

    Steps:
    1. Outer merge on Datetime
    2. Sort chronologically
    3. Crop to the first ECCC timestamp (to match original app behavior)
    4. Reset index
    """

    # Ensure datetime is datetime
    stl_df = stl_df.copy()
    eccc_df = eccc_df.copy()

    stl_df["Datetime"] = pd.to_datetime(stl_df["Datetime"], errors="coerce")
    eccc_df["Datetime"] = pd.to_datetime(eccc_df["Datetime"], errors="coerce")

    # ------------------------------------------------------------------
    # 1. Outer merge on Datetime
    # ------------------------------------------------------------------
    merged = pd.merge(
        stl_df,
        eccc_df,
        how="outer",
        on="Datetime",
        sort=True
    )

    # ------------------------------------------------------------------
    # 2. Sort chronologically
    # ------------------------------------------------------------------
    merged = merged.sort_values("Datetime").reset_index(drop=True)

    # ------------------------------------------------------------------
    # 3. Crop to first ECCC timestamp
    # ------------------------------------------------------------------
    if not eccc_df["Datetime"].isna().all():
        first_eccc_date = eccc_df["Datetime"].min()
        merged = merged[merged["Datetime"] >= first_eccc_date]

    # ------------------------------------------------------------------
    # 4. Reset index again after cropping
    # ------------------------------------------------------------------
    merged = merged.reset_index(drop=True)

    return merged