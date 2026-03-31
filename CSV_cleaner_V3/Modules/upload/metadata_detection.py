import re

def detect_metadata_rows(text, sep=","):
    """
    Detect whether metadata rows exist above the true header row.

    Uses a 3-rule heuristic:
        1. width threshold
        2. non-empty density
        3. header-like token score

    Returns
    -------
    has_metadata : bool
    header_index : int or None
    """

    raw_lines = text.splitlines()
    split_lines = [line.split(sep) for line in raw_lines]

    if not split_lines:
        return False, None

    row_widths = [len(r) for r in split_lines]
    max_width = max(row_widths)

    def nonempty_fraction(row):
        return sum(1 for c in row if c.strip() != "") / max_width

    def looks_like_header_cell(cell):
        cell = cell.strip()
        if cell == "":
            return False
        if re.match(r"^\d", cell):
            return False
        if re.match(r"^\d{4}-\d{2}-\d{2}", cell):
            return False
        if "SN" in cell.upper():
            return False
        return True

    def header_token_fraction(row):
        return sum(looks_like_header_cell(c) for c in row) / max_width

    HEADER_THRESHOLD = 0.9
    NONEMPTY_THRESHOLD = 0.6
    HEADER_TOKEN_THRESHOLD = 0.5

    header_index = None

    for i, row in enumerate(split_lines):
        width = len(row)

        if width < HEADER_THRESHOLD * max_width:
            continue
        if nonempty_fraction(row) < NONEMPTY_THRESHOLD:
            continue
        if header_token_fraction(row) < HEADER_TOKEN_THRESHOLD:
            continue

        header_index = i
        break

    has_metadata = header_index not in (0, None)
    return has_metadata, header_index
