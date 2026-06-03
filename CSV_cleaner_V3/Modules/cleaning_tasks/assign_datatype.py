import pandas as pd

def assign_datatype(
    df: pd.DataFrame,
    *,
    type_mapping,
    **kwargs
):
    """
    Convert selected columns to user-assigned data types.

    Supported conversions include date, date_only, time_only, integer, float,
    and string. Columns that cannot be converted are reported as warnings.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset whose columns will be converted.

    type_mapping : dict[str, str]
        Mapping of column name → target dtype keyword.
        Supported types:
            - "date"
            - "date_only"
            - "time_only"
            - "integer"
            - "float"
            - "string"

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A copy of the input DataFrame with converted columns where possible.
    """

    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors
    # -----------------------------------------------------

    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    if not isinstance(type_mapping, dict):
        raise ValueError("type_mapping must be a dictionary.")

    converters = {
        "date": lambda s: pd.to_datetime(s, errors="coerce"),
        "date_only": lambda s: pd.to_datetime(s, errors="coerce").dt.date,
        "time_only": lambda s: pd.to_datetime(s, errors="coerce").dt.time,
        "integer": lambda s: pd.to_numeric(s, errors="coerce").astype("Int64"),
        "float": lambda s: pd.to_numeric(s, errors="coerce").astype(float),
        "string": lambda s: s.astype("string"),
    }

    # Validate dtype keywords
    for col, dtype in type_mapping.items():
        if dtype not in converters:
            raise ValueError(
                f"Unknown data type '{dtype}' for column '{col}'. "
                f"Supported types: {list(converters.keys())}"
            )

    cleaned_df = df.copy()

    # -----------------------------------------------------
    # 2. CORE PROCESSING
    # -----------------------------------------------------

    for col, dtype in type_mapping.items():

        # Skip missing columns - widget handles soft validation
        if col not in cleaned_df.columns:
            continue

        try:
            cleaned_df[col] = converters[dtype](cleaned_df[col])
        except Exception:
            # Conversion errors are silently ignored - widget handles warnings
            pass

    # -----------------------------------------------------
    # 3. RETURN
    # -----------------------------------------------------
    return cleaned_df
