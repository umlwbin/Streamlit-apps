import streamlit as st
from Modules.utils.ui_utils import big_caption


def headers_widgets(df=None, show_button=True):
    """
    Widget for configuring header-cleaning settings.

    Parameters
    ----------
    show_button : bool
        If True, show the “Let’s Go” trigger button.
        If False, return settings immediately (used inside tidy-data widget).

    Returns:
        {
            "naming_style": ...,
            "preserve_units": ...,
            "no_units_in_header": ...
        }
        or None until the curator confirms.
    """

    # ---------------------------------------------------------
    # SECTION: Intro
    # ---------------------------------------------------------
    st.write("#### Header Cleaning Settings")
    big_caption(
        "Choose how your column names should be cleaned and whether units "
        "should be preserved.")

    # ---------------------------------------------------------
    # SECTION: Naming Style
    # ---------------------------------------------------------
    naming_style = st.radio("Choose a naming style for cleaned headers", ["snake_case", "camelCase", "Title Case"],key="header_style")

    # ---------------------------------------------------------
    # SECTION: Unit Handling
    # ---------------------------------------------------------
    st.write("#### Unit Handling")

    st.info("• If your dataset includes bracketed units inside the column names (e.g., "
        "`Temperature (°C)` or `Flow [m³/s]`), the cleaner can extract and "
        "normalize them. \n\n"
        "• If your units aren’t written in brackets, " 
        "the cleaner will attempt to recognize and standardize them using our internal unit map.\n\n"
        "• If your dataset does **NOT** include units in headers, or you do not want any unit handling, "
        "enable the option below.")

    no_units_in_header = st.checkbox( "My dataset does NOT include units in the column names", value=False, key="no_units_in_header")

    # If user says “no units in header”, disable unit preservation
    if no_units_in_header:
        preserve_units = False
        st.info(
            "Unit handling disabled because you indicated that your dataset "
            "does not include units in the column names.")
    else:
        # user chooses whether to keep or strip units
        preserve_units = (st.radio("**How should units be handled?**",["Strip units","Preserve units"],key="header_units") == "Preserve units")

        st.info(
            "For maximum interoperability, we recommed keeping column headers free of units (**Strip units** above) so "
            "headers can remain simple and machine‑friendly while the generated metadata table "
            "preserves full unit information. Ideally, add units to a **data dictionary**. ")

        st.info(
            "If the automated header cleaning didn’t produce the exact names you want, use the **Rename Columns** task to manually edit your headers. " \
            "It also produces a metadata table so you can easily copy the final variable names into your data dictionary. \n\n" \
            "**Be sure to download the metadata table below if you need the unit info before selecting another task** "
        )
    # ---------------------------------------------------------
    # Build settings dict
    # ---------------------------------------------------------
    settings = {
        "naming_style": naming_style,
        "preserve_units": preserve_units,
        "no_units_in_header": no_units_in_header,
    }

    # ---------------------------------------------------------
    # EXECUTE-ONCE TRIGGER (only when show_button=True)
    # ---------------------------------------------------------
    if not show_button:
        # Tidy-data widget will handle the trigger
        return settings

    if st.button("Let's Go", type="primary", key="headers_go"):
        st.session_state.headers_trigger = True

    triggered = st.session_state.get("headers_trigger", False)
    st.session_state.headers_trigger = False

    if not triggered:
        return None

    # ---------------------------------------------------------
    # SUCCESS ---> Return kwargs for clean_headers task
    # ---------------------------------------------------------
    return settings
