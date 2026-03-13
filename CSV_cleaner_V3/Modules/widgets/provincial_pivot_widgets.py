import streamlit as st

def provincial_pivot_widget(df):
    """
    Widget for collecting all user inputs required for the Provincial Chemistry Pivot.

    Supports:
        - selecting the variable column
        - selecting the value column
        - optionally merging metadata columns into the final header names
        - auto-detection of likely variable/value columns
        - one-shot trigger pattern for consistent UX

    Returns
    -------
    dict or None
        {
            "var_col": str,
            "value_col": str,
            "additional_params": list[str] or None
        }
        or None if the user has not completed the widget.
    """

    st.markdown("""
    This tool restructures provincial chemistry files where:
    - one column contains **variable/parameter names**
    - another contains **values**

    Each variable becomes its own column, and optional metadata (e.g., Units, VMV codes)
    can be merged into the header names.
    """)

    # ---------------------------------------------------------
    # Remove unnamed or empty columns (common in CSV exports)
    # ---------------------------------------------------------
    df = df.loc[:, ~df.columns.str.contains("^Unnamed", case=False)]

    # Normalize column names to strings
    cols = [str(c) for c in df.columns]

    # ---------------------------------------------------------
    # Auto-detect likely variable and value columns
    # ---------------------------------------------------------
    variable_keywords = ["variable", "parameter", "name"]
    value_keywords = ["value", "result"]
    exclude_keywords = ["code", "unit"]

    def find_variable_index():
        # Prefer columns with variable keywords and no exclude keywords
        for i, col in enumerate(cols):
            col_lower = col.lower()
            if any(k in col_lower for k in variable_keywords) and not any(e in col_lower for e in exclude_keywords):
                return i

        # Fallback: first non-code/unit column
        for i, col in enumerate(cols):
            if not any(e in col.lower() for e in exclude_keywords):
                return i

        return 0

    def find_value_index():
        for i, col in enumerate(cols):
            if any(k in col.lower() for k in value_keywords):
                return i
        return 0

    var_default = find_variable_index()
    val_default = find_value_index()

    # ---------------------------------------------------------
    # 1. Select variable + value columns
    # ---------------------------------------------------------
    st.markdown("#### 1. Select the Variable and Value columns")

    c1, c2 = st.columns(2)
    var_col = c1.selectbox("Variable column", cols, index=var_default)
    value_col = c2.selectbox("Value column", cols, index=val_default)

    # ---------------------------------------------------------
    # 2. Optional metadata merging
    # ---------------------------------------------------------
    st.markdown("#### 2. Add metadata to the variable header names (optional)")
    st.caption("For example: `Temperature_degC_567`")

    metadata_keywords = [
        "unit", "units",
        "vmv", "vmv_code",
        "variable_code", "code",
        "method", "method_code"
    ]

    metadata_options = [col for col in cols if col != var_col]

    default_meta = [
        col for col in metadata_options
        if any(k in col.lower() for k in metadata_keywords)
    ]

    add_meta = st.radio(
        "Merge metadata columns into the variable header?",
        ["No", "Yes"],
        horizontal=True
    )

    additional_params = None
    if add_meta == "Yes":
        additional_params = st.multiselect(
            "Select metadata columns to merge",
            metadata_options,
            default=default_meta
        )

        # Prevent variable column from being metadata
        if var_col in additional_params:
            st.error("The variable column cannot also be used as metadata. Please remove it.")
            return None

        # Validate metadata columns
        additional_params = [p for p in additional_params if p in df.columns]

    # ---------------------------------------------------------
    # 3. Final confirmation button
    # ---------------------------------------------------------
    st.markdown("---")
    apply_now = st.button("Apply Pivot", type="primary")

    if apply_now:
        return {
            "var_col": var_col,
            "value_col": value_col,
            "additional_params": additional_params
        }

    return None
