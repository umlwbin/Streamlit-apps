import streamlit as st

def headers_widgets(df=None, show_button=True):
    """
    Render header-cleaning widgets for the updated clean_headers() logic.

    If show_button=True:
        - Show the "Let's Go" button
        - Return settings only when pressed

    If show_button=False:
        - Always return settings immediately
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
    # NEW: No units in header
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
        preserve_units = st.radio(
            "How should units be handled?",
            ["Preserve units", "Strip units"],
            key="header_units"
        ) == "Preserve units"

    # ---------------------------------------------------------
    # Additional metadata extraction
    # ---------------------------------------------------------
    extract_additional = st.checkbox(
        "Extract additional information in header (sensor information, scales, media, notes)",
        value=True,
        key="extract_additional"
    )

    # ---------------------------------------------------------
    # Return settings
    # ---------------------------------------------------------
    settings = {
        "naming_style": naming_style,
        "preserve_units": preserve_units,
        "extract_additional": extract_additional,
        "no_units_in_header": no_units_in_header,
    }

    if show_button:
        if st.button("Let's Go", type="primary", key="headers_go"):
            return settings
        return None

    return settings
