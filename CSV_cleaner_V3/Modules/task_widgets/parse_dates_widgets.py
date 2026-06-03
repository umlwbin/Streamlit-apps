import streamlit as st
from Modules.utils.ui_utils import big_caption


def parse_dates_widgets(df):
    """
    Widget for selecting a datetime column to split into
    Year, Month, Day, and optionally Time.
    """

    big_caption("Parse a datetime column into Year, Month, Day, and Time")

    # ---------------------------------------------------------
    # 0. Snapshot of Data
    # ---------------------------------------------------------
    st.markdown(' ')
    st.markdown('##### Snapshot of Data')
    st.dataframe(df.head(3))
    st.markdown(' ')


    # ---------------------------------------------------------
    # 1. Column selection
    # ---------------------------------------------------------
    cols = df.columns.tolist()

    default_idx = next(
        (i for i, c in enumerate(cols)
         if "date" in c.lower() or "time" in c.lower()),0)

    
    col1, col2 = st.columns(2)
    date_time_col = col1.selectbox(
        "Datetime column",
        options=cols,
        index=default_idx,
        key="parse_dates_select"
    )

    extract_time = col1.checkbox(
        "Extract time component",
        value=True,
        key="parse_dates_extract_time"
    )

    # ---------------------------------------------------------
    # 2. Soft validation
    # ---------------------------------------------------------
    if date_time_col:
        series = df[date_time_col].astype(str).str.strip()

        if series.eq("").all():
            col1.warning(
                f"Column **{date_time_col}** is blank. "
                "Parsed columns will be empty.",
                icon="⚠️"
            )

        elif series.isna().all():
            col1.warning(
                f"Column **{date_time_col}** contains only missing values.",
                icon="⚠️"
            )

    # ---------------------------------------------------------
    # 3. One-shot trigger button
    # ---------------------------------------------------------
    if col1.button("Next", type="primary", key="parse_dates_next"):
        st.session_state.parse_dates_trigger = True

    triggered = st.session_state.get("parse_dates_trigger", False)
    st.session_state.parse_dates_trigger = False

    if triggered:

        # Hard validation (widget-level)
        if not date_time_col:
            col1.error("Please select a datetime column.", icon="🚨")
            return None

        # SUCCESS ---> return kwargs
        return {
            "date_time_col": date_time_col,
            "extract_time": extract_time
        }

    return None
