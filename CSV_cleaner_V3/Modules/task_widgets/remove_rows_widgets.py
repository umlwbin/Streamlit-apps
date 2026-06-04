import streamlit as st
from Modules.utils.ui_utils import big_caption

def remove_rows_widgets(df):

    # ---------------------------------------------------------
    # Soft Validation
    # ---------------------------------------------------------
    if df.empty:
        st.warning("The dataset is empty. No rows can be removed.")
        return None

    max_index = len(df) - 1
    big_caption(f"The first row is index 0. This dataset has <b>{len(df)} rows</b> (0 to {max_index}).")

    st.info(
        "If you remove multiple rows in separate steps, the table is reindexed "
        "after each removal. \n\nThis means the next removal always starts from a fresh index "
        "range **beginning at zero**.", icon="ℹ️"
    )

    # ---------------------------------------------------------
    # Row selection
    # ---------------------------------------------------------
    row_index = st.number_input(
        "**Select the row index to remove:**",
        min_value=0,
        max_value=max_index,
        step=1,
        key="remove_row_index"
    )

    # ---------------------------------------------------------
    # One shot trigger
    # ---------------------------------------------------------
    if st.button("Next", key="remove_row_next"):
        st.session_state.remove_row_trigger = True

    triggered = st.session_state.get("remove_row_trigger", False)
    st.session_state.remove_row_trigger = False

    if triggered:
        return {"row_index": row_index}

    return None
