import pandas as pd
import re

def clean_column_values(df: pd.DataFrame, *, column, **kwargs):
    """
    Remove all non-alphanumeric characters from a column.
    Keeps letters, numbers, and underscores.

    Input: column - column to clean (str)
    """

    # -----------------------------------------------------
    # 1. VALIDATION (raise errors)
    # -----------------------------------------------------
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    # -----------------------------------------------------
    # 2. CORE PROCESSING LOGIC
    # -----------------------------------------------------
    cleaned_df = df.copy()

    cleaned_df[column] = (
        cleaned_df[column]
        .astype(str)
        .apply(lambda x: re.sub(r"[^A-Za-z0-9.-]+", "", x)) #find everything BUT the alphanumeric charcaters (plus - and .) and remove them
    )

    # -----------------------------------------------------
    # 3. RETURN STANDARDIZED OUTPUT
    # -----------------------------------------------------
    return cleaned_df
