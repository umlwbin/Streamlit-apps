import streamlit as st
from streamlit_sortables import sort_items

def reorder_columns_widget(df):
    """
    Widget for reordering columns using drag-and-drop.

    Supports:
        - interactive drag-and-drop ordering
        - warning when no changes are made
        - one-shot trigger pattern for consistent UX

    Returns
    -------
    dict or None
        {
            "reordered_variables": list[str]
        }
        or None if the user has not completed the widget.
    """

    st.markdown("##### Drag and drop the column names below to set the new order.")

    cols = df.columns.tolist()

    # ---------------------------------------------------------
    # Sortable widget
    # ---------------------------------------------------------
    reordered = sort_items(cols)

    st.info(f"Total columns: **{len(cols)}**")

    # ---------------------------------------------------------
    # One-shot trigger
    # ---------------------------------------------------------
    st.button("Next", type="primary", key="reorderNext_WidgetKey")

    triggered = st.session_state.get("reorderNext_WidgetKey", False)

    if triggered:

        # Validation
        if not reordered:
            st.error("You did not reorder any columns.", icon="🚨")
            return None

        # Detect unchanged order
        if reordered == cols:
            st.warning("Column order unchanged.", icon="⚠️")

        # SUCCESS --> Return kwargs
        return {"reordered_variables": reordered}

    return None
