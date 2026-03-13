import streamlit as st

def add_row_widget(df):
    """
    Widget for inserting a new row or generating alphabetical headers.

    Supports:
        - manual entry
        - pasting a delimited list
        - auto-generating alphabetical headers

    Returns
    -------
    dict or None
        {
            "row_values": list[str] or None,
            "as_header": bool,
            "auto_headers": bool
        }
        or None if the user has not completed the widget.
    """

    st.markdown("""
    Add a new row to your table. You can enter values manually, paste a delimited list,  
    or auto-generate alphabetical headers (A, B, C, ...).
    """)

    # ---------------------------------------------------------
    # Preview
    # ---------------------------------------------------------
    st.markdown("##### Preview of your data")
    st.dataframe(df.head(5))

    # ---------------------------------------------------------
    # Input mode selection
    # ---------------------------------------------------------
    st.markdown("##### How would you like to enter the row values?")
    mode = st.radio(
        "Select",
        ["Manual entry", "Paste delimited list", "Generate alphabetical headers"],
        horizontal=True
    )

    row_values = None
    auto_headers = False

    # ---------------------------------------------------------
    # AUTO-GENERATE HEADERS
    # ---------------------------------------------------------
    if mode == "Generate alphabetical headers":
        st.info("Alphabetical headers (A, B, C, ...) will replace the current column names.")
        auto_headers = True

    # ---------------------------------------------------------
    # MANUAL ENTRY
    # ---------------------------------------------------------
    elif mode == "Manual entry":
        row_values = []
        st.markdown("##### Enter values for the new row")
        cols = st.columns(3)

        for i, col in enumerate(df.columns):
            with cols[i % 3]:
                val = st.text_input(f"{col}", key=f"addrow_{i}")
                row_values.append(val)

    # ---------------------------------------------------------
    # DELIMITED LIST
    # ---------------------------------------------------------
    else:
        st.markdown("#### Paste a comma, tab, semicolon, pipe, or newline-delimited list")
        raw = st.text_area(
            "Row values",
            placeholder="Example:\nA, 10, mg/L, 2024-01-01"
        )

        delimiter = st.selectbox(
            "Delimiter",
            options=[",", "tab", ";", "|", "newline"],
            index=0
        )

        if delimiter == "tab":
            delimiter = "\t"
        elif delimiter == "newline":
            delimiter = "\n"

        if raw.strip():
            normalized = raw.replace("\r\n", "\n")
            row_values = [v.strip() for v in normalized.split(delimiter)]
        else:
            row_values = []

    # ---------------------------------------------------------
    # Header option
    # ---------------------------------------------------------
    as_header = st.checkbox(
        "Use this row as the new header",
        disabled=auto_headers
    )

    st.markdown("---")
    apply_now = st.button("Add Row", type="primary")

    if apply_now:
        return {
            "row_values": row_values,
            "as_header": as_header,
            "auto_headers": auto_headers
        }

    return None
