import streamlit as st

def rename_widgets(df):
    """
    Widget for renaming columns in the dataset.

    Supports:
        - editing each column name individually
        - warning about duplicates (auto-numbered later by the task)
        - preventing empty column names
        - one-shot trigger pattern for consistent UX

    Returns
    -------
    dict or None
        {
            "standardized_names": list[str]
        }
        or None if the user has not completed the widget.
    """

    st.markdown("##### Enter the new names you want to use for each column.")

    new_names = []
    col1, col2 = st.columns(2)

    cols = df.columns.tolist()

    # ---------------------------------------------------------
    # Collect new names
    # ---------------------------------------------------------
    for c in cols:
        new_name = col1.text_input(
            label=f"Rename '{c}' to:",
            value=c,
            key=f"rename_{c}"
        )
        new_names.append(new_name)

    # ---------------------------------------------------------
    # Validation feedback
    # ---------------------------------------------------------
    if len(new_names) != len(set(new_names)):
        col1.warning("Duplicate column names detected - duplicates will be auto‑numbered.", icon="⚠️")

    if any(n.strip() == "" for n in new_names):
        col1.error("Column names cannot be empty.", icon="🚨")

    # ---------------------------------------------------------
    # Run
    # ---------------------------------------------------------
    col1.button("Next", type="primary", key="renameNext_WidgetKey")

    triggered = st.session_state.get("renameNext_WidgetKey", False)

    if triggered:

        # Final validation
        if any(n.strip() == "" for n in new_names):
            col1.error("Please fix empty column names before continuing.", icon="🚨")
            return None

        # SUCCESS → Return kwargs
        return {"standardized_names": new_names}

    return None
