import streamlit as st
from Modules.utils.ui_utils import big_caption

def merge_ymd_widgets(df):
    """
    Widget for selecting year, month, and day columns to merge into a single date column.
    """

    big_caption("📆 Merge Year, Month, Day columns into a full date!")

    if df.empty or df.columns.empty:
        st.error("This dataset has no columns.")
        return None

    cols = df.columns

    # Auto-detect defaults
    def_year = next((i for i, c in enumerate(cols) if "year" in c.lower()), None)
    def_month = next((i for i, c in enumerate(cols) if "month" in c.lower()), None)
    def_day = next((i for i, c in enumerate(cols) if "day" in c.lower()), None)

    col1, col2, col3 = st.columns(3)

    year_col = col1.selectbox("Year column", cols, index=def_year, key="ymd_year")
    month_col = col2.selectbox("Month column", cols, index=def_month, key="ymd_month")
    day_col = col3.selectbox("Day column", cols, index=def_day, key="ymd_day")

    # Soft validation
    if df[year_col].astype(str).str.strip().eq("").all():
        st.warning(f"Year column **{year_col}** is empty. Resulting dates will be missing.")

    if df[month_col].astype(str).str.strip().eq("").all():
        st.info(f"Month column **{month_col}** is empty. Missing months will be replaced with **1**.")

    if df[day_col].astype(str).str.strip().eq("").all():
        st.info(f"Day column **{day_col}** is empty. Missing days will be replaced with **1**.")

    # One-shot execution button
    if col1.button("Next", type="primary", key="ymd_next"):
        st.session_state.ymd_trigger = True

    triggered = st.session_state.get("ymd_trigger", False)
    st.session_state.ymd_trigger = False

    if triggered:

        # Hard validation
        if len({year_col, month_col, day_col}) < 3:
            st.error("Year, month, and day columns must be different.", icon="🚨")
            return None

        return {
            "year_column": year_col,
            "month_column": month_col,
            "day_column": day_col
        }

    return None
