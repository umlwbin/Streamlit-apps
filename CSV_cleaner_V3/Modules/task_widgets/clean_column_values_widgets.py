import streamlit as st

def clean_column_values_widgets(df):
    """
    Widget for selecting a column whose values will be cleaned by removing
    all non‑alphanumeric characters (except - and .).
    """

    cols = df.columns.tolist()

    left, right = st.columns([0.8, 0.2])

    # ---------------------------------------------------------
    # 1. Column selection
    # ---------------------------------------------------------
    column_to_clean = left.selectbox(
        label="**Select a column to clean**",
        options=cols,
        key="clean_column_select"
    )

    # ---------------------------------------------------------
    # 2. Soft validation
    # ---------------------------------------------------------
    if df[column_to_clean].isna().all():
        left.warning( f"Column **{column_to_clean}** contains only missing values.",icon="⚠️")

    # Detect non-string values (common in numeric columns)
    # if not df[column_to_clean].dtype == "object":
    #     left.info(f"Column **{column_to_clean}** is not text. "
    #               "Values will be converted to strings before cleaning."
    #     )

    # Show a preview of the first few raw values
    sample = df[column_to_clean].head(5).astype(str).tolist()
    left.write("Preview of raw values:")
    left.code("\n".join(sample))

    # ---------------------------------------------------------
    # 3. One‑shot trigger button
    # ---------------------------------------------------------
    left.button("Next", type="primary", key="cleanColumnNext_WidgetKey")

    triggered = st.session_state.get("cleanColumnNext_WidgetKey", False)

    if triggered:

        # Hard validation
        if not column_to_clean:
            left.error("Please select a column to clean.", icon="🚨")
            return None

        # SUCCESS --> Return kwargs
        return {"column": column_to_clean}

    return None
