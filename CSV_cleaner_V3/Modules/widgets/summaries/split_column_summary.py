import streamlit as st

def render_split_column_summary(summary):
    col = summary.get("column")
    new_cols = summary.get("new_columns", [])
    delims = summary.get("delimiters", [])
    rows = summary.get("rows_split", 0)

    st.success("Split Column")

    st.write(f"**Column:** {col}")
    st.write(f"**Delimiters:** {', '.join(delims)}")
    st.write(f"**Rows split:** {rows}")

    if new_cols:
        st.write("**New columns created:** " + ", ".join(new_cols))
    else:
        st.info("No new columns were created.")
