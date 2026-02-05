import pandas as pd
import numpy as np

def clean_stl(df):
    """Clean St. Laurent weather station data and return hourly averages with _StL suffix."""
    df = df.copy()

    # ---------------------------------------------------------
    # 1. Rename Rain → Precipitation
    # ---------------------------------------------------------
    if "Rain" in df.columns:
        df.rename(columns={"Rain": "Precipitation"}, inplace=True)

    # ---------------------------------------------------------
    # 2. Add RVQ columns
    # ---------------------------------------------------------
    for col in df.columns:
        if col != "Datetime":
            df[f"{col}_Result_Value_Qualifier"] = ""

    # ---------------------------------------------------------
    # 3. Convert datetime
    # ---------------------------------------------------------
    df["Datetime"] = pd.to_datetime(df["Datetime"], errors="coerce")
    df["Datetime"] = df["Datetime"].dt.tz_localize(None)

    year = df["Datetime"].dt.year
    month = df["Datetime"].dt.month
    day = df["Datetime"].dt.day

    # ---------------------------------------------------------
    # 4. Threshold cleaning
    # ---------------------------------------------------------
    def apply_bounds(col, low, high):
        if col in df.columns:
            df.loc[(df[col] < low) | (df[col] > high), col] = None

    apply_bounds("Air Pressure", 660, 1070)
    apply_bounds("Photosynthetically Active Radiation", 0, 2500)
    apply_bounds("Air Temperature", -40, 75)
    apply_bounds("Relative Humidity", 0, 100)
    apply_bounds("Precipitation", 0, 127)
    apply_bounds("Wind Speed", 0, 115)
    apply_bounds("Wind speed of gust", 0, 115)

    # Wind speed = gust speed and >115 → bad
    if "Wind Speed" in df.columns and "Wind speed of gust" in df.columns:
        mask = (df["Wind Speed"] == df["Wind speed of gust"]) & (df["Wind Speed"] > 115)
        df.loc[mask, ["Wind Speed", "Wind speed of gust"]] = None

    # Wind direction dead zone
    if "Wind From Direction" in df.columns:
        df.loc[(df["Wind From Direction"] > 355) & (df["Wind From Direction"] < 360),
               "Wind From Direction"] = None

    # ---------------------------------------------------------
    # 5. Seasonal precipitation rules
    # ---------------------------------------------------------
    winter = month.isin([12, 1, 2])
    df.loc[winter, "Precipitation"] = None

    df.loc[(month == 10) & (df["Precipitation"] > 0) & (df["Air Temperature"] <= 1),
           "Precipitation"] = None
    df.loc[(month == 11) & (df["Precipitation"] > 0) & (df["Air Temperature"] <= 2),
           "Precipitation"] = None
    df.loc[(month == 3) & (df["Precipitation"] > 0) & (df["Air Temperature"] <= 2),
           "Precipitation"] = None
    df.loc[(month == 4) & (df["Precipitation"] > 0) & (df["Air Temperature"] <= 2),
           "Precipitation"] = None

    # Deployment day rule
    deploy_mask = (year == 2021) & (month == 9) & (day == 24)
    df.loc[deploy_mask & (df["Precipitation"] > 0), "Precipitation"] = None

    # ---------------------------------------------------------
    # 6. Hourly averaging
    # ---------------------------------------------------------
    df["date_and_hour"] = df["Datetime"].dt.floor("H")
    hourly = df.groupby("date_and_hour").mean(numeric_only=True).reset_index()
    hourly.rename(columns={"date_and_hour": "Datetime"}, inplace=True)

    # ---------------------------------------------------------
    # 7. Drop unneeded St. Laurent variables
    # ---------------------------------------------------------
    drop_cols = [
        "Battery Voltage",
        "Photosynthetically Active Radiation"
    ]

    hourly = hourly.drop(columns=[c for c in drop_cols if c in hourly.columns], errors="ignore")

    # ---------------------------------------------------------
    # 8. Add _StL suffix
    # ---------------------------------------------------------
    hourly.columns = [
        "Datetime" if c == "Datetime" else f"{c}_StL"
        for c in hourly.columns
    ]

    return hourly
