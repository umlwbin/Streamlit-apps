import pandas as pd

def assign(df, type_mapping):
    """
    Convert selected columns to user-assigned data types.
    """

    cleaned_df = df.copy()

    # Minimal summary
    summary = {
        "task_name": "assign_datatype",
        "converted": [],
        "errors": []
    }

    # Supported converters
    converters = {
        "date": lambda s: pd.to_datetime(s, errors="coerce"),
        "date_only": lambda s: pd.to_datetime(s, errors="coerce").dt.date,
        "time_only": lambda s: pd.to_datetime(s, errors="coerce").dt.time,
        "integer": lambda s: pd.to_numeric(s, errors="coerce").astype("Int64"),
        "float": lambda s: pd.to_numeric(s, errors="coerce").astype(float),
        "string": lambda s: s.astype("string")
    }

    # ---------------------------------------------------------
    # Apply conversions
    # ---------------------------------------------------------
    for col, dtype in type_mapping.items():

        # Column does not exist
        if col not in cleaned_df.columns:
            summary["errors"].append(f"Column '{col}' does not exist and was skipped.")
            continue

        # Unknown dtype
        if dtype not in converters:
            summary["errors"].append(f"Unknown data type '{dtype}' for column '{col}'.")
            continue

        try:
            # Apply conversion
            cleaned_df[col] = converters[dtype](cleaned_df[col])
            summary["converted"].append((col, dtype))

        except Exception as e:
            # Catch unexpected conversion errors
            summary["errors"].append(f"Failed to convert '{col}' to '{dtype}': {str(e)}")

    return cleaned_df, summary
