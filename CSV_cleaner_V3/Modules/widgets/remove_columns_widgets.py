import streamlit as st

def remove_columns_widgets(df):
    """
    Widget for selecting one or more columns to remove from the dataset.

    Supports:
        - multiselect of columns
        - warning when all columns are selected
        - one-shot trigger pattern for consistent UX

    Returns
    -------
    dict or None
        {
            "variables_to_remove": list[str]
        }
        or None if the user has not completed the widget.
    """

    st.markdown("##### Select one or more columns to remove from your dataset.")

    left, right = st.columns([0.8, 0.2])

    cols = df.columns.tolist()

    variables_to_remove = left.multiselect(
        label="Columns to remove",
        options=cols,
        key="remove_cols_select"
    )

    # ---------------------------------------------------------
    # Feedback
    # ---------------------------------------------------------
    if variables_to_remove:
        left.info(f"Selected **{len(variables_to_remove)}** column(s).")

    if variables_to_remove and len(variables_to_remove) == len(cols):
        left.warning("You have selected **all** columns. This will produce an empty dataset.")

    # ---------------------------------------------------------
    # One-shot trigger
    # ---------------------------------------------------------
    left.button("Next", type="primary", key="removeColsNext_WidgetKey")

    triggered = st.session_state.get("removeColsNext_WidgetKey", False)

    if triggered:

        # Validation
        if not variables_to_remove:
            left.error("Please select at least one column to remove.", icon="🚨")
            return None

        # SUCCESS → Return kwargs
        return {"variables_to_remove": variables_to_remove}

    return None
