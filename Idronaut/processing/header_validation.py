import pandas as pd

# ============================================================
# HEADER VALIDATION
# ============================================================
def validate_idronaut_headers(df):
    """
    Check that the uploaded Idronaut file contains the columns we expect.

    This helps catch cases where:
      - The file is not an Idronaut export
      - Column names are misspelled or formatted differently
      - The file uses unexpected spacing or capitalization

    The function:
      1. Compares the file’s column names to the expected Idronaut names
      2. Reports missing columns in a friendly error message
      3. Renames columns to a consistent format (e.g., fixes capitalization)

    Returns:
      (cleaned_dataframe, None) if everything looks good
      (None, "error message") if something is wrong
    """

    expected = [
        "Date", "Time", "Pres", "Temp", "Cond",
        "Sal", "Turb", "SigmaT", "Cond25"
    ]

    # Normalize column names for comparison
    df_cols_lower = [c.strip().lower() for c in df.columns]
    expected_lower = [c.lower() for c in expected]

    # Identify missing columns
    missing = [col for col in expected_lower if col not in df_cols_lower]

    # If *all* expected columns are missing, the file is probably not Idronaut
    if len(missing) == len(expected_lower):
        return None, (
            "❌ None of the expected Idronaut columns were found.\n\n"
            f"Expected columns include:\n{expected}"
        )

    # If only some are missing, warn the user
    if missing:
        return None, (
            "⚠️ Some required Idronaut columns are missing.\n\n"
            f"Missing: {missing}\n\n"
            "Please check your file format."
        )

    # Build a rename map so columns match our expected names exactly
    rename_map = {}
    for col in df.columns:
        col_clean = col.strip().lower()
        if col_clean in expected_lower:
            rename_map[col] = expected[expected_lower.index(col_clean)]

    df = df.rename(columns=rename_map)

    return df, None
