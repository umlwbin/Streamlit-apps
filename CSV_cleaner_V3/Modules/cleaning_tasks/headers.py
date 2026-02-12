"""
Clean and standardize messy scientific column headers, while also extracting
useful metadata such as units, sensor models, calibration scales, media types,
and processing notes.

This function supports two modes:

1. **Normal mode (default)**  
   Units are expected to appear inside brackets (e.g., "[ml/l]") and are
   preserved or removed depending on user settings.

2. **No-units mode**  
   Use when the dataset does *not* include units in the header. Bracket content
   is treated as part of the variable name, and units are never included in the
   cleaned header.

---------------------------------------------------------------------------
What the function does
---------------------------------------------------------------------------

1. **Normalize text**
   - Converts accented or special characters to plain ASCII
   - Lowercases everything for consistent parsing

2. **Extract scientific metadata**
   - Units inside brackets (e.g., "[ml/l]", "(deg C)")
   - Sensor model names (e.g., "SBE 43", "WET Labs C-Star")
   - Calibration scales (e.g., "ITS-90")
   - Media types (e.g., "salt water")
   - Processing notes after commas (e.g., "WS = 2")

3. **Clean the variable name**
   - Removes sensor names, scales, media, and notes
   - Removes bracket blocks
   - Removes stray punctuation and separators
   - Leaves only the core scientific variable name

4. **Build the cleaned header**
   - Optionally includes units (normal mode only)
   - Replaces symbols (e.g., "%" → "percent", "/" → "_per_")
   - Replaces non-alphanumeric characters with underscores
   - Collapses repeated underscores
   - Applies naming style:
        • "snake_case"   → water_temperature_c  
        • "camelCase"    → waterTemperatureC  
        • "Title Case"   → Water Temperature C  

5. **Ensure uniqueness**
   - Appends suffixes (_2, _3, …) when duplicate names occur

---------------------------------------------------------------------------
Parameters
---------------------------------------------------------------------------

df : pandas.DataFrame  
    The DataFrame whose column names should be cleaned.

naming_style : {"snake_case", "camelCase", "Title Case"}, optional  
    Naming convention for the cleaned column names.  
    Default is "snake_case".

preserve_units : bool, optional  
    If True (default), units are included in the cleaned header.  
    Ignored when `no_units_in_header=True`.

extract_additional : bool, optional  
    If True (default), extract sensor models, calibration scales, media types,
    and processing notes into metadata.

no_units_in_header : bool, optional  
    If True, assume the dataset does *not* include units in the header.  
    - Units are never included in the cleaned header  
    - Bracket content is treated as part of the variable name  
    - Unit detection is disabled  
    Default is False.

---------------------------------------------------------------------------
Returns
---------------------------------------------------------------------------

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
                    "additional_notes": ...,
                    "cleaned_header": ...
                },
                ...
            }
        }

---------------------------------------------------------------------------
Basic Example (normal mode)
---------------------------------------------------------------------------

>>> import pandas as pd
>>> df = pd.DataFrame(columns=[
...     "Oxygen, SBE 43 [ml/l], WS = 2",
...     "Potential Temperature [ITS-90, deg C]",
...     "Sample ID"
... ])

>>> cleaned_df, summary = clean_headers(df)

---------------------------------------------------------------------------
Example (no-units mode)
---------------------------------------------------------------------------

>>> cleaned_df, summary = clean_headers(
...     df,
...     naming_style="camelCase",
...     preserve_units=False,
...     extract_additional=True,
...     no_units_in_header=True
... )
"""


import re
import unicodedata
import pandas as pd

# -----------------------------------------
# Controlled vocabularies
# -----------------------------------------

