import streamlit as st
import re
from Modules.utils.ui_utils import big_caption


def split_column_widget(df):
    """
    Widget for splitting a column into multiple new columns based on one or more delimiters.

    Supports:
        - selecting a column
        - choosing a predefined or custom delimiter
        - previewing the split on the first 5 rows
    """

    big_caption("Choose a column and delimiter(s) to split it into multiple new columns.")

    st.info('The new columns will have the name of the original split column + `_1`, `_2`, etc. Example, `Temp_1`')

    # ---------------------------------------------------------
    # Step 1 - Choose the column
    # ---------------------------------------------------------
    col = st.selectbox("**Column to split**", options=list(df.columns))

    # ---------------------------------------------------------
    # Step 2 - Choose delimiter(s)
    # ---------------------------------------------------------

    delimiter_choice = st.selectbox(
        "**Choose a Delimiter**",
        [
            "Space (one or more)",
            "Tab (\\t)",
            "Comma (,)",
            "Pipe (|)",
            "Slash (/)",
            "Semicolon (;)",
            "Newline (\\n)",
            "Custom..."
        ]
    )

    # Map dropdown choice → actual delimiter(s)
    if delimiter_choice == "Space (one or more)":
        delimiters = [r"\s+"]  # regex
    elif delimiter_choice == "Tab (\\t)":
        delimiters = ["\t"]
    elif delimiter_choice == "Comma (,)":
        delimiters = [","]
    elif delimiter_choice == "Pipe (|)":
        delimiters = ["|"]
    elif delimiter_choice == "Slash (/)":
        delimiters = ["/"]
    elif delimiter_choice == "Semicolon (;)":
        delimiters = [";"]
    elif delimiter_choice == "Newline (\\n)":
        delimiters = ["\n"]
    else:
        raw = st.text_input("Enter custom delimiter(s), separated by commas")
        delimiters = [d.strip() for d in raw.split(",") if d.strip() != ""]

    # ---------------------------------------------------------
    # Step 3 - Preview (first 5 rows)
    # ---------------------------------------------------------
    st.write(" ")
    st.write("#### Preview")

    if delimiters:
        preview_series = (
            df[col]
            .astype(str)
            .str.replace("\u00A0", " ", regex=False)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

        # Build regex pattern
        escaped = [
            d if d.startswith("\\") else re.escape(d)
            for d in delimiters
        ]
        pattern = "|".join(escaped)

        preview_split = preview_series.head(5).str.split(pattern, expand=True)

        st.dataframe(preview_split, use_container_width=True)
        st.info(f"Splitting will create **{preview_split.shape[1]}** new column(s).")
    else:
        st.info("Select or enter at least one delimiter to preview splits.")

    # ---------------------------------------------------------
    # Step 4 - Execute-once trigger
    # ---------------------------------------------------------
    st.markdown("---")

    if st.button("Split Column", type="primary"):
        st.session_state.split_trigger = True

    triggered = st.session_state.get("split_trigger", False)
    st.session_state.split_trigger = False

    if not triggered:
        return None

    # ---------------------------------------------------------
    # Step 5 - Final validation
    # ---------------------------------------------------------
    if not delimiters:
        st.error("Please select or enter at least one delimiter.", icon="🚨")
        return None

    # ---------------------------------------------------------
    # Step 6 - Return kwargs
    # ---------------------------------------------------------
    return {
        "column": col,
        "delimiters": delimiters
    }
