import re

# ------------------------------------------------------------
# BASIC NAME CLEANING
# ------------------------------------------------------------

def clean_metadata_name(name: str) -> str:
    """
    Clean up a metadata variable name so it is safe to use as a column name.

    Steps:
    - Convert to string
    - Remove special characters (keep letters, numbers, spaces)
    - Collapse multiple spaces
    - Strip leading/trailing spaces
    """
    name = str(name)
    name = re.sub(r"[^a-zA-Z0-9 ]+", "", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()


# ------------------------------------------------------------
# NORMALIZATION STYLES
# ------------------------------------------------------------

def to_snake_case(name: str) -> str:
    """
    Convert a cleaned name into snake_case.
    Example: "Start Longitude" → "start_longitude"
    """
    name = clean_metadata_name(name)
    return name.lower().replace(" ", "_")


def to_odv_name(name: str) -> str:
    """
    Convert a cleaned name into ODV-style UPPERCASE_UNDERSCORES.
    Example: "Start Longitude" → "START_LONGITUDE"
    """
    name = clean_metadata_name(name)
    return name.upper().replace(" ", "_")


# ------------------------------------------------------------
# MAIN NORMALIZATION ENTRY POINT
# ------------------------------------------------------------

def normalize_column_name(name: str, mode: str) -> str:
    """
    Normalize a column name based on the selected mode.

    mode options:
    - "Keep cleaned names"
    - "snake_case"
    - "ODV-friendly (UPPERCASE_UNDERSCORES)"
    """
    if mode == "snake_case":
        return to_snake_case(name)
    elif mode.startswith("ODV"):
        return to_odv_name(name)
    else:
        return clean_metadata_name(name)
