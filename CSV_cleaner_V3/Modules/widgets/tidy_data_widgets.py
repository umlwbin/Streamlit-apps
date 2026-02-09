import streamlit as st
from Modules.ui_utils import big_caption
from Modules.widgets.headers_widgets import headers_widgets


def tidy_data_widgets():
    """
    Collect user settings for the Tidy Data pipeline.

    This widget now reuses the same header-cleaning controls used by the
    standalone "Clean Headers" task, ensuring that any updates to header
    cleaning logic or UI are automatically reflected here.

    Returns a dictionary with:
    - nans: list of user-specified NaN tokens
    - naming_style: header naming style
    - preserve_units: bool
    - extract_sensors: bool
    - extract_scales: bool
    - extract_processing_notes: bool
    """

    big_caption("These settings will be applied to all uploaded files.")

    # ---------------------------------------------------------
    # NaN Token Standardization
    # ---------------------------------------------------------
    st.markdown("#### NaN Check")
    st.markdown("Are there any NaN representations in your file(s) that are not in the following list?")
    st.markdown("**NA**, **?**, **N/A**, **\" \"**, **np.nan**, **None**, **Nan**, **NaN**")
    st.markdown("If yes, enter additional NaN representation(s) below (comma‑separated):")

    nan_tokens = st.text_input("", placeholder="e.g., -, --, missing")
    nans = [t.strip() for t in nan_tokens.split(",") if t.strip()]

    # ---------------------------------------------------------
    # Header Cleaning Settings (reused from main header widget)
    # ---------------------------------------------------------
    st.markdown("---")
    header_settings = headers_widgets(show_button=False) or {} # df not needed for widget logic

    # ---------------------------------------------------------
    # Return all settings when user continues
    # ---------------------------------------------------------
    if st.button("Continue", type="primary", key="cleanupContinue"):
        return {
            "nans": nans,
            **(header_settings)  # merge header settings if returned
        }
