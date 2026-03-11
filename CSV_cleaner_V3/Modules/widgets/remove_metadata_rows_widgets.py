import streamlit as st
import pandas as pd

def remove_metadata_rows_widget(df):
    """
    Widget for:
      • collecting header identifiers
      • previewing metadata rows
      • letting the user extract metadata values into new columns
      • requiring a 'Next' button before returning extraction instructions
    """

    st.write("##### Step 1 - Identify the true header row")
    st.write("Enter three column names that appear in the real header row.")

    col1, col2, col3 = st.columns(3)
    with col1:
        id1 = st.text_input("Header name 1", "")
    with col2:
        id2 = st.text_input("Header name 2", "")
    with col3:
        id3 = st.text_input("Header name 3", "")

    identifiers = [id1.strip(), id2.strip(), id3.strip()]

    if any(x == "" for x in identifiers):
        st.info("Enter all three header names to continue.")
        return None

    # ---------------------------------------------------------
    # Detect metadata rows
    # ---------------------------------------------------------
    df_str = df.astype(str).applymap(lambda x: x.strip().lower())
    header_index = None

    for idx, row in df_str.iterrows():
        row_values = set(row.tolist())
        if all(identifier.lower() in row_values for identifier in identifiers):
            header_index = idx
            break

    if header_index is None:
        st.error("Could not detect header row with these identifiers.")
        return None

    metadata_df = df.iloc[:header_index].copy()

    # ---------------------------------------------------------
    # Step 2 — Show metadata preview BEFORE extraction
    # ---------------------------------------------------------
    st.write("##### Step 2 — Metadata rows detected above the header")
    st.dataframe(metadata_df)

    st.write("You can extract values from these metadata rows into new columns.")

    # ---------------------------------------------------------
    # Step 3 — Let the user define metadata extractions
    # ---------------------------------------------------------
    st.write("##### Step 3 — Extract metadata into new columns")

    metadata_extract = {}

    for row_idx in range(len(metadata_df)):
        row = metadata_df.iloc[row_idx]
        non_empty = [cell for cell in row.tolist() if str(cell).strip() != ""]

        if not non_empty:
            continue  # skip empty rows

        with st.expander(f"Metadata row {row_idx}", expanded=False):
            st.write("Row contents:")
            st.code(non_empty)

            st.write("You can extract multiple values from this row.")

            # Allow up to 3 extractions per row
            for extract_i in range(3):
                st.markdown(f"**Extraction #{extract_i+1}**")

                selected_value = st.selectbox(
                    f"Select value to extract (row {row_idx})",
                    options=["(none)"] + non_empty,
                    key=f"value_select_{row_idx}_{extract_i}"
                )

                if selected_value == "(none)":
                    continue

                # Editable version of the selected value
                edited_value = st.text_input(
                    "Edit extracted value (optional)",
                    value=selected_value,
                    key=f"edited_value_{row_idx}_{extract_i}"
                )

                st.info(f"Final value to extract: **{edited_value}**")

                new_col = st.text_input(
                    f"New column name for this value",
                    key=f"newcol_{row_idx}_{extract_i}"
                )

                if new_col.strip() != "":
                    metadata_extract[new_col] = {
                        "row": row_idx,
                        "col_index": non_empty.index(selected_value),
                        "edit": edited_value if edited_value != selected_value else None
                    }
                    st.success(f"Will extract: **{edited_value}** → column **{new_col}**")

    # ---------------------------------------------------------
    # Step 4 — Require a Next button before returning
    # ---------------------------------------------------------
    proceed = st.button("Next", type="primary")

    if not proceed:
        return None

    # ---------------------------------------------------------
    # Final return
    # ---------------------------------------------------------
    return {
        "identifiers": identifiers,
        "metadata_extract": metadata_extract
    }
