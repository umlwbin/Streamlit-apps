import re
import unicodedata
import pandas as pd

def clean_headers(df, naming_style="snake_case", preserve_units=True):
    """
    Clean messy scientific column headers and convert them into consistent,
    safe, machine‑friendly names.

    This function:
        - normalizes unicode characters (e.g., ³ → 3, ° → deg)
        - optionally removes units in parentheses (e.g., "(mg/L)")
        - lowercases and standardizes text
        - replaces symbols like "%" and "/" with readable words
        - replaces non‑alphanumeric characters with underscores
        - collapses repeated underscores and trims edges
        - applies a naming style (snake_case, camelCase, or Title Case)
        - ensures all final column names are unique

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame whose column names you want to clean.

    naming_style : str, optional
        The style to apply to the cleaned column names.
        Options:
            - "snake_case"  (default)
            - "camelCase"
            - "Title Case"
        Example:
            "water temperature (°C)" → "water_temperature_c" (snake_case)
            → "waterTemperatureC" (camelCase)
            → "Water Temperature C" (Title Case)

    preserve_units : bool, optional
        If True (default), units inside parentheses are kept but cleaned.
        If False, anything inside parentheses is removed entirely.
        Example:
            "(mg/L)" → "mg_l"   (preserved)
            "(mg/L)" → ""       (stripped)

    Returns
    -------
    cleaned_df : pandas.DataFrame
        A copy of the original DataFrame with cleaned column names.

    summary : dict
        A dictionary describing what changed.
        Structure:
            {
                "changed": {original_name: new_name, ...},
                "unchanged": [names that stayed the same]
            }

    Examples
    --------
    >>> df.columns
    ['Water Temp (°C)', 'NO3-N (mg/L)', 'Sample ID']

    >>> cleaned_df, summary = clean_headers(df)

    >>> cleaned_df.columns
    ['water_temp_c', 'no3_n_mg_l', 'sample_id']
    """


    original = list(df.columns)
    cleaned = []
    summary = {"changed": {}, "unchanged": []}

    for col in original:
        new = col

        # Normalize unicode (e.g., ³ → 3, ° → deg)
        new = unicodedata.normalize("NFKD", new)
        new = new.encode("ascii", "ignore").decode("ascii") # removes anything that isn’t plain ASCII

        # Optionally strip units in parentheses
        if not preserve_units:
            new = re.sub(r"\([^)]*\)", "", new)

        # Lowercase for normalization
        new = new.lower()

        # Replace common scientific symbols
        replacements = {
            "%": "percent",
            "/": "_per_",
        }
        for old, rep in replacements.items():
            new = new.replace(old, rep)

        # Replace parentheses with underscores (if preserving units)
        new = re.sub(r"[()]", "_", new)

        # Replace any non-alphanumeric with underscore
        new = re.sub(r"[^a-z0-9]+", "_", new)

        # Collapse multiple underscores
        new = re.sub(r"_+", "_", new)

        # Remove leading/trailing underscores
        new = new.strip("_")

        # Apply naming style
        if naming_style == "camelCase":
            parts = new.split("_")
            new = parts[0] + "".join(p.capitalize() for p in parts[1:])
        elif naming_style == "Title Case":
            new = " ".join(p.capitalize() for p in new.split("_"))
        # snake_case is already handled

        cleaned.append(new)

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

    # Build summary
    for old, new in zip(original, final):
        if old != new:
            summary["changed"][old] = new
        else:
            summary["unchanged"].append(old)

    cleaned_df = df.copy()
    cleaned_df.columns = final

    return cleaned_df, summary