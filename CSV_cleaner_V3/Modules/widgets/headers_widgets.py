import streamlit as st

def headers_widgets(df):

    # Naming style toggle
    naming_style = st.radio(
        "Choose a naming style",
        ["snake_case", "camelCase", "Title Case"],
        key="header_style"
    )

    # Unit handling toggle
    preserve_units = st.radio(
        "How should units be handled? **Note - Units must be in parenthesis**",
        ["Preserve units", "Strip units"],
        key="header_units"
    )

    if st.button("Let's Go", type="primary", key="headers_go"):
        return {
            "naming_style": naming_style,
            "preserve_units": (preserve_units == "Preserve units")
        }

    return None