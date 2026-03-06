import streamlit as st
import re

def split_column_widget(df):
    """
    Widget for splitting a column based on a predefined set of delimiters.
    """

    st.markdown("""
    This tool splits a single column into multiple new columns based on a chosen delimiter.
    """)

    # ---------------------------------------------------------
    # Step 1 — Choose the column
    # ---------------------------------------------------------
    st.markdown("##### Select the column to scan")
    col = st.selectbox("Column", options=list(df.columns))

    # ---------------------------------------------------------
    # Step 2 — Choose delimiter
    # ---------------------------------------------------------
    st.markdown("##### Choose a delimiter")

    delimiter_choice = st.selectbox(
        "Delimiter",
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
        delimiters = [r"\s+"]  # REGEX delimiter
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
        delimiters = [d for d in raw.split(",") if d != ""]

    # ---------------------------------------------------------
    # Step 3 — Preview (first 10 rows)
    # ---------------------------------------------------------
    st.markdown("##### Preview of detected splits (first 5 rows)")

    if delimiters:
        # Normalize whitespace and strip edges
        preview_series = (
            df[col]
            .astype(str)
            .str.replace("\u00A0", " ", regex=False)   # convert NBSP → space
            .str.replace(r"\s+", " ", regex=True)      # collapse all whitespace
            .str.strip()
        )

        # Build regex pattern (regex delimiters are NOT escaped)
        escaped = [
            d if d.startswith("\\") else re.escape(d)
            for d in delimiters
        ]
        pattern = "|".join(escaped)

        # Perform preview split
        preview_split = preview_series.head(5).str.split(pattern, expand=True)

        # Show preview table
        st.dataframe(preview_split, use_container_width=True)

        # Show how many columns will be created
        st.info(f"Splitting will create **{preview_split.shape[1]}** new column(s).")

    else:
        st.info("Select or enter at least one delimiter to preview splits.")

    # ---------------------------------------------------------
    # Step 4 — Run
    # ---------------------------------------------------------
    st.markdown("---")
    apply_now = st.button("Split Column", type="primary")

    if apply_now:
        if not delimiters:
            st.warning("Please select or enter at least one delimiter.")
            return None

        return {
            "column": col,
            "delimiters": delimiters
        }

    return None
