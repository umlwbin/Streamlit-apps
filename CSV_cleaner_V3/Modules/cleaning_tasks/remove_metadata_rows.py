import pandas as pd

def remove_metadata_rows(
    df: pd.DataFrame,
    *,
    filename=None,
    identifiers,
    metadata_extract=None,
    **kwargs
):
    """
    Detect and remove metadata rows that appear above the true header row.

    This task:
        - Detects the header row using user-provided identifiers.
        - Removes all rows above the detected header (metadata rows).
        - Promotes the detected header row to column names.
        - Ensures column names are unique.
        - Optionally extracts metadata values into new columns using rule-based cleaning.
        - Returns a preview of metadata rows for UI display.
    """

    # -----------------------------------------------------
    # 1. HARD VALIDATION
    # -----------------------------------------------------
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    if not isinstance(identifiers, list) or not all(isinstance(x, str) for x in identifiers):
        raise ValueError("identifiers must be a list of strings.")

    if len(identifiers) == 0:
        raise ValueError("At least one identifier must be provided.")

    if metadata_extract is not None and not isinstance(metadata_extract, dict):
        raise ValueError("metadata_extract must be a dictionary or None.")

    cleaned_df = df.copy()

    # -----------------------------------------------------
    # 2. SOFT VALIDATION
    # -----------------------------------------------------
    warnings = []

    identifiers_norm = [x.strip().lower() for x in identifiers]

    df_str = cleaned_df.astype(str).applymap(lambda x: x.strip().lower())

    # -----------------------------------------------------
    # 3. CORE PROCESSING
    # -----------------------------------------------------

    def make_unique(names):
        seen = {}
        unique = []
        for name in names:
            if name not in seen:
                seen[name] = 0
                unique.append(name)
            else:
                seen[name] += 1
                unique.append(f"{name}_{seen[name]}")
        return unique

    # Detect header row
    header_index = None
    for idx, row in df_str.iterrows():
        row_values = set(row.tolist())
        if all(identifier in row_values for identifier in identifiers_norm):
            header_index = idx
            break

    if header_index is None:
        warnings.append(
            "No header row matched the provided identifiers. Dataset returned unchanged."
        )
        summary = {
            "metadata_preview": [],
            "filename": filename,
            "warnings": warnings,
        }
        return cleaned_df.copy(), summary, None

    metadata_df = cleaned_df.iloc[:header_index].copy()

    if metadata_df.empty:
        warnings.append("No metadata rows found above the detected header.")

    # Promote header row
    new_header = cleaned_df.iloc[header_index].astype(str).tolist()
    new_header = make_unique(new_header)

    cleaned_df = cleaned_df.iloc[header_index + 1:].copy()
    cleaned_df.columns = new_header
    cleaned_df = cleaned_df.reset_index(drop=True)

    # Build metadata preview
    preview = metadata_df.head(10).to_dict(orient="records")

    # -----------------------------------------------------
    # 3B. APPLY RULE-BASED METADATA EXTRACTION
    # -----------------------------------------------------
    if metadata_extract:
        for new_col, info in metadata_extract.items():

            if "row" not in info or "col_index" not in info:
                warnings.append(f"Metadata extraction for '{new_col}' is missing required keys.")
                continue

            row_idx = info["row"]
            col_index = info["col_index"]
            rules = info.get("rules", {})

            if row_idx >= len(metadata_df):
                warnings.append(
                    f"Metadata extraction row {row_idx} out of range for '{new_col}'."
                )
                continue

            row = metadata_df.iloc[row_idx]
            non_empty = [cell for cell in row.tolist() if str(cell).strip() != ""]

            if col_index >= len(non_empty):
                warnings.append(
                    f"Metadata extraction col_index {col_index} out of range for '{new_col}'."
                )
                continue

            raw_value = str(non_empty[col_index])
            value = raw_value

            # -----------------------------
            # Apply cleaning rules
            # -----------------------------
            if rules.get("strip_whitespace"):
                value = value.strip()

            if rules.get("remove_direction"):
                for d in ["N", "S", "E", "W"]:
                    value = value.replace(d, "").replace(d.lower(), "")

            if rules.get("remove_degree_symbol"):
                value = value.replace("°", "")

            cleaned_df[new_col] = value

    # -----------------------------------------------------
    # 4. SUMMARY
    # -----------------------------------------------------
    summary = {
        "metadata_preview": preview,
        "filename": filename,
        "warnings": warnings,
    }

    # -----------------------------------------------------
    # 5. SUMMARY DATAFRAME
    # -----------------------------------------------------
    summary_df = None

    # -----------------------------------------------------
    # 6. RETURN
    # -----------------------------------------------------
    return cleaned_df, summary, summary_df
