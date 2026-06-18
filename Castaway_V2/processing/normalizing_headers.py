"""
normalizing_headers.py

Utility functions for cleaning metadata variable names so they can be
safely used as column names in the final dataframe.

This file is intentionally simple - the Castaway workflow only needs
basic name cleaning, not full normalization modes.
"""

import re

# -------------------------------------------------------------------
# BASIC NAME CLEANING
# -------------------------------------------------------------------

def clean_metadata_name(name: str) -> str:
    """
    Clean up a metadata variable name so it is safe to use as a column name.

    This function:
      • Converts the name to a string
      • Removes punctuation and special characters; keeps only letters, numbers, and spaces
      • Collapses multiple spaces into one
      • Strips leading/trailing whitespace

    Examples:
        "Cast time (UTC)"   → "Cast time UTC"
        "% Start latitude"  → "Start latitude"
        "File-name"         → "File name"

    This function is used throughout the workflow whenever metadata
    variables are inserted into the final dataframe.

    **** If you're looking for where this is used, check:
      processing/processing.py → build_final_dataframe()
    """

    name = str(name)

    # Remove punctuation and symbols (keep letters, numbers, spaces)
    name = re.sub(r"[^a-zA-Z0-9 ]+", "", name)

    # Collapse multiple spaces
    name = re.sub(r"\s+", " ", name)

    return name.strip()
