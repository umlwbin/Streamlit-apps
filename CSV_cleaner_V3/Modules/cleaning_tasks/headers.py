import re
import unicodedata
import pandas as pd

# -----------------------------------------
# Controlled vocabularies
# -----------------------------------------

KNOWN_UNITS = {
    # Add as many as needed - all will be detected even without brackets
    "utc", "degrees north", "degrees east", "m", "db", "ms/cm", "psu",
    "deg c", "degc", "us cm^-1", "mg l^-1", "ntu", "rfu", "rfub",
    "ue m^-2 s^-1", "m s^-1", "kg/m^3", "10^-8 m^3/kg", "ml/l",
    "umol/kg", "% saturation", "%sat", "% sat", "mg/m^3",
    "umol photons/m^2/sec", "%", "1/m"
}

KNOWN_SENSORS = {
    "sbe 43": "SBE 43",
    "wet labs c-star": "WET Labs C-Star",
    "wet labs eco-afl/fl": "WET Labs ECO-AFL/FL",
    "wet labs cdom": "WET Labs CDOM",
    "biospherical/licor": "Biospherical/Licor",
    "strain gauge": "Strain Gauge"
}

KNOWN_SCALES = {
    "its-90": "ITS-90",
    "sigma-theta": "sigma-theta",
}

KNOWN_MEDIA = {
    "salt water": "salt water",
    "fresh water": "fresh water"
}


