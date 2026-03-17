import streamlit as st

def parse_dates_widgets(df):
    """
    Widget for selecting a datetime column to split into
    Year, Month, Day, and optionally Time.

    Supports:
        - auto-detection of likely datetime columns
        - optional extraction of time component
        - one-shot trigger pattern for consistent UX

    Returns
    -------
    dict or None
        {
            "date_time_col": str,
            "extract_time": bool
        }
        or None if the user has not completed the widget.
    """

    st.markdown("#### Parse a datetime column into Year, Month, Day, and Time")
    st.markdown("##### Choose the datetime column")

    cols = df.columns

    # ---------------------------------------------------------
    # Auto-detect a likely datetime column
    # ---------------------------------------------------------
    default_idx = next(
        (i for i, c in enumerate(cols)
         if "date" in c.lower() or "time" in c.lower()),
        0
    )

    col1, col2 = st.columns(2)

    date_time_col = col1.selectbox(
        "Datetime column",
        options=list(cols),
        index=default_idx,
        key="parse_dates_select"
    )

    extract_time = col2.checkbox(
        "Extract time component",
        value=True,
        key="parse_dates_extract_time"
    )

    # ---------------------------------------------------------
    # One-shot trigger
    # ---------------------------------------------------------
    if col1.button("Next", type="primary", key="parse_dates_next"):
        st.session_state.parse_dates_trigger = True

    triggered = st.session_state.get("parse_dates_trigger", False)
    st.session_state.parse_dates_trigger = False

    if triggered:

        # ---------------------------------------------------------
        # Validation
        # ---------------------------------------------------------
        if not date_time_col:
            col1.error("Please select a datetime column.", icon="🚨")
            return None

        # ---------------------------------------------------------
        # SUCCESS --> Return kwargs
        # ---------------------------------------------------------
        return {
            "date_time_col": date_time_col,
            "extract_time": extract_time
        }

    return None
