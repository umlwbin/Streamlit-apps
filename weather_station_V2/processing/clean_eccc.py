import pandas as pd


def clean_eccc(df):
    """Clean ECCC weather station data and return cleaned dataframe."""
    df = df.copy()

    # ------------------------------------------------------------------
    # 1. Remove milliseconds and convert datetime
    # ------------------------------------------------------------------
    if df["Datetime"].dtype == object:
        df["Datetime"] = df["Datetime"].str.split(".").str[0]

    df["Datetime"] = pd.to_datetime(df["Datetime"], errors="coerce")
    df["Datetime"] = df["Datetime"].dt.tz_localize(None)


    # ------------------------------------------------------------------
    # 2. Drop unused columns (same list as original app)
    # ------------------------------------------------------------------
    drop_cols = [
        '3-hour pressure tendency amount',
        '3-hour pressure tendency characteristic',
        '5-minute cumulative precipitation gauge filtered weight for minutes 55 to 60',
        'Average 10 meter wind speed over past 10 minutes',
        'Average 10 meter wind speed over past 2 minutes',
        'Average snow depth over past 5 minutes',
        'Average wind direction at 10 meters over past 2 minutes',
        'Average wind speed at precipitation gauge over past 10 minutes',
        'Data Availability',
        'Datalogger panel temperature',
        'Dew Point Temperature',
        'Maximum 10 meter wind speed over past 1 hour',
        'Maximum 10 meter wind speed over past 10 minutes',
        'Maximum Air Temperature over past 1 hour',
        'Maximum Air Temperature over past 24 hours',
        'Maximum Air Temperature over past 6 hours',
        'Maximum Battery Voltage over past 1 hour',
        'Maximum Relative Humidity over past 1 hour',
        'Minimum Air Temperature over past 1 hour',
        'Minimum Air Temperature over past 24 hours',
        'Minimum Air Temperature over past 6 hours',
        'Minimum Battery Voltage Past 1 Hour',
        'Minimum Relative Humidity over past 1 hour',
        'Precipitation Amount since last synoptic hour',
        'Precipitation amount over past 24 hours',
        'Precipitation amount over past 3 hours',
        'Precipitation amount over past 6 hours',
        'Timestamp of maximum wind speed over past hour',
        'Vectoral average 10 meter wind direction over past 10 minutes',
        'Wet-bulb Temperature',
        'Wind direction associated with the maximum wind speed at 10 meters over past 1 hour',
        'Wind direction associated with the maximum wind speed at 10 meters over past 10 minutes',
        'MS'
    ]

    df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")

    return df
