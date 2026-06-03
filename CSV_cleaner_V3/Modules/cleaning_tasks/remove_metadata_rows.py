import pandas as pd
import streamlit as st

def remove_metadata_rows(
    df: pd.DataFrame,
    *,
    filename=None,
    identifiers,
    metadata_extract=None,
    **kwargs
):
    """
    Detect and remove metadata rows above the true header row.

    This task:
        - Detects the header row using user-provided identifiers.
        - Removes all rows above the detected header (metadata rows).
        - Promotes the detected header row to column names.
        - Ensures column names are unique.
        - Optionally extracts metadata values into new columns using rule-based cleaning.
        - Updates row_map (Streamlit mode).
        - Returns only cleaned_df.
    """

    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors
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
    # 2. CORE PROCESSING
    # -----------------------------------------------------

    # Normalize identifiers
    identifiers_norm = [x.strip().lower() for x in identifiers]

    # Normalize df for detection
    df_str = cleaned_df.astype(str).applymap(lambda x: x.strip().lower())

    # Detect header row
    header_index = None
    for idx, row in df_str.iterrows():
        row_values = set(row.tolist())
        if all(identifier in row_values for identifier in identifiers_norm):
            header_index = idx
            break

    # If no header found → return unchanged
    if header_index is None:
        return cleaned_df

    # Metadata rows (to extract from)
    metadata_df = cleaned_df.iloc[:header_index].copy()

    # Promote header row
    new_header = cleaned_df.iloc[header_index].astype(str).tolist()

    # Ensure unique column names
    seen = {}
    unique_header = []
    for name in new_header:
        if name not in seen:
            seen[name] = 0
            unique_header.append(name)
        else:
            seen[name] += 1
            unique_header.append(f"{name}_{seen[name]}")

    # Slice to rectangular data
    cleaned_df = cleaned_df.iloc[header_index + 1:].copy()
    cleaned_df.columns = unique_header
    cleaned_df = cleaned_df.reset_index(drop=True)

    # -----------------------------------------------------
    # 3. APPLY RULE-BASED METADATA EXTRACTION
    # -----------------------------------------------------

    if metadata_extract:
        for new_col, info in metadata_extract.items():

            row_idx = info.get("row")
            col_index = info.get("col_index")
            rules = info.get("rules", {})

            # Skip invalid instructions
            if row_idx is None or col_index is None:
                continue
            if row_idx >= len(metadata_df):
                continue

            # Extract non-empty values from the metadata row
            row = metadata_df.iloc[row_idx]
            non_empty = [cell for cell in row.tolist() if str(cell).strip() != ""]
            if col_index >= len(non_empty):
                continue

            raw_value = str(non_empty[col_index])
            value = raw_value

            # Cleaning rules
            if rules.get("strip_whitespace"):
                value = value.strip()

            if rules.get("remove_direction"):
                for d in ["N", "S", "E", "W"]:
                    value = value.replace(d, "").replace(d.lower(), "")

            if rules.get("remove_degree_symbol"):
                value = value.replace("°", "")

            cleaned_df[new_col] = value

    # -----------------------------------------------------
    # 4. UPDATE ROW MAP (Streamlit mode)
    # -----------------------------------------------------
    # This task removes metadata rows + the header row, so row_map must be
    # updated to keep undo/redo and provenance correct.
    #
    # In Streamlit:
    #     original_map = st.session_state.row_map[filename]
    #     new_map = original_map[header_index + 1:]
    #     st.session_state.row_map[filename] = new_map
    #
    # Outside Streamlit:
    #     You must maintain your own row_map.
    #     Example:
    #         original_map = list(range(1, len(df) + 1))
    #         # Remove rows 0..header_index (inclusive)
    #         new_map = original_map[header_index + 1:]
    #
    # The task itself does NOT depend on Streamlit; only the row_map update does.

    if filename is not None and "row_map" in st.session_state:
        original_map = st.session_state.row_map.get(filename, [])
        new_map = original_map[header_index + 1:]
        st.session_state.row_map[filename] = new_map

    # -----------------------------------------------------
    # 5. RETURN
    # -----------------------------------------------------
    return cleaned_df
