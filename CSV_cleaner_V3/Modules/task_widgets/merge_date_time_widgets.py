import streamlit as st
from Modules.utils.ui_utils import big_caption


def merge_date_time_widgets(df):
    """
    Widget for selecting a date column and a time column to merge into a single
    ISO datetime column.
    """
    big_caption("Merge a date column and a time column into one ISO datetime column")

    # ---------------------------------------------------------
    # Handle empty DataFrame
    # ---------------------------------------------------------
    if df.empty or df.columns.empty:
        st.error("This dataset has no columns.")
        return None

    cols = df.columns

    # ---------------------------------------------------------
    # Preview
    # ---------------------------------------------------------
    st.markdown('')
    st.markdown('##### Data Table Snapshot')
    st.dataframe(df.head(3))
    st.markdown('')

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
    # Soft validation
    # ---------------------------------------------------------
    if date_column:
        if df[date_column].astype(str).str.strip().eq("").all():
            st.warning(f"Date column **{date_column}** is empty. Resulting Date_Time will be all missing.")

    if time_column:
        if df[time_column].astype(str).str.strip().eq("").all():
            st.info(f"Time column **{time_column}** is empty. Missing times will be replaced with **00:00:00**.")

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
