from data_ingest.fetch_stl import fetch_stl_data
from data_ingest.fetch_eccc import fetch_eccc_data
from data_ingest.curated_loader import load_curated_data

from processing.clean_stl import clean_stl
from processing.clean_eccc import clean_eccc
from processing.merge import merge_dataframes


def load_all_weather_data(use_curated=True):
    """Main orchestrator for ingestion → cleaning → merging."""

    # Fetch raw data
    stl_raw = fetch_stl_data()
    eccc_raw = fetch_eccc_data()
    if stl_raw is None or eccc_raw is None:
        return None  # signals failure to app.py

    # Clean
    stl_clean = clean_stl(stl_raw)
    eccc_clean = clean_eccc(eccc_raw)

    # Merge curated data
    if use_curated:
        curated = load_curated_data()
        import pandas as pd

        stl_clean = pd.concat([curated["stl"], stl_clean], ignore_index=True)
        eccc_clean = pd.concat([curated["eccc"], eccc_clean], ignore_index=True)


    # Final combined dataframe
    combined = merge_dataframes(stl_clean, eccc_clean)

    return stl_clean, eccc_clean, combined
