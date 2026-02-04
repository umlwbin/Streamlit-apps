import streamlit as st

def merge_date_time_widgets(df):
    """
    Widget for selecting a date column and a time column to merge into a single
    ISO datetime column. Uses one-shot triggers and consistent UX patterns.
    """

    st.markdown("#### Merge a date column and a time column into one ISO datetime")

    # Auto-detect defaults
    def_date = next((i for i, c in enumerate(cols) if "date" in c.lower()), None)
    def_time = next((i for i, c in enumerate(cols) if "time" in c.lower()), None)

    col1, col2 = st.columns(2)

    cols = df.columns
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

    # One-shot trigger
    if col1.button("Next", type="primary", key="merge_date_time_next"):
        st.session_state.merge_dt_trigger = True

    triggered = st.session_state.get("merge_dt_trigger", False)
    st.session_state.merge_dt_trigger = False

    if triggered:

        # Validation
        if not date_column or not time_column:
            st.error("Please select both a date column and a time column.", icon="🚨")
            return None

        if date_column == time_column:
            st.error("Date and time columns must be different.", icon="🚨")
            return None

        # Return task inputs
        return {
            "date_column": date_column,
            "time_column": time_column
        }

    return None