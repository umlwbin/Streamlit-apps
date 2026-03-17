import streamlit as st

def headers_widgets(df=None, show_button=True):
    """
    Widget for configuring header-cleaning settings.

    Supports:
        - choosing naming style
        - controlling unit handling
        - optional "Let's Go" confirmation button

    Parameters
    ----------
    df : pandas.DataFrame or None
        Unused, but included for consistency with other widgets.

    show_button : bool
        If True, show a confirmation button and return settings only when pressed.
        If False, return settings immediately.

    Returns
    -------
    dict or None
        {
            "naming_style": str,
            "preserve_units": bool,
            "no_units_in_header": bool
        }
        or None if show_button=True and the user has not pressed the button.
    """

    st.markdown("#### Header Cleaning Settings")

    # ---------------------------------------------------------
    # Naming style
    # ---------------------------------------------------------
    naming_style = st.radio(
        "Choose a naming style for cleaned headers",
        ["snake_case", "camelCase", "Title Case"],
        key="header_style"
    )

    # ---------------------------------------------------------
    # No units in header
    # ---------------------------------------------------------
    no_units_in_header = st.checkbox(
        "No units in header (dataset does not include units in column names)",
        value=False,
        key="no_units_in_header"
    )

    # ---------------------------------------------------------
    # Unit handling (disabled if no_units_in_header=True)
    # ---------------------------------------------------------
    if no_units_in_header:
        preserve_units = False
        st.info("Unit handling disabled because 'No units in header' is selected.")
    else:
        preserve_units = (
            st.radio(
                "How should units be handled?",
                ["Preserve units", "Strip units"],
                key="header_units"
            ) == "Preserve units"
        )

    # ---------------------------------------------------------
    # Build kwargs dict
    # ---------------------------------------------------------
    settings = {
        "naming_style": naming_style,
        "preserve_units": preserve_units,
        "no_units_in_header": no_units_in_header,
    }

    # ---------------------------------------------------------
    # Return settings
    # ---------------------------------------------------------
    if show_button:
        if st.button("Let's Go", type="primary", key="headers_go"):
            return settings
        return None

    return settings
