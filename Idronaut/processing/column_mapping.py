"""
column_mapping.py — Centralized mapping of Idronaut column names
to CanWIN-standard variable names.

Why this helper exists:
    • Keeps the main cleaning pipeline clean and readable
    • Makes it easy to update or extend mappings later
    • Ensures all renaming logic lives in one predictable place
"""

def map_idronaut_column(col):
    """
    Map a raw Idronaut column name to a CanWIN-standard name.

    This function receives the *original* column name from the file
    (after header validation has standardized capitalization),
    and returns the new standardized name.

    If the column is not recognized, it is returned unchanged.

    Parameters
    ----------
    col : str
        The original column name from the Idronaut file.

    Returns
    -------
    str
        The mapped CanWIN-standard column name.
    """

    # Metadata columns are handled separately in the cleaning pipeline
    if col in ["Datetime", "Latitude", "Longitude", "Site ID"]:
        return col

    # Core Idronaut → CanWIN mappings
    if "Pres" in col:
        return "Pres_Z"
    if "Temp" in col:
        return "CTDTmp90"
    if col == "Cond":
        return "CTDCond"
    if "Sal" in col:
        return "CTDSal"
    if "Turb" in col:
        return "Turbidity"
    if "SigmaT" in col:
        return "SigTheta"
    if "Cond25" in col:
        return "CTDCond25_raw"
    if "Cond_std25_calculated" in col:
        return "CTDCond25_calc"

    # Unknown columns are preserved as-is
    return col


def rvq_name_for(column_name):
    """
    Given a standardized CanWIN column name, return the corresponding
    Result Value Qualifier (RVQ) column name.

    Example:
        "CTDTmp90" → "CTDTmp90_Result_Value_Qualifier"

    This helper keeps RVQ naming consistent across the workflow.
    """
    return f"{column_name}_Result_Value_Qualifier"
