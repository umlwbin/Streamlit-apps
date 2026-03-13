import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def excel_label_to_index(label: str) -> int:
    label = label.upper()
    index = 0
    for i, char in enumerate(reversed(label)):
        index += (ord(char) - 64) * (26 ** i)
    return index - 1


def excel_index_to_label(n: int) -> str:
    result = ""
    while n >= 0:
        n, remainder = divmod(n, 26)
        result = chr(65 + remainder) + result
        n -= 1
    return result


def parse_range(input_str: str, df: pd.DataFrame) -> list:
    input_str = input_str.replace(" ", "").upper()
    if "-" not in input_str:
        return []

    try:
        start_label, end_label = input_str.split("-")
        start_idx = excel_label_to_index(start_label)
        end_idx = excel_label_to_index(end_label)

        if start_idx > end_idx:
            start_idx, end_idx = end_idx, start_idx

        if start_idx < 0 or end_idx >= len(df.columns):
            return []

        return df.columns[start_idx:end_idx + 1].tolist()

    except Exception:
        return []


# ---------------------------------------------------------
# Main widget
# ---------------------------------------------------------

def assign_datatype_widgets(df):
    """
    Widget for assigning data types to selected columns.

    Supports:
        - selecting columns via multiselect
        - selecting columns via Excel-style ranges (e.g., B-F)

    Returns
    -------
    dict or None
        {
            "type_mapping": {column_name: dtype, ...}
        }
        or None if the user has not completed the widget.
    """

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

    # ---------------------------------------------------------
    # Build kwargs dict - type_mapping
    # ---------------------------------------------------------
    type_mapping = {}
    for dtype in dtypes:
        selected = st.session_state.get(f"{dtype}_select", [])
        ranged = parse_range(st.session_state.get(f"{dtype}_range", ""), df)

        for col in set(selected + ranged):
            type_mapping[col] = dtype

    if not type_mapping:
        st.info("No columns selected yet.")

    # ---------------------------------------------------------
    # Return settings
    # ---------------------------------------------------------
    # Next button
    if st.button("Next", type="primary", key="assignNext"):
        if type_mapping:
            return {"type_mapping": type_mapping}
        else:
            st.warning("No columns were selected!", icon="⚠️")

    return None
