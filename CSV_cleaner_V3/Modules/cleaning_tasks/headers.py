"""
    Clean and standardize messy scientific column headers, while also extracting
    useful metadata such as units, media, sensor models, calibration scales, and
    processing notes. For example:

        "Oxygen, SBE 43 [ml/l], WS = 2"
        "Potential Temperature [ITS-90, deg C]"
        "Beam Transmission, WET Labs C-Star [%]"

    The function separates this information into structured metadata and
    produces clean, machine‑friendly column names.

    --------------------------------------------------------------------------
    What the function does
    --------------------------------------------------------------------------
    1. Normalizes text:
        - Converts accented or special characters to plain ASCII
        - Lowercases everything for consistency

    2. Extracts scientific metadata:
        - Units inside parentheses or square brackets (e.g., "[ml/l]")
        - Sensor model names (e.g., "SBE 43", "WET Labs C-Star")
        - Calibration scales (e.g., "ITS-90")
        - Processing notes after the units (e.g., "WS = 2")

    3. Cleans the variable name:
        - Removes sensor names, calibration scales, and notes
        - Keeps only the core variable name (e.g., "Oxygen")

    4. Builds a clean column name:
        - Optionally keeps units (e.g., "oxygen_ml_l")
        - Replaces symbols like "%" and "/" with readable words
        - Replaces non‑alphanumeric characters with underscores
        - Collapses repeated underscores
        - Applies a naming style:
            • "snake_case"   → water_temperature_c
            • "camelCase"    → waterTemperatureC
            • "Title Case"   → Water Temperature C

    5. Ensures all final column names are unique.

    --------------------------------------------------------------------------
    Parameters
    --------------------------------------------------------------------------
    df : pandas.DataFrame
        The DataFrame whose column names you want to clean.

    naming_style : str, optional
        Naming convention for the cleaned column names.
        Options:
            - "snake_case"  (default)
            - "camelCase"
            - "Title Case"

    preserve_units : bool, optional
        If True (default), units are included in the cleaned column name.
        If False, units are removed entirely.

    extract_sensors : bool, optional
        If True (default), known sensor model names are detected and removed
        from the cleaned header, and stored in metadata.

    extract_scales : bool, optional
        If True (default), known calibration scales are detected and removed
        from the cleaned header, and stored in metadata.

    extract_processing_notes : bool, optional
        If True (default), text after the units (e.g., "WS = 2") is extracted
        and stored in metadata.

    --------------------------------------------------------------------------
    Returns
    --------------------------------------------------------------------------
    cleaned_df : pandas.DataFrame
        A copy of the original DataFrame with cleaned column names.

    summary : dict
        A dictionary describing:
            - which column names changed
            - which stayed the same
            - extracted metadata for each original header

        Structure:
            {
                "changed": {original_name: new_name, ...},
                "unchanged": [...],
                "header_metadata": {
                    original_name: {
                        "variable": ...,
                        "units": ...,
                        "sensor_model": ...,
                        "calibration_settings": ...,
                        "processing_notes": ...
                    },
                    ...
                }
            }

    --------------------------------------------------------------------------
    Basic Example (uses all default settings)
    --------------------------------------------------------------------------

    >>> import pandas as pd
    >>> df = pd.DataFrame(columns=[
    ...     "Oxygen, SBE 43 [ml/l], WS = 2",
    ...     "Potential Temperature [ITS-90, deg C]",
    ...     "Sample ID"
    ... ])

    >>> cleaned_df, summary = clean_headers(df)

    >>> cleaned_df.columns
    Index(['oxygen_ml_l', 'potential_temperature_deg_c', 'sample_id'], dtype='object')

    --------------------------------------------------------------------------
    Advanced Example (custom options)
    --------------------------------------------------------------------------

    >>> cleaned_df, summary = clean_headers(
    ...     df,
    ...     naming_style="camelCase",
    ...     preserve_units=False,
    ...     extract_sensors=False,
    ...     extract_scales=True,
    ...     extract_processing_notes=False,
    ...     extract_media=True
    ... )

    >>> cleaned_df.columns
    Index(['oxygen', 'potentialTemperature', 'sampleId'], dtype='object')

"""
import re
import unicodedata
import pandas as pd

# -----------------------------------------
# Controlled vocabularies
# These act like "lookup tables" that help us
# recognize known scientific terms inside headers.
# Please add to these tables as you notice new metadata in headers.
# -----------------------------------------

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
    "salt water": "salt water"
}