KNOWN_UNITS = {
    "utc", "degrees north", "degrees east", "m", "db", "ms/cm", "psu",
    "deg c", "kg/m^3", "10^-8 m^3/kg", "ml/l", "umol/kg", "% saturation",
    "mg/m^3", "umol photons/m^2/sec", "%", "1/m"
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


    original = list(df.columns)
    cleaned = []
    summary = {"changed": {}, "unchanged": []}
    metadata = {}

    bracket_pattern = r"\[[^\]]*\]|\([^\)]*\)"
    processing_pattern = r",\s*(.*)$"

    for col in original:
        raw = col
        meta = {"variable": None, "units": None, "additional_notes": None}
        notes = []

        # -----------------------------------------
        # STEP 1 — Normalize text
        # -----------------------------------------
        new = unicodedata.normalize("NFKD", raw)
        new = new.encode("ascii", "ignore").decode("ascii")

        # -----------------------------------------
        # STEP 2 — Extract bracket blocks
        # -----------------------------------------
        bracket_blocks = re.findall(bracket_pattern, new)

        # -----------------------------------------
        # IF no units in header
        # -----------------------------------------
        if no_units_in_header:
            # Remove brackets but keep content
            new_no_brackets = re.sub(bracket_pattern, "", new)

            # Extract bracket content as potential metadata
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
                    # KNOWN_UNITS ignored because user said "no units in header"

            # Now treat entire header (minus brackets) as variable name
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

            if naming_style == "camelCase":
                parts = header.split("_")
                header = parts[0] + "".join(p.capitalize() for p in parts[1:])
            elif naming_style == "Title Case":
                header = " ".join(p.capitalize() for p in header.split("_"))

            cleaned.append(header)
            meta["cleaned_header"] = header
            metadata[raw] = meta
            continue

        # -----------------------------------------
        # NORMAL MODE: units expected in header
        # -----------------------------------------

        # STEP 3 — Parse bracket metadata
        for block in bracket_blocks:
            content = block.strip("[]()")
            parts = [p.strip().lower() for p in content.split(",")]

            for p in parts:
                if p in KNOWN_UNITS:
                    meta["units"] = p
                elif p in KNOWN_SENSORS:
                    notes.append(KNOWN_SENSORS[p])
                elif p in KNOWN_SCALES:
                    notes.append(KNOWN_SCALES[p])
                elif p in KNOWN_MEDIA:
                    notes.append(KNOWN_MEDIA[p])
                else:
                    # Unknown token: treat as unit if none assigned yet
                    if meta["units"] is None:
                        meta["units"] = p
                    else:
                        notes.append(p)

        # Remove bracket blocks
        new = re.sub(bracket_pattern, "", new)

        # STEP 4 — Extract processing notes after comma
        m = re.search(processing_pattern, new)
        if m:
            if extract_additional:
                notes.append(m.group(1).strip())
            new = new[:m.start()]

        # STEP 5 — Extract variable name
        variable = new.strip().rstrip(",")
        variable = re.sub(r"^[^A-Za-z0-9]+", "", variable)

        # STEP 6 — Detect metadata inside variable text
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

        variable = variable.strip(" ,_-")
        meta["variable"] = variable

        # STEP 7 — Build cleaned header
        header = variable
        if preserve_units and meta["units"]:
            header = f"{header} ({meta['units']})"

        header = header.lower()
        header = header.replace("%", "percent")
        header = header.replace("/", "_per_")
        header = re.sub(r"[()]", "_", header)
        header = re.sub(r"[^a-z0-9]+", "_", header)
        header = re.sub(r"_+", "_", header).strip("_")

        if naming_style == "camelCase":
            parts = header.split("_")
            header = parts[0] + "".join(p.capitalize() for p in parts[1:])
        elif naming_style == "Title Case":
            header = " ".join(p.capitalize() for p in header.split("_"))

        cleaned.append(header)
        meta["cleaned_header"] = header

        if extract_additional and notes:
            meta["additional_notes"] = ", ".join(notes)

        metadata[raw] = meta

    # -----------------------------------------
    # STEP 8 — Ensure uniqueness
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
    # STEP 9 — Build summary
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
