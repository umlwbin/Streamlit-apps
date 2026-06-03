import streamlit as st
import pandas as pd
from Modules.utils.ui_utils import big_caption


def remove_metadata_rows_widget(df):
    """
    Widget for:
        - collecting header identifiers
        - detecting metadata rows above the true header
        - previewing metadata rows
        - allowing the user to extract metadata values into new columns
        - returning extraction instructions only after an execute-once trigger
    """

    # ---------------------------------------------------------
    # Step 1 - Identify the true header row
    # ---------------------------------------------------------
    st.write("#### Step 1 - Identify the true header row")
    big_caption("Enter three column names that appear in the real header row.")

    c1, c2, c3 = st.columns(3)
    id1 = c1.text_input("Header name 1", "")
    id2 = c2.text_input("Header name 2", "")
    id3 = c3.text_input("Header name 3", "")

    identifiers = [id1.strip(), id2.strip(), id3.strip()]

    # Soft validation
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
        st.error("Could not detect a header row with these identifiers.")
        return None

    metadata_df = df.iloc[:header_index].copy()

    # Soft validation: no metadata rows
    if metadata_df.empty:
        st.warning("No metadata rows found above the detected header.")
        # Still allow user to continue - they may only want header promotion

    # ---------------------------------------------------------
    #  Preview metadata rows
    # ---------------------------------------------------------
    st.write(" ")
    st.write("##### Metadata rows detected above the header")
    st.dataframe(metadata_df)
    big_caption("You may extract values from these metadata rows into new columns.")

    # ---------------------------------------------------------
    # Step 2 - Define metadata extractions
    # ---------------------------------------------------------
    st.write(" ")
    st.write("#### Step 2 - Extract metadata into new columns (optional)")
    st.markdown("✎ From each metadata row, as shown in the preview above, you can extract a parameter "
                "from one of the cells in that row.")
    
    st.markdown("✎ You can apply optional cleaning rules for the extracted parameter - we recommend stripping leading/trailing whitespace.")

    st.markdown("✎ Next, **add the name of the new column** under which the extracted metadata parameter will live.")

    st.markdown("For e.g., if the filename you want to extract from the metadata row is `weather_data_2024.csv`, then you could create a column called **Filename**. " \
    "`weather_data_2024.csv` will be populated right throughout the column.")
     

    metadata_extract = {}
    used_new_cols = set()

    for row_idx in range(len(metadata_df)):
        row = metadata_df.iloc[row_idx]
        non_empty = [cell for cell in row.tolist() if str(cell).strip() != ""]

        if not non_empty:
            continue

        with st.expander(f"Metadata row {row_idx}", expanded=False):
            st.write("Row contents:")
            st.code(non_empty)

            st.write("You may extract multiple values from this row.")

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

                # Cleaning rules
                st.markdown("**Cleaning rules**")

                strip_ws = st.checkbox(
                    "Strip leading/trailing whitespace",
                    value=True,
                    key=f"strip_ws_{row_idx}_{extract_i}"
                )

                remove_dir = st.checkbox(
                    "Remove direction letters (N, S, E, W)",
                    value=False,
                    key=f"remove_dir_{row_idx}_{extract_i}"
                )

                remove_deg = st.checkbox(
                    "Remove degree symbol (°)",
                    value=False,
                    key=f"remove_deg_{row_idx}_{extract_i}"
                )

                # New column name
                new_col = st.text_input(
                    "New column name",
                    key=f"newcol_{row_idx}_{extract_i}"
                ).strip()

                # Warn if user selected a value but did not enter a column name
                if selected_value != "(none)" and new_col == "":
                    st.warning("You selected a value to extract, but did not enter a new column name.", icon="⚠️")

                # Soft validation when a column name is provided
                if new_col:
                    if new_col in used_new_cols:
                        st.error(f"Column name '{new_col}' is already used.", icon="🚨")
                        continue

                    used_new_cols.add(new_col)

                    metadata_extract[new_col] = {
                        "row": row_idx,
                        "col_index": non_empty.index(selected_value),
                        "rules": {
                            "strip_whitespace": strip_ws,
                            "remove_direction": remove_dir,
                            "remove_degree_symbol": remove_deg,
                        }
                    }

                    st.success(f"Will extract **{selected_value}** → **{new_col}** (rules applied)")


    # ---------------------------------------------------------
    # Step 4 - Execute-once trigger button
    # ---------------------------------------------------------
    if st.button("Next", type="primary"):
        st.session_state.remove_metadata_trigger = True

    triggered = st.session_state.get("remove_metadata_trigger", False)
    st.session_state.remove_metadata_trigger = False

    if not triggered:
        return None

    # ---------------------------------------------------------
    # Final return
    # ---------------------------------------------------------
    return {
        "identifiers": identifiers,
        "metadata_extract": metadata_extract
    }
