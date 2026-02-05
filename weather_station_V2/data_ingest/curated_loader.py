import pandas as pd
import os


def load_curated_data():
    """
    Load curated St. Laurent and ECCC data from the data/ directory.
    These files contain older, pre-cleaned historical data that should
    be appended to newly ingested data before merging.
    """
    base = os.path.join(os.path.dirname(__file__), "..", "data")

    stl_path = os.path.join(base, "stl_avgs_curated.csv")
    eccc_path = os.path.join(base, "eccc_df_curated.csv")

    stl = pd.read_csv(stl_path)
    eccc = pd.read_csv(eccc_path)

    # Parse datetime columns
    stl["Datetime"] = pd.to_datetime(stl["Datetime"], errors="coerce")
    eccc["Datetime"] = pd.to_datetime(eccc["Datetime"], errors="coerce")

    return {
        "stl": stl,
        "eccc": eccc
    }
