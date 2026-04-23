import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# Helper: Detect numeric-majority columns
# ---------------------------------------------------------
def detect_numeric_majority_columns(df, threshold=0.6):
    numeric_cols = []
    for col in df.columns:
        series = df[col]

        # Ignore NaNs entirely
        non_null = series.dropna()

        # If the column is all NaN, skip it
        if len(non_null) == 0:
            continue

        # Try converting remaining values to numeric
        numeric = pd.to_numeric(non_null, errors="coerce")

        # Compute ratio of numeric values among non-null values
        ratio = numeric.notna().mean()

        if ratio >= threshold:
            numeric_cols.append(col)

    return numeric_cols




def add_rvqs_widget(df):
    """
    Widget for configuring RVQ (Result Validation/Qualification) rules.

    Returns
    -------
    dict or None
        {
            "columns": [...],
            "rules": [...],
            "keep_original": bool,
            "negative_rule_enabled": bool,
            "negative_rvq_code": str or None,
            "negative_exceptions": [...]
        }
        or None if the user has not completed the widget.
    """

    st.markdown(
        "RVQs help identify values that are missing, unusual, or flagged by "
        "instrument codes. This tool scans selected variables and inserts "
        "a new `<variable>_RVQ` column beside each one."
    )

    # ---------------------------------------------------------
    # RVQ reference table
    # ---------------------------------------------------------
    with st.expander("**ℹ️ See list of RVQ codes and meanings**"):
        try:
            rvq_df = pd.read_csv("rvq_dict.csv")
            st.table(rvq_df)
        except Exception:
            st.info("RVQ dictionary file not found (rvq_dict.csv).")

    # ---------------------------------------------------------
    # Step 1 - Select measured variables
    # ---------------------------------------------------------
    st.markdown("#### 1. Select variables to scan for RVQ codes")

    # a) - detect numeric-majority columns
    detected = detect_numeric_majority_columns(df)

    # b) - auto-exclude patterns
    AUTO_EXCLUDE_PATTERNS = [
        "day", "month", "year",
        "date", "time", "datetime", "timestamp",
        "lat", "latitude", "lon", "long", "longitude",
        "coord", "xcoord", "ycoord",
        "easting", "northing",
        "station", "sample", "id",
    ]

    auto_excluded = []
    candidate_cols = []

    for col in detected:
        col_lower = col.lower()
        if any(pattern in col_lower for pattern in AUTO_EXCLUDE_PATTERNS):
            auto_excluded.append(col)
        else:
            candidate_cols.append(col)


    # c) - option to clear auto-detected numeric columns
    clear_auto = st.checkbox(
        "Clear all auto-detected numeric columns",
        help="Useful if you only want to add a few columns manually."
    )

    # d) - multiselect
    default_selection = [] if clear_auto else candidate_cols

    selected_cols = st.multiselect(
        "Select columns to apply RVQ rules:",
        options=list(df.columns),
        default=default_selection,
        help="These columns appear to be mostly numeric. Adjust as needed.",
        key="rvq_select_columns"
    )


    if selected_cols:
        st.info(f"Selected **{len(selected_cols)}** variable(s).")


    # ---------------------------------------------------------
    # Step 2 - Define RVQ rules
    # ---------------------------------------------------------
    st.markdown("#### 2. Define RVQ rules")

    with st.expander("**ℹ️ How to enter RVQ rules**"):
        st.markdown("""
        **Examples**

        • A data code **9999** may represent the RVQ **ND** (Not Detected).  
        • To associate **empty data cells or NaN cells** with an RVQ, use `'nan'` as the Data Code.

        **Detection Limits**
        - To capture detection limits, enter the starting letter (or number) before the actual limit.
        - Example: **L0.4** means the detection limit is **0.4** (Below Detection Limit).
          Enter **L** as the Data Code and **BDL** as the RVQ.
        """)

    # ---------------------------------------------------------
    # 2A - Negative number rule
    # ---------------------------------------------------------
    st.markdown("##### 2A. Negative Number Rule (Optional)")

    negative_rule_enabled = st.checkbox(
        "Flag any negative number as an RVQ",
        key="rvq_negative_rule",
        disabled=(len(selected_cols) == 0)
    )

    negative_rvq_code = None
    negative_exceptions = []

    if negative_rule_enabled:
        negative_rvq_code = st.selectbox(
            "RVQ code to assign to negative values",
            options=["BDL", "ADL", "ND", "NC", "FD", "LD", "EFAI", "FEF", "FEQ", "FFB", "FFD", "FFS"],
            key="rvq_negative_code"
        )

        negative_exceptions = st.multiselect(
            "Exceptions (variables allowed to have negative values)",
            options=selected_cols,
            help="Temperature, depth, elevation, etc.",
            key="rvq_negative_exceptions"
        )

    # ---------------------------------------------------------
    # 2B - Manual RVQ Rules (simplified to full/contains)
    # ---------------------------------------------------------
    st.markdown("##### 2B. Manual RVQ Rules")

    st.markdown("""
    Enter a **Data Code**, an **RVQ Code**, and choose whether the match should be:

    - **Full** - the entire cell must **equal** the data code  
        - Example: data code `-1` matches only cells that are exactly `-1`  
        - Detection limit is extracted from the numeric part of the code itself  

    - **Contains** - the data code appears anywhere in the cell  
        - Example: data code `<` matches `<2`, `ND<1`, `value<3stuff`  
        - Detection limit is extracted from any number in the cell  
    """)

    rules = []
    for i in range(43):
        cols = st.columns([2, 2, 2])

        data_code = cols[0].text_input(
            f"Data code {i+1}",
            key=f"rvq_code_{i}",
            placeholder="e.g., < or -1 or L",
        )

        rvq_code = cols[1].text_input(
            f"RVQ {i+1}",
            key=f"rvq_rvq_{i}",
            placeholder="e.g., BDL or NC",
        )

        match_type = cols[2].selectbox(
            f"Match type {i+1}",
            ["contains", "full" ],
            key=f"rvq_match_{i}",
        )

        if data_code and rvq_code:
            rules.append({
                "data_code": data_code,
                "rvq_code": rvq_code,
                "match_type": match_type,
            })

    # ---------------------------------------------------------
    # Step 3 - Output Options
    # ---------------------------------------------------------
    st.markdown("#### 3. Output Options")
    st.markdown("Keep original data codes in the data column? \n\n"
    "(Selecting `No` will remove the data code from your measured variable columns - recommended)")

    keep_original = st.radio(
        " Select ",
        ["No", "Yes"],
        horizontal=True,
        key="rvq_keep_original"
    )

    # ---------------------------------------------------------
    # Step 4 - NEXT BUTTON
    # ---------------------------------------------------------
    st.markdown("---")
    st.button("Next", type="primary", key="rvq_next_button")

    if not st.session_state.get("rvq_next_button"):
        return None

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    if not selected_cols:
        st.error("Please select at least one variable to scan.")
        return None

    if not rules and not negative_rule_enabled:
        st.error(
            "Please enter at least one RVQ rule, or enable the negative number rule."
        )
        return None

    if negative_rule_enabled and not negative_rvq_code:
        st.error("Please select an RVQ code for negative values.")
        return None

    # Pre-scan for matches
    found_any = False

    # Manual rules
    for col in selected_cols:
        series = df[col].astype(str)
        for rule in rules:
            code = rule["data_code"]
            match = rule["match_type"]

            if match == "full":
                mask = series == code
            elif match == "contains":
                mask = series.str.contains(code, na=False)
            else:
                mask = False


            if mask.any():
                found_any = True
                break

    # Negative rule
    if negative_rule_enabled:
        for col in selected_cols:
            if col not in negative_exceptions:
                numeric = pd.to_numeric(df[col], errors="coerce")
                if (numeric < 0).any():
                    found_any = True
                    break

    if not found_any:
        st.warning(
            "None of the entered data codes or negative values were found in the selected columns. "
            "Try adjusting the match type (full, prefix, suffix, contains)."
        )
        return None

    # ---------------------------------------------------------
    # SUCCESS -> Return kwargs
    # ---------------------------------------------------------
    return {
        "columns": selected_cols,
        "rules": rules,
        "keep_original": (keep_original == "Yes"),
        "negative_rule_enabled": negative_rule_enabled,
        "negative_rvq_code": negative_rvq_code,
        "negative_exceptions": negative_exceptions,
    }
