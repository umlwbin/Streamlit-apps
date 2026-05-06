import re
import pandas as pd
from datetime import datetime


# ---------------------------------------------------------
# STRING CLEANING
# ---------------------------------------------------------
def clean_string(value):
    """Normalize whitespace and safely handle non-strings."""
    if isinstance(value, str):
        return value.replace("\n", " ").replace("\r", " ").strip()
    return value


def clean_dict_values(d):
    """Apply clean_string to all values in a dict."""
    return {k: clean_string(v) for k, v in d.items()}


# ---------------------------------------------------------
# COLUMN FINDING (robust, partial, case-insensitive)
# ---------------------------------------------------------
def find_column(normalized_cols, search_term):
    """
    Find the first column whose name contains search_term (case-insensitive).
    Ignores trailing spaces and asterisks.
    """
    search_norm = search_term.strip().lower().replace("*", "")
    for col in normalized_cols:
        col_norm = col.strip().lower().replace("*", "")
        if search_norm in col_norm:
            return col
    return None


def safe_get(row, search_term, default=""):
    """
    Find the correct column containign the label, eg, "Datset name" and gets the value. It does this robustly by using:
    - partial match
    - case-insensitive
    - ignores asterisks and trailing spaces
    - returns default if missing or NaN
    """
    # Normalize all column names
    normalized_cols = [c for c in row.index]

    # Find matching column
    col = find_column(normalized_cols, search_term)
    if not col:
        return default

    try:
        val = row[col]
        if pd.isna(val):
            return default
        return clean_string(val)
    except Exception:
        return default


# ---------------------------------------------------------
# LONG-TEXT BLOCK PARSING
# ---------------------------------------------------------
def extract_metadata_blocks(text, anchor):
    """
    Split a long metadata cell into separate blocks.

    A "block" is one complete entry (e.g., for one creator, one contributor,
    one related resource). Each block starts when the anchor appears
    as a FIELD LABEL on its own, not inside another label.

    Example:
        Anchor = "Name:"
        Valid block start: "Name: John Doe"
        NOT a block start: "Type of Name: Personal"

    This function:
    - cleans weird Excel whitespace
    - finds all real block starts
    - slices the text from one block start to the next
    """

    # If the cell is empty or not text, return nothing
    if not isinstance(text, str):
        return []

    # Excel sometimes inserts hidden characters; remove them
    cleaned = (
        text.replace("\r", "")     # carriage returns
            .replace("\xa0", " ")  # non-breaking spaces
    )

    # ---------------------------------------------------------
    # Identify REAL block starts
    #
    # A field label always appears:
    #   - at the start of the text
    #   - OR after a comma+space
    #   - OR after a newline 0 not likely, but im keeping it in just in case
    # ---------------------------------------------------------
    pattern = rf"(?:(?<=^)|(?<=,\s)|(?<=\n)){re.escape(anchor)}"

    matches = list(re.finditer(pattern, cleaned))

    blocks = []

    # ---------------------------------------------------------
    # Slice the text from one block start to the next
    # ---------------------------------------------------------
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(cleaned)
        block = cleaned[start:end].strip()
        blocks.append(block)

    return blocks




def extract_metadata_value(text, start_marker, end_marker=None):
    """
    Extract substring between markers, tolerant to punctuation, spacing, and newline differences.
    Returns a cleaned string or "" if markers not found.
    """

    if not isinstance(text, str):
        return ""

    try:
        # Normalize whitespace and punctuation weirdness
        cleaned = (
            text.replace("\r", "")
                .replace("\xa0", " ")
                .replace("：", ":")  # Unicode colon --> normal colon
        )

        # -----------------------------
        # 1. Locate start marker
        # -----------------------------
        start_idx = cleaned.find(start_marker)
        if start_idx == -1:
            return ""

        start_idx += len(start_marker)

        # -----------------------------
        # 2. If no end marker --> return rest
        # -----------------------------
        if not end_marker:
            return clean_string(cleaned[start_idx:])

        # -----------------------------
        # 3. Try multiple end‑marker variants
        # -----------------------------
        candidates = [
            end_marker,                         # exact
            "\n" + end_marker,                  # newline before
            end_marker.replace(" ", ""),        # no spaces
            end_marker.replace(":", ""),        # missing colon
            end_marker.rstrip(),                # trailing spaces removed
            end_marker + " ",                   # extra space
            end_marker + "\n",                  # newline after
            "," + end_marker.lstrip(", "),      # missing comma
        ]

        end_idx = -1
        for candidate in candidates:
            pos = cleaned.find(candidate, start_idx)
            if pos != -1:
                end_idx = pos
                break

        # -----------------------------
        # 4. If still not found ---> return rest of block
        # -----------------------------
        if end_idx == -1:
            return clean_string(cleaned[start_idx:])

        # -----------------------------
        # 5. Extract + clean
        # -----------------------------
        return clean_string(cleaned[start_idx:end_idx])

    except Exception:
        return ""





# ---------------------------------------------------------
# DATE NORMALIZATION
# ---------------------------------------------------------
def normalize_date(date_str):
    """
    Convert various date formats into ISO 'YYYY-MM-DD'.Returns empty string if parsing fails.
    """
    if not isinstance(date_str, str):
        return ""

    try:
        dt = datetime.strptime(date_str.strip(), "%b %d, %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        try:
            dt = pd.to_datetime(date_str)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return ""


# ---------------------------------------------------------
# SLUGIFY
# ---------------------------------------------------------
def slugify(text):
    """
    Convert a string into a CKAN-safe slug:lowercase, underscores, alphanumeric only.
    """
    if not isinstance(text, str):
        return ""
    text = text.strip().lower().replace(" ", "_")
    return "".join(c for c in text if c.isalnum() or c in ["_", "-"])


# ---------------------------------------------------------
# NORMALIZE SPATIAL REGIONS TO MATCH CKAN FIELDS
# ---------------------------------------------------------
def normalize_spatial_region(value):
    """
    Normalize spatial region names into CKAN-safe slugs.
    - lowercase
    - trim whitespace
    - replace spaces with dashes
    - safe for None / NaN / non-strings
    """
    if not isinstance(value, str):
        return ""
    cleaned = value.strip().lower()
    cleaned = re.sub(r"\s+", "-", cleaned)  # collapse multiple spaces
    return cleaned

