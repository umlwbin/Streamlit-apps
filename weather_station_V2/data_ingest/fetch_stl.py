import pandas as pd

def fetch_stl_data():
    """Fetch raw St. Laurent weather station data from server."""
    url = "https://sta-canwin.ad.umanitoba.ca/loader/11"
    rows = 88178
    cols = [
        'Datetime', 'Air Pressure', 'Air Temperature', 'Battery Voltage',
        'Photosynthetically Active Radiation', 'Rain', 'Relative Humidity',
        'Wind From Direction', 'Wind Speed', 'Wind speed of gust'
    ]

    try:
        return pd.read_csv(url, skiprows=rows+1, names=cols)
    except Exception as e:
        return None
