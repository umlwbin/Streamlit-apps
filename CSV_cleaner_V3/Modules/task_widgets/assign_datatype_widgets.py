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
    Streamlit widget for assigning data types to selected columns.

    This widget:
    - shows a preview of the dataset with Excel-style column labels
    - lets the user select columns using multiselects or Excel-style ranges
    - builds a mapping of column_name --> chosen data type
    - returns the mapping only when the user clicks "Next"

    Returns
    -------
    dict or None
        {
            "type_mapping": {column_name: dtype, ...}
        }
        or None if the user has not completed the widget.


    NOTE:
    We wrap the entire widget inside a Streamlit form.
    Forms prevent Streamlit from re-creating widgets on every rerun,
    which avoids key errors and allow a multi-step UI to be stable.
    """


    # ---------------------------------------------------------
    # Streamlit Form
    # ---------------------------------------------------------
    # A form groups widgets together and only triggers a rerun
    # when the user presses the submit button.
    with st.form("assign_datatype_form"):

        # ---------------------------------------------------------
        # Column Preview
        # ---------------------------------------------------------
        # Show the first two rows of the dataset.
        # We add Excel-style labels (A, B, C...) to help users
        # reference columns when typing ranges like "B-F".
        st.markdown("##### Column Preview")

        preview = df.head(2).copy()
        preview.columns = [
            f"{excel_index_to_label(i)} | {col}"
            for i, col in enumerate(df.columns)]
        
        st.dataframe(preview)

        # ---------------------------------------------------------
        # Data Type Selection
        # ---------------------------------------------------------
        st.markdown("##### Assign Columns to Data Types")

        # Supported data types
        dtypes = ["date_only", "time_only", "date", "integer", "float", "string"]

        # Friendly labels for the UI
        dtype_labels = {
            "date_only": "Date Only (YYYY-MM-DD)",
            "time_only": "Time Only (HH:MM:SS)",
            "date": "Full Datetime (date + time)",
            "integer": "Integer (whole numbers)",
            "float": "Float (decimal numbers)",
            "string": "String (text)"
        }

        # Each data type gets its own expander. Inside each expander:
        # - a multiselect for choosing columns
        # - a text input for Excel-style ranges (e.g., B-F)
        for dtype in dtypes:
            with st.expander(f"Select {dtype_labels[dtype]} columns"):
                st.multiselect(
                    f"Choose columns for {dtype_labels[dtype]}",
                    options=df.columns.tolist(),
                    key=f"{dtype}_select"
                )
                st.text_input("Or enter column range (e.g., B-F)",key=f"{dtype}_range" )

        # ---------------------------------------------------------
        # Build the type_mapping dictionary
        # ---------------------------------------------------------
        # We combine:
        # - columns selected via multiselect
        # - columns selected via Excel-style ranges
        type_mapping = {}
        for dtype in dtypes:
            selected = st.session_state.get(f"{dtype}_select", [])
            ranged = parse_range(st.session_state.get(f"{dtype}_range", ""), df)

            # Assign each selected column to the chosen dtype
            for col in set(selected + ranged):
                type_mapping[col] = dtype

        # ---------------------------------------------------------
        # Submit Button
        # ---------------------------------------------------------
        # This button belongs to the form, so when clicked, the form submits and the function reruns only once.
        submitted = st.form_submit_button("Next", type="primary")

        # If the user clicked Next:
        if submitted:
            if type_mapping:
                # Return the mapping to the task runner
                return {"type_mapping": type_mapping}
            else:
                # Warn if nothing was selected
                st.warning("No columns were selected!", icon="⚠️")

    # If the form hasn't been submitted yet, return nothing
    return None