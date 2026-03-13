import re
import unicodedata
import pandas as pd


def clean_headers(
    df: pd.DataFrame,
    *,
    naming_style="snake_case",
    preserve_units=True,
    no_units_in_header=False
):

    """
    Clean and standardize messy scientific column headers while extracting metadata.

    This task normalizes header text, detects units, removes bracketed content,
    resolves ambiguous unit suffixes, enforces naming conventions, and ensures
    uniqueness. It also produces a metadata table describing how each header
    was interpreted and transformed.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset whose column headers will be cleaned.

    naming_style : {"snake_case", "camelCase", "Title Case"}, optional
        Naming convention to apply to cleaned headers.

    preserve_units : bool, optional
        If True, detected units are appended to the cleaned variable name.

    extract_additional : bool, optional
        Reserved for future use. Included for API stability.

    no_units_in_header : bool, optional
        If True, unit detection is skipped entirely.

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A copy of the input DataFrame with cleaned and standardized column names.

    summary : dict
        {
            "changed": {old_name: new_name},
            "unchanged": [list of unchanged headers],
            "warnings": [list of soft validation messages],
            "header_metadata": {original_header: metadata_dict}
        }

    summary_df : pandas.DataFrame
        A table describing variable names, detected units, and final headers.

    Notes
    -----
    - Hard validation errors (e.g., invalid naming_style) raise exceptions.
    - Soft validation issues (e.g., empty headers, failed parsing) appear in
      summary["warnings"] but do not stop execution.
    """


    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors (A, B, C…)
    # -----------------------------------------------------
    # A. df must be a DataFrame
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    # B. naming_style must be valid
    if naming_style not in {"snake_case", "camelCase", "Title Case"}:
        raise ValueError(
            "naming_style must be one of: 'snake_case', 'camelCase', 'Title Case'."
        )

    # -----------------------------------------------------
    # 2. VALIDATION - Soft Checks (A, B, C…)
    # -----------------------------------------------------
    warnings = []  # user‑friendly issues that do not stop execution

    # (No soft checks needed before processing - all soft issues occur per‑column)

    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------
    UNIT_MAP = {
        # -----------------------------
        # CTD dataset units
        # -----------------------------
        "deg c": "degc",                 # Temperature, Potential Temperature
        "degc": "degc",                  # Temperature, Potential Temperature
        "psu": "psu",                    # Practical Salinity
        "db": "db",                      # Pressure (strain gauge)
        "ms/cm": "ms_cm",                # Conductivity
        "kg/m^3": "kg_m_3",              # Density, Sigma-theta Density
        "10^-8 m^3/kg": "1e-8_m3_kg",    # Specific Volume Anomaly
        "ml/l": "ml_l",                  # Dissolved Oxygen (ml/l)
        "umol/kg": "umol_kg",            # Dissolved Oxygen (umol/kg)
        "% saturation": "percent_sat",   # Oxygen Saturation
        "%sat": "percent_sat",           # Oxygen Saturation
        "mg/m^3": "mg_m_3",              # CDOM Fluorescence, Chlorophyll Fluorescence
        "1/m": "1_m",                    # Beam Attenuation
        "umol photons/m^2/sec": "umol_photons_m2_s",  # PAR / Irradiance
        "%": "percent",                  # Beam Transmission, Oxygen Saturation

        # -----------------------------
        # CEOS common water chemistry
        # -----------------------------
        "mg/l": "mg_l",                  # nutrients, ions, TSS
        "ug/l": "ug_l",                  # chlorophyll, trace metals
        "umol/l": "umol_l",              # nutrients (NO3, PO4, SiO2)
        "um": "um",                      # nutrients (NO3, PO4, SiO2)
        "mg/m2": "mg_m2",                # sedimentation, benthic flux, chlorophyll-a
        
        

        # -----------------------------
        # Atmospheric / meteorological
        # -----------------------------
        "m/s": "m_s",                    # wind speed
        "km/h": "km_h",                  # wind speed (alternate)
        "kpa": "kpa",                    # air pressure
        "hpa": "hpa",                    # atmospheric pressure
        "w/m^2": "w_m2",                 # radiation
        "mm": "mm",                      # precipitation
        "%rh": "percent_rh",             # relative humidity
        "ppm": "ppm",                    # CO2, CH4

        # -----------------------------
        # Hydrology / cryosphere
        # -----------------------------
        "cm": "cm",                      # snow depth, ice thickness
        "ppt": "ppt",                    # legacy salinity
        "mwe": "mwe",                    # water equivalent

        # -----------------------------
        # Optics
        # -----------------------------
        "m^-1": "m_neg1",                # attenuation coefficients
        "sr^-1": "sr_neg1",              # radiance
        "nm": "nm",                      # wavelengths

        # -----------------------------
        # Biology
        # -----------------------------
        "cells/ml": "cells_ml",          # phytoplankton
        "mg c/m^3": "mg_c_m3",           # biomass
        "#/l": "count_l",                # zooplankton counts
    }


    AMBIGUOUS_UNITS = {
        "m",   # meter (Depth, Height)
        "g",   # gram (Weight_g)
        "s",   # seconds (Time_s)
        "%",   # percent (Saturation, Transmission)
        "h",   # hours (Time_h)
        "l",   # liter (Volume_l)
    }


    def detect_units(text):
        lower = text.lower()
        bracket_match = re.findall(r"\[(.*?)\]|\((.*?)\)", text)
        if bracket_match:
            content = next(filter(None, bracket_match[0]))
            return content.strip()
        for raw_unit in UNIT_MAP:
            if raw_unit in lower:
                return raw_unit
        return None

    def clean_variable_name(name):
        name = name.lower()
        name = re.sub(r"[^a-z0-9]+", "_", name)
        name = re.sub(r"_+", "_", name).strip("_")
        return name

    original = list(df.columns)
    cleaned = []
    metadata = {}

    for raw in original:

        # Handle empty or invalid headers
        if not isinstance(raw, str) or raw.strip() == "":
            fallback = "unnamed_column"
            cleaned.append(fallback)
            metadata[raw] = {
                "variable": fallback,
                "units_raw": None,
                "units_clean": None,
                "cleaned_header": fallback,
            }
            warnings.append(
                f"Column '{raw}' was empty or invalid and replaced with '{fallback}'."
            )
            continue

        try:
            new = unicodedata.normalize("NFKD", raw)
            new = new.encode("ascii", "ignore").decode("ascii")

            # Detect units
            raw_units = None if no_units_in_header else detect_units(new)
            cleaned_units = None
            units_raw_original = None

            if raw_units:
                cleaned_units = UNIT_MAP.get(raw_units.lower(), raw_units.lower())
                match = re.search(re.escape(raw_units), new, flags=re.IGNORECASE)
                if match:
                    units_raw_original = match.group(0)

            variable = new
            if raw_units:
                variable = re.sub(re.escape(raw_units), "", variable, flags=re.IGNORECASE)

            variable = re.sub(r"\[[^\]]*\]|\([^\)]*\)", "", variable)
            variable = variable.strip().rstrip(",")

            variable_clean = clean_variable_name(variable)

            # Detect if cleaned variable already ends with a known cleaned unit (multi-token aware)
            if cleaned_units is None:
                tokens = variable_clean.split("_")
                # Try suffixes of length 1, 2, 3, ... up to full length
                for i in range(1, len(tokens) + 1):
                    suffix = "_".join(tokens[-i:])
                    if suffix in UNIT_MAP.values():
                        cleaned_units = suffix
                        variable_clean = "_".join(tokens[:-i])
                        break



            # Ambiguous units
            if cleaned_units is None:
                tokens = variable_clean.split("_")
                last = tokens[-1]
                if last in AMBIGUOUS_UNITS:
                    cleaned_units = last
                    variable_clean = "_".join(tokens[:-1])

            # Build final header
            header = variable_clean
            if preserve_units and cleaned_units:
                header = f"{header}_{cleaned_units}"

            if naming_style == "camelCase":
                parts = header.split("_")
                header = parts[0] + "".join(p.capitalize() for p in parts[1:])
            elif naming_style == "Title Case":
                header = " ".join(p.capitalize() for p in header.split("_"))

            if header == "":
                header = "unnamed_column"
                warnings.append(
                    f"Header '{raw}' cleaned to an empty name and replaced with 'unnamed_column'."
                )

            cleaned.append(header)

            metadata[raw] = {
                "variable": variable_clean,
                "units_raw": units_raw_original,
                "units_clean": cleaned_units,
                "cleaned_header": header,
            }

        except Exception as e:
            cleaned.append(raw)
            metadata[raw] = {
                "variable": raw,
                "units_raw": None,
                "units_clean": None,
                "cleaned_header": raw,
            }
            warnings.append(f"Failed to clean header '{raw}': {str(e)}")

    # Ensure uniqueness
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
    # 4. SUMMARY
    # -----------------------------------------------------
    changed = {}
    unchanged = []

    for old, new in zip(original, final):
        if old != new:
            changed[old] = new
        else:
            unchanged.append(old)

    summary = {
        "changed": changed,
        "unchanged": unchanged,
        "warnings": warnings,
        "header_metadata": metadata,
    }

    # -----------------------------------------------------
    # 5. SUMMARY DATAFRAME
    # -----------------------------------------------------
    summary_df = pd.DataFrame(metadata).transpose().reset_index().rename(
        columns={"index": "original_header"}
    )

    # -----------------------------------------------------
    # 6. RETURN
    # -----------------------------------------------------
    cleaned_df = df.copy()
    cleaned_df.columns = final

    return cleaned_df, summary, summary_df
