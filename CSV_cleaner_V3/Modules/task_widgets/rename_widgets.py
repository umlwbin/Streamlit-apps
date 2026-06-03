import streamlit as st
from Modules.utils.ui_utils import big_caption


def rename_widgets(df):
    """
    Widget for renaming columns in the dataset.
    """

    big_caption("Edit the names below. Duplicate names will be auto-numbered during processing.")

    cols = df.columns.tolist()
    new_names = []

    left, right = st.columns([0.7, 0.3])

    # ---------------------------------------------------------
    # Step 1 - Collect new names
    # ---------------------------------------------------------
    for c in cols:
        new_name = left.text_input(
            label=f"Rename '{c}' to:",
            value=c,
            key=f"rename_{c}"
        )
        new_names.append(new_name)

    # ---------------------------------------------------------
    # Step 2 - Soft validation feedback
    # ---------------------------------------------------------
    if len(new_names) != len(set(new_names)):
        left.warning("Duplicate column names detected - duplicates will be auto-numbered.", icon="⚠️")

    if any(n.strip() == "" for n in new_names):
        left.error("Column names cannot be empty.", icon="🚨")

    # ---------------------------------------------------------
    # Step 3 - Execute-once trigger button
    # ---------------------------------------------------------
    if left.button("Next", type="primary"):
        st.session_state.rename_trigger = True

    triggered = st.session_state.get("rename_trigger", False)
    st.session_state.rename_trigger = False

    if not triggered:
        return None

    # ---------------------------------------------------------
    # Step 4 - Final validation before returning
    # ---------------------------------------------------------
    if any(n.strip() == "" for n in new_names):
        left.error("Please fix empty column names before continuing.", icon="🚨")
        return None

    # ---------------------------------------------------------
    # Step 5 - Return standardized names
    # ---------------------------------------------------------
    return {"standardized_names": new_names}
