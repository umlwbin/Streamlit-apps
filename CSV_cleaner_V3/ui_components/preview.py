import streamlit as st
import pandas as pd

def show_live_preview():
    """
    Preview renderer that maps to the live application state
    """
    st.markdown("### Live Data Preview")

    # If there is no data in memory, show the placeholder message
    if not st.session_state.get("current_data"):
        st.info("Upload a file and run a task to see the preview.")
        return

    # Grab the first file currently in the data dictionary
    fname, df = next(iter(st.session_state.current_data.items()))


    # Generate a dynamic key based on history position.
    # This destroys the widget cache on Undo/Redo, forcing Streamlit to refresh the data table
    history_version = len(st.session_state.get("history_stack", [])) + len(st.session_state.get("redo_stack", []))
    compare_widget_key = f"compare_mode_v{history_version}"

    # Check box for comparing with original baseline data
    compare_mode = st.checkbox("Compare with original", key=compare_widget_key)

    st.markdown(f"##### File: `{fname}`")

    # Processed preview (Top 5 rows only - very lightweight)
    st.markdown("##### Processed Data (Top 5 Rows)")
    st.dataframe(df.head(5), use_container_width=True)

    # Original preview (Only builds if the user explicitly requests it)
    if compare_mode and fname in st.session_state.original_data:
        st.markdown("##### Original Data (Top 5 Rows)")
        st.dataframe(st.session_state.original_data[fname].head(5), use_container_width=True)