import pandas as pd


# Explicit formats we want to support for Idronaut exports
IDRONAUT_DATE_FORMATS = [
    "%Y-%m-%d",     # 2024-01-15
    "%d-%m-%Y",     # 15-01-2024
    "%m/%d/%Y",     # 01/15/2024
    "%Y/%m/%d",     # 2024/01/15
    "%d/%m/%Y",     # 15/01/2024
]

IDRONAUT_TIME_FORMATS = [
    "%H:%M:%S",          # 13:59:23
    "%H:%M",             # 13:59
    "%H:%M:%S.%f",       # 13:59:23.69 or 13:59:23.123456
    "%I:%M:%S %p",       # 1:59:23 PM
    "%I:%M %p",          # 1:59 PM
]



# ============================================================
# Helper: Parse a date/time column using multiple formats
# ============================================================
def parse_with_formats(series, formats, description="value"):
    """
    Try to parse a pandas Series using a list of explicit formats.

    Why this helper exists:
      - Pandas will try to "guess" the format if none is provided
      - Guessing triggers warnings and can lead to inconsistent results
      - Idronaut files sometimes vary in formatting (e.g., 2024-01-15 vs 15/01/2024)

    This function:
      1. Tries each format in the provided list
      2. Returns the first successful parse
      3. Falls back to pandas' flexible parser only if needed

    Parameters
    ----------
    series : pd.Series
        The column to parse (e.g., df["Date"] or df["Time"])
    formats : list of str
        A list of datetime format strings to try
    description : str
        A friendly label used in error messages

    Returns
    -------
    pd.Series (datetime64)
        A parsed datetime series (or NaT for unparseable rows)
    """
    # Try each explicit format in order
    for fmt in formats:
        try:
            return pd.to_datetime(series, format=fmt)
        except Exception:
            continue

    # If none of the formats worked, fall back to pandas' flexible parser.
    # This avoids errors but may produce NaT for inconsistent values.
    return pd.to_datetime(series, errors="coerce")
