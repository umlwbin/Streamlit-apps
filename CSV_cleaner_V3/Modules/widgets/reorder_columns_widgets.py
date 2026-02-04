import streamlit as st
from streamlit_sortables import sort_items

def redorder_widget(df):
    st.markdown("##### Drag and drop the column names below to set the new order.")

    cols = df.columns
    # Sortable widget
    reordered = sort_items(list(cols))

    # Show count
    st.info(f"Total columns: **{len(cols)}**")

    # One-shot trigger
    st.button("Next", type="primary", key="reorderNext_WidgetKey")

    if st.session_state.get("reorderNext_WidgetKey"):
        if not reordered:
            st.error("You did not reorder any columns.", icon="🚨")
            return None

        # Detect if user made no changes
        if list(cols) == reordered:
            st.warning("Column order unchanged.", icon="⚠️")

        return {"reordered_variables": reordered}