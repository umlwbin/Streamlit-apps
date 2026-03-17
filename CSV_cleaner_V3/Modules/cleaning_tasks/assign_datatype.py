import pandas as pd


def assign_datatype(
    df: pd.DataFrame,
    *,
    filename=None,
    type_mapping
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

    summary : dict
        {
            "converted": [(column, dtype)],
            "warnings": [list of soft validation messages]
        }

    summary_df : None
        Always None for this task (included for template consistency).

    Notes
    -----
    - Hard validation errors (e.g., unknown dtype keyword) raise exceptions.
    - Soft validation issues (e.g., missing columns, conversion failures) appear
      in summary["warnings"] but do not stop execution.
    """


    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors (A, B, C…)
    # -----------------------------------------------------

    # A. df must be a DataFrame
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    # B. type_mapping must be a dict
    if not isinstance(type_mapping, dict):
        raise ValueError("type_mapping must be a dictionary.")

    # C. dtype keywords must be valid
    converters = {
        "date": lambda s: pd.to_datetime(s, errors="coerce"),
        "date_only": lambda s: pd.to_datetime(s, errors="coerce").dt.date,
        "time_only": lambda s: pd.to_datetime(s, errors="coerce").dt.time,
        "integer": lambda s: pd.to_numeric(s, errors="coerce").astype("Int64"),
        "float": lambda s: pd.to_numeric(s, errors="coerce").astype(float),
        "string": lambda s: s.astype("string"),
    }

    for col, dtype in type_mapping.items():
        if dtype not in converters:
            raise ValueError(
                f"Unknown data type '{dtype}' for column '{col}'. "
                f"Supported types: {list(converters.keys())}"
            )

    cleaned_df = df.copy()

    # -----------------------------------------------------
    # 2. VALIDATION - Soft Checks (A, B, C…)
    # -----------------------------------------------------
    warnings = []

    # A. Warn if a column does not exist (but continue)
    for col in type_mapping:
        if col not in cleaned_df.columns:
            warnings.append(f"Column '{col}' does not exist and was skipped.")

    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------
    converted = []

    for col, dtype in type_mapping.items():

        # Skip missing columns (already warned)
        if col not in cleaned_df.columns:
            continue

        try:
            cleaned_df[col] = converters[dtype](cleaned_df[col])
            converted.append((col, dtype))

        except Exception as e:
            warnings.append(f"Failed to convert '{col}' to '{dtype}': {str(e)}")

    # -----------------------------------------------------
    # 4. SUMMARY
    # -----------------------------------------------------
    summary = {
        "converted": converted,
        "warnings": warnings,
    }

    # -----------------------------------------------------
    # 5. SUMMARY DATAFRAME
    # -----------------------------------------------------
    summary_df = None

    # -----------------------------------------------------
    # 6. RETURN
    # -----------------------------------------------------
    return cleaned_df, summary, summary_df