def clean_headers(
    df,
    naming_style="snake_case",
    preserve_units=True,
    extract_sensors=True,
    extract_scales=True,
    extract_processing_notes=True,
    extract_media=True,
):
    """
    Header cleaning function.
    (Docstring omitted here — you already have a great one.)
    """

    # Store original column names
    original = list(df.columns)

    # These lists will hold the cleaned names and summary info
    cleaned = []
    summary = {"changed": {}, "unchanged": []}
    metadata = {}

    # Regex patterns:
    # bracket_pattern → finds anything inside [...] or (...)
    # processing_pattern → finds text after a comma (processing notes)
    bracket_pattern = r"\[[^\]]*\]|\([^\)]*\)"
    processing_pattern = r",\s*(.*)$"

    # Process each column name one by one
    for col in original:
        raw = col  # keep the original name for reference

        # Each column gets a metadata dictionary
        meta = {
            "variable": None,
            "units": None,
            "media": None,
            "sensor_model": None,
            "calibration_settings": None,
            "processing_notes": None,
        }

        # -----------------------------------------
        # STEP 1 — Normalize text
        # -----------------------------------------
        # Many scientific files contain special characters (°, µ, ³, etc.)
        # This converts them into plain ASCII so our regexes work reliably.
        new = unicodedata.normalize("NFKD", raw)
        new = new.encode("ascii", "ignore").decode("ascii")

        # -----------------------------------------
        # STEP 2 — Extract ALL bracket blocks
        # -----------------------------------------
        # Example: "[salt water, m]" or "(deg C)"
        # We extract them first so we can safely remove them later.
        bracket_blocks = re.findall(bracket_pattern, new)

        # -----------------------------------------
        # STEP 3 — Parse metadata from bracket blocks
        # -----------------------------------------
        for block in bracket_blocks:
            # Remove the surrounding brackets
            content = block.strip("[]()")

            # Split by comma → ["salt water", "m"]
            parts = []
            for p in content.split(","):
                # Clean whitespace and lowercase for matching
                p = p.strip().lower()
                p = " ".join(p.split())  # collapse weird spacing
                parts.append(p)

            # Now classify each piece
            for p in parts:
                if extract_sensors and p in KNOWN_SENSORS:
                    meta["sensor_model"] = KNOWN_SENSORS[p]
                elif extract_scales and p in KNOWN_SCALES:
                    meta["calibration_settings"] = KNOWN_SCALES[p]
                elif extract_media and p in KNOWN_MEDIA:
                    meta["media"] = KNOWN_MEDIA[p]
                else:
                    # If it's not a known sensor/scale/media,
                    # we assume it's a unit (e.g., "m", "deg c")
                    if meta["units"] is None:
                        meta["units"] = p

        # -----------------------------------------
        # STEP 4 — Remove bracket blocks from the header
        # -----------------------------------------
        new = re.sub(bracket_pattern, "", new)

        # -----------------------------------------
        # STEP 5 — Extract processing notes
        # -----------------------------------------
        # Processing notes may appear after a comma:
        # "Depth [m], using lat = 64.4264"
        m = re.search(processing_pattern, new)
        if m:
            if extract_processing_notes:
                meta["processing_notes"] = m.group(1).strip()
            # Remove the notes from the header text
            new = new[:m.start()]

        # -----------------------------------------
        # STEP 6 — Extract the variable name
        # -----------------------------------------
        # After removing brackets + notes, the remaining text
        # should be the "core" variable name.
        variable = new.strip().rstrip(",")

        # -----------------------------------------
        # STEP 7 — Detect sensors/scales inside the variable text
        # -----------------------------------------
        # Sometimes sensors appear *outside* brackets:
        # "Oxygen SBE 43"
        lower_var = variable.lower()

        for key, label in KNOWN_SENSORS.items():
            if extract_sensors and key in lower_var:
                meta["sensor_model"] = label
                variable = re.sub(key, "", lower_var).strip(" ,")
                lower_var = variable

        for key, label in KNOWN_SCALES.items():
            if extract_scales and key in lower_var:
                meta["calibration_settings"] = label
                variable = re.sub(key, "", lower_var).strip(" ,")
                lower_var = variable

        meta["variable"] = variable

        # -----------------------------------------
        # STEP 8 — Build the cleaned header name
        # -----------------------------------------
        header = variable

        # Optionally append units to the name
        if preserve_units and meta["units"]:
            header = f"{header} ({meta['units']})"

        # Lowercase everything for consistency
        header = header.lower()

        # Replace symbols with readable words
        header = header.replace("%", "percent")
        header = header.replace("/", "_per_")

        # Replace parentheses with underscores
        header = re.sub(r"[()]", "_", header)

        # Replace anything not a-z or 0-9 with underscores
        header = re.sub(r"[^a-z0-9]+", "_", header)

        # Collapse multiple underscores into one
        header = re.sub(r"_+", "_", header).strip("_")

        # Apply naming style
        if naming_style == "camelCase":
            parts = header.split("_")
            header = parts[0] + "".join(p.capitalize() for p in parts[1:])
        elif naming_style == "Title Case":
            header = " ".join(p.capitalize() for p in header.split("_"))

        cleaned.append(header)
        metadata[raw] = meta

    # -----------------------------------------
    # STEP 9 — Ensure uniqueness
    # -----------------------------------------
    # If two columns clean to the same name,
    # we append _2, _3, etc.
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
    # STEP 10 — Build summary
    # -----------------------------------------
    for old, new in zip(original, final):
        if old != new:
            summary["changed"][old] = new
        else:
            summary["unchanged"].append(old)

    summary["header_metadata"] = metadata

    # Return cleaned DataFrame + summary
    cleaned_df = df.copy()
    cleaned_df.columns = final

    return cleaned_df, summary
