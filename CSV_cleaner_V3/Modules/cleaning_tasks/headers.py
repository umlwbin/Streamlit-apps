import re
import unicodedata
import pandas as pd

from Modules.utils.units import UNIT_MAP



import pandas as pd
import re
import unicodedata


# =========================================================
# UNIT NORMALIZATION HELPERS
# =========================================================
def normalize_unit_string(unit_raw):
    """
    Normalize a raw unit string into ASCII-safe, CF-style format:
        - remove unicode
        - replace slashes with spaces
        - convert superscripts to ASCII
        - ensure negative exponents use '-'
        - collapse whitespace
    """
    if not unit_raw:
        return None

    # ASCII normalize (strip accents, unicode)
    u = unicodedata.normalize("NFKD", unit_raw)
    u = u.encode("ascii", "ignore").decode("ascii")

    # Replace slashes with spaces
    u = u.replace("/", " ")

    # Replace caret exponents like m^2 or m^-2
    u = re.sub(r"\^(-?\d+)", r"\1", u)

    # Replace unicode superscripts
    superscript_map = {
        "⁻": "-",
        "⁺": "+",
        "¹": "1",
        "²": "2",
        "³": "3",
    }
    for k, v in superscript_map.items():
        u = u.replace(k, v)

    # Collapse whitespace
    u = re.sub(r"\s+", " ", u).strip()

    return u.lower()




# ---------------------------------------------------------
# LOAD UNIT MAP FROM GOOGLE SHEET
# ---------------------------------------------------------

GOOGLE_SHEET_CSV_URL = ("https://docs.google.com/spreadsheets/d/e/2PACX-1vS-NlRtFkD24tm2P6v5WjMioxGqggjb9bzalVsg664tHgWX1IPiLxhSpnySSTEe4i7IbzYkfuKXt9OH/pub?gid=1618419054&single=true&output=csv")

unit_map_dict = None
def load_unit_map():
    global unit_map_dict
    if unit_map_dict is not None:
        return unit_map_dict

    try:
        df = pd.read_csv(GOOGLE_SHEET_CSV_URL) # read google sheet with units
        df = df.dropna(subset=["raw_unit", "normalized_unit"])  # Required columns: raw_unit, normalized_unit

        # Build unit map dict raw -> normalized
        unit_map_dict = {
            normalize_unit_string(row["raw_unit"]): str(row["normalized_unit"]).strip()
            for _, row in df.iterrows()
        }

        return unit_map_dict

    except Exception as e:
        print("Failed to load unit map from Google Sheet:", e)
        unit_map_dict = {}
        return unit_map_dict

UNIT_MAP = load_unit_map()





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
    Clean and standardize messy scientific column headers while extracting metadata.
        - extracts units from headers
        - normalizes units to CF-style ASCII
        - cleans variable names into snake_case / camelCase / Title Case
        - reattaches units as: variable_name (units)
        - returns a metadata table describing the transformation

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

    # These units are ambiguous because they could possibly be apart of the variable name 
    # (they are too short essentially; not unique enough to be clearly identified as units)
    AMBIGUOUS_UNITS = {"m", "g", "s", "%", "h", "l"}


    # -----------------------------------------------------
    # UNIT DETECTION HELPER
    # -----------------------------------------------------
    def detect_units(text):
        # Find bracketed units first
        bracket_match = re.findall(r"\[(.*?)\]|\((.*?)\)", text) # checks for content in () or [] - this is assumed to be the units (returns a list of tuples). eg, [("m/s", "")]

        if bracket_match:
            content = next(filter(None, bracket_match[0])) # filters out the non empty string or any falsey value out of the first tuple. next() takes the first item from the filtered results. 
            return content.strip() # return units

        # Fallback: UNIT_MAP search
        lower = text.lower() #the UNIT_MAP units are added in lower case tobe safe.
        for raw_unit in UNIT_MAP:
            if raw_unit in lower:
                return raw_unit

        return None

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
                "variable": fallback,
                "units_raw": None,
                "units_clean": None,
                "cleaned_header": fallback,
            }
            continue

        try:
            # ASCII normalize
            new = unicodedata.normalize("NFKD", raw) # This breaks apart characters into their simplest ASCII‑friendly components.
            new = new.encode("ascii", "ignore").decode("ascii") # Ignore any character that can't be represented in ASCII, thn decode back from byte sting to regular python string

            # -----------------------------
            # UNIT EXTRACTION
            # -----------------------------
            raw_units = None if no_units_in_header else detect_units(new)
            cleaned_units = None
            units_raw_original = None

            if raw_units:
                # Normalize raw unit string
                # 1. Try exact raw lookup first
                cleaned_units = UNIT_MAP.get(normalize_unit_string(raw_units))

                # 2. If not found, normalize the raw unit
                if cleaned_units is None:
                    normalized = normalize_unit_string(raw_units)

                    # 3. Try lookup on normalized form
                    cleaned_units = UNIT_MAP.get(normalized, normalized)


                # Capture the exact raw_units regardless of case (we want to store this in the metadata table as the original units)
                match = re.search(re.escape(raw_units), new, flags=re.IGNORECASE)
                if match:
                    units_raw_original = match.group(0) #group(0) returns teh the full matched substring

            # Remove units from variable name
            variable = new
            if raw_units:
                variable = re.sub(re.escape(raw_units), "", variable, flags=re.IGNORECASE) # Find all instances of the exact raw_units in variable (case insensitive)

            # Remove any left over bracketed content or just the empty brackets themselves
            variable = re.sub(r"\[[^\]]*\]|\([^\)]*\)", "", variable)
            variable = variable.strip().rstrip(",")

            # Clean variable name
            variable_clean = clean_variable_name(variable)

            # Ambiguous unit suffixes - check if the last token matches an ambiguous unit e.g., _g, 
            if not no_units_in_header and cleaned_units is None:
                tokens = variable_clean.split("_")
                last = tokens[-1]
                if last in AMBIGUOUS_UNITS:
                    cleaned_units = last
                    variable_clean = "_".join(tokens[:-1])


            # -----------------------------
            # FINAL HEADER ASSEMBLY
            # -----------------------------
            # HEre we are putting the units in square bracktes as it is more machine compatible
            if preserve_units and cleaned_units:
                header = f"{variable_clean} [{cleaned_units}]"
            else:
                header = variable_clean

            # Naming style
            if naming_style == "camelCase":
                parts = variable_clean.split("_")
                header = parts[0] + "".join(p.capitalize() for p in parts[1:])
                if preserve_units and cleaned_units:
                    header = f"{header} [{cleaned_units}]"

            elif naming_style == "Title Case":
                header = " ".join(p.capitalize() for p in variable_clean.split("_"))
                if preserve_units and cleaned_units:
                    header = f"{header} [{cleaned_units}]"


            # Fallback for empty header
            if header == "":
                header = "unnamed_column"

            cleaned.append(header)

            metadata[raw] = {
                "variable": variable_clean,
                "units_raw": units_raw_original,
                "units_clean": cleaned_units,
                "cleaned_header": header,
            }

        except Exception:
            # If anything fails, preserve original header
            cleaned.append(raw)
            metadata[raw] = {
                "variable": raw,
                "units_raw": None,
                "units_clean": None,
                "cleaned_header": raw,
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
    metadata_df = (
        pd.DataFrame(metadata)
        .transpose()
        .reset_index()
        .rename(columns={"index": "original_header"})
    )

    # -----------------------------------------------------
    # 5. RETURN
    # -----------------------------------------------------
    cleaned_df = df.copy()
    cleaned_df.columns = final

    return cleaned_df, metadata_df
