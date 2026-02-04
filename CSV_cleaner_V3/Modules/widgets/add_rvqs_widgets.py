import streamlit as st
import pandas as pd
from Modules.cleaning_tasks.add_rvqs import detect_numeric_majority_columns


def render(df):
    st.markdown(
        "RVQs help identify values that are missing, unusual, or flagged by "
        "instrument codes. This tool scans selected variables and inserts "
        "a new `<variable>_RVQ` column beside each one."
    )

    # ---------------------------------------------------------
    # RVQ reference table
    # ---------------------------------------------------------
    with st.expander("See list of RVQ codes and meanings"):
        try:
            rvq_df = pd.read_csv("rvq_dict.csv")
            st.table(rvq_df)
        except Exception:
            st.info("RVQ dictionary file not found (rvq_dict.csv).")

    # ---------------------------------------------------------
    # Step 1 — Select measured variables
    # ---------------------------------------------------------
    st.markdown("### 1. Select variables to scan for RVQ codes")

    detected = detect_numeric_majority_columns(df)

    selected_cols = st.multiselect(
        "Measured variables",
        options=list(df.columns),
        default=detected,
        help="These columns appear to be mostly numeric. Adjust as needed.",
        key="rvq_select_columns"
    )

    if selected_cols:
        st.info(f"Selected **{len(selected_cols)}** variable(s).")

    # ---------------------------------------------------------
    # Step 2 — Define RVQ rules
    # ---------------------------------------------------------
    st.markdown("### 2. Define RVQ rules")

    # ---------------------------------------------------------
    # Guidance expander
    # ---------------------------------------------------------
    with st.expander("How to enter RVQ rules"):
        st.markdown("""
        **Examples**

        • A data code **9999** may represent the RVQ **ND** (Not Detected).  
        • To associate **empty data cells** with an RVQ, use **nan** as the Data Code.

        **Detection Limits**
        - To capture detection limits, enter the starting letter (or number) before the actual limit.
        - Example: **L0.4** means the detection limit is **0.4** (Below Detection Limit).
          Enter **L** as the Data Code and **BDL** as the RVQ.
        """)

    # ---------------------------------------------------------
    # 2A — Negative number rule (now inside RVQ rules section)
    # ---------------------------------------------------------
    st.markdown("#### 2A. Negative Number Rule (Optional)")

    negative_rule_enabled = st.checkbox(
        "Flag **any negative number** as an RVQ",
        key="rvq_negative_rule"
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
            options=selected_cols,   # <-- ONLY measured variables
            help="Temperature, depth, elevation, etc.",
            key="rvq_negative_exceptions"
        )

    # ---------------------------------------------------------
    # 2B — Manual RVQ rules
    # ---------------------------------------------------------
    st.markdown("#### 2B. Manual RVQ Rules")

    rules = []
    for i in range(5):
        cols = st.columns([2, 2, 2])

        data_code = cols[0].text_input(
            f"Data code {i+1}",
            key=f"rvq_code_{i}",
            placeholder="e.g., -999 or L",
        )

        rvq_code = cols[1].text_input(
            f"RVQ {i+1}",
            key=f"rvq_rvq_{i}",
            placeholder="e.g., NC or BDL",
        )

        match_type = cols[2].selectbox(
            f"Match type {i+1}",
            ["full", "prefix", "suffix", "contains"],
            key=f"rvq_match_{i}",
        )

        if data_code and rvq_code:
            rules.append(
                {
                    "data_code": data_code,
                    "rvq_code": rvq_code,
                    "match_type": match_type,
                }
            )

    # ---------------------------------------------------------
    # Step 3 — Output Options
    # ---------------------------------------------------------
    st.markdown("### 3. Output Options")

    keep_original = st.radio(
        "Keep original data codes in the data column?",
        ["Yes", "No"],
        horizontal=True,
        key="rvq_keep_original"
    )

    remove_empty_rvq_cols = st.checkbox(
        "Remove RVQ columns that contain no RVQ values",
        key="rvq_remove_empty_cols"
    )

    # ---------------------------------------------------------
    # Step 4 — NEXT BUTTON
    # ---------------------------------------------------------
    st.markdown("---")
    st.button("Next", type="primary", key="rvq_next_button")

    if not st.session_state.get("rvq_next_button"):
        return None

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    if not selected_cols:
        st.error("Please select at least one variable to scan.", icon="🚨")
        return None

    if not rules and not negative_rule_enabled:
        st.error(
            "Please enter at least one RVQ rule, or enable the negative number rule.",
            icon="🚨"
        )
        return None

    if negative_rule_enabled and not negative_rvq_code:
        st.error("Please select an RVQ code for negative values.", icon="🚨")
        return None

    # Pre-scan for matches
    found_any = False

    # Check manual rules
    for col in selected_cols:
        series = df[col].astype(str)
        for rule in rules:
            code = rule["data_code"]
            match = rule["match_type"]

            if match == "full":
                mask = series == code
            elif match == "prefix":
                mask = series.str.startswith(code)
            elif match == "suffix":
                mask = series.str.endswith(code)
            elif match == "contains":
                mask = series.str.contains(code, na=False)
            else:
                mask = False

            if mask.any():
                found_any = True
                break

    # Check negative rule
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
    # SUCCESS → Return parameters
    # ---------------------------------------------------------
    return {
        "columns": selected_cols,
        "rules": rules,
        "keep_original": (st.session_state["rvq_keep_original"] == "Yes"),
        "negative_rule_enabled": negative_rule_enabled,
        "negative_rvq_code": negative_rvq_code,
        "negative_exceptions": negative_exceptions,
        "remove_empty_rvq_cols": remove_empty_rvq_cols,
    }
