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
#GOOGLE_SHEET_CSV_URL = ("https://docs.google.com/spreadsheets/d/e/2PACX-1vS-NlRtFkD24tm2P6v5WjMioxGqggjb9bzalVsg664tHgWX1IPiLxhSpnySSTEe4i7IbzYkfuKXt9OH/pub?gid=1618419054&single=true&output=csv")

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
UNIT_KEYS = sorted(
    UNIT_MAP.keys(),
    key=len,
    reverse=True
)


# =========================================================
# MAIN CLEANING FUNCTION
# =========================================================
def clean_headers(
    df: pd.DataFrame,
    *,
    naming_style="snake_case",
    preserve_units=True,
    no_units_in_header=False,
    **kwargs
):
    """
    Clean scientific column headers using a curated Unit Map.

    Process:
        - finds units using spreadsheet lookups only!
        - removes units from variable names
        - standardizes variable naming style
        - optionally reattaches normalized units
        - returns metadata describing the transformation

    The Unit Map is the single source of truth. No unit guessing done. 
    Returns:
        cleaned_df, metadata_df
    """

    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors
    # -----------------------------------------------------
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    if naming_style not in {"snake_case", "camelCase", "Title Case"}:
        raise ValueError("naming_style must be one of: 'snake_case', 'camelCase', 'Title Case'.")

    # -----------------------------------------------------
    # 2. CORE PROCESSING LOGIC
    # -----------------------------------------------------

    # -----------------------------------------------------
    # UNIT DETECTION HELPER
    # -----------------------------------------------------
    def detect_units(text):
        """
        Detect units using ONLY values from the Unit Map.

        Returns:
            raw_unit_found, normalized_unit
        """

        text_lower = text.lower()

        for raw_unit in UNIT_KEYS:
            if text_lower.endswith(raw_unit):
                return raw_unit, UNIT_MAP[raw_unit]

        return None, None

    # -----------------------------------------------------
    # VARIABLE NAME CLEANING HELPER
    # -----------------------------------------------------
    def clean_variable_name(name):
        name = name.lower()
        name = re.sub(r"[^a-z0-9]+", "_", name)
        name = re.sub(r"_+", "_", name).strip("_")
        return name

    # -----------------------------------------------------
    # BEGIN PROCESSING EACH HEADER
    # -----------------------------------------------------
    original = list(df.columns)
    cleaned = []
    metadata = {}

    for raw in original:

        # Handle empty headers
        if not isinstance(raw, str) or raw.strip() == "":
            fallback = "unnamed_column"
            cleaned.append(fallback)
            metadata[raw] = {
                "units_raw": None,
                "units_clean": None,
                "cleaned_header": fallback,
            }
            continue

        try:
            new = str(raw).strip()

            # -----------------------------
            # UNIT EXTRACTION
            # -----------------------------
            raw_units = None
            cleaned_units = None
            units_raw_original = None

            if not no_units_in_header:
                raw_units, cleaned_units = detect_units(new)

                if raw_units:
                    units_raw_original = raw_units


            # Remove units from variable name
            variable = new
            if raw_units:
                variable = re.sub(re.escape(raw_units), "", variable, flags=re.IGNORECASE)


            # Remove any left over bracketed content or just the empty brackets themselves
            variable = re.sub(r"\[[^\]]*\]|\([^\)]*\)", "", variable)
            variable = variable.strip().rstrip(",")

            # Clean variable name
            variable_clean = clean_variable_name(variable)

            # -----------------------------
            # FINAL HEADER ASSEMBLY
            # -----------------------------
            # HEre we are putting the units in round bracktes
            if preserve_units and cleaned_units:
                header = f"{variable_clean} ({cleaned_units})"
            else:
                header = variable_clean

            # Naming style
            if naming_style == "camelCase":
                parts = variable_clean.split("_")
                header = parts[0] + "".join(p.capitalize() for p in parts[1:])
                if preserve_units and cleaned_units:
                    header = f"{header} ({cleaned_units})"

            elif naming_style == "Title Case":
                header = " ".join(p.capitalize() for p in variable_clean.split("_"))
                if preserve_units and cleaned_units:
                    header = f"{header} ({cleaned_units})"


            # Fallback for empty header
            if header == "":
                header = "unnamed_column"

            cleaned.append(header)

            # The metadata dict looks like: "{ Temp (°C)": {"variable": "temp", "units_raw": "C", "units_clean": "degC", "cleaned_header": "temp [degC]"} , ... },
            metadata[raw] = {
                "cleaned_header": header,
                "units_raw": units_raw_original,
                "units_clean": cleaned_units,
            }

        except Exception:
            # If anything fails, preserve original header
            cleaned.append(raw)
            metadata[raw] = {
                "cleaned_header": raw,
                "units_raw": None,
                "units_clean": None,
            }
    # -----------------------------------------------------
    # 3d. ENSURE UNIQUENESS
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
    # 4. BUILD METADATA TABLE
    # -----------------------------------------------------
    # When you convert a dict of dicts into a DataFrame, the outer dictionary keys automatically become the index
    metadata_df = (
        pd.DataFrame(metadata)
        .transpose()
        .reset_index()
        .rename(columns={"index": "original_header"}) # turns the keys into the “original_header” column
    )

    # -----------------------------------------------------
    # 5. RETURN
    # -----------------------------------------------------
    cleaned_df = df.copy()
    cleaned_df.columns = final

    return cleaned_df, metadata_df
