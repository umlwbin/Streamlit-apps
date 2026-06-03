import streamlit as st
from streamlit_sortables import sort_items
from Modules.utils.ui_utils import big_caption


def reorder_columns_widget(df):
    """
    Widget for reordering columns using drag-and-drop.
    """
    big_caption("Drag and drop the column names below to set the new order.")

    cols = df.columns.tolist()

    # ---------------------------------------------------------
    # Step 1 - Drag-and-drop ordering
    # ---------------------------------------------------------
    reordered = sort_items(cols)

    st.info(f"Total columns: **{len(cols)}**")

    # ---------------------------------------------------------
    # Step 2 - Execute-once trigger
    # ---------------------------------------------------------
    if st.button("Next", type="primary"):
        st.session_state.reorder_trigger = True

    triggered = st.session_state.get("reorder_trigger", False)
    st.session_state.reorder_trigger = False

    if not triggered:
        return None

    # ---------------------------------------------------------
    # Step 3 - Final validation
    # ---------------------------------------------------------

    # Should never happen, but safe to check
    if not reordered:
        st.error("No columns detected - cannot reorder.", icon="🚨")
        return None

    # Soft validation: unchanged order
    if reordered == cols:
        st.warning("Column order unchanged.", icon="⚠️")

    # ---------------------------------------------------------
    # Step 4 - Return standardized order
    # ---------------------------------------------------------
    return {"reordered_variables": reordered}
