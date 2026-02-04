import streamlit as st

def reshape_widgets(df):
    """
    Unified widget for reshaping data:
      • Transpose
      • Pivot wide → long (melt)
      • Pivot long → wide (pivot)
    Returns a dictionary of kwargs for reshape().
    """
    st.markdown("Choose how you want to transform your table.")

    # --- EXPLANATIONS -----------------------------------------------------
    with st.expander("What do these options mean?", expanded=False):
        st.markdown("""
    ##### 🔁 Transpose  
    Turns rows into columns and columns into rows.

    **Before (original):**

    | Col1 | Col2 | Col3 |
    |------|------|------|
    |  A   |  10  |  X   |
    |  B   |  20  |  Y   |

    **After (transposed):**

    | index | 0  | 1  |
    |-------|----|----|
    | Col1  | A  | B  |
    | Col2  | 10 | 20 |
    | Col3  | X  | Y  |


    ---

    ##### ↘️ Pivot Wide → Long (Melt)  
    Useful when you have **many measurement columns** and want to stack them into rows.

    **Before (wide):**

    | Site | Jan | Feb | Mar |
    |------|-----|-----|-----|
    | S1   |  5  |  7  |  9  |
    | S2   |  4  |  6  |  8  |

    **After (long):**

    | Site | Month | Value |
    |------|--------|--------|
    | S1   | Jan    |   5    |
    | S1   | Feb    |   7    |
    | S1   | Mar    |   9    |
    | S2   | Jan    |   4    |
    | S2   | Feb    |   6    |
    | S2   | Mar    |   8    |

    This is great when you want one row per measurement.


    ---

    ##### ↗️ Pivot Long → Wide  
    Useful when you have **one column that contains variable names** and you want to spread them into separate columns.

    **Before (long):**

    | Site | Month | Value |
    |------|--------|--------|
    | S1   | Jan    |   5    |
    | S1   | Feb    |   7    |
    | S1   | Mar    |   9    |
    | S2   | Jan    |   4    |
    | S2   | Feb    |   6    |
    | S2   | Mar    |   8    |

    **After (wide):**

    | Site | Jan | Feb | Mar |
    |------|-----|-----|-----|
    | S1   |  5  |  7  |  9  |
    | S2   |  4  |  6  |  8  |

    This is great when you want one row per site with multiple measurement columns.
        """)


    # --- OPERATION SELECTION ----------------------------------------------
    operation = st.radio(
        "Choose a reshape operation:",
        options=[
            "Transpose",
            "Pivot wide → long",
            "Pivot long → wide"
        ],
        key="reshape_operation"
    )

    cols = df.columns

    # =========================================================
    # TRANSPOSE
    # =========================================================
    if operation == "Transpose":
        st.info("This will flip your table so rows become columns and columns become rows.")

        with st.form("transpose_form"):
            submitted = st.form_submit_button("Transpose Data", type="primary")
            if submitted:
                return {"operation": "transpose"}

        return None

    # =========================================================
    # PIVOT WIDE → LONG
    # =========================================================
    if operation == "Pivot wide → long":
        st.markdown("#### Select columns to keep fixed (ID columns)")

        id_cols = st.multiselect(
            "ID columns (optional)",
            options=list(cols),
            key="reshape_id_cols"
        )

        # Auto-detect value columns
        default_value_cols = [c for c in cols if c not in id_cols] if id_cols else list(cols)

        value_cols = st.multiselect(
            "Value columns (to melt)",
            options=list(cols),
            default=default_value_cols,
            key="reshape_value_cols"
        )

        col1, col2 = st.columns(2)
        var_name = col1.text_input("Name for variable column", value="Variable")
        value_name = col2.text_input("Name for value column", value="Value")

        with st.form("wide_to_long_form"):
            submitted = st.form_submit_button("Pivot Wide → Long", type="primary")
            if submitted:

                if not value_cols:
                    st.error("Please select at least one value column.", icon="🚨")
                    return None

                return {
                    "operation": "wide_to_long",
                    "id_cols": id_cols,
                    "value_cols": value_cols,
                    "var_name": var_name,
                    "value_name": value_name
                }

        return None

    # =========================================================
    # PIVOT LONG → WIDE
    # =========================================================
    if operation == "Pivot long → wide":
        st.markdown("#### Select columns for pivoting")

        variable_col = st.selectbox(
            "Column containing variable names",
            options=list(cols),
            key="reshape_variable_col"
        )

        value_col = st.selectbox(
            "Column containing values",
            options=list(cols),
            key="reshape_value_col"
        )

        id_cols = st.multiselect(
            "ID columns (define unique rows)",
            options=[c for c in cols if c not in [variable_col, value_col]],
            key="reshape_id_cols_wide"
        )

        with st.form("long_to_wide_form"):
            submitted = st.form_submit_button("Pivot Long → Wide", type="primary")
            if submitted:

                if not variable_col or not value_col:
                    st.error("Please select both variable and value columns.", icon="🚨")
                    return None

                return {
                    "operation": "long_to_wide",
                    "variable_col": variable_col,
                    "value_col": value_col,
                    "id_cols": id_cols
                }

        return None