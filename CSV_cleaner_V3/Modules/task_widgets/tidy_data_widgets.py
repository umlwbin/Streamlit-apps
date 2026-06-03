import streamlit as st
from Modules.utils.ui_utils import big_caption
from Modules.task_widgets.headers_widgets import headers_widgets


def tidy_data_widgets(df):
    """
    Widget for collecting user settings for the Tidy Data pipeline.

    Includes:
        - NaN standardization
        - Header cleaning settings (reusing the main header widget)
        - A clear list of all cleaning steps that will be applied
    """

    big_caption("These settings will be applied to all uploaded files.")

    # ---------------------------------------------------------
    # Pipeline Overview (accurate to the refactored task)
    # ---------------------------------------------------------
    st.markdown("#### What this cleaning pipeline will do")

    st.markdown("""
    The **Tidy Data** pipeline will automatically apply the following steps:

    1. **Remove empty columns**  
    2. **Remove empty rows**  
    3. **Standardize NaN-like values** (including your custom NaN tokens)  
    4. **Trim whitespace** from all cells  
    5. **Fix duplicate column names**  
    6. **Clean and standardize column headers** (using your chosen naming style and unit-handling settings)
    """)

    st.markdown("---")

    # ---------------------------------------------------------
    # NaN Token Standardization
    # ---------------------------------------------------------
    st.markdown("#### NaN Check")
    st.markdown(
        "If your dataset uses additional symbols to represent missing values "
        "(e.g., `999`, `missing`), enter them below.")

    st.markdown("Recognized by default: `NA`, `?`, `N/A`, `\" \"`, `np.nan`, `None`, `Nan`, `NaN`, `NAN`, `NA`, `Null`")

    nan_tokens = st.text_input("", placeholder="e.g., 999, missing")
    nans = [t.strip() for t in nan_tokens.split(",") if t.strip()]

    # ---------------------------------------------------------
    # Header Cleaning Settings (reused from main header widget)
    # ---------------------------------------------------------
    st.markdown("#### Header Cleaning Option")
    skip_headers = st.checkbox(
        "Skip cleaning headers",value=True)

    if skip_headers:
        st.info(
            "Header cleaning will be skipped. If you want to rename columns manually instead, "
            "use the **Rename Columns** task - it works across multiple files.")
        
        header_settings = {"skip_headers": True }
    else:
        header_settings = headers_widgets(show_button=False) or {} # ensures tht the header widget does NOT show its own button
        header_settings["skip_headers"] = False

    # ---------------------------------------------------------
    # Execute-once trigger
    # ---------------------------------------------------------
    if st.button("Continue", type="primary", key="cleanupContinue"):
        st.session_state.tidy_trigger = True

    triggered = st.session_state.get("tidy_trigger", False)
    st.session_state.tidy_trigger = False

    if not triggered:
        return None

    # ---------------------------------------------------------
    # SUCCESS ---> Return kwargs for basic_cleaning task
    # ---------------------------------------------------------
    return {
        "nans": nans,
        **header_settings
    }
