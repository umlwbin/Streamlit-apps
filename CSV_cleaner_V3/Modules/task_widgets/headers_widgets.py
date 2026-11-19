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
        {"header_handling":...}
        or None until the curator confirms.
    """

    # ---------------------------------------------------------
    # SECTION: Intro
    # ---------------------------------------------------------
    st.write("#### Header Cleaning Settings")
    st.info("This function will clean your headers by removing problematic special characters and converting them to `snake_case`. " \
    "\n\nIt can also identify and remove units and move them to a metadata table, keeping your headers simple and understandable.")

    st.info("If header cleaning does not produce the exact names you want, "
    "use the **Rename Columns** task to manually edit your headers.")


    # ---------------------------------------------------------
    # SECTION: Header Style
    # ---------------------------------------------------------
    header_handling = st.radio("Select an option", ["Keep units in headers", "Move units to metadata table (recommended)"],key="header_style")

    if header_handling=="Move units to metadata table (recommended)":
        st.info("**Remember to download the metadata table before selecting another task!**")


    # ---------------------------------------------------------
    # Build settings dict
    # ---------------------------------------------------------
    settings = {"header_handling": header_handling}

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
