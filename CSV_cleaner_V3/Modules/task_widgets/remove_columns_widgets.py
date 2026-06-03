import streamlit as st

def remove_columns_widgets(df):
    """
    Widget for selecting one or more columns to remove from the dataset.
    """

    cols = df.columns.tolist()

    left, right = st.columns([0.8, 0.2])

    # ---------------------------------------------------------
    # 1. Column selection
    # ---------------------------------------------------------
    variables_to_remove = left.multiselect(
        label="**Columns to remove**",
        options=cols,
        key="remove_cols_select"
    )

    # ---------------------------------------------------------
    # 2. Soft validation
    # ---------------------------------------------------------
    if variables_to_remove:
        left.info(f"Selected **{len(variables_to_remove)}** column(s).")

    if variables_to_remove and len(variables_to_remove) == len(cols):
        left.warning("You have selected **all** columns. This will produce an empty dataset.",icon="⚠️")

    # Detect columns that appear duplicated (rare but anything is possible 😅)
    if len(cols) != len(set(cols)):
        left.warning(
            "Your dataset contains duplicate column names. Removing one may affect multiple columns.", icon="⚠️" )

    # Detect if user selected a column that is entirely blank
    for col in variables_to_remove:
        if df[col].isna().all():
            left.warning(
                f"Column **{col}** contains only missing values.",icon="⚠️")

    # ---------------------------------------------------------
    # 3. Execute‑once trigger button
    # ---------------------------------------------------------
    left.button("Next", type="primary", key="removeColsNext_WidgetKey")

    triggered = st.session_state.get("removeColsNext_WidgetKey", False)

    if triggered:

        # Hard validation
        if not variables_to_remove:
            left.error("Please select at least one column to remove.", icon="🚨")
            return None

        # SUCCESS --> Return kwargs
        return {"variables_to_remove": variables_to_remove}

    return None
