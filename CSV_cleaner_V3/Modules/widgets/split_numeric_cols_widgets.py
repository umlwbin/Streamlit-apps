import streamlit as st
import re

def split_numeric_columns_widget(df):
    """
    Widget for splitting columns that contain two numeric values
    separated by spaces or tabs (PDF → Excel artifacts).
    """

    st.markdown("""
    For tables with **two numeric values in one column**,
    separated by inconsistent spaces or tabs.

    This tool detects those patterns and splits them into two new columns.
    Only whitespace‑separated numeric pairs are split.
    """)

    # Auto-detect candidate columns
    candidate_cols = []
    pattern = re.compile(r"^\s*[+-]?\d*\.?\d+\s+[+-]?\d*\.?\d+\s*$")

    for col in df.columns:
        sample = df[col].astype(str).head(20)
        if any(pattern.match(re.sub(r"\s+", " ", v.strip())) for v in sample):
            candidate_cols.append(col)


    st.markdown("##### Table Preview")
    st.dataframe(df.head(5))

    st.markdown("##### Columns containing possible numeric pairs")
    if candidate_cols:
        st.write(candidate_cols)
    else:
        st.info("No obvious numeric‑pair columns detected. You may still select manually.")

    st.markdown("##### Select columns to split")
    selected = st.multiselect(
        "Columns to split",
        options=list(df.columns),
        default=candidate_cols
    )

    st.markdown("##### New column suffixes")
    c1, c2 = st.columns(2)
    suffix1 = c1.text_input("Suffix for first value", value="A")
    suffix2 = c2.text_input("Suffix for second value", value="B")

    st.markdown("---")
    apply_now = st.button("Split Columns", type="primary")

    if apply_now:
        return {
            "columns": selected,
            "new_col_suffixes": (suffix1, suffix2)
        }
