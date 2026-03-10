import re
import unicodedata
import pandas as pd

def clean_headers(
    df,
    naming_style="snake_case",
    preserve_units=True,
    extract_additional=True,
    no_units_in_header=False
):
    """
    Clean and standardize messy scientific column headers while extracting metadata.

    This simplified version uses:
        • A UNIT_MAP for known units (can extend this anytime)
        • Bracket-first unit detection (e.g., [mg L^-1])
        • Mapping-based detection for inline units (e.g., Temp_mg L^-1)
        • A post-check for ambiguous units like _m, _g, _s
    """

    # ---------------------------------------------------------
    # 1. Known units (safe, unambiguous)
    # ---------------------------------------------------------
    UNIT_MAP = {
        "deg c": "degc",
        "degc": "degc",
        "psu": "psu",
        "db": "db",
        "ntu": "ntu",
        "rfu": "rfu",
        "rfub": "rfub",
        "%sat": "percent_sat",
        "% saturation": "percent_sat",
        "umol/kg": "umol_kg",
        "mg/m^3": "mg_m_3",
        "ml/l": "ml_l",
        "us cm^-1": "us_cm_neg1",
        "mg l^-1": "mg_l_neg1",
        "ue m^-2 s^-1": "ue_m_neg2_s_neg1",
        "m s^-1": "m_s_neg1",
        "umol photons/m^2/sec": "umol_photons_m_neg2_sec_neg1",
    }

    # ---------------------------------------------------------
    # 2. Ambiguous units (only detected if isolated at end)
    # ---------------------------------------------------------
    AMBIGUOUS_UNITS = {"m", "g", "s", "%", "h", "l"}

    # ---------------------------------------------------------
    # 3. Helper: detect units using brackets or UNIT_MAP
    # ---------------------------------------------------------
    def detect_units(text):
        lower = text.lower()

        # Step 1: Bracket units always win
        bracket_match = re.findall(r"\[(.*?)\]|\((.*?)\)", text)
        if bracket_match:
            content = next(filter(None, bracket_match[0]))
            return content.strip()

        # Step 2: Check UNIT_MAP keys
        for raw_unit in UNIT_MAP:
            if raw_unit in lower:
                return raw_unit

        return None

    # ---------------------------------------------------------
    # 4. Helper: clean variable names
    # ---------------------------------------------------------
    def clean_variable_name(name):
        name = name.lower()
        name = re.sub(r"[^a-z0-9]+", "_", name)
        name = re.sub(r"_+", "_", name).strip("_")
        return name

    # ---------------------------------------------------------
    # 5. Prepare output structures
    # ---------------------------------------------------------
    original = list(df.columns)
    cleaned = []
    metadata = {}

    summary = {
        "task_name": "clean_headers",
        "changed": {},
        "unchanged": [],
        "errors": []
    }

    # ---------------------------------------------------------
    # 6. Process each column header
    # ---------------------------------------------------------
    for raw in original:

        if not isinstance(raw, str) or raw.strip() == "":
            fallback = "unnamed_column"
            cleaned.append(fallback)
            metadata[raw] = {
                "variable": fallback,
                "units": None,
                "cleaned_header": fallback
            }
            summary["errors"].append(
                f"Column with empty or invalid name was replaced with '{fallback}'."
            )
            continue

        try:
            # Normalize text
            new = unicodedata.normalize("NFKD", raw)
            new = new.encode("ascii", "ignore").decode("ascii")

            # -------------------------------------------------
            # Step A: Detect units (brackets or UNIT_MAP)
            # -------------------------------------------------
            raw_units = None if no_units_in_header else detect_units(new)

            cleaned_units = None
            units_raw_original = None

            if raw_units:
                # Cleaned unit from UNIT_MAP
                cleaned_units = UNIT_MAP.get(raw_units.lower(), raw_units.lower())

                # Capture the exact original substring from the header
                match = re.search(re.escape(raw_units), new, flags=re.IGNORECASE)
                if match:
                    units_raw_original = match.group(0)


            # -------------------------------------------------
            # NEW: Remove the raw unit substring from the variable text
            # -------------------------------------------------
            if raw_units:
                # Remove the exact raw unit substring (case-insensitive)
                pattern = re.escape(raw_units)
                variable = re.sub(pattern, "", new, flags=re.IGNORECASE)
            else:
                variable = new

            # IMPORTANT: remove bracket content AFTER removing units
            variable = re.sub(r"\[[^\]]*\]|\([^\)]*\)", "", variable)
            variable = variable.strip().rstrip(",")

            variable_clean = clean_variable_name(variable)

            # -------------------------------------------------
            # Step C: Post-check ambiguous units
            # -------------------------------------------------
            if cleaned_units is None:
                tokens = variable_clean.split("_")
                last = tokens[-1]

                if last in AMBIGUOUS_UNITS:
                    cleaned_units = last
                    variable_clean = "_".join(tokens[:-1])

            # -------------------------------------------------
            # Step D: Build final header (AFTER units finalized)
            # -------------------------------------------------
            header = variable_clean
            if preserve_units and cleaned_units:
                header = f"{header}_{cleaned_units}"

            # Naming style
            if naming_style == "camelCase":
                parts = header.split("_")
                header = parts[0] + "".join(p.capitalize() for p in parts[1:])
            elif naming_style == "Title Case":
                header = " ".join(p.capitalize() for p in header.split("_"))

            if header == "":
                header = "unnamed_column"
                summary["errors"].append(
                    f"Header '{raw}' cleaned to an empty name and was replaced with 'unnamed_column'."
                )

            # -------------------------------------------------
            # Step E: Save results
            # -------------------------------------------------
            cleaned.append(header)
            metadata[raw] = {
                "variable": variable_clean,
                "units_raw": units_raw_original,
                "units_clean": cleaned_units,
                "cleaned_header": header
            }


        except Exception as e:
            fallback = raw
            cleaned.append(fallback)
            metadata[raw] = {
                "variable": fallback,
                "units": None,
                "cleaned_header": fallback
            }
            summary["errors"].append(
                f"Failed to clean header '{raw}': {str(e)}"
            )
            continue


    # ---------------------------------------------------------
    # 7. Ensure uniqueness
    # ---------------------------------------------------------
    final = []
    seen = {}
    for name in cleaned:
        if name not in seen:
            seen[name] = 1
            final.append(name)
        else:
            seen[name] += 1
            final.append(f"{name}_{seen[name]}")

    # ---------------------------------------------------------
    # 8. Build summary
    # ---------------------------------------------------------
    for old, new in zip(original, final):
        if old != new:
            summary["changed"][old] = new
        else:
            summary["unchanged"].append(old)

    summary["header_metadata"] = metadata

    cleaned_df = df.copy()
    cleaned_df.columns = final

    return cleaned_df, summary
