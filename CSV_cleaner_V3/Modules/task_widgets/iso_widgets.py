import streamlit as st
import pandas as pd
from Modules.utils.ui_utils import big_caption

def iso_widgets(df):
    """
    Simple widget for configuring ISO date-time parsing.

    Collects:
        - the date-time column
        - how ambiguous dates should be interpreted
    """

    st.markdown(" ")
    st.markdown("##### ISO Date-Time Settings")
    big_caption("Choose the date-time column and how ambiguous dates should be interpreted. ")

    cols = df.columns.tolist()
    if not cols:
        st.error("This dataset has no columns.")
        return None

    # ---------------------------------------------------------
    # Select datetime column
    # ---------------------------------------------------------
    date_time_col = st.selectbox(
        "**Select the date-time column**",
        options=cols,
        index=None,
        key="iso_col_select"
    )

    # ---------------------------------------------------------
    # Ambiguous date handling
    # ---------------------------------------------------------
    st.markdown(" ")
    ambiguous_mode = st.radio(
        "**How should ambiguous dates be interpreted?**",
        [
            "Assume year-first (YYYY-MM-DD)",
            "Assume month-first (MM/DD/YYYY)",
            "Assume day-first (DD/MM/YYYY)",
        ],
        key="iso_ambiguous_mode"
    )

    # ---------------------------------------------------------
    # Confirmation button
    # ---------------------------------------------------------
    if st.button("Next", type="primary", key="iso_next"):
        if not date_time_col:
            st.error("Please select a date-time column.", icon="🚨")
            return None

        return {
            "date_time_col": date_time_col,
            "ambiguous_mode": ambiguous_mode
        }

    return None