def clean_headers(
    df,
    naming_style="snake_case",
    preserve_units=True,
    extract_additional=True,
    no_units_in_header=False
):
    """
    Clean and standardize messy scientific column headers while extracting metadata.

    Improvements in this version:
        • Detect units even when not inside brackets (e.g., Temp_degC, Chl_NTU)
        • Detect multi-token units (e.g., "mg L^-1", "uS cm^-1")
        • Beginner-friendly comments
        • Safe fallbacks and error capturing
        • Empty-header detection
        • Duplicate-header resolution
    """

    original = list(df.columns)
    cleaned = []
    metadata = {}

    summary = {
        "task_name": "clean_headers",
        "changed": {},
        "unchanged": [],
        "errors": []
    }

    # Regex patterns
    bracket_pattern = r"\[[^\]]*\]|\([^\)]*\)"
    processing_pattern = r",\s*(.*)$"

    # -----------------------------------------
    # Helper: detect multi-token units inside raw text
    # -----------------------------------------
    def detect_units_in_text(text):
        """
        Detect units even when not in brackets, and return the exact substring
        as it appears in the original header.
        """
        lower_text = text.lower()

        for unit in KNOWN_UNITS:
            u = unit.lower()
            if u in lower_text:
                # Find the exact substring in the original text
                start = lower_text.index(u)
                end = start + len(u)
                return text[start:end]   # original formatting preserved

        return None


    # -----------------------------------------
    # Process each header safely
    # -----------------------------------------
    for raw in original:

        # Handle empty or invalid header names
        if not isinstance(raw, str) or raw.strip() == "":
            fallback = "unnamed_column"
            cleaned.append(fallback)
            metadata[raw] = {
                "variable": fallback,
                "units": None,
                "additional_notes": None,
                "cleaned_header": fallback
            }
            summary["errors"].append(
                f"Column with empty or invalid name was replaced with '{fallback}'."
            )
            continue

        try:
            # ---------------------------------------------------------
            # BEGIN NORMAL PROCESSING
            # ---------------------------------------------------------
            col = raw
            meta = {"variable": None, "units": None, "additional_notes": None}
            notes = []

            # STEP 1 - Normalize text (remove accents, enforce ASCII)
            new = unicodedata.normalize("NFKD", col)
            new = new.encode("ascii", "ignore").decode("ascii")

            # STEP 2 - Extract bracket blocks
            bracket_blocks = re.findall(bracket_pattern, new)

            # ---------------------------------------------------------
            # MODE: no units in header
            # ---------------------------------------------------------
            if no_units_in_header:

                # Remove brackets but keep content
                new_no_brackets = re.sub(bracket_pattern, "", new)

                # Extract metadata from bracket content
                for block in bracket_blocks:
                    content = block.strip("[]()")
                    parts = re.split(r"[ ,_\-]+", content.lower())

                    for p in parts:
                        if p in KNOWN_SENSORS:
                            notes.append(KNOWN_SENSORS[p])
                        elif p in KNOWN_SCALES:
                            notes.append(KNOWN_SCALES[p])
                        elif p in KNOWN_MEDIA:
                            notes.append(KNOWN_MEDIA[p])
                        # Units intentionally ignored in this mode

                # Treat entire header as variable name
                variable = new_no_brackets.strip().rstrip(",")

                # Extract metadata from variable text
                tokens = re.split(r"[ ,_\-]+", variable.lower())
                for t in tokens:
                    if t in KNOWN_SENSORS:
                        notes.append(KNOWN_SENSORS[t])
                        variable = re.sub(t, "", variable, flags=re.IGNORECASE)
                    elif t in KNOWN_SCALES:
                        notes.append(KNOWN_SCALES[t])
                        variable = re.sub(t, "", variable, flags=re.IGNORECASE)
                    elif t in KNOWN_MEDIA:
                        notes.append(KNOWN_MEDIA[t])
                        variable = re.sub(t, "", variable, flags=re.IGNORECASE)

                variable = variable.strip(" ,_-")
                meta["variable"] = variable
                meta["units"] = None
                if extract_additional and notes:
                    meta["additional_notes"] = ", ".join(notes)

                # Build cleaned header
                header = variable.lower()
                header = re.sub(r"[^a-z0-9]+", "_", header)
                header = re.sub(r"_+", "_", header).strip("_")

                # Naming style
                if naming_style == "camelCase":
                    parts = header.split("_")
                    header = parts[0] + "".join(p.capitalize() for p in parts[1:])
                elif naming_style == "Title Case":
                    header = " ".join(p.capitalize() for p in header.split("_"))

                # Detect empty header after cleaning
                if header == "":
                    header = "unnamed_column"
                    summary["errors"].append(
                        f"Header '{raw}' cleaned to an empty name and was replaced with 'unnamed_column'."
                    )

                cleaned.append(header)
                meta["cleaned_header"] = header
                metadata[raw] = meta
                continue

            # ---------------------------------------------------------
            # NORMAL MODE (units expected)
            # ---------------------------------------------------------

            # STEP 3 - Parse bracket metadata
            detected_units = []
            for block in bracket_blocks:
                content = block.strip("[]()")
                parts = [p.strip().lower() for p in content.split(",")]

                for p in parts:
                    if p in KNOWN_UNITS:
                        detected_units.append(p)
                    elif p in KNOWN_SENSORS:
                        notes.append(KNOWN_SENSORS[p])
                    elif p in KNOWN_SCALES:
                        notes.append(KNOWN_SCALES[p])
                    elif p in KNOWN_MEDIA:
                        notes.append(KNOWN_MEDIA[p])
                    else:
                        notes.append(p)

            # STEP 3b - Detect units outside brackets (multi-token or single-token)
            if not detected_units:
                unit_found = detect_units_in_text(new)
                if unit_found:
                    detected_units.append(unit_found)

            # Handle multiple units
            if len(detected_units) > 1:
                summary["errors"].append(
                    f"Multiple units detected in '{raw}'. Using '{detected_units[0]}'."
                )

            if detected_units:
                meta["units"] = detected_units[0]

            # Remove bracket blocks
            new = re.sub(bracket_pattern, "", new)

            # STEP 4 - Extract processing notes after comma
            m = re.search(processing_pattern, new)
            if m:
                if extract_additional:
                    notes.append(m.group(1).strip())
                new = new[:m.start()]

            # STEP 5 - Extract variable name
            variable = new.strip().rstrip(",")
            variable = re.sub(r"^[^A-Za-z0-9]+", "", variable)

            # STEP 6 - Detect metadata inside variable text
            tokens = re.split(r"[ ,_\-]+", variable.lower())
            for t in tokens:
                if t in KNOWN_SENSORS:
                    notes.append(KNOWN_SENSORS[t])
                    variable = re.sub(t, "", variable, flags=re.IGNORECASE)
                elif t in KNOWN_SCALES:
                    notes.append(KNOWN_SCALES[t])
                    variable = re.sub(t, "", variable, flags=re.IGNORECASE)
                elif t in KNOWN_MEDIA:
                    notes.append(KNOWN_MEDIA[t])
                    variable = re.sub(t, "", variable, flags=re.IGNORECASE)
                elif t in KNOWN_UNITS and meta["units"] is None:
                    meta["units"] = t
                    variable = re.sub(t, "", variable, flags=re.IGNORECASE)

            variable = variable.strip(" ,_-")
            meta["variable"] = variable

            # ---------------------------------------------------------
            # REMOVE DUPLICATED UNITS ()
            # ---------------------------------------------------------
            if meta["units"]:
                # Remove exact unit (original formatting)
                variable = re.sub(re.escape(meta["units"]), "", variable, flags=re.IGNORECASE)

                # Remove normalized unit (after lowercasing + symbol normalization)
                normalized_unit = (
                    meta["units"]
                    .lower()
                    .replace("%", "percent")
                    .replace("/", "_per_")
                    .replace(" ", "_")
                    .replace("-", "_")
                )
                variable = re.sub(normalized_unit, "", variable.lower(), flags=re.IGNORECASE)

                variable = variable.strip(" ,_-")

            # STEP 7 - Build cleaned header
            header = variable
            if preserve_units and meta["units"]:
                header = f"{header} ({meta['units']})"

            header = header.lower()
            header = header.replace("%", "percent")
            header = header.replace("/", "_per_")
            header = re.sub(r"[()]", "_", header)
            header = re.sub(r"[^a-z0-9]+", "_", header)
            header = re.sub(r"_+", "_", header).strip("_")

            # Naming style
            if naming_style == "camelCase":
                parts = header.split("_")
                header = parts[0] + "".join(p.capitalize() for p in parts[1:])
            elif naming_style == "Title Case":
                header = " ".join(p.capitalize() for p in header.split("_"))

            # Detect empty header after cleaning
            if header == "":
                header = "unnamed_column"
                summary["errors"].append(
                    f"Header '{raw}' cleaned to an empty name and was replaced with 'unnamed_column'."
                )

            cleaned.append(header)
            if extract_additional and notes:
                meta["additional_notes"] = ", ".join(notes)
            meta["cleaned_header"] = header
            metadata[raw] = meta

        except Exception as e:
            # ---------------------------------------------------------
            # SAFE FALLBACK
            # ---------------------------------------------------------
            fallback = raw if isinstance(raw, str) else "unnamed_column"
            cleaned.append(fallback)
            metadata[raw] = {
                "variable": fallback,
                "units": None,
                "additional_notes": None,
                "cleaned_header": fallback
            }
            summary["errors"].append(
                f"Failed to clean header '{raw}': {str(e)}"
            )
            continue

    # -----------------------------------------
    # STEP 8 - Ensure uniqueness
    # -----------------------------------------
    final = []
    seen = {}
    for name in cleaned:
        if name not in seen:
            seen[name] = 1
            final.append(name)
        else:
            seen[name] += 1
            final.append(f"{name}_{seen[name]}")

    # -----------------------------------------
    # STEP 9 - Build summary
    # -----------------------------------------
    for old, new in zip(original, final):
        if old != new:
            summary["changed"][old] = new
        else:
            summary["unchanged"].append(old)

    summary["header_metadata"] = metadata

    cleaned_df = df.copy()
    cleaned_df.columns = final

    return cleaned_df, summary
