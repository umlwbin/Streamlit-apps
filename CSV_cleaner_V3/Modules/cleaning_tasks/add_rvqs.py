import pandas as pd
import re


def apply_rvq_rules(
    df: pd.DataFrame,
    *,
    filename=None,
    columns,
    rules,
    keep_original=True,
    negative_rule_enabled=False,
    negative_rvq_code=None,
    negative_exceptions=None,
    remove_empty_rvq_cols=False
):
    """
    Apply RVQ (Result Value Qualifier) rules to selected columns.

    RVQs flag values that may be unusual, below detection limits, or otherwise
    require curator attention. Rules can match:
        - exact values ("full")
        - prefixes (e.g., "<", "<0.5")
        - suffixes
        - substrings ("contains")

    This task:
        • creates a new <column>_RVQ column beside each selected variable
        • applies user‑defined RVQ rules
        • optionally applies a negative‑value rule
        • extracts detection limits from prefix and negative rules
        • optionally removes empty RVQ columns
        • stores a long‑form detection‑limit table in
        st.session_state.supplementary_outputs
        • returns only the cleaned DataFrame and a summary dictionary

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset.

    columns : list[str]
        Columns to which RVQ rules should be applied.

    rules : list[dict]
        Each rule must contain:
            {
                "data_code": str,
                "rvq_code": str,
                "match_type": {"full", "prefix", "suffix", "contains"}
            }

    negative_rule_enabled : bool, optional
        If True, negative numeric values are flagged with `negative_rvq_code`.

    negative_rvq_code : str or None, optional
        RVQ code to apply to negative values.

    negative_exceptions : list[str] or None, optional
        Columns exempt from the negative‑value rule.

    keep_original : bool, optional
        If False, matched values are replaced with empty strings.

    remove_empty_rvq_cols : bool, optional
        If True, RVQ columns containing only empty values are removed.

    Returns
    -------
    cleaned_df : pandas.DataFrame
        DataFrame with RVQ columns added and values optionally cleaned.

    summary_dict : dict
        A dictionary summarizing RVQ assignments:
            {
                column_name: {rvq_code: count},
                "_rvq_task": True,
                "warnings": str (optional)
            }

    Notes
    -----
    • Detection‑limit tables are no longer returned; they are stored in
    st.session_state.supplementary_outputs for the summary renderer.
    • Hard validation errors raise exceptions.
    • Soft validation issues (e.g., missing columns) are recorded in
    summary_dict["warnings"].
    """

    # -----------------------------------------------------
    # 1. VALIDATION - Hard Errors
    # -----------------------------------------------------
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    if not isinstance(columns, list):
        raise ValueError("columns must be a list of column names.")

    if not isinstance(rules, list):
        raise ValueError("rules must be a list of rule dictionaries.")

    for rule in rules:
        if not all(k in rule for k in ["data_code", "rvq_code", "match_type"]):
            raise ValueError("Each rule must contain data_code, rvq_code, and match_type.")

        if rule["match_type"] not in {"full", "prefix", "suffix", "contains"}:
            raise ValueError(f"Invalid match_type '{rule['match_type']}'.")

    if negative_exceptions is not None and not isinstance(negative_exceptions, list):
        raise ValueError("negative_exceptions must be a list or None.")

    cleaned_df = df.copy()

    # -----------------------------------------------------
    # 2. VALIDATION - Soft Checks
    # -----------------------------------------------------
    warnings = []

    missing_cols = [c for c in columns if c not in cleaned_df.columns]
    if missing_cols:
        warnings.append(f"Columns not found and skipped: {missing_cols}")
        columns = [c for c in columns if c in cleaned_df.columns]

    if negative_rule_enabled and not negative_rvq_code:
        warnings.append("Negative rule enabled but no negative_rvq_code provided.")

    if negative_exceptions is None:
        negative_exceptions = []


    # -----------------------------------------------------
    # 3. CORE PROCESSING (Simplified)
    # -----------------------------------------------------
    summary_dict = {}        # Counts of RVQ codes per column
    detection_limits = {}    # Extracted detection limits per column/RVQ

    for col in columns:

        # -------------------------------------------------
        # 3A. Create the RVQ column beside the data column
        # -------------------------------------------------
        rvq_col = f"{col}_RVQ"

        if rvq_col in cleaned_df.columns:
            cleaned_df = cleaned_df.drop(columns=[rvq_col])

        col_pos = cleaned_df.columns.get_loc(col)
        cleaned_df.insert(col_pos + 1, rvq_col, "")

        summary_dict[col] = {}
        detection_limits[col] = {}

        # Work with strings for pattern matching
        series = cleaned_df[col].astype(str)
        
        # -------------------------------------------------
        # 3B. Apply each RVQ rule
        # -------------------------------------------------
        for rule in rules:
            code = rule["data_code"]      # e.g., "<", "-1", "L"
            rvq  = rule["rvq_code"]       # e.g., "BDL", "ND"
            match = rule["match_type"]    # "full" or "contains"

            # -------------------------
            # Determine matching rows
            # -------------------------
            if match == "full":
                # Cell must equal the data code exactly
                mask = series == code

            elif match == "contains":

                # Special case: user enters "nan"
                if code.lower() == "nan":
                    mask = (
                        series.str.contains("nan", case=False, na=False) |
                        (series.str.strip() == "") |   # blank cells
                        (series == "nan") |
                        (series == "NaN") |
                        (series == "NAN")
                    )
                else:
                    # Normal contains rule: code appears anywhere in the cell
                    mask = series.str.contains(re.escape(code), na=False)

            else:
                # Should never happen, but safe fallback
                mask = False

            if not mask.any():
                continue


            # -------------------------------------------------
            # Assign RVQ code to matching rows
            # -------------------------------------------------
            cleaned_df.loc[mask, rvq_col] = rvq
            summary_dict[col][rvq] = summary_dict[col].get(rvq, 0) + mask.sum()

            # -------------------------------------------------
            # Extract detection limits
            # -------------------------------------------------

            # FULL MATCH CASE:
            # If the entire cell equals the data code, and the code itself
            # contains a number (e.g., "-1"), then that number is the limit.
            if match == "full":
                nums = re.findall(r"([0-9]*\.?[0-9]+)", code)
                if nums:
                    limit = float(nums[0])
                    detection_limits[col].setdefault(rvq, {})
                    detection_limits[col][rvq][limit] = (
                        detection_limits[col][rvq].get(limit, 0) + mask.sum()
                    )

            # CONTAINS CASE:
            # Extract ANY number in the cell (except those inside the code itself)
            if match == "contains":
                # Find all numbers in each matching cell
                number_lists = series[mask].str.findall(r"([0-9]*\.?[0-9]+)")

                for nums in number_lists:
                    if nums:
                        limit = float(nums[0])  # Use the first number found
                        detection_limits[col].setdefault(rvq, {})
                        detection_limits[col][rvq][limit] = (
                            detection_limits[col][rvq].get(limit, 0) + 1
                        )

            # -------------------------------------------------
            # Optionally remove original data code
            # -------------------------------------------------
            if not keep_original:
                cleaned_df.loc[mask, col] = ""


        # -----------------------------------------------------
        # 3D. Negative-value rule (runs AFTER manual rules)
        # -----------------------------------------------------
        if negative_rule_enabled and col not in negative_exceptions and negative_rvq_code:

            numeric = pd.to_numeric(cleaned_df[col], errors="coerce")

            # Only flag negative values that do NOT already have an RVQ
            neg_mask = (numeric < 0) & (cleaned_df[rvq_col] == "")

            if neg_mask.any():
                cleaned_df.loc[neg_mask, rvq_col] = negative_rvq_code
                summary_dict[col][negative_rvq_code] = (
                    summary_dict[col].get(negative_rvq_code, 0) + neg_mask.sum()
                )

                # Detection limit = absolute value of the negative number
                for val in numeric[neg_mask].dropna():
                    limit = abs(float(val))
                    detection_limits[col].setdefault(negative_rvq_code, {})
                    detection_limits[col][negative_rvq_code][limit] = (
                        detection_limits[col][negative_rvq_code].get(limit, 0) + 1
                    )

                if not keep_original:
                    cleaned_df.loc[neg_mask, col] = ""



    # -----------------------------------------------------
    # Remove empty RVQ columns
    # -----------------------------------------------------
    if remove_empty_rvq_cols:
        to_drop = []
        for col in cleaned_df.columns:
            if col.endswith("_RVQ") and cleaned_df[col].replace("", pd.NA).isna().all():
                to_drop.append(col)
        if to_drop:
            cleaned_df = cleaned_df.drop(columns=to_drop)

    # -----------------------------------------------------
    # 4. SUMMARY
    # -----------------------------------------------------
    summary_dict["_rvq_task"] = True
    if warnings:
        summary_dict["warnings"] = "; ".join(warnings)

    # -----------------------------------------------------
    # 5. SUMMARY DATAFRAME
    # -----------------------------------------------------
    summary_rows = []

    for col, rvqs in summary_dict.items():
        if col.startswith("_"):
            continue

        for rvq_code, count in rvqs.items():

            if rvq_code in detection_limits[col]:
                for limit, limit_count in detection_limits[col][rvq_code].items():
                    summary_rows.append({
                        "Variable": col,
                        "RVQ Code": rvq_code,
                        "Detection Limit": limit,
                        "Count": limit_count
                    })
            else:
                summary_rows.append({
                    "Variable": col,
                    "RVQ Code": rvq_code,
                    "Detection Limit": None,
                    "Count": count
                })

    summary_df = pd.DataFrame(summary_rows)

    # -----------------------------------------------------
    # 6. RETURN (pure, Streamlit‑free)
    # -----------------------------------------------------
    return cleaned_df, summary_dict, summary_df

