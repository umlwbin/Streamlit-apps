import streamlit as st

def which_cols_widgets(df):
    st.markdown("##### Select one or more columns to remove from your dataset.")

    left, right = st.columns([0.8, 0.2])

    cols = df.columns
    variables_to_remove = left.multiselect(
        label="Columns to remove",
        options=list(cols),
        key="remove_cols_select"
    )

    # Show count
    if variables_to_remove:
        left.info(f"Selected **{len(variables_to_remove)}** column(s).")

    # Warn if user selects all columns
    if variables_to_remove and len(variables_to_remove) == len(cols):
        left.warning("You have selected **all** columns. This will produce an empty dataset.")

    # One-shot trigger
    left.button("Next", type="primary", key="removeColsNext_WidgetKey")

    # Handle trigger
    if st.session_state.get("removeColsNext_WidgetKey"):
        if not variables_to_remove:
            left.error("Please select at least one column to remove.", icon="🚨")
            return None

        return {"variables_to_remove": variables_to_remove}