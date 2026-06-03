import streamlit as st
from Modules.utils.ui_utils import big_caption


def provincial_pivot_widget(df):
    """
    Widget for collecting user inputs for the Provincial Chemistry Pivot.
    """

    st.markdown("""
    This tool restructures provincial chemistry files where:
    - one column contains **variable/parameter names**
    - another contains **values**

    Each variable becomes its own column. \n\n Optional metadata (e.g., Units, VMV codes)
    can be merged into the header names first before pivoting.
    """)

    # ---------------------------------------------------------
    # 0. Clean column names (common CSV artifacts)
    # ---------------------------------------------------------
    df = df.loc[:, ~df.columns.str.contains("^Unnamed", case=False)]
    cols = [str(c) for c in df.columns]

    # ---------------------------------------------------------
    # 1. Auto-detect variable + value columns
    # ---------------------------------------------------------
    variable_keywords = ["variable", "parameter", "name"]
    value_keywords = ["value", "result"]
    exclude_keywords = ["code", "unit"]

    def find_variable_index():
        for i, col in enumerate(cols):
            col_lower = col.lower()
            if any(k in col_lower for k in variable_keywords) and not any(e in col_lower for e in exclude_keywords):
                return i
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
    # 2. Select variable + value columns
    # ---------------------------------------------------------
    st.markdown(" ")
    st.markdown("#### 1. Select the Variable and Value columns")

    c1, c2 = st.columns(2)
    var_col = c1.selectbox("Variable column", cols, index=var_default)
    value_col = c2.selectbox("Value column", cols, index=val_default)

    # ---------------------------------------------------------
    # Soft validation (curator-facing)
    # ---------------------------------------------------------
    if var_col == value_col:
        c1.error("Variable and Value columns must be different.", icon="🚨")
        return None

    if df[var_col].isna().all():
        c1.warning(f"Column **{var_col}** contains only missing values.", icon="⚠️")

    if df[value_col].isna().all():
        c2.warning(f"Column **{value_col}** contains only missing values.", icon="⚠️")

    # ---------------------------------------------------------
    # 3. Optional metadata merging
    # ---------------------------------------------------------
    st.markdown(" ")
    st.markdown("#### 2. Add metadata to the variable header names (optional)")

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
        "Merge metadata columns into the variable header? For example: `Temperature_degC_567`",
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

        # Soft validation
        if var_col in additional_params:
            st.error("The variable column cannot also be used as metadata.", icon="🚨")
            return None

        if any(df[p].isna().all() for p in additional_params):
            st.warning("One or more metadata columns contain only missing values.", icon="⚠️")

    # ---------------------------------------------------------
    # 4. One-shot trigger button
    # ---------------------------------------------------------
    st.markdown("---")
    if st.button("Apply Pivot", type="primary"):
        return {
            "var_col": var_col,
            "value_col": value_col,
            "additional_params": additional_params
        }

    return None
