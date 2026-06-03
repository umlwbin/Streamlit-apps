import streamlit as st
import pandas as pd
from Modules.utils.ui_utils import big_caption


# ---------------------------------------------------------
# Helper: Detect numeric-majority columns
# ---------------------------------------------------------
def detect_numeric_majority_columns(df, threshold=0.6):
    """
    Identify columns where at least 60% of the non-null values
    are interpreted as numeric. Used to auto-suggest RVQ candidates.
    """
    numeric_cols = []
    for col in df.columns:
        series = df[col]

        # Ignore NaNs entirely
        non_null = series.dropna()

        if len(non_null) == 0:
            continue

        # Attempt numeric conversion
        numeric = pd.to_numeric(non_null, errors="coerce")

        # Ratio of numeric values among non-null entries
        ratio = numeric.notna().mean()

        if ratio >= threshold:
            numeric_cols.append(col)

    return numeric_cols



def add_rvqs_widget(df):
    """
    Widget for configuring RVQ (Result Validation/Qualification) rules.
    """

    # =========================================================
    # INTRO
    # =========================================================
    st.markdown(
        "RVQs help to identify values that are missing, unusual, or flagged by "
        "instrument codes. \n\nThis tool inserts a new `<variable>_RVQ` column "
        "beside each selected variable."
    )

    # =========================================================
    # RVQ REFERENCE TABLE
    # =========================================================
    with st.expander("ℹ️ RVQ Codes and Meanings"):
        try:
            rvq_df = pd.read_csv("rvq_dict.csv")
            st.table(rvq_df)
        except Exception:
            st.info("RVQ dictionary file not found (rvq_dict.csv).")

    # =========================================================
    # STEP 1 - SELECT VARIABLES
    # =========================================================
    st.write(" ")
    st.write("#### 1. Select variables to scan")

    # 1A - Auto-detect numeric-majority columns
    detected = detect_numeric_majority_columns(df)

    # 1B - Auto-exclude common metadata/time/coordinate columns
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

    # 1C - Allow curator to clear auto-detected list
    clear_auto = st.checkbox("Clear all auto-detected numeric columns", help="Useful if you only want to add a few columns manually.")

    # 1D - Multiselect for final selection
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

    # =========================================================
    # STEP 2 - DEFINE RVQ RULES
    # =========================================================
    st.write(" ")
    st.write("#### 2. Define RVQ rules")

    # ---------------------------------------------------------
    # 2A - NEGATIVE NUMBER RULE
    # ---------------------------------------------------------
    st.write("##### 2A. Negative Number Rule (Optional)")

    negative_rule_enabled = st.checkbox(
        "Flag any negative number as an RVQ", key="rvq_negative_rule",disabled=(len(selected_cols) == 0))

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
    # 2B - MANUAL RULES
    # ---------------------------------------------------------
    st.write(" ")
    st.write("##### 2B. Manual RVQ Rules")

    with st.expander("ℹ️ How to enter RVQ rules"):
        st.markdown("""
        **Examples**

        • Data code: `9999` → RVQ code: `ND`, Match type:`Full`  
        • To add an RVQ for Empty or NaN cells → use data code `nan` (literally, just  type `nan`)          
        • Detection limits examples:  
          - For a case where `L0.5` means below detection limit (BDL) of 0.5
            - Enter `L` as the Data Code and `BDL` as the RVQ code , with match type `Contains`
        """)

    rules = []

    # Up to 20 rules
    for i in range(20):
        cols3 = st.columns([2, 2, 2])

        data_code = cols3[0].text_input(
            f"Data code {i+1}",
            key=f"rvq_code_{i}",
            placeholder="e.g., < or -1 or L",
        )

        rvq_code = cols3[1].text_input(
            f"RVQ {i+1}",
            key=f"rvq_rvq_{i}",
            placeholder="e.g., BDL or NC",
        )

        match_type = cols3[2].selectbox(
            f"Match type {i+1}",
            ["contains", "full"],
            key=f"rvq_match_{i}",
        )

        if data_code and rvq_code:
            rules.append({
                "data_code": data_code,
                "rvq_code": rvq_code,
                "match_type": match_type,
            })

    # =========================================================
    # STEP 3 - OUTPUT OPTIONS
    # =========================================================
    st.write(" ")
    st.write("#### 3. Output Options")
    st.write("##### Keep the data codes in the measured variable columns? ")
    big_caption("Selecting <b>No</b> will remove the data code from your measured variable columns (recommended).")

    keep_original = st.radio(
        "Keep original data codes?",
        ["No", "Yes"],
        horizontal=True,
        key="rvq_keep_original"
    )

    # =========================================================
    # STEP 4 - EXECUTE-ONCE TRIGGER
    # =========================================================
    st.markdown("---")

    if st.button("Next", type="primary"):
        st.session_state.rvq_trigger = True

    triggered = st.session_state.get("rvq_trigger", False)
    st.session_state.rvq_trigger = False

    if not triggered:
        return None

    # =========================================================
    # VALIDATION (soft - widget only)
    # =========================================================

    if not selected_cols:
        st.error("Please select at least one variable to scan.")
        return None

    if not rules and not negative_rule_enabled:
        st.error("Please enter at least one RVQ rule, or enable the negative number rule.")
        return None

    if negative_rule_enabled and not negative_rvq_code:
        st.error("Please select an RVQ code for negative values.")
        return None

    # Pre-scan for matches (curator feedback)
    found_any = False

    # Manual rules
    for col in selected_cols:
        series = df[col].astype(str)
        for rule in rules:
            code = rule["data_code"]
            match = rule["match_type"]

            if match == "full":
                mask = series == code
            else:
                mask = series.str.contains(code, na=False)

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
            "Try adjusting the match type."
        )
        return None

    # =========================================================
    # SUCCESS - RETURN KWARGS FOR TASK
    # =========================================================
    return {
        "columns": selected_cols,
        "rules": rules,
        "keep_original": (keep_original == "Yes"),
        "negative_rule_enabled": negative_rule_enabled,
        "negative_rvq_code": negative_rvq_code,
        "negative_exceptions": negative_exceptions,
    }
