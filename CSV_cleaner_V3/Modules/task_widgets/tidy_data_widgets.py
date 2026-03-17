import streamlit as st
from Modules.utils.ui_utils import big_caption
from Modules.task_widgets.headers_widgets import headers_widgets

def tidy_data_widgets():
    """
    Widget for collecting user settings for the Tidy Data pipeline.

    Includes:
        - NaN token standardization
        - Header cleaning settings (reusing the main header widget)
    
    Returns
    -------
    dict or None
        {
            "nans": list[str],
            "naming_style": str,
            "preserve_units": bool,
            "extract_additional": bool,
            "no_units_in_header": bool
        }
        or None if the user has not completed the widget.
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
    header_settings = headers_widgets(show_button=False) or {}

    # ---------------------------------------------------------
    # Final confirmation
    # ---------------------------------------------------------
    if st.button("Continue", type="primary", key="cleanupContinue"):
        return {
            "nans": nans,
            **header_settings
        }

    return None
