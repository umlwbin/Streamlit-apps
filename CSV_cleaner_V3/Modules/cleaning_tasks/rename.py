import pandas as pd

def dedupe_columns(cols):
    """
    Ensure column names are unique by appending suffixes (_1, _2, ...).
    """
    seen = {}
    new_cols = []
    for col in cols:
        if col not in seen:
            seen[col] = 0
            new_cols.append(col)
        else:
            seen[col] += 1
            new_cols.append(f"{col}_{seen[col]}")
    return new_cols


def rename_columns(
    df: pd.DataFrame,
    *,
    filename=None,
    standardized_names,
    **kwargs
):
    """
    Rename the columns of a DataFrame in a safe and predictable way.

    This task:
        - works on a copy of the DataFrame
        - validates that the number of new names matches the number of existing columns
        - trims whitespace and converts new names to strings
        - ensures uniqueness by appending suffixes (_1, _2, ...)
        - returns only cleaned_df
    """

    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors
    # -----------------------------------------------------

    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    if not isinstance(standardized_names, list):
        raise ValueError("standardized_names must be a list of column names.")

    try:
        standardized_names = [str(n).strip() for n in standardized_names]
    except Exception:
        raise ValueError("All standardized_names must be convertible to strings.")

    # Make a copy!
    cleaned_df = df.copy()

    # -----------------------------------------------------
    # 2. VALIDATION - Column count must match
    # -----------------------------------------------------

    if len(cleaned_df.columns) != len(standardized_names):
        # soft validation is handled in the widget; If mismatch --> return unchanged.
        metadata_df = pd.DataFrame({
                    "original_header": cleaned_df.columns,
                    "renamed_header": cleaned_df.columns
                })
        return cleaned_df, metadata_df

    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------

    safe_names = dedupe_columns(standardized_names)
    cleaned_df.columns = safe_names

    # -----------------------------------------------------
    # 4. BUILD METADATA TABLE
    # -----------------------------------------------------
    metadata_df=pd.DataFrame({
            "original_header":df.columns,
            "renamed_headers": safe_names
        })
    # -----------------------------------------------------
    # 5. RETURN
    # -----------------------------------------------------
    return cleaned_df, metadata_df
