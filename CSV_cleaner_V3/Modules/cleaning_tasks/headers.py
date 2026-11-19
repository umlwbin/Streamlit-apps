import re
import unicodedata
import pandas as pd
import streamlit as st


# =========================================================
# UNIT NORMALIZATION HELPERS
# =========================================================
def normalize_unit_string(unit_raw):

    if not unit_raw:
        return ""

    return (
        str(unit_raw)
        .strip()
        .lower()
    )


# ---------------------------------------------------------
# LOAD UNIT MAP FROM GOOGLE SHEET
# ---------------------------------------------------------
GOOGLE_SHEET_CSV_URL = ("https://docs.google.com/spreadsheets/d/e/2PACX-1vS-NlRtFkD24tm2P6v5WjMioxGqggjb9bzalVsg664tHgWX1IPiLxhSpnySSTEe4i7IbzYkfuKXt9OH/pub?gid=1132759519&single=true&output=csv")

unit_map_dict = None
def load_unit_map():
    global unit_map_dict
    if unit_map_dict is not None:
        return unit_map_dict

    try:
        df = pd.read_csv(GOOGLE_SHEET_CSV_URL) # read google sheet with units

        df = df.dropna(subset=["raw_unit", "normalized_unit"])  # Required columns: raw_unit, normalized_unit

        # Build unit map dict raw -> normalized
        unit_map = {}

        for _, row in df.iterrows():
            normalized_unit = (str(row["normalized_unit"]).strip())

            # We have multiple variations of the same unit on the same row in Unit Map separated by commas.
            # They shoudl all be mapped to the same normalized value, as in the Unit Map. 
            raw_unit_cell=normalize_unit_string(str(row["raw_unit"])) # normalize the entire cell first
            raw_variants = raw_unit_cell.split(",")  # Split raw_unit on commas

            for raw in raw_variants: 
                raw = raw.strip()
                if not raw:
                    continue

                normalized_raw = normalize_unit_string(raw) # noramlize each variant, just in case. 
                unit_map[normalized_raw] = normalized_unit

        unit_map_dict = unit_map  
        return unit_map_dict

    except Exception as e:
        print("Failed to load unit map from Google Sheet:", e)
        unit_map_dict = {}
        return unit_map_dict

UNIT_MAP = load_unit_map()

# Longest matches first
UNIT_KEYS = sorted(UNIT_MAP.keys(),key=len,reverse=True)

# Add any other special charcaters we want to replace with something specific. That we dont want to remove. 
SPECIAL_CHAR_MAP = {
    "%": "percent",
    "µ": "u",
    "μ": "u",  # Greek mu
    "°": "deg",
}


def clean_headers(
    df: pd.DataFrame,
    *,
    header_handling="Move units to metadata table (recommended)",
    **kwargs
):
    """
    Clean scientific column headers.

    Options:
        Keep units in headers
            - removes problematic characters
            - converts headers to snake_case
            - preserves units as part of the header text

        Move units to metadata table
            - detects units using Unit Map
            - strips units from headers
            - stores units in metadata output

    Returns:
        cleaned_df, metadata_df
    """

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    if header_handling not in {
        "Keep units in headers",
        "Move units to metadata table (recommended)",
    }:
        raise ValueError(
            "header_handling must be either "
            "'Keep units in headers' or "
            "'Move units to metadata table (recommended)'."
        )

    # -----------------------------------------------------
    # UNIT DETECTION
    # -----------------------------------------------------
    def detect_units(text):
        """
        Detect units using only the Unit Map.
        """

        text_lower = text.lower()

        for raw_unit in UNIT_KEYS:
            if text_lower.endswith(raw_unit):
                return raw_unit, UNIT_MAP[raw_unit]

        return None, None

    # -----------------------------------------------------
    # HEADER CLEANING
    # -----------------------------------------------------
    def clean_variable_name(name):

        # Preserve a few scientific symbols
        for symbol, replacement in SPECIAL_CHAR_MAP.items():
            name = name.replace(symbol, f"_{replacement}_")

        name = name.lower()

        # Everything else becomes underscore
        name = re.sub(r"[^a-z0-9]+", "_", name)

        # Collapse duplicate underscores
        name = re.sub(r"_+", "_", name)

        return name.strip("_")

    # -----------------------------------------------------
    # PROCESS HEADERS
    # -----------------------------------------------------
    original = list(df.columns)

    cleaned = []
    metadata = {}

    for raw in original:

        # Empty column names
        if not isinstance(raw, str) or raw.strip() == "":

            header = "unnamed_column"

            cleaned.append(header)

            metadata[raw] = {
                "cleaned_header": header,
                "units_raw": None,
                "units_clean": None,
            }
            continue

        try:

            new = str(raw).strip()

            raw_units = None
            cleaned_units = None
            units_raw_original = None

            variable = new

            # -----------------------------------------
            # MOVE UNITS TO METADATA
            # -----------------------------------------
            if header_handling == "Move units to metadata table (recommended)":

                raw_units, cleaned_units = detect_units(new)

                if raw_units:
                    units_raw_original = raw_units

                    variable = re.sub(
                        re.escape(raw_units),
                        "",
                        variable,
                        flags=re.IGNORECASE,
                    )

                # remove leftover brackets
                variable = re.sub(
                    r"\[[^\]]*\]|\([^\)]*\)",
                    "",
                    variable,
                )

            # -----------------------------------------
            # CLEAN HEADER
            # -----------------------------------------
            header = clean_variable_name(variable)

            if not header:
                header = "unnamed_column"

            cleaned.append(header)

            metadata[raw] = {
                "cleaned_header": header,
                "units_raw": units_raw_original,
                "units_clean": cleaned_units,
            }

        except Exception:

            cleaned.append(raw)

            metadata[raw] = {
                "cleaned_header": raw,
                "units_raw": None,
                "units_clean": None,
            }

    # -----------------------------------------------------
    # ENSURE UNIQUE NAMES
    # -----------------------------------------------------
    final = []
    seen = {}

    for name in cleaned:
        if name not in seen:
            seen[name] = 1
            final.append(name)

        else:

            seen[name] += 1
            final.append(f"{name}_{seen[name]}")

    # -----------------------------------------------------
    # METADATA TABLE
    # -----------------------------------------------------
    metadata_df = (
        pd.DataFrame(metadata)
        .transpose()
        .reset_index()
        .rename(columns={"index": "original_header"})
    )

    # -----------------------------------------------------
    # OUTPUT
    # -----------------------------------------------------
    cleaned_df = df.copy()

    cleaned_df.columns = final

    return cleaned_df, metadata_df