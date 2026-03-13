import streamlit as st

def merge_date_time_widgets(df):
    """
    Widget for selecting a date column and a time column to merge into a single
    ISO datetime column.

    Supports:
        - auto-detection of likely date/time columns
        - validation that both columns are selected and distinct
        - one-shot trigger pattern for consistent UX

    Returns
    -------
    dict or None
        {
            "date_column": str,
            "time_column": str
        }
        or None if the user has not completed the widget.
    """

    st.markdown("#### Merge a date column and a time column into one ISO datetime")

    # ---------------------------------------------------------
    # Handle empty DataFrame
    # ---------------------------------------------------------
    if df.empty or df.columns.empty:
        st.error("This dataset has no columns.")
        return None

    cols = df.columns

    # ---------------------------------------------------------
    # Auto-detect defaults
    # ---------------------------------------------------------
    def_date = next((i for i, c in enumerate(cols) if "date" in c.lower()), None)
    def_time = next((i for i, c in enumerate(cols) if "time" in c.lower()), None)

    col1, col2 = st.columns(2)

    date_column = col1.selectbox(
        "Date column",
        options=list(cols),
        index=def_date,
        key="merge_date_select"
    )

    time_column = col2.selectbox(
        "Time column",
        options=list(cols),
        index=def_time,
        key="merge_time_select"
    )

    # ---------------------------------------------------------
    # One-shot trigger
    # ---------------------------------------------------------
    if col1.button("Next", type="primary", key="merge_date_time_next"):
        st.session_state.merge_dt_trigger = True

    triggered = st.session_state.get("merge_dt_trigger", False)
    st.session_state.merge_dt_trigger = False

    if triggered:

        # ---------------------------------------------------------
        # Validation
        # ---------------------------------------------------------
        if not date_column or not time_column:
            st.error("Please select both a date column and a time column.", icon="🚨")
            return None

        if date_column == time_column:
            st.error("Date and time columns must be different.", icon="🚨")
            return None

        # ---------------------------------------------------------
        # SUCCESS ---> Return kwargs
        # ---------------------------------------------------------
        return {
            "date_column": date_column,
            "time_column": time_column
        }

    return None
