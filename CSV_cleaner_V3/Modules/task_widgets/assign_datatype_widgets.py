import streamlit as st
import pandas as pd

from Modules.utils.ui_utils import big_caption


# ---------------------------------------------------------
# Auto-detection rules based on column name patterns
# ---------------------------------------------------------
AUTO_TYPE_MAP = {
    "date": "date",
    "time": "time_only",
    "datetime": "date",
    "station": "string",
    "location": "string",
    "notes": "string",
    "type": "string",
    "units": "string",
    "code": "string",
    "comments": "string",
}


def detect_type(colname: str) -> str:
    """
    Return an auto-detected type based on column name. Defaults to float because, you know, environmental data.
    """
    name = colname.lower()

    for keyword, dtype in AUTO_TYPE_MAP.items():
        if keyword in name:
            return dtype

    # Default for environmental data!
    return "float"



def assign_datatype_widgets(df):
    """
    Widget for assigning data types to each column.
    - Auto-detects likely types based on column names
    - Shows human-readable labels for each type
    """

    # ---------------------------------------------------------
    # Intro text - explain WHY this matters
    # ---------------------------------------------------------
    big_caption(
        "Assigning data types ensures tasks behave correctly downstream, "
        "like parsing dates, for example. <br> Also guarantees your Excel "
        "download preserves real dates, numbers, and text."
    )

    # ---------------------------------------------------------
    # Defensive guards
    # ---------------------------------------------------------
    if not isinstance(df, pd.DataFrame):
        st.error("No valid data available for preview.")
        return None

    if df.empty:
        st.warning("Your dataset is empty - nothing to preview.")
        return None

    # ---------------------------------------------------------
    # Human-readable labels for the dropdown
    # ---------------------------------------------------------
    dtype_options = {
        "string": "String (text)",
        "integer": "Integer (whole numbers)",
        "float": "Float (decimal numbers)",
        "date": "Full Datetime (date + time)",
        "date_only": "Date Only (YYYY-MM-DD)",
        "time_only": "Time Only (HH:MM:SS)",
    }

    type_mapping = {}

    # ---------------------------------------------------------
    # Column-by-column selection
    # ---------------------------------------------------------
    st.write("#### Assign a datatype to each column in your table")

    for col in df.columns:

        # Auto-detect a reasonable default
        auto_type = detect_type(col)

        # Curator-friendly label
        st.markdown(f"**{col}**")

        selected = st.selectbox(
            f"Select datatype for '{col}'",
            options=list(dtype_options.keys()),
            index=list(dtype_options.keys()).index(auto_type),
            format_func=lambda x: dtype_options[x],
            key=f"type_{col}"
        )

        type_mapping[col] = selected

        st.markdown("---")

    # ---------------------------------------------------------
    # Execute-once trigger button
    # ---------------------------------------------------------
    if st.button("Apply Types", type="primary"):
        st.session_state.assign_types_trigger = True

    triggered = st.session_state.get("assign_types_trigger", False)
    st.session_state.assign_types_trigger = False

    if not triggered:
        return None

    # ---------------------------------------------------------
    # SUCCESS ---> Return kwargs for the task
    # ---------------------------------------------------------
    return {"type_mapping": type_mapping}
