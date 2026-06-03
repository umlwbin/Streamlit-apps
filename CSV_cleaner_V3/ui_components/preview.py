import streamlit as st
import pandas as pd

@st.fragment
def show_live_preview():
    """
    Isolated preview renderer.
    This fragment prevents the entire app from re-running when preview updates.
    """

    st.markdown("### Live Data Preview")

    if not st.session_state.current_data:
        st.info("Upload a file and run a task to see the preview.")
        return

    # Always use the first file for preview
    fname, df = next(iter(st.session_state.current_data.items()))

    # ---------------------------------------------------------
    # PREVIEW CACHE KEY
    # ---------------------------------------------------------
    # Preview depends on:
    #   - filename
    #   - current dataframe id (changes after each task)
    #   - whether compare mode is on
    # ---------------------------------------------------------
    compare_mode = st.checkbox("Compare with original", key="compare_mode")

    df_id = id(df)  # unique per task run
    cache_key = (fname, df_id, compare_mode)

    # ---------------------------------------------------------
    # CACHE HIT --> instant preview
    # ---------------------------------------------------------
    if cache_key in st.session_state.preview_cache:
        st.session_state.preview_cache[cache_key]()
        return

    # ---------------------------------------------------------
    # CACHE MISS --> build preview once
    # ---------------------------------------------------------
    def render_preview():
        st.markdown(f"##### File: `{fname}`")

        # Processed preview
        processed_preview = df.head(5)
        st.markdown("##### Processed Data (Top 5 Rows)")
        st.dataframe(processed_preview, use_container_width=True)

        if compare_mode:
            # Original preview
            original_df = st.session_state.original_data[fname]
            original_preview = original_df.head(5)

            st.markdown("##### Original Data (Top 5 Rows)")
            st.dataframe(original_preview, use_container_width=True)

    # Store in cache
    st.session_state.preview_cache[cache_key] = render_preview

    # Render now
    render_preview()
