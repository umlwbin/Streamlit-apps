import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def excel_label_to_index(label: str) -> int:
    """
    Convert an Excel-style column label (A, B, C, ..., Z, AA, AB, ...)
    into a zero-based column index.

    Example:
        A → 0
        B → 1
        Z → 25
        AA → 26
        AB → 27

    This lets users enter column ranges like "B-F" instead of numbers.
    """
    label = label.upper()
    index = 0

    # Process letters from right to left (like base-26 math)
    for i, char in enumerate(reversed(label)):
        # ord('A') = 65, so subtract 64 to make A=1, B=2, ...
        index += (ord(char) - 64) * (26 ** i)

    return index - 1   # Convert from 1-based to 0-based indexing


def excel_index_to_label(n: int) -> str:
    """
    Convert a zero-based column index into an Excel-style label.

    Example:
        0 → A
        1 → B
        25 → Z
        26 → AA
        27 → AB

    Used to show column previews like "A | column_name".
    """
    result = ""

    # Repeatedly divide by 26 to extract letters
    while n >= 0:
        n, remainder = divmod(n, 26)
        result = chr(65 + remainder) + result
        n -= 1  # Adjust because Excel labels are 1-based

    return result


def parse_range(input_str: str, df: pd.DataFrame) -> list:
    """
    Convert a user-entered Excel-style range (e.g., "B-F")
    into a list of actual column names from the DataFrame.

    Steps:
        1. Clean the input (remove spaces, uppercase)
        2. Split into start and end labels
        3. Convert labels to numeric indices
        4. Return the slice of df.columns between those indices

    If the input is invalid or out of bounds, return an empty list.
    """
    input_str = input_str.replace(" ", "").upper()

    # Must contain a dash to be a valid range
    if "-" not in input_str:
        return []

    try:
        start_label, end_label = input_str.split("-")

        start_idx = excel_label_to_index(start_label)
        end_idx = excel_label_to_index(end_label)

        # Ensure start <= end
        if start_idx > end_idx:
            start_idx, end_idx = end_idx, start_idx

        # Ensure indices are within the DataFrame
        if start_idx < 0 or end_idx >= len(df.columns):
            return []

        return df.columns[start_idx:end_idx + 1].tolist()

    except Exception:
        # Any parsing error → return empty list
        return []



# ---------------------------------------------------------
# Main widget
# ---------------------------------------------------------

def assign_datatype_widgets(df):

    st.markdown("##### Column Preview")

    # Show first 2 rows with Excel-style labels
    preview = df.head(2).copy()
    preview.columns = [
        f"{excel_index_to_label(i)} | {col}"
        for i, col in enumerate(df.columns)
    ]
    st.dataframe(preview)

    st.markdown("##### Assign Columns to Data Types")

    dtypes = ["date_only", "time_only", "date", "integer", "float", "string"]

    dtype_labels = {
        "date_only": "Date Only (YYYY-MM-DD)",
        "time_only": "Time Only (HH:MM:SS)",
        "date": "Full Datetime (date + time)",
        "integer": "Integer (whole numbers)",
        "float": "Float (decimal numbers)",
        "string": "String (text)"
    }

    # Collect user selections
    for dtype in dtypes:
        with st.expander(f"Select {dtype_labels[dtype]} columns"):
            st.multiselect(
                f"Choose columns for {dtype_labels[dtype]}",
                options=df.columns.tolist(),
                key=f"{dtype}_select"
            )
            st.text_input(
                "Or enter column range (e.g., B-F)",
                key=f"{dtype}_range"
            )

    # Build mapping
    type_mapping = {}
    for dtype in dtypes:
        selected = st.session_state.get(f"{dtype}_select", [])
        ranged = parse_range(st.session_state.get(f"{dtype}_range", ""), df)

        for col in set(selected + ranged):
            type_mapping[col] = dtype

    if not type_mapping:
        st.info("No columns selected yet.")

    # Next button
    if st.button("Next", type="primary", key="assignNext"):
        if type_mapping:
            return {"type_mapping": type_mapping}
        else:
            st.warning("No columns were selected!", icon="⚠️")

    return None
