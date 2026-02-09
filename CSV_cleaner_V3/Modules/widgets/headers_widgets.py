import streamlit as st
def headers_widgets(df=None, show_button=True):
    """
    Render header-cleaning widgets.

    If show_button=True (default):
        - Show the "Let's Go" button
        - Return settings only when the button is pressed

    If show_button=False:
        - Do NOT show the button
        - Always return the settings immediately
    """

    st.markdown("#### Header Cleaning Settings")

    # Naming style toggle
    st.markdown("##### Choose a naming style for the headers")
    naming_style = st.radio(
        "Select",
        ["snake_case", "camelCase", "Title Case"],
        key="header_style"
    )

    # Unit handling toggle
    st.markdown("##### How should units be handled?")
    preserve_units = st.radio(
        "Select",
        ["Preserve units", "Strip units"],
        key="header_units"
    )
    st.info("The units will still be added to a metadata table below; you can add this to your **data dictionary**")

    st.markdown("##### Advanced Extraction")

    extract_sensors = st.checkbox(
        "Extract sensor model names",
        value=True,
        key="extract_sensors"
    )

    extract_scales = st.checkbox(
        "Extract calibration scales",
        value=True,
        key="extract_scales"
    )

    extract_processing_notes = st.checkbox(
        "Extract processing notes",
        value=True,
        key="extract_processing_notes"
    )

    # ---------------------------------------------------------
    # Behavior depends on show_button
    # ---------------------------------------------------------
    settings = {
        "naming_style": naming_style,
        "preserve_units": (preserve_units == "Preserve units"),
        "extract_sensors": extract_sensors,
        "extract_scales": extract_scales,
        "extract_processing_notes": extract_processing_notes,
    }

    if show_button:
        if st.button("Let's Go", type="primary", key="headers_go"):
            return settings
        return None

    # If show_button=False → always return settings
    return settings
