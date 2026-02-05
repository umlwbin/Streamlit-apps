import pandas as pd

def fetch_eccc_data():
    """Fetch raw ECCC weather station data from server."""
    url = "https://sta-canwin.ad.umanitoba.ca/loader/18"
    rows = 8978
    cols = [
        'Datetime', '3-hour pressure tendency amount',
        '3-hour pressure tendency characteristic',
        '5-minute cumulative precipitation gauge filtered weight for minutes 55 to 60',
        'Air Temperature', 'Average 10 meter wind speed over past 1 hour',
        'Average 10 meter wind speed over past 10 minutes',
        'Average 10 meter wind speed over past 2 minutes',
        'Average air temperature over past 1 hour',
        'Average snow depth over past 5 minutes',
        'Average wind direction at 10 meters over past 2 minutes',
        'Average wind speed at precipitation gauge over past 10 minutes',
        'Data Availability', 'Datalogger panel temperature',
        'Dew Point Temperature', 'Maximum 10 meter wind speed over past 1 hour',
        'Maximum 10 meter wind speed over past 10 minutes',
        'Maximum Air Temperature over past 1 hour',
        'Maximum Air Temperature over past 24 hours',
        'Maximum Air Temperature over past 6 hours',
        'Maximum Battery Voltage over past 1 hour',
        'Maximum Relative Humidity over past 1 hour',
        'Mean Sea Level Pressure', 'Minimum Air Temperature over past 1 hour',
        'Minimum Air Temperature over past 24 hours',
        'Minimum Air Temperature over past 6 hours',
        'Minimum Battery Voltage Past 1 Hour',
        'Minimum Relative Humidity over past 1 hour',
        'Precipitation Amount over past 1 hour',
        'Precipitation Amount since last synoptic hour',
        'Precipitation amount over past 24 hours',
        'Precipitation amount over past 3 hours',
        'Precipitation amount over past 6 hours',
        'Rainfall amount over past 1 hour', 'Relative Humidity',
        'Station Pressure', 'Timestamp of maximum wind speed over past hour',
        'Vector average 10 meter wind direction over past 1 hour',
        'Vectoral average 10 meter wind direction over past 10 minutes',
        'Wet-bulb Temperature',
        'Wind direction associated with the maximum wind speed at 10 meters over past 1 hour',
        'Wind direction associated with the maximum wind speed at 10 meters over past 10 minutes'
    ]

    try:
        return pd.read_csv(url, skiprows=rows+1, names=cols)
    except Exception as e:
        return None
